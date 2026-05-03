"""
Notification Pydantic schemas.
REQ-019: Notify on new health record (caregiver + all viewers)
REQ-020: Notify on critical status
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.database.enums import NotificationChannel, NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    recipient_id: UUID
    elderly_id: Optional[UUID] = None
    notification_type: NotificationType
    channel: NotificationChannel
    title: str
    body: str
    payload: Optional[dict] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    total: int
    notifications: list[NotificationResponse]


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    id: UUID
    user_id: UUID
    notification_type: NotificationType
    email_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    notification_type: NotificationType
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None


class NotificationPreferenceList(BaseModel):
    preferences: list[NotificationPreferenceResponse]


class MarkReadResponse(BaseModel):
    success: bool
    marked_count: int = 1