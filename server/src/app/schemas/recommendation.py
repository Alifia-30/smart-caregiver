"""
Recommendation Pydantic schemas.
REQ-016: AI reads onboarding profile → generates activity recommendations
REQ-017: Caregiver views recommendations per elderly
REQ-018: Approve → auto-create schedule entry
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from src.database.enums import ActivityCategory, RecommendationStatus


class RecommendationGenerateRequest(BaseModel):
    additional_context: Optional[str] = Field(
        None,
        description="Optional context or specific request from caregiver"
    )


class RecommendationResponse(BaseModel):
    id: UUID
    elderly_id: UUID
    activity_name: str
    category: ActivityCategory
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    frequency_suggestion: Optional[str] = None
    ai_reasoning: Optional[str] = None
    ai_model_version: Optional[str] = None
    ai_prompt_version: Optional[str] = None
    status: RecommendationStatus
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    generated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationList(BaseModel):
    total: int
    recommendations: List[RecommendationResponse]


class RecommendationApproveRequest(BaseModel):
    scheduled_at: Optional[datetime] = Field(
        None,
        description="When to schedule the activity. Required if creating schedule."
    )
    duration_minutes: Optional[int] = Field(
        None,
        ge=1,
        le=1440,
        description="Duration for the schedule"
    )
    reminder_minutes: Optional[List[int]] = Field(
        None,
        description="Alarm triggers (e.g. [10, 30])"
    )


class RecommendationRejectRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for rejecting (optional, for transparency)"
    )


class RecommendationActionResponse(BaseModel):
    success: bool
    recommendation_id: UUID
    status: RecommendationStatus
    schedule_id: Optional[UUID] = None
    message: str