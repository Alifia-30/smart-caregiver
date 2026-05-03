"""
Pydantic schemas for Dashboard endpoints.

Separation:
  DashboardOverviewResponse → list of elderly with latest health status
  HealthTrendsResponse     → health data trends for charting
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class DashboardElderlyItem(BaseModel):
    """Lightweight elderly info for dashboard overview."""

    elderly_id: uuid.UUID
    full_name: str
    age: int
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    mobility_level: str
    latest_health_status: Optional[str] = None
    latest_recorded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DashboardOverviewResponse(BaseModel):
    """Response for GET /dashboard/overview."""

    total: int
    elderly: list[DashboardElderlyItem]


class HealthTrendDataPoint(BaseModel):
    """Single data point for health trend - one date with all vital parameters."""

    date: date
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    blood_sugar: Optional[float] = None
    heart_rate: Optional[float] = None
    body_temperature: Optional[float] = None
    body_weight: Optional[float] = None
    cholesterol: Optional[float] = None
    uric_acid: Optional[float] = None
    spo2_level: Optional[float] = None


class HealthTrendsParameterSummary(BaseModel):
    """Summary statistics for a single health parameter."""

    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    count: int = 0


class HealthTrendsSummary(BaseModel):
    """Summary statistics for all health parameters."""

    systolic_bp: Optional[HealthTrendsParameterSummary] = None
    diastolic_bp: Optional[HealthTrendsParameterSummary] = None
    blood_sugar: Optional[HealthTrendsParameterSummary] = None
    heart_rate: Optional[HealthTrendsParameterSummary] = None
    body_temperature: Optional[HealthTrendsParameterSummary] = None
    body_weight: Optional[HealthTrendsParameterSummary] = None
    cholesterol: Optional[HealthTrendsParameterSummary] = None
    uric_acid: Optional[HealthTrendsParameterSummary] = None
    spo2_level: Optional[HealthTrendsParameterSummary] = None


class HealthTrendsResponse(BaseModel):
    """Response for GET /elderly/{elderly_id}/health/trends."""

    elderly_id: uuid.UUID
    range: str  # "7d" or "30d"
    data: list[HealthTrendDataPoint]
    summary: HealthTrendsSummary