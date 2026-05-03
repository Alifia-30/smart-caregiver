"""
Viewer Router

Endpoints:
  POST   /elderly/{elderly_id}/viewers/invite       → Invite a viewer
  GET    /elderly/{elderly_id}/viewers             → List all viewers
  POST   /viewer-invitations/{token}/accept        → Accept invitation
  DELETE /elderly/{elderly_id}/viewers/{invitation_id} → Revoke invitation

Authentication:
  - Invite/List/Revoke: requires caregiver owner (JWT)
  - Accept: can be done with or without login (token-based)
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.viewer import (
    AcceptInvitationResponse,
    ViewerInvitationCreate,
    ViewerInvitationListResponse,
    ViewerInvitationResponse,
)
from src.app.services import viewer_service
from src.app.core.auth import get_current_user, get_current_user_optional, require_caregiver_owner
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["viewer"])


@router.post(
    "/elderly/{elderly_id}/viewers/invite",
    response_model=ViewerInvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a viewer",
    description=(
        "Create an invitation for someone to view an elderly profile. "
        "Returns a token that can be shared with the viewer. "
        "Only the caregiver owner can invite viewers."
    ),
)
async def invite_viewer(
    elderly_id: uuid.UUID,
    payload: ViewerInvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ViewerInvitationResponse:
    _, _ = await require_caregiver_owner(elderly_id, current_user, db)

    try:
        return await viewer_service.invite_viewer(
            elderly_id=elderly_id,
            payload=payload,
            invited_by=current_user.id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/elderly/{elderly_id}/viewers",
    response_model=ViewerInvitationListResponse,
    summary="List all viewers",
    description=(
        "Get all viewer invitations for an elderly profile. "
        "Only the caregiver owner can view this list."
    ),
)
async def get_elderly_viewers(
    elderly_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ViewerInvitationListResponse:
    _, _ = await require_caregiver_owner(elderly_id, current_user, db)

    return await viewer_service.get_elderly_viewers(
        elderly_id=elderly_id,
        db=db,
    )


@router.post(
    "/viewer-invitations/{token}/accept",
    response_model=AcceptInvitationResponse,
    summary="Accept an invitation",
    description=(
        "Accept a viewer invitation using the token. "
        "If the user is logged in, they will be linked to the invitation. "
        "If not logged in, they can still accept but will need to register/login later to access."
    ),
)
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AcceptInvitationResponse:
    viewer_id = current_user.id if current_user else None

    try:
        return await viewer_service.accept_invitation(
            token=token,
            viewer_id=viewer_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/elderly/{elderly_id}/viewers/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an invitation",
    description=(
        "Revoke a viewer invitation. The viewer will lose access to the elderly profile. "
        "Only the caregiver owner can revoke invitations."
    ),
)
async def revoke_invitation(
    elderly_id: uuid.UUID,
    invitation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _, _ = await require_caregiver_owner(elderly_id, current_user, db)

    try:
        await viewer_service.revoke_invitation(
            invitation_id=invitation_id,
            elderly_id=elderly_id,
            caregiver_id=current_user.id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )