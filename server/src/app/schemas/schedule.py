"""
Schedule Pydantic schemas.
REQ-013: Create/read/update/delete schedules (medication, checkup, daily activity)
REQ-014: Alarm reminders per schedule
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from src.database.enums import RecurrenceType, ScheduleType


class ScheduleAlarmResponse(BaseModel):
    id: UUID
    schedule_id: UUID
    reminder_minutes: int
    alarm_at: datetime
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduleCreate(BaseModel):
    schedule_type: ScheduleType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_rule: Optional[str] = None
    recurrence_end_at: Optional[datetime] = None
    reminder_minutes: List[int] = Field(
        default_factory=list,
        description="Minutes before scheduled_at to trigger alarm (e.g. [10, 30, 60])"
    )


class ScheduleUpdate(BaseModel):
    schedule_type: Optional[ScheduleType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    reminder_minutes: Optional[List[int]] = Field(
        None,
        description="Update alarm triggers. Empty list removes all alarms."
    )


class ScheduleResponse(BaseModel):
    id: UUID
    elderly_id: UUID
    created_by: Optional[UUID] = None
    ai_recommendation_id: Optional[UUID] = None
    schedule_type: ScheduleType
    title: str
    description: Optional[str] = None
    source: str
    scheduled_at: datetime
    duration_minutes: Optional[int] = None
    recurrence_type: RecurrenceType
    recurrence_rule: Optional[str] = None
    recurrence_end_at: Optional[datetime] = None
    is_active: bool
    is_completed: bool
    completed_at: Optional[datetime] = None
    alarms: List[ScheduleAlarmResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleList(BaseModel):
    total: int
    schedules: List[ScheduleResponse]


class ScheduleCompleteResponse(BaseModel):
    success: bool
    schedule_id: UUID
    completed_at: datetime


class AlarmDispatchResponse(BaseModel):
    dispatched_count: int
    notifications_created: int