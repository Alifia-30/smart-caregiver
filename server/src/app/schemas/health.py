"""
Pydantic schemas for Health Record endpoints.

Separation:
  HealthRecordCreate   → validated request body
  HealthRecordResponse → full DB record returned to client
  FuzzyResultSchema    → standalone fuzzy analysis result (no DB save)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ── Request schemas ────────────────────────────────────────────────────────────

class HealthRecordCreate(BaseModel):
    """
    Body for POST /health/records.

    All health parameters are optional so partial measurements can be
    recorded.  At least one parameter should be provided — the service
    layer enforces this.

    Fuzzy analysis is run automatically for whichever modules have
    sufficient data:
      Cardiovascular : systolic_bp + heart_rate + spo2_level
      Metabolic      : any of blood_sugar / cholesterol / uric_acid / body_weight
      Infection      : body_temperature + spo2_level
    """

    elderly_id: uuid.UUID
    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the measurements were taken (not when they were entered).",
    )

    # ── Cardiovascular parameters ──────────────────────────────────────────────
    systolic_bp: Optional[float] = Field(
        None, ge=60, le=250, description="Systolic blood pressure (mmHg)"
    )
    diastolic_bp: Optional[float] = Field(
        None, ge=40, le=150, description="Diastolic blood pressure (mmHg)"
    )
    heart_rate: Optional[float] = Field(
        None, ge=20, le=250, description="Heart rate (bpm)"
    )
    spo2_level: Optional[float] = Field(
        None, ge=50, le=100, description="Oxygen saturation SpO₂ (%)"
    )

    # ── Metabolic parameters ───────────────────────────────────────────────────
    blood_sugar: Optional[float] = Field(
        None, ge=20, le=600, description="Blood glucose (mg/dL)"
    )
    cholesterol: Optional[float] = Field(
        None, ge=50, le=600, description="Total cholesterol (mg/dL)"
    )
    uric_acid: Optional[float] = Field(
        None, ge=0.5, le=20, description="Uric acid (mg/dL)"
    )
    body_weight: Optional[float] = Field(
        None, ge=20, le=300, description="Body weight (kg)"
    )

    # ── Infection / respiratory parameters ────────────────────────────────────
    body_temperature: Optional[float] = Field(
        None, ge=30, le=45, description="Body temperature (°C)"
    )

    # ── Notes ─────────────────────────────────────────────────────────────────
    daily_notes: Optional[str] = Field(None, max_length=2000)
    complaints: Optional[str] = Field(None, max_length=2000)

    @field_validator("recorded_at", mode="before")
    @classmethod
    def _ensure_tz_aware(cls, v: Any) -> Any:
        """Accept naive datetimes and treat them as UTC."""
        if isinstance(v, datetime) and v.tzinfo is None:
            from datetime import timezone
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "elderly_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "recorded_at": "2026-04-28T10:00:00Z",
            "systolic_bp": 145,
            "diastolic_bp": 90,
            "heart_rate": 105,
            "spo2_level": 94,
            "blood_sugar": 180,
            "cholesterol": 220,
            "uric_acid": 8,
            "body_weight": 75,
            "body_temperature": 38.5,
            "daily_notes": "Pasien mengeluh pusing ringan.",
            "complaints": "Kepala terasa berat.",
        }
    }}


# ── Fuzzy sub-schemas ──────────────────────────────────────────────────────────

class FuzzyModuleSchema(BaseModel):
    """Score + status + parameter breakdown for one fuzzy module."""
    score: float
    status: str
    parameters: dict[str, str]


class FuzzyResultSchema(BaseModel):
    """
    Full fuzzy analysis result — returned inside HealthRecordResponse
    and also by the standalone /analyze endpoint.
    """
    cardiovascular: Optional[FuzzyModuleSchema] = None
    metabolic: Optional[FuzzyModuleSchema] = None
    infection: Optional[FuzzyModuleSchema] = None
    final_score: float
    final_status: str    # Normal | Warning | Critical


# ── Response schemas ───────────────────────────────────────────────────────────

class HealthRecordResponse(BaseModel):
    """Full health record including fuzzy analysis results."""

    id: uuid.UUID
    elderly_id: uuid.UUID
    recorded_by: Optional[uuid.UUID] = None
    recorded_at: datetime
    created_at: datetime

    # ── Vital parameters ───────────────────────────────────────────────────────
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    blood_sugar: Optional[float] = None
    heart_rate: Optional[float] = None
    body_temperature: Optional[float] = None
    body_weight: Optional[float] = None
    cholesterol: Optional[float] = None
    uric_acid: Optional[float] = None
    spo2_level: Optional[float] = None

    # ── Notes ─────────────────────────────────────────────────────────────────
    daily_notes: Optional[str] = None
    complaints: Optional[str] = None

    # ── Overall status (set by fuzzy analysis) ─────────────────────────────────
    health_status: str

    # ── Fuzzy scores ───────────────────────────────────────────────────────────
    cardio_score: Optional[float] = None
    metabolic_score: Optional[float] = None
    infection_score: Optional[float] = None
    fuzzy_final_score: Optional[float] = None

    # ── Embedded fuzzy detail ──────────────────────────────────────────────────
    fuzzy_analysis: Optional[FuzzyResultSchema] = None

    model_config = {"from_attributes": True}


class HealthRecordListResponse(BaseModel):
    """Paginated list of health records."""
    total: int
    records: list[HealthRecordResponse]


class HealthRecordSummary(BaseModel):
    """Lightweight summary — used by the /latest endpoint."""
    id: uuid.UUID
    elderly_id: uuid.UUID
    recorded_at: datetime
    health_status: str
    fuzzy_final_score: Optional[float] = None
    cardio_score: Optional[float] = None
    metabolic_score: Optional[float] = None
    infection_score: Optional[float] = None

    model_config = {"from_attributes": True}
