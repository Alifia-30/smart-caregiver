"""
Notification Router

Endpoints:
  GET    /notifications                    → List notifications (paginated)
  GET    /notifications/unread-count         → Get unread count
  PATCH  /notifications/{id}/read            → Mark single as read
  PATCH  /notifications/read-all            → Mark all as read
  GET    /notification-preferences           → Get all preferences
  PUT    /notification-preferences           → Update a preference

Authentication:
  All endpoints require JWT bearer token.
  Users can only access their own notifications.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.notification import (
    MarkReadResponse,
    NotificationList,
    NotificationPreferenceList,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
    UnreadCountResponse,
)
from src.app.services import notification_service
from src.app.core.auth import get_current_user
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["notifications"])


@router.get("", response_model=NotificationList)
async def list_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of notifications for the current user.
    """
    total, notifications = await notification_service.get_notifications(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )

    notification_responses = [
        NotificationResponse(
            id=n.id,
            recipient_id=n.recipient_id,
            elderly_id=n.elderly_id,
            notification_type=n.notification_type,
            channel=n.channel,
            title=n.title,
            body=n.body,
            payload=n.payload,
            is_read=n.is_read,
            read_at=n.read_at,
            created_at=n.created_at,
        )
        for n in notifications
    ]

    return NotificationList(total=total, notifications=notification_responses)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get count of unread notifications for the current user.
    """
    count = await notification_service.get_unread_count(
        db=db,
        user_id=current_user.id,
    )
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a single notification as read.
    """
    try:
        await notification_service.mark_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return MarkReadResponse(success=True, marked_count=1)


@router.patch("/read-all", response_model=MarkReadResponse)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all notifications as read for the current user.
    """
    marked_count = await notification_service.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )

    return MarkReadResponse(success=True, marked_count=marked_count)


@router.get("/notification-preferences", response_model=NotificationPreferenceList)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all notification preferences for the current user.
    """
    preferences = await notification_service.get_preferences(
        db=db,
        user_id=current_user.id,
    )

    preference_responses = [
        NotificationPreferenceResponse(
            id=p.id,
            user_id=p.user_id,
            notification_type=p.notification_type,
            email_enabled=p.email_enabled,
            push_enabled=p.push_enabled,
            in_app_enabled=p.in_app_enabled,
            updated_at=p.updated_at,
        )
        for p in preferences
    ]

    return NotificationPreferenceList(preferences=preference_responses)


@router.put("/notification-preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    payload: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update or create a notification preference.
    """
    preference = await notification_service.update_preference(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )

    return NotificationPreferenceResponse(
        id=preference.id,
        user_id=preference.user_id,
        notification_type=preference.notification_type,
        email_enabled=preference.email_enabled,
        push_enabled=preference.push_enabled,
        in_app_enabled=preference.in_app_enabled,
        updated_at=preference.updated_at,
    )