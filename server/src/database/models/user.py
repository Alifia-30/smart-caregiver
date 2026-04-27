"""
Auth & Onboarding models
REQ-001: email+password registration
Google OAuth: via oauth_accounts table (one user → many providers)
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
from src.database.enums import AuthProvider


class User(Base):
    """
    Core user table. Works for both Caregiver and Viewer roles.
    Role is determined contextually via viewer_invitations, NOT a column here.
    Supports email/password AND Google OAuth simultaneously on the same account.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # ── Password auth (nullable — Google-only users have no password) ─────────
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verification_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Password reset ────────────────────────────────────────────────────────
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Account state ─────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    elderly_profiles: Mapped[list["ElderlyProfile"]] = relationship(  # noqa: F821
        back_populates="caregiver", cascade="all, delete-orphan", lazy="select"
    )
    sent_invitations: Mapped[list["ViewerInvitation"]] = relationship(  # noqa: F821
        back_populates="invited_by_user",
        foreign_keys="ViewerInvitation.invited_by",
        cascade="all, delete-orphan",
        lazy="select",
    )
    viewer_access: Mapped[list["ViewerInvitation"]] = relationship(  # noqa: F821
        back_populates="viewer",
        foreign_keys="ViewerInvitation.viewer_id",
        lazy="select",
    )
    notifications: Mapped[list["Notification"]] = relationship(  # noqa: F821
        back_populates="recipient", cascade="all, delete-orphan", lazy="select"
    )
    notification_preferences: Mapped[list["NotificationPreference"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

    @property
    def has_password(self) -> bool:
        """True if user can log in with email+password."""
        return self.hashed_password is not None

    @property
    def google_linked(self) -> bool:
        """True if Google OAuth is linked to this account."""
        return any(a.provider == AuthProvider.GOOGLE for a in self.oauth_accounts)


class OAuthAccount(Base):
    """
    One row per OAuth provider per user.
    Allows one user to link multiple providers (email + google, etc.).

    Flow:
      1. User signs in with Google → look up by (provider, provider_user_id).
      2. Found  → update tokens, return existing user.
      3. Not found → check if email already exists in users table.
         a. Exists  → link this OAuth account to existing user.
         b. New     → create User + OAuthAccount together.
    """

    __tablename__ = "oauth_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[AuthProvider] = mapped_column(
        String(50), nullable=False
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # ── Tokens (store encrypted in production via pgcrypto or app-layer AES) ──
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Profile snapshot from provider ────────────────────────────────────────
    provider_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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
    user: Mapped["User"] = relationship(back_populates="oauth_accounts")

    # ── Constraints ───────────────────────────────────────────────────────────
    from sqlalchemy import UniqueConstraint

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_uid"),
    )

    def __repr__(self) -> str:
        return f"<OAuthAccount provider={self.provider} user_id={self.user_id}>"
