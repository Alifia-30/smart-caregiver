"""
Health Records Router

Endpoints:
  POST   /health/records                          → Create record + auto fuzzy analysis
  GET    /health/records/{record_id}              → Detail of one record
  POST   /health/records/{record_id}/analyze      → Re-run fuzzy without creating new record
  GET    /elderly/{elderly_id}/health/records     → Paginated list (newest first)
  GET    /elderly/{elderly_id}/health/latest      → Latest record summary

All endpoints return structured JSON responses.  Authentication is handled
via the `recorded_by` parameter which accepts an optional user-id header
(X-User-Id) for now — replace with a proper JWT dependency when auth
middleware is wired up.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.health import (
    HealthRecordCreate,
    HealthRecordListResponse,
    HealthRecordResponse,
    HealthRecordSummary,
)
from src.app.services import health_service
from src.database.session import get_db

router = APIRouter(tags=["health"])


# ── Dependency: optional caller identity ──────────────────────────────────────
# TODO: Replace with JWT bearer dependency when auth middleware is ready.

async def _get_caller_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> Optional[uuid.UUID]:
    """Extract caller user-id from request header (temporary, no JWT yet)."""
    if x_user_id is None:
        return None
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id header must be a valid UUID.",
        )


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
        "The analysis result is embedded in the response and persisted to the database."
    ),
)
async def create_health_record(
    payload: HealthRecordCreate,
    db: AsyncSession = Depends(get_db),
    caller_id: Optional[uuid.UUID] = Depends(_get_caller_id),
) -> HealthRecordResponse:
    return await health_service.create_health_record(
        db=db,
        payload=payload,
        recorded_by=caller_id,
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
) -> HealthRecordResponse:
    record = await health_service.get_health_record(db=db, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health record {record_id} not found.",
        )
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
) -> HealthRecordResponse:
    record = await health_service.reanalyze_health_record(db=db, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health record {record_id} not found.",
        )
    return record


@router.get(
    "/elderly/{elderly_id}/health/records",
    response_model=HealthRecordListResponse,
    summary="List all health records for an elderly person",
    description="Returns paginated health records ordered by measurement date (newest first).",
)
async def list_health_records(
    elderly_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100, description="Number of records per page"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db),
) -> HealthRecordListResponse:
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
) -> HealthRecordSummary:
    summary = await health_service.get_latest_health_record(
        db=db, elderly_id=elderly_id
    )
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No health records found for elderly {elderly_id}.",
        )
    return summary
