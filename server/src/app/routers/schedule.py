"""
Schedule Router

Endpoints:
  POST   /elderly/{elderly_id}/schedules              → Create schedule
  GET    /elderly/{elderly_id}/schedules              → List schedules
  GET    /schedules/{schedule_id}                    → Get schedule
  PUT    /schedules/{schedule_id}                    → Update schedule
  DELETE /schedules/{schedule_id}                    → Delete schedule
  PATCH  /schedules/{schedule_id}/complete           → Mark complete

Internal (MVP):
  POST   /internal/jobs/dispatch-due-alarms           → Dispatch pending alarms

Authentication:
  All endpoints require caregiver owner or viewer with accepted invitation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.schedule import (
    AlarmDispatchResponse,
    ScheduleCompleteResponse,
    ScheduleCreate,
    ScheduleList,
    ScheduleResponse,
    ScheduleUpdate,
)
from src.app.services import schedule_service
from src.app.core.auth import get_current_user, require_elderly_access
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["schedules"])


def _to_schedule_response(schedule) -> ScheduleResponse:
    """Convert ORM model to response schema."""
    return ScheduleResponse(
        id=schedule.id,
        elderly_id=schedule.elderly_id,
        created_by=schedule.created_by,
        ai_recommendation_id=schedule.ai_recommendation_id,
        schedule_type=schedule.schedule_type,
        title=schedule.title,
        description=schedule.description,
        source=schedule.source,
        scheduled_at=schedule.scheduled_at,
        duration_minutes=schedule.duration_minutes,
        recurrence_type=schedule.recurrence_type,
        recurrence_rule=schedule.recurrence_rule,
        recurrence_end_at=schedule.recurrence_end_at,
        is_active=schedule.is_active,
        is_completed=schedule.is_completed,
        completed_at=schedule.completed_at,
        alarms=[
            type("Obj", (), {
                "id": a.id,
                "schedule_id": a.schedule_id,
                "reminder_minutes": a.reminder_minutes,
                "alarm_at": a.alarm_at,
                "is_sent": a.is_sent,
                "sent_at": a.sent_at,
                "created_at": a.created_at,
            })()
            for a in schedule.alarms
        ],
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def _to_schedule_response_from_service(schedule) -> ScheduleResponse:
    """Convert Schedule from service (may not have alarms loaded) to response schema.
    This handles both cases - with and without alarms relationship loaded.
    """
    alarms = getattr(schedule, 'alarms', []) or []
    return ScheduleResponse(
        id=schedule.id,
        elderly_id=schedule.elderly_id,
        created_by=schedule.created_by,
        ai_recommendation_id=schedule.ai_recommendation_id,
        schedule_type=schedule.schedule_type,
        title=schedule.title,
        description=schedule.description,
        source=schedule.source,
        scheduled_at=schedule.scheduled_at,
        duration_minutes=schedule.duration_minutes,
        recurrence_type=schedule.recurrence_type,
        recurrence_rule=schedule.recurrence_rule,
        recurrence_end_at=schedule.recurrence_end_at,
        is_active=schedule.is_active,
        is_completed=schedule.is_completed,
        completed_at=schedule.completed_at,
        alarms=[
            type("Obj", (), {
                "id": a.id,
                "schedule_id": a.schedule_id,
                "reminder_minutes": a.reminder_minutes,
                "alarm_at": a.alarm_at,
                "is_sent": a.is_sent,
                "sent_at": a.sent_at,
                "created_at": a.created_at,
            })()
            for a in alarms
        ],
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


@router.post(
    "/elderly/{elderly_id}/schedules",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    elderly_id: uuid.UUID,
    payload: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new schedule for an elderly profile."""
    await require_elderly_access(elderly_id, current_user, db)

    try:
        schedule = await schedule_service.create_schedule(
            db=db,
            elderly_id=elderly_id,
            creator_id=current_user.id,
            schedule_type=payload.schedule_type.value,
            title=payload.title,
            description=payload.description,
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            recurrence_type=payload.recurrence_type.value,
            recurrence_rule=payload.recurrence_rule,
            recurrence_end_at=payload.recurrence_end_at,
            reminder_minutes=payload.reminder_minutes,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return _to_schedule_response(schedule)


@router.get("/elderly/{elderly_id}/schedules", response_model=ScheduleList)
async def list_schedules(
    elderly_id: uuid.UUID,
    schedule_type: str | None = Query(None, description="Filter by type"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    from_date: datetime | None = Query(None, description="Filter from date"),
    to_date: datetime | None = Query(None, description="Filter to date"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List schedules for an elderly profile."""
    await require_elderly_access(elderly_id, current_user, db)

    total, schedules = await schedule_service.list_schedules(
        db=db,
        elderly_id=elderly_id,
        schedule_type=schedule_type,
        is_active=is_active,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )

    return ScheduleList(
        total=total,
        schedules=[_to_schedule_response(s) for s in schedules]
    )


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a schedule by ID."""
    schedule = await schedule_service.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found",
        )

    await require_elderly_access(schedule.elderly_id, current_user, db)

    return _to_schedule_response(schedule)


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: uuid.UUID,
    payload: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a schedule."""
    schedule = await schedule_service.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found",
        )

    await require_elderly_access(schedule.elderly_id, current_user, db)

    try:
        schedule = await schedule_service.update_schedule(
            db=db,
            schedule_id=schedule_id,
            schedule_type=payload.schedule_type.value if payload.schedule_type else None,
            title=payload.title,
            description=payload.description,
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            recurrence_type=payload.recurrence_type.value if payload.recurrence_type else None,
            recurrence_rule=payload.recurrence_rule,
            recurrence_end_at=payload.recurrence_end_at,
            is_active=payload.is_active,
            reminder_minutes=payload.reminder_minutes,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return _to_schedule_response(schedule)


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a schedule."""
    schedule = await schedule_service.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found",
        )

    await require_elderly_access(schedule.elderly_id, current_user, db)

    try:
        await schedule_service.delete_schedule(db, schedule_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return {"success": True, "schedule_id": schedule_id}


@router.patch(
    "/schedules/{schedule_id}/complete",
    response_model=ScheduleCompleteResponse,
)
async def mark_schedule_complete(
    schedule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a schedule as completed."""
    schedule = await schedule_service.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found",
        )

    await require_elderly_access(schedule.elderly_id, current_user, db)

    try:
        schedule = await schedule_service.mark_complete(db, schedule_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return ScheduleCompleteResponse(
        success=True,
        schedule_id=schedule.id,
        completed_at=schedule.completed_at,
    )


@router.post(
    "/internal/jobs/dispatch-due-alarms",
    response_model=AlarmDispatchResponse,
)
async def dispatch_due_alarms(
    db: AsyncSession = Depends(get_db),
):
    """
    Internal endpoint to dispatch due alarms.
    For MVP, call manually. Later can be scheduled via APScheduler/Celery.
    """
    dispatched, notifications = await schedule_service.dispatch_due_alarms(db)
    return AlarmDispatchResponse(
        dispatched_count=dispatched,
        notifications_created=notifications,
    )