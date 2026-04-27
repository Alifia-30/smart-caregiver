"""
Notification models
REQ-019: Notify on new health record (caregiver + all viewers)
REQ-020: Notify on critical status
REQ-021: Weekly summary notification
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.enums import NotificationChannel, NotificationType


class Notification(Base):
    """
    Single-table for all notification types and channels.

    Fan-out strategy for REQ-019 / REQ-020:
        1. Health record saved for elderly_id X.
        2. Service fetches all accepted viewer_invitations WHERE elderly_id = X.
        3. Inserts one Notification row per recipient (caregiver + each viewer).
        4. Background worker reads unsent rows → dispatches via email/push/in-app.

    metadata (JSONB) stores context per notification_type, e.g.:
        health_recorded  → { "health_record_id": "...", "health_status": "needs_attention" }
        critical_alert   → { "health_record_id": "...", "triggered_params": ["systolic_bp"] }
        alarm_reminder   → { "schedule_id": "...", "schedule_title": "Minum Obat Pagi" }
        weekly_summary   → { "period_start": "...", "period_end": "..." }
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Which elderly triggered this notification (for quick lookup / filtering)
    elderly_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("elderly_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Content ───────────────────────────────────────────────────────────────
    notification_type: Mapped[NotificationType] = mapped_column(
        String(40), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        String(20), nullable=False, default=NotificationChannel.IN_APP
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # ── State ─────────────────────────────────────────────────────────────────
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # sent_at = None means not yet dispatched (worker polls this)
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    recipient: Mapped["User"] = relationship(  # noqa: F821
        back_populates="notifications", lazy="select"
    )
    elderly: Mapped[Optional["ElderlyProfile"]] = relationship(lazy="select")  # noqa: F821

    from sqlalchemy import Index

    __table_args__ = (
        # Inbox query: unread notifications for a user, newest first
        Index("ix_notifications_inbox", "recipient_id", "is_read", "created_at"),
        # Worker query: unsent notifications
        Index(
            "ix_notifications_unsent",
            "sent_at",
            postgresql_where="sent_at IS NULL",
        ),
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.notification_type} recipient={self.recipient_id}>"


class NotificationPreference(Base):
    """
    Per-user, per-type channel preferences.
    If no row exists for a (user_id, notification_type) pair,
    service falls back to default (all channels enabled).
    """

    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        String(40), nullable=False
    )

    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="notification_preferences", lazy="select"
    )

    from sqlalchemy import UniqueConstraint

    __table_args__ = (
        UniqueConstraint(
            "user_id", "notification_type", name="uq_notif_pref_user_type"
        ),
    )

    def __repr__(self) -> str:
        return f"<NotificationPreference user_id={self.user_id} type={self.notification_type}>"
