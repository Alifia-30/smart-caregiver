"""
Notification Service — business logic for in-app notifications.

Responsibilities:
  1. Create single notification for a recipient
  2. Create fan-out notifications (caregiver + all accepted viewers)
  3. List, mark read, get preferences for a user
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.notification import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from src.database.enums import InvitationStatus, NotificationChannel, NotificationType
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.notification import Notification, NotificationPreference
from src.database.models.user import User


async def create_notification(
    db: AsyncSession,
    recipient_id: uuid.UUID,
    notification_type: NotificationType,
    title: str,
    body: str,
    elderly_id: Optional[uuid.UUID] = None,
    channel: NotificationChannel = NotificationChannel.IN_APP,
    payload: Optional[dict] = None,
) -> Notification:
    """
    Create a single notification for a recipient.

    Args:
        db: Database session
        recipient_id: UUID of the recipient user
        notification_type: Type of notification
        title: Notification title
        body: Notification body
        elderly_id: Optional elderly ID for context
        channel: Notification channel (default: in_app)
        payload: Optional additional payload

    Returns:
        Created Notification object
    """
    notification = Notification(
        recipient_id=recipient_id,
        elderly_id=elderly_id,
        notification_type=notification_type,
        channel=channel,
        title=title,
        body=body,
        payload=payload,
    )
    db.add(notification)
    await db.flush()
    return notification


async def create_health_record_notification(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    health_record_id: uuid.UUID,
    health_status: str,
) -> list[uuid.UUID]:
    """
    Create notifications when a health record is recorded.
    Fan-out to: caregiver (owner) + all accepted viewers.

    Args:
        db: Database session
        elderly_id: UUID of the elderly profile
        health_record_id: UUID of the created health record
        health_status: Health status from the record

    Returns:
        List of created notification IDs
    """
    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()

    if not elderly:
        return []

    recipient_ids = [elderly.caregiver_id]

    viewers_stmt = select(ViewerInvitation).where(
        ViewerInvitation.elderly_id == elderly_id,
        ViewerInvitation.status == InvitationStatus.ACCEPTED,
    )
    viewers_result = await db.execute(viewers_stmt)
    viewers = viewers_result.scalars().all()

    for viewer in viewers:
        if viewer.viewer_id:
            recipient_ids.append(viewer.viewer_id)

    notifications = []
    notification_type = NotificationType.CRITICAL_ALERT if health_status == "critical" else NotificationType.HEALTH_RECORDED

    title_map = {
        NotificationType.HEALTH_RECORDED: "Health Record Created",
        NotificationType.CRITICAL_ALERT: "Critical Health Alert",
    }

    body_map = {
        NotificationType.HEALTH_RECORDED: f"A new health record has been recorded for {elderly.full_name}.",
        NotificationType.CRITICAL_ALERT: f"Critical health status detected for {elderly.full_name}. Immediate attention required.",
    }

    payload = {
        "health_record_id": str(health_record_id),
        "health_status": health_status,
        "elderly_id": str(elderly_id),
        "elderly_name": elderly.full_name,
    }

    for recipient_id in recipient_ids:
        notification = Notification(
            recipient_id=recipient_id,
            elderly_id=elderly_id,
            notification_type=notification_type,
            channel=NotificationChannel.IN_APP,
            title=title_map[notification_type],
            body=body_map[notification_type],
            payload=payload,
        )
        db.add(notification)
        notifications.append(notification)

    await db.flush()
    return [n.id for n in notifications]


async def get_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> tuple[int, list[Notification]]:
    """
    Get paginated notifications for a user.

    Args:
        db: Database session
        user_id: UUID of the user
        limit: Max number of results
        offset: Pagination offset
        unread_only: Filter for unread only

    Returns:
        (total_count, list_of_notifications)
    """
    count_stmt = select(uuid.uuid4()).select_from(Notification).where(
        Notification.recipient_id == user_id
    )
    if unread_only:
        count_stmt = count_stmt.where(Notification.is_read == False)
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    stmt = (
        select(Notification)
        .where(Notification.recipient_id == user_id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
        .offset(offset)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return total, list(notifications)


async def get_unread_count(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """
    Get count of unread notifications for a user.

    Args:
        db: Database session
        user_id: UUID of the user

    Returns:
        Number of unread notifications
    """
    stmt = select(uuid.uuid4()).select_from(Notification).where(
        and_(
            Notification.recipient_id == user_id,
            Notification.is_read == False,
        )
    )
    result = await db.execute(stmt)
    return len(result.all())


async def mark_as_read(
    db: AsyncSession,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Mark a single notification as read.

    Args:
        db: Database session
        notification_id: UUID of the notification
        user_id: UUID of the user (for authorization)

    Returns:
        True if marked successfully

    Raises:
        ValueError: If notification not found or not owned by user
    """
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()

    if not notification:
        raise ValueError("Notification not found")

    if notification.recipient_id != user_id:
        raise ValueError("Not authorized to modify this notification")

    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    await db.flush()
    return True


async def mark_all_as_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """
    Mark all notifications as read for a user.

    Args:
        db: Database session
        user_id: UUID of the user

    Returns:
        Number of notifications marked as read
    """
    stmt = select(Notification).where(
        and_(
            Notification.recipient_id == user_id,
            Notification.is_read == False,
        )
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    now = datetime.now(timezone.utc)
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    await db.flush()
    return len(notifications)


async def get_preferences(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[NotificationPreference]:
    """
    Get all notification preferences for a user.

    Args:
        db: Database session
        user_id: UUID of the user

    Returns:
        List of notification preferences
    """
    stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_preference(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: NotificationPreferenceUpdate,
) -> NotificationPreference:
    """
    Update or create a notification preference for a user.

    Args:
        db: Database session
        user_id: UUID of the user
        payload: Preference update data

    Returns:
        Updated/created preference
    """
    stmt = select(NotificationPreference).where(
        and_(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == payload.notification_type,
        )
    )
    result = await db.execute(stmt)
    preference = result.scalar_one_or_none()

    if preference:
        if payload.email_enabled is not None:
            preference.email_enabled = payload.email_enabled
        if payload.push_enabled is not None:
            preference.push_enabled = payload.push_enabled
        if payload.in_app_enabled is not None:
            preference.in_app_enabled = payload.in_app_enabled
    else:
        preference = NotificationPreference(
            user_id=user_id,
            notification_type=payload.notification_type,
            email_enabled=payload.email_enabled if payload.email_enabled is not None else True,
            push_enabled=payload.push_enabled if payload.push_enabled is not None else True,
            in_app_enabled=payload.in_app_enabled if payload.in_app_enabled is not None else True,
        )
        db.add(preference)

    await db.flush()
    return preference