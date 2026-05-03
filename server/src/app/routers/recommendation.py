"""
Recommendation Router — AI activity recommendations.

Endpoints:
  POST   /elderly/{elderly_id}/recommendations/generate → Generate AI recommendation
  GET    /elderly/{elderly_id}/recommendations     → List recommendations
  GET    /elderly/{elderly_id}/recommendations/{id} → Get single recommendation
  POST   /elderly/{elderly_id}/recommendations/{id}/approve → Approve → create schedule
  POST   /elderly/{elderly_id}/recommendations/{id}/reject  → Reject recommendation

Authentication:
  Generate/Approve/Reject: caregiver owner only
  List/GET: caregiver owner OR viewer with accepted invitation
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.recommendation import (
    RecommendationActionResponse,
    RecommendationApproveRequest,
    RecommendationGenerateRequest,
    RecommendationList,
    RecommendationRejectRequest,
    RecommendationResponse,
)
from src.app.services import recommendation_service
from src.app.core.auth import AccessLevel, get_current_user, require_caregiver_owner, require_elderly_access
from src.database.enums import RecommendationStatus
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(tags=["recommendations"])


def _to_response(rec) -> RecommendationResponse:
    """Convert ORM model to response schema."""
    return RecommendationResponse(
        id=rec.id,
        elderly_id=rec.elderly_id,
        activity_name=rec.activity_name,
        category=rec.category,
        description=rec.description,
        duration_minutes=rec.duration_minutes,
        frequency_suggestion=rec.frequency_suggestion,
        ai_reasoning=rec.ai_reasoning,
        ai_model_version=rec.ai_model_version,
        ai_prompt_version=rec.ai_prompt_version,
        status=rec.status,
        approved_by=rec.approved_by,
        approved_at=rec.approved_at,
        rejection_reason=rec.rejection_reason,
        generated_at=rec.generated_at,
        created_at=rec.created_at,
    )


@router.post(
    "/elderly/{elderly_id}/recommendations/generate",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendation(
    elderly_id: uuid.UUID,
    request: RecommendationGenerateRequest,
    _: tuple[uuid.UUID, User] = Depends(require_caregiver_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI activity recommendation for an elderly profile.
    Requires caregiver ownership.
    """
    _, user = _
    try:
        recommendation = await recommendation_service.generate_recommendation(
            db=db,
            elderly_id=elderly_id,
            additional_context=request.additional_context,
        )
        await db.commit()
        return _to_response(recommendation)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/elderly/{elderly_id}/recommendations", response_model=RecommendationList)
async def list_recommendations(
    elderly_id: uuid.UUID,
    status_filter: Optional[RecommendationStatus] = Query(
        None, alias="status", description="Filter by status"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: tuple[uuid.UUID, User, AccessLevel] = Depends(require_elderly_access),
    db: AsyncSession = Depends(get_db),
):
    """
    List recommendations for an elderly profile.
    Accessible to caregiver owner or viewer with accepted invitation.
    """
    total, recommendations = await recommendation_service.list_recommendations(
        db=db,
        elderly_id=elderly_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return RecommendationList(
        total=total,
        recommendations=[_to_response(r) for r in recommendations],
    )


@router.get("/elderly/{elderly_id}/recommendations/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    elderly_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    _: tuple[uuid.UUID, User, AccessLevel] = Depends(require_elderly_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single recommendation by ID.
    Accessible to caregiver owner or viewer with accepted invitation.
    """
    recommendation = await recommendation_service.get_recommendation(
        db=db,
        recommendation_id=recommendation_id,
    )
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )
    return _to_response(recommendation)


@router.post("/elderly/{elderly_id}/recommendations/{recommendation_id}/approve", response_model=RecommendationActionResponse)
async def approve_recommendation(
    elderly_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    request: RecommendationApproveRequest,
    _: tuple[uuid.UUID, User] = Depends(require_caregiver_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a recommendation and optionally create a schedule.
    REQ-018: Approve → auto-create schedule entry
    Requires caregiver ownership.
    """
    elderly_id, user = _
    try:
        recommendation, schedule_id = await recommendation_service.approve_recommendation(
            db=db,
            recommendation_id=recommendation_id,
            approver_id=user.id,
            scheduled_at=request.scheduled_at,
            duration_minutes=request.duration_minutes,
            reminder_minutes=request.reminder_minutes,
        )
        await db.commit()

        return RecommendationActionResponse(
            success=True,
            recommendation_id=recommendation_id,
            status=recommendation.status,
            schedule_id=schedule_id,
            message="Recommendation approved" + (" and schedule created" if schedule_id else ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/elderly/{elderly_id}/recommendations/{recommendation_id}/reject", response_model=RecommendationActionResponse)
async def reject_recommendation(
    elderly_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    request: RecommendationRejectRequest,
    _: tuple[uuid.UUID, User] = Depends(require_caregiver_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject a recommendation.
    Requires caregiver ownership.
    """
    _, user = _
    try:
        recommendation = await recommendation_service.reject_recommendation(
            db=db,
            recommendation_id=recommendation_id,
            approver_id=user.id,
            reason=request.reason,
        )
        await db.commit()

        return RecommendationActionResponse(
            success=True,
            recommendation_id=recommendation_id,
            status=recommendation.status,
            schedule_id=None,
            message="Recommendation rejected",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))