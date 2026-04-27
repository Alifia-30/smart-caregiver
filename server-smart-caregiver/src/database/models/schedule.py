"""
Schedule and alarm models
REQ-013: Schedules (medication, checkup, daily activity)
REQ-014: Alarm notifications per schedule
REQ-018: AI-approved activities auto-added to schedule
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.enums import RecurrenceType, ScheduleType


class Schedule(Base):
    """
    Calendar entry for an elderly person.

    source: 'manual' (caregiver created) | 'ai_approved' (from AIActivityRecommendation)
    When an AI recommendation is approved (REQ-018), service creates a Schedule
    with source='ai_approved' and ai_recommendation_id set.

    Recurring schedules use recurrence_type + recurrence_rule (iCal RRULE string).
    E.g. RRULE:FREQ=DAILY;BYHOUR=8;BYMINUTE=0 — parsed by the alarm scheduler.
    """

    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    elderly_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("elderly_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Link back to AI recommendation if auto-generated (REQ-018)
    ai_recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_activity_recommendations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Content ───────────────────────────────────────────────────────────────
    schedule_type: Mapped[ScheduleType] = mapped_column(
        String(30), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual"  # 'manual' | 'ai_approved'
    )

    # ── Timing ────────────────────────────────────────────────────────────────
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)

    # ── Recurrence (REQ-013) ──────────────────────────────────────────────────
    recurrence_type: Mapped[RecurrenceType] = mapped_column(
        String(20), nullable=False, default=RecurrenceType.NONE
    )
    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True  # iCal RRULE for complex patterns
    )
    recurrence_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    elderly: Mapped["ElderlyProfile"] = relationship(  # noqa: F821
        back_populates="schedules", lazy="select"
    )
    creator: Mapped[Optional["User"]] = relationship(lazy="select")  # noqa: F821
    alarms: Mapped[list["ScheduleAlarm"]] = relationship(
        back_populates="schedule", cascade="all, delete-orphan", lazy="selectin"
    )
    ai_recommendation: Mapped[Optional["AIActivityRecommendation"]] = relationship(  # noqa: F821
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Schedule id={self.id} title={self.title} type={self.schedule_type}>"


class ScheduleAlarm(Base):
    """
    One or more alarm triggers per schedule (REQ-014).

    alarm_at = schedule.scheduled_at - timedelta(minutes=reminder_minutes)
    Background job (Celery beat / APScheduler) polls:
        SELECT * FROM schedule_alarms
        WHERE is_sent = false AND alarm_at <= NOW()
    """

    __tablename__ = "schedule_alarms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reminder_minutes: Mapped[int] = mapped_column(nullable=False)  # 10, 30, 60, etc.
    alarm_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    schedule: Mapped["Schedule"] = relationship(back_populates="alarms", lazy="select")

    # ── Index for background job polling ─────────────────────────────────────
    from sqlalchemy import Index

    __table_args__ = (
        Index("ix_schedule_alarms_pending", "alarm_at", postgresql_where="is_sent = false"),
    )

    def __repr__(self) -> str:
        return f"<ScheduleAlarm schedule_id={self.schedule_id} alarm_at={self.alarm_at} sent={self.is_sent}>"
