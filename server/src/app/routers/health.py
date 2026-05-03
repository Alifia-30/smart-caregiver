"""
Health Records Router

Endpoints:
  POST   /health/records                          → Create record + auto fuzzy analysis
  GET    /health/records/{record_id}              → Detail of one record
  POST   /health/records/{record_id}/analyze    → Re-run fuzzy without creating new record
  GET    /elderly/{elderly_id}/health/records     → Paginated list (newest first)
  GET    /elderly/{elderly_id}/health/latest      → Latest record summary

Authentication:
  All endpoints require JWT bearer token authentication.
  - Caregiver can read/write health records for their elderly profiles
  - Viewer with accepted invitation can only read health records
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.health import (
    HealthRecordCreate,
    HealthRecordListResponse,
    HealthRecordResponse,
    HealthRecordSummary,
)
from src.app.services import health_service
from src.app.core.auth import get_current_user, require_caregiver_owner, require_elderly_access
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["health"])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/health/records",
    response_model=HealthRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit health data and run fuzzy analysis",
    description=(
        "Creates a new health record for the specified elderly person and "
        "automatically runs fuzzy logic analysis across three domains: "
        "Cardiovascular, Metabolic, and Infection/Respiratory. "
        "The analysis result is embedded in the response and persisted to the database. "
        "Requires caregiver owner authentication."
    ),
)
async def create_health_record(
    payload: HealthRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthRecordResponse:
    _, _ = await require_caregiver_owner(payload.elderly_id, current_user, db)
    return await health_service.create_health_record(
        db=db,
        payload=payload,
        recorded_by=current_user.id,
    )


@router.get(
    "/health/records/{record_id}",
    response_model=HealthRecordResponse,
    summary="Get a health record by ID",
    description="Retrieves a single health record with its stored fuzzy analysis scores.",
)
async def get_health_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthRecordResponse:
    record = await health_service.get_health_record(db=db, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health record {record_id} not found.",
        )
    await require_caregiver_owner(record.elderly_id, current_user, db)
    return record


@router.post(
    "/health/records/{record_id}/analyze",
    response_model=HealthRecordResponse,
    summary="Re-run fuzzy analysis on an existing record",
    description=(
        "Re-executes all applicable fuzzy modules on the stored vital parameters "
        "and overwrites the fuzzy scores in the database.  Useful when fuzzy "
        "membership functions are updated and historical records need recalculation."
    ),
)
async def reanalyze_health_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthRecordResponse:
    record = await health_service.get_health_record(db=db, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health record {record_id} not found.",
        )
    _, _ = await require_caregiver_owner(record.elderly_id, current_user, db)
    return await health_service.reanalyze_health_record(db=db, record_id=record_id)


@router.get(
    "/elderly/{elderly_id}/health/records",
    response_model=HealthRecordListResponse,
    summary="List all health records for an elderly person",
    description=(
        "Returns paginated health records ordered by measurement date (newest first). "
        "Requires caregiver owner or viewer with accepted invitation."
    ),
)
async def list_health_records(
    elderly_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100, description="Number of records per page"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthRecordListResponse:
    _, _ = await require_elderly_access(elderly_id, current_user, db)
    total, records = await health_service.list_health_records(
        db=db,
        elderly_id=elderly_id,
        limit=limit,
        offset=offset,
    )
    return HealthRecordListResponse(total=total, records=records)


@router.get(
    "/elderly/{elderly_id}/health/latest",
    response_model=HealthRecordSummary,
    summary="Get the latest health record summary",
    description="Returns a lightweight summary of the most recent health record for quick status checks.",
)
async def get_latest_health_record(
    elderly_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthRecordSummary:
    _, _ = await require_elderly_access(elderly_id, current_user, db)
    summary = await health_service.get_latest_health_record(
        db=db, elderly_id=elderly_id
    )
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No health records found for elderly {elderly_id}.",
        )
    return summary
