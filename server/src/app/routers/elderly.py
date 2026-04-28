"""
Elderly Profile Router

REQ-002: Caregiver creates elderly profile
REQ-003: Multiple profiles per caregiver

Endpoints:
  POST   /elderly                  → Create new profile (REQ-002)
  GET    /elderly                  → List all profiles for this caregiver (REQ-003)
  GET    /elderly/{id}             → Get one profile detail
  PUT    /elderly/{id}             → Update profile (partial)
  DELETE /elderly/{id}             → Soft-delete (set status = inactive)
  DELETE /elderly/{id}/permanent   → Hard-delete (permanent, with confirmation)

Authentication:
  All write endpoints require X-Caregiver-Id header (UUID of the logged-in caregiver).
  TODO: Replace with JWT bearer dependency when auth middleware is ready.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.elderly import (
    ElderlyProfileCreate,
    ElderlyProfileListResponse,
    ElderlyProfileResponse,
    ElderlyProfileUpdate,
)
from src.app.services import elderly_service
from src.database.enums import ElderlyStatus
from src.database.session import get_db

router = APIRouter(prefix="/elderly", tags=["elderly"])


# ── Auth dependency (temporary — swap for JWT later) ──────────────────────────

async def _require_caregiver_id(
    x_caregiver_id: str = Header(..., alias="X-Caregiver-Id"),
) -> uuid.UUID:
    """Extract and validate caregiver UUID from request header.

    Raises 400 if the header is missing or not a valid UUID.
    TODO: Replace with JWT `get_current_user` dependency.
    """
    try:
        return uuid.UUID(x_caregiver_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Caregiver-Id header must be a valid UUID.",
        )


async def _optional_caregiver_id(
    x_caregiver_id: Optional[str] = Header(None, alias="X-Caregiver-Id"),
) -> Optional[uuid.UUID]:
    if x_caregiver_id is None:
        return None
    try:
        return uuid.UUID(x_caregiver_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Caregiver-Id header must be a valid UUID.",
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ElderlyProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat profil lansia baru (REQ-002)",
    description=(
        "Caregiver membuat profil baru untuk lansia yang dirawatnya. "
        "Satu caregiver dapat memiliki banyak profil lansia (REQ-003). "
        "Header **X-Caregiver-Id** wajib diisi dengan UUID caregiver."
    ),
)
async def create_elderly_profile(
    payload: ElderlyProfileCreate,
    db: AsyncSession = Depends(get_db),
    caregiver_id: uuid.UUID = Depends(_require_caregiver_id),
) -> ElderlyProfileResponse:
    return await elderly_service.create_profile(
        db=db,
        payload=payload,
        caregiver_id=caregiver_id,
    )


@router.get(
    "",
    response_model=ElderlyProfileListResponse,
    summary="Daftar semua profil lansia milik caregiver (REQ-003)",
    description=(
        "Mengembalikan semua profil lansia yang dimiliki oleh caregiver ini. "
        "Mendukung filter status dan pagination."
    ),
)
async def list_elderly_profiles(
    status_filter: Optional[ElderlyStatus] = Query(
        None,
        alias="status",
        description="Filter berdasarkan status: active | inactive | critical",
    ),
    limit: int = Query(20, ge=1, le=100, description="Jumlah profil per halaman"),
    offset: int = Query(0, ge=0, description="Skip N profil"),
    db: AsyncSession = Depends(get_db),
    caregiver_id: uuid.UUID = Depends(_require_caregiver_id),
) -> ElderlyProfileListResponse:
    return await elderly_service.list_profiles(
        db=db,
        caregiver_id=caregiver_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{profile_id}",
    response_model=ElderlyProfileResponse,
    summary="Detail profil lansia",
    description="Mengambil detail lengkap satu profil lansia. Hanya bisa diakses oleh caregiver pemilik profil.",
)
async def get_elderly_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    caregiver_id: Optional[uuid.UUID] = Depends(_optional_caregiver_id),
) -> ElderlyProfileResponse:
    profile = await elderly_service.get_profile(
        db=db,
        profile_id=profile_id,
        caregiver_id=caregiver_id,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia dengan id {profile_id} tidak ditemukan.",
        )
    return profile


@router.put(
    "/{profile_id}",
    response_model=ElderlyProfileResponse,
    summary="Update profil lansia",
    description=(
        "Memperbarui data profil lansia. Hanya field yang dikirim yang akan diubah "
        "(partial update). Hanya caregiver pemilik yang dapat mengupdate."
    ),
)
async def update_elderly_profile(
    profile_id: uuid.UUID,
    payload: ElderlyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    caregiver_id: uuid.UUID = Depends(_require_caregiver_id),
) -> ElderlyProfileResponse:
    profile = await elderly_service.update_profile(
        db=db,
        profile_id=profile_id,
        payload=payload,
        caregiver_id=caregiver_id,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia {profile_id} tidak ditemukan atau bukan milik Anda.",
        )
    return profile


@router.delete(
    "/{profile_id}",
    response_model=ElderlyProfileResponse,
    summary="Nonaktifkan profil lansia (soft delete)",
    description=(
        "Mengubah status profil menjadi **inactive**. "
        "Data kesehatan dan jadwal tetap tersimpan. "
        "Untuk menghapus permanen gunakan endpoint `/elderly/{id}/permanent`."
    ),
)
async def deactivate_elderly_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    caregiver_id: uuid.UUID = Depends(_require_caregiver_id),
) -> ElderlyProfileResponse:
    profile = await elderly_service.deactivate_profile(
        db=db,
        profile_id=profile_id,
        caregiver_id=caregiver_id,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia {profile_id} tidak ditemukan atau bukan milik Anda.",
        )
    return profile


@router.delete(
    "/{profile_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus permanen profil lansia ⚠️",
    description=(
        "**PERINGATAN:** Menghapus profil secara permanen beserta SEMUA data terkait "
        "(rekaman kesehatan, jadwal, rekomendasi, undangan viewer). "
        "Aksi ini tidak dapat dibatalkan. "
        "Gunakan endpoint DELETE biasa untuk soft-delete yang aman."
    ),
)
async def delete_elderly_profile_permanent(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    caregiver_id: uuid.UUID = Depends(_require_caregiver_id),
) -> None:
    deleted = await elderly_service.delete_profile(
        db=db,
        profile_id=profile_id,
        caregiver_id=caregiver_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia {profile_id} tidak ditemukan atau bukan milik Anda.",
        )
