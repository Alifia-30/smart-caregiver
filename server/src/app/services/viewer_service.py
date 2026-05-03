"""
Viewer Service — business logic for viewer invitation and access management.

Responsibilities:
  1. Create viewer invitation with unique token
  2. List all invitations for an elderly profile
  3. Accept invitation (link to user, update status)
  4. Revoke invitation
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.viewer import (
    AcceptInvitationResponse,
    ViewerInvitationCreate,
    ViewerInvitationListResponse,
    ViewerInvitationResponse,
    ViewerInvitationWithoutToken,
)
from src.database.enums import InvitationStatus
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.user import User


def _generate_token() -> str:
    """Generate a secure random token for invitation."""
    return secrets.token_urlsafe(32)


async def invite_viewer(
    elderly_id: uuid.UUID,
    payload: ViewerInvitationCreate,
    invited_by: uuid.UUID,
    db: AsyncSession,
) -> ViewerInvitationResponse:
    """
    Create a new viewer invitation.

    Args:
        elderly_id: UUID of the elderly profile
        payload: Invitation details (email, expires_in_days)
        invited_by: UUID of the caregiver creating the invitation
        db: Database session

    Returns:
        ViewerInvitationResponse with the created invitation (including token)

    Raises:
        ValueError: If email already has a pending invitation
    """
    stmt = select(ViewerInvitation).where(
        ViewerInvitation.elderly_id == elderly_id,
        ViewerInvitation.email == payload.email,
        ViewerInvitation.status == InvitationStatus.PENDING,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(f"Pending invitation already exists for email: {payload.email}")

    expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days)

    invitation = ViewerInvitation(
        elderly_id=elderly_id,
        invited_by=invited_by,
        email=payload.email,
        token=_generate_token(),
        status=InvitationStatus.PENDING,
        expires_at=expires_at,
    )

    db.add(invitation)
    await db.flush()

    return ViewerInvitationResponse(
        id=invitation.id,
        elderly_id=invitation.elderly_id,
        invited_by=invitation.invited_by,
        viewer_id=invitation.viewer_id,
        email=invitation.email,
        token=invitation.token,
        status=invitation.status.value,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        created_at=invitation.created_at,
    )


async def get_elderly_viewers(
    elderly_id: uuid.UUID,
    db: AsyncSession,
) -> ViewerInvitationListResponse:
    """
    Get all viewer invitations for an elderly profile.

    Args:
        elderly_id: UUID of the elderly profile
        db: Database session

    Returns:
        ViewerInvitationListResponse with all invitations
    """
    stmt = (
        select(ViewerInvitation)
        .where(ViewerInvitation.elderly_id == elderly_id)
        .order_by(ViewerInvitation.created_at.desc())
    )
    result = await db.execute(stmt)
    invitations = result.scalars().all()

    items = []
    for inv in invitations:
        viewer_name = None
        if inv.viewer_id:
            user_stmt = select(User).where(User.id == inv.viewer_id)
            user_result = await db.execute(user_stmt)
            viewer = user_result.scalar_one_or_none()
            if viewer:
                viewer_name = viewer.full_name

        status_val = inv.status
        if hasattr(status_val, 'value'):
            status_val = status_val.value

        items.append(
            ViewerInvitationWithoutToken(
                id=inv.id,
                elderly_id=inv.elderly_id,
                viewer_id=inv.viewer_id,
                viewer_name=viewer_name,
                email=inv.email,
                status=status_val,
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
                created_at=inv.created_at,
            )
        )

    return ViewerInvitationListResponse(total=len(items), invitations=items)


async def get_invitation_by_token(
    token: str,
    db: AsyncSession,
) -> Optional[ViewerInvitation]:
    """
    Get invitation by token.

    Args:
        token: The invitation token
        db: Database session

    Returns:
        ViewerInvitation or None if not found
    """
    stmt = select(ViewerInvitation).where(ViewerInvitation.token == token)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def accept_invitation(
    token: str,
    viewer_id: Optional[uuid.UUID],
    db: AsyncSession,
) -> AcceptInvitationResponse:
    """
    Accept a viewer invitation.

    Args:
        token: The invitation token
        viewer_id: UUID of the user accepting (if logged in)
        db: Database session

    Returns:
        AcceptInvitationResponse with result

    Raises:
        ValueError: If invitation not found, expired, or already accepted
    """
    invitation = await get_invitation_by_token(token, db)

    if not invitation:
        raise ValueError("Invalid invitation token")

    if invitation.status == InvitationStatus.ACCEPTED:
        raise ValueError("Invitation has already been accepted")

    if invitation.status == InvitationStatus.REVOKED:
        raise ValueError("Invitation has been revoked")

    if invitation.status == InvitationStatus.EXPIRED:
        raise ValueError("Invitation has expired")

    now = datetime.now(timezone.utc)
    if now > invitation.expires_at:
        invitation.status = InvitationStatus.EXPIRED
        await db.flush()
        raise ValueError("Invitation has expired")

    invitation.viewer_id = viewer_id
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = now

    await db.flush()

    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == invitation.elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()

    return AcceptInvitationResponse(
        success=True,
        message="Invitation accepted successfully",
        elderly_id=invitation.elderly_id,
        elderly_name=elderly.full_name if elderly else None,
    )


async def revoke_invitation(
    invitation_id: uuid.UUID,
    elderly_id: uuid.UUID,
    caregiver_id: uuid.UUID,
    db: AsyncSession,
) -> bool:
    """
    Revoke a viewer invitation.

    Args:
        invitation_id: UUID of the invitation to revoke
        elderly_id: UUID of the elderly profile (for verification)
        caregiver_id: UUID of the caregiver (must be owner)
        db: Database session

    Returns:
        True if revoked successfully

    Raises:
        ValueError: If invitation not found or not authorized
    """
    stmt = select(ViewerInvitation).where(ViewerInvitation.id == invitation_id)
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise ValueError("Invitation not found")

    if invitation.elderly_id != elderly_id:
        raise ValueError("Invitation does not belong to this elderly")

    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()

    if not elderly or elderly.caregiver_id != caregiver_id:
        raise ValueError("Not authorized to revoke this invitation")

    invitation.status = InvitationStatus.REVOKED
    await db.flush()

    return True


async def delete_invitation(
    invitation_id: uuid.UUID,
    elderly_id: uuid.UUID,
    caregiver_id: uuid.UUID,
    db: AsyncSession,
) -> bool:
    """
    Delete a viewer invitation completely.

    Args:
        invitation_id: UUID of the invitation to delete
        elderly_id: UUID of the elderly profile (for verification)
        caregiver_id: UUID of the caregiver (must be owner)
        db: Database session

    Returns:
        True if deleted successfully

    Raises:
        ValueError: If invitation not found or not authorized
    """
    stmt = select(ViewerInvitation).where(ViewerInvitation.id == invitation_id)
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise ValueError("Invitation not found")

    if invitation.elderly_id != elderly_id:
        raise ValueError("Invitation does not belong to this elderly")

    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()

    if not elderly or elderly.caregiver_id != caregiver_id:
        raise ValueError("Not authorized to delete this invitation")

    await db.delete(invitation)
    await db.flush()

    return True