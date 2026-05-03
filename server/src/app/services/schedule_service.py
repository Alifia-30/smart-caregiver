"""
Schedule Service — business logic for schedules and alarms.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enums import (
    InvitationStatus,
    NotificationChannel,
    NotificationType,
)
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.notification import Notification
from src.database.models.schedule import Schedule, ScheduleAlarm


async def create_schedule(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    creator_id: uuid.UUID,
    schedule_type: str,
    title: str,
    scheduled_at: datetime,
    description: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    recurrence_type: str = "none",
    recurrence_rule: Optional[str] = None,
    recurrence_end_at: Optional[datetime] = None,
    reminder_minutes: Optional[List[int]] = None,
    source: str = "manual",
    ai_recommendation_id: Optional[uuid.UUID] = None,
) -> Schedule:
    """
    Create a schedule with optional alarms.
    """
    schedule = Schedule(
        elderly_id=elderly_id,
        created_by=creator_id,
        ai_recommendation_id=ai_recommendation_id,
        schedule_type=schedule_type,
        title=title,
        description=description,
        source=source,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        recurrence_type=recurrence_type,
        recurrence_rule=recurrence_rule,
        recurrence_end_at=recurrence_end_at,
    )
    db.add(schedule)
    await db.flush()

    if reminder_minutes:
        for mins in reminder_minutes:
            alarm_at = scheduled_at - timedelta(minutes=mins)
            alarm = ScheduleAlarm(
                schedule_id=schedule.id,
                reminder_minutes=mins,
                alarm_at=alarm_at,
            )
            db.add(alarm)

    await db.flush()
    await db.refresh(schedule, ["alarms"])
    return schedule


async def get_schedule(
    db: AsyncSession,
    schedule_id: uuid.UUID,
) -> Optional[Schedule]:
    """Get a schedule by ID."""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_schedules(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    schedule_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[Schedule]]:
    """List schedules for an elderly profile."""
    conditions = [Schedule.elderly_id == elderly_id]

    if schedule_type:
        conditions.append(Schedule.schedule_type == schedule_type)
    if is_active is not None:
        conditions.append(Schedule.is_active == is_active)
    if from_date:
        conditions.append(Schedule.scheduled_at >= from_date)
    if to_date:
        conditions.append(Schedule.scheduled_at <= to_date)

    count_stmt = select(func.count()).select_from(Schedule).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    stmt = (
        select(Schedule)
        .where(and_(*conditions))
        .order_by(Schedule.scheduled_at)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    return total, list(schedules)


async def update_schedule(
    db: AsyncSession,
    schedule_id: uuid.UUID,
    schedule_type: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    scheduled_at: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    recurrence_type: Optional[str] = None,
    recurrence_rule: Optional[str] = None,
    recurrence_end_at: Optional[datetime] = None,
    is_active: Optional[bool] = None,
    reminder_minutes: Optional[List[int]] = None,
) -> Schedule:
    """Update a schedule and its alarms."""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise ValueError(f"Schedule {schedule_id} not found")

    if schedule_type:
        schedule.schedule_type = schedule_type
    if title is not None:
        schedule.title = title
    if description is not None:
        schedule.description = description
    if scheduled_at:
        schedule.scheduled_at = scheduled_at
    if duration_minutes is not None:
        schedule.duration_minutes = duration_minutes
    if recurrence_type:
        schedule.recurrence_type = recurrence_type
    if recurrence_rule is not None:
        schedule.recurrence_rule = recurrence_rule
    if recurrence_end_at is not None:
        schedule.recurrence_end_at = recurrence_end_at
    if is_active is not None:
        schedule.is_active = is_active

    if reminder_minutes is not None:
        existing_alarms = select(ScheduleAlarm).where(
            ScheduleAlarm.schedule_id == schedule_id
        )
        alarm_result = await db.execute(existing_alarms)
        existing = alarm_result.scalars().all()
        for alarm in existing:
            await db.delete(alarm)

        if reminder_minutes:
            for mins in reminder_minutes:
                alarm_at = schedule.scheduled_at - timedelta(minutes=mins)
                alarm = ScheduleAlarm(
                    schedule_id=schedule.id,
                    reminder_minutes=mins,
                    alarm_at=alarm_at,
                )
                db.add(alarm)

    await db.flush()
    await db.refresh(schedule, ["alarms"])
    return schedule


async def delete_schedule(
    db: AsyncSession,
    schedule_id: uuid.UUID,
) -> bool:
    """Delete a schedule (cascades to alarms)."""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise ValueError(f"Schedule {schedule_id} not found")

    await db.delete(schedule)
    await db.flush()
    return True


async def mark_complete(
    db: AsyncSession,
    schedule_id: uuid.UUID,
) -> Schedule:
    """Mark a schedule as completed."""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise ValueError(f"Schedule {schedule_id} not found")

    schedule.is_completed = True
    schedule.completed_at = datetime.now(timezone.utc)

    await db.flush()
    return schedule


async def dispatch_due_alarms(
    db: AsyncSession,
) -> tuple[int, int]:
    """
    Poll for due alarms and create notifications.
    For MVP, called manually via internal endpoint.
    """
    now = datetime.now(timezone.utc)

    stmt = (
        select(ScheduleAlarm)
        .where(
            ScheduleAlarm.is_sent == False,
            ScheduleAlarm.alarm_at <= now,
        )
        .limit(100)
    )
    result = await db.execute(stmt)
    due_alarms = result.scalars().all()

    if not due_alarms:
        return 0, 0

    notifications_created = 0
    processed_count = 0

    for alarm in due_alarms:
        schedule = alarm.schedule
        if not schedule or not schedule.is_active:
            alarm.is_sent = True
            alarm.sent_at = now
            await db.flush()
            continue

        elderly = schedule.elderly
        if not elderly:
            alarm.is_sent = True
            alarm.sent_at = now
            await db.flush()
            continue

        recipient_ids = [elderly.caregiver_id]

        viewers_stmt = select(ViewerInvitation).where(
            ViewerInvitation.elderly_id == elderly.id,
            ViewerInvitation.status == InvitationStatus.ACCEPTED,
        )
        viewers_result = await db.execute(viewers_stmt)
        viewers = viewers_result.scalars().all()
        for viewer in viewers:
            if viewer.viewer_id:
                recipient_ids.append(viewer.viewer_id)

        title = f"Reminder: {schedule.title}"
        body = f"It's time for {schedule.schedule_type.replace('_', ' ')}: {schedule.title}"

        payload = {
            "schedule_id": str(schedule.id),
            "alarm_id": str(alarm.id),
            "elderly_id": str(elderly.id),
            "elderly_name": elderly.full_name,
            "schedule_type": schedule.schedule_type,
            "title": schedule.title,
            "scheduled_at": schedule.scheduled_at.isoformat(),
            "reminder_minutes": alarm.reminder_minutes,
        }

        for recipient_id in recipient_ids:
            notification = Notification(
                recipient_id=recipient_id,
                elderly_id=elderly.id,
                notification_type=NotificationType.ALARM_REMINDER,
                channel=NotificationChannel.IN_APP,
                title=title,
                body=body,
                payload=payload,
            )
            db.add(notification)
            notifications_created += 1

        alarm.is_sent = True
        alarm.sent_at = now
        processed_count += 1

    await db.flush()
    return processed_count, notifications_created