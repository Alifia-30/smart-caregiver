"""
Elderly profile and access control models
REQ-002: Caregiver creates elderly profile
REQ-003: Multiple profiles per caregiver
REQ-011: Viewer invitation per elderly
REQ-012: Viewer sees only invited elderly data
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.enums import ElderlyStatus, InvitationStatus, MobilityLevel


class ElderlyProfile(Base):
    """
    One row per elderly person. Belongs to exactly one caregiver.
    """

    __tablename__ = "elderly_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    caregiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Identity ──────────────────────────────────────────────────────────────
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # male, female, other
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Medical background (REQ-002) ──────────────────────────────────────────
    medical_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    physical_condition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mobility_level: Mapped[MobilityLevel] = mapped_column(
        String(20), nullable=False, default=MobilityLevel.INDEPENDENT
    )
    hobbies_interests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # ── Status ────────────────────────────────────────────────────────────────
    status: Mapped[ElderlyStatus] = mapped_column(
        String(20), nullable=False, default=ElderlyStatus.ACTIVE, index=True
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
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
    caregiver: Mapped["User"] = relationship(  # noqa: F821
        back_populates="elderly_profiles", lazy="select"
    )
    viewer_invitations: Mapped[list["ViewerInvitation"]] = relationship(
        back_populates="elderly", cascade="all, delete-orphan", lazy="select"
    )
    health_records: Mapped[list["HealthRecord"]] = relationship(  # noqa: F821
        back_populates="elderly",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="HealthRecord.recorded_at.desc()",
    )
    health_thresholds: Mapped[list["HealthThreshold"]] = relationship(  # noqa: F821
        back_populates="elderly", cascade="all, delete-orphan", lazy="selectin"
    )
    schedules: Mapped[list["Schedule"]] = relationship(  # noqa: F821
        back_populates="elderly", cascade="all, delete-orphan", lazy="select"
    )
    ai_recommendations: Mapped[list["AIActivityRecommendation"]] = relationship(  # noqa: F821
        back_populates="elderly", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ElderlyProfile id={self.id} name={self.full_name}>"


class ViewerInvitation(Base):
    """
    Access control gate for Viewer role (REQ-011, REQ-012).
    A Viewer can only access elderly profiles they have been explicitly invited to.

    Lookup pattern for authorization middleware:
        SELECT 1 FROM viewer_invitations
        WHERE viewer_id = :user_id
          AND elderly_id = :elderly_id
          AND status = 'accepted'
    """

    __tablename__ = "viewer_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    elderly_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("elderly_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    # viewer_id is NULL until the invitee accepts (they may not have an account yet)
    viewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Invitation delivery ───────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    status: Mapped[InvitationStatus] = mapped_column(
        String(20), nullable=False, default=InvitationStatus.PENDING, index=True
    )

    # ── Timing ────────────────────────────────────────────────────────────────
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    elderly: Mapped["ElderlyProfile"] = relationship(
        back_populates="viewer_invitations", lazy="select"
    )
    invited_by_user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="sent_invitations",
        foreign_keys=[invited_by],
        lazy="select",
    )
    viewer: Mapped[Optional["User"]] = relationship(  # noqa: F821
        back_populates="viewer_access",
        foreign_keys=[viewer_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<ViewerInvitation elderly_id={self.elderly_id} email={self.email} status={self.status}>"
