"""
Pydantic schemas for Elderly Profile endpoints.

REQ-002: Caregiver creates elderly profile
REQ-003: Multiple profiles per caregiver
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.database.enums import ElderlyStatus, MobilityLevel


# ── Request schemas ────────────────────────────────────────────────────────────

class ElderlyProfileCreate(BaseModel):
    """Body for POST /elderly — create a new elderly profile."""

    full_name: str = Field(..., min_length=2, max_length=255, description="Nama lengkap lansia")
    age: int = Field(..., ge=50, le=120, description="Usia lansia (tahun)")
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$", description="male | female | other")
    photo_url: Optional[str] = Field(None, max_length=500)

    # ── Medical background (REQ-002) ───────────────────────────────────────────
    medical_history: Optional[str] = Field(None, max_length=5000, description="Riwayat penyakit")
    physical_condition: Optional[str] = Field(None, max_length=2000, description="Kondisi fisik saat ini")
    mobility_level: MobilityLevel = Field(
        MobilityLevel.INDEPENDENT,
        description="independent | assisted | wheelchair | bedridden",
    )
    hobbies_interests: Optional[str] = Field(None, max_length=1000, description="Hobi dan minat")
    allergies: Optional[str] = Field(None, max_length=1000, description="Alergi yang diketahui")

    # ── Emergency contact ──────────────────────────────────────────────────────
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Siti Rahayu",
                "age": 72,
                "gender": "female",
                "medical_history": "Hipertensi, diabetes tipe 2",
                "physical_condition": "Dapat berjalan mandiri dengan tongkat",
                "mobility_level": "assisted",
                "hobbies_interests": "Berkebun, membaca Al-Quran",
                "allergies": "Penisilin",
                "emergency_contact_name": "Budi Santoso",
                "emergency_contact_phone": "081234567890",
            }
        }
    }


class ElderlyProfileUpdate(BaseModel):
    """Body for PUT /elderly/{id} — partial update (all fields optional)."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    age: Optional[int] = Field(None, ge=50, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    photo_url: Optional[str] = Field(None, max_length=500)
    medical_history: Optional[str] = Field(None, max_length=5000)
    physical_condition: Optional[str] = Field(None, max_length=2000)
    mobility_level: Optional[MobilityLevel] = None
    hobbies_interests: Optional[str] = Field(None, max_length=1000)
    allergies: Optional[str] = Field(None, max_length=1000)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[ElderlyStatus] = Field(
        None, description="active | inactive (gunakan DELETE untuk menonaktifkan)"
    )


# ── Response schemas ───────────────────────────────────────────────────────────

class ElderlyProfileResponse(BaseModel):
    """Full elderly profile returned to client."""

    id: uuid.UUID
    caregiver_id: uuid.UUID

    full_name: str
    age: int
    gender: Optional[str] = None
    photo_url: Optional[str] = None

    medical_history: Optional[str] = None
    physical_condition: Optional[str] = None
    mobility_level: MobilityLevel
    hobbies_interests: Optional[str] = None
    allergies: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    status: ElderlyStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ElderlyProfileSummary(BaseModel):
    """Lightweight card — used in list responses."""

    id: uuid.UUID
    caregiver_id: uuid.UUID
    full_name: str
    age: int
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    mobility_level: MobilityLevel
    status: ElderlyStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ElderlyProfileListResponse(BaseModel):
    """Paginated list of elderly profiles."""

    total: int
    profiles: list[ElderlyProfileSummary]
