"""
Pydantic schemas for Viewer Invitation endpoints.

Separation:
  ViewerInvitationCreate → request to invite a viewer
  ViewerInvitationResponse → full invitation details
  ViewerInvitationListResponse → paginated list of invitations
  AcceptInvitationResponse → response after accepting invitation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ViewerInvitationCreate(BaseModel):
    """Request body for inviting a viewer."""

    email: EmailStr = Field(..., description="Email address of the viewer to invite")
    expires_in_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days until the invitation expires",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "email": "viewer@example.com",
            "expires_in_days": 7,
        }
    }}


class ViewerInvitationResponse(BaseModel):
    """Full viewer invitation details."""

    id: uuid.UUID
    elderly_id: uuid.UUID
    invited_by: uuid.UUID
    viewer_id: Optional[uuid.UUID] = None
    email: str
    token: str  # Only shown once when created
    status: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViewerInvitationWithoutToken(BaseModel):
    """Viewer invitation details without token (for listing)."""

    id: uuid.UUID
    elderly_id: uuid.UUID
    viewer_id: Optional[uuid.UUID] = None
    viewer_name: Optional[str] = None
    email: str
    status: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViewerInvitationListResponse(BaseModel):
    """Paginated list of viewer invitations."""

    total: int
    invitations: list[ViewerInvitationWithoutToken]


class AcceptInvitationResponse(BaseModel):
    """Response after successfully accepting an invitation."""

    success: bool
    message: str
    elderly_id: Optional[uuid.UUID] = None
    elderly_name: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "success": True,
            "message": "Invitation accepted successfully",
            "elderly_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "elderly_name": "Budi Santoso",
        }
    }}