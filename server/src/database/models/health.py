"""
Health tracking models
REQ-004: Select elderly to record
REQ-005: Daily health parameters
REQ-006: Daily notes and complaints
REQ-007: Normal / Needs Attention status
REQ-009: Trend data (indexed for 7/30 day queries)
REQ-015: Threshold-based alert triggering
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.enums import HealthParameter, HealthStatus


class HealthRecord(Base):
    """
    One row per health check session.
    All vital parameters recorded together in one session.

    health_status is set automatically by the service layer:
        - Compare each non-null value against HealthThreshold for this elderly.
        - If any value is out of range → NEEDS_ATTENTION or CRITICAL.
        - All values normal or no thresholds defined → NORMAL.
    """

    __tablename__ = "health_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    elderly_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("elderly_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,    # SET NULL if user is deleted; record is preserved
    )

    # ── Vital parameters (REQ-005) ────────────────────────────────────────────
    systolic_bp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # mmHg
    diastolic_bp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)     # mmHg
    blood_sugar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # mg/dL
    heart_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)       # bpm
    body_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # °C
    body_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # kg

    # ── Qualitative notes (REQ-006) ───────────────────────────────────────────
    daily_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    complaints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Computed status (REQ-007) ─────────────────────────────────────────────
    health_status: Mapped[HealthStatus] = mapped_column(
        String(20), nullable=False, default=HealthStatus.NORMAL, index=True
    )

    # ── When was this measured (not when it was entered) ──────────────────────
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    elderly: Mapped["ElderlyProfile"] = relationship(  # noqa: F821
        back_populates="health_records", lazy="select"
    )
    recorder: Mapped[Optional["User"]] = relationship(lazy="select")  # noqa: F821

    # ── Composite index for trend queries (REQ-009) ───────────────────────────
    from sqlalchemy import Index

    __table_args__ = (
        Index("ix_health_records_elderly_recorded", "elderly_id", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<HealthRecord id={self.id} elderly_id={self.elderly_id} status={self.health_status}>"


class HealthThreshold(Base):
    """
    Normal range per health parameter per elderly (REQ-007, REQ-015).
    Each elderly can have individually configured thresholds (e.g. diabetic patients
    have different acceptable blood sugar ranges).

    Service evaluates after every HealthRecord insert:
        SELECT * FROM health_thresholds
        WHERE elderly_id = :id AND is_active = true

    Then for each parameter with a recorded value:
        if value < min_value OR value > max_value → flag as out-of-range
    """

    __tablename__ = "health_thresholds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    elderly_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("elderly_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parameter: Mapped[HealthParameter] = mapped_column(String(30), nullable=False)
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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
        back_populates="health_thresholds", lazy="select"
    )

    from sqlalchemy import UniqueConstraint

    __table_args__ = (
        UniqueConstraint("elderly_id", "parameter", name="uq_threshold_elderly_param"),
    )

    def __repr__(self) -> str:
        return f"<HealthThreshold elderly_id={self.elderly_id} param={self.parameter} [{self.min_value}, {self.max_value}]>"
