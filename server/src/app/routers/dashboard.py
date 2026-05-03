"""
Dashboard Router

Endpoints:
  GET /dashboard/overview      → Overview of all accessible elderly
  GET /elderly/{elderly_id}/health/trends → Health trends data (7d/30d)

Authentication:
  All endpoints require JWT bearer token.
  - Caregivers see their own elderly profiles
  - Viewers see elderly they have accepted access to
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.dashboard import (
    DashboardOverviewResponse,
    HealthTrendsResponse,
)
from src.app.services import dashboard_service
from src.app.core.auth import get_current_user, require_elderly_access
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["dashboard"])


@router.get(
    "/dashboard/overview",
    response_model=DashboardOverviewResponse,
    summary="Get dashboard overview",
    description=(
        "Returns a list of all elderly profiles the current user has access to. "
        "Caregivers see their own elderly, viewers see elderly they have accepted access to. "
        "Each entry includes basic info and the latest health status if available."
    ),
)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOverviewResponse:
    return await dashboard_service.get_dashboard_overview(
        user=current_user,
        db=db,
    )


@router.get(
    "/elderly/{elderly_id}/health/trends",
    response_model=HealthTrendsResponse,
    summary="Get health trends for an elderly person",
    description=(
        "Returns health data trends over a specified period (7d or 30d). "
        "Data is aggregated by date, showing vital parameters for each day. "
        "Includes summary statistics (min, max, avg) for each parameter. "
        "Requires caregiver owner or viewer with accepted invitation."
    ),
)
async def get_health_trends(
    elderly_id: uuid.UUID,
    range: str = Query("7d", pattern="^(7d|30d)$", description="Trend range: 7d or 30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthTrendsResponse:
    _, _, _ = await require_elderly_access(elderly_id, current_user, db)

    try:
        return await dashboard_service.get_health_trends(
            elderly_id=elderly_id,
            range=range,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )