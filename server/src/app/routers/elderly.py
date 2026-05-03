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
  All endpoints require JWT bearer token authentication.
  - Caregiver can read/write their own elderly profiles
  - Viewer with accepted invitation can read elderly profiles
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.elderly import (
    ElderlyProfileCreate,
    ElderlyProfileListResponse,
    ElderlyProfileResponse,
    ElderlyProfileUpdate,
)
from src.app.services import elderly_service
from src.app.core.auth import (
    AccessLevel,
    get_current_user,
    require_caregiver_owner,
    require_elderly_access,
    get_viewer_access_elderly_ids,
)
from src.database.enums import ElderlyStatus
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(prefix="/elderly", tags=["elderly"])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ElderlyProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat profil lansia baru (REQ-002)",
    description=(
        "Caregiver membuat profil baru untuk lansia yang dirawatnya. "
        "Satu caregiver dapat memiliki banyak profil lansia (REQ-003). "
        "Requires JWT authentication."
    ),
)
async def create_elderly_profile(
    payload: ElderlyProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ElderlyProfileResponse:
    return await elderly_service.create_profile(
        db=db,
        payload=payload,
        caregiver_id=current_user.id,
    )


@router.get(
    "",
    response_model=ElderlyProfileListResponse,
    summary="Daftar semua profil lansia milik caregiver (REQ-003)",
    description=(
        "Mengembalikan semua profil lansia yang dimiliki oleh caregiver ini. "
        "Mendukung filter status dan pagination. "
        "Also returns elderly profiles the viewer has accepted access to."
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
    current_user: User = Depends(get_current_user),
) -> ElderlyProfileListResponse:
    return await elderly_service.list_profiles(
        db=db,
        caregiver_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
async def create_elderly_profile(
    payload: ElderlyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ElderlyProfileResponse:
    caregiver_id = current_user.id
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ElderlyProfileListResponse:
    caregiver_id = current_user.id
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
    description=(
        "Mengambil detail lengkap satu profil lansia. "
        "Dapat diakses oleh caregiver pemilik atau viewer dengan invitation accepted."
    ),
)
async def get_elderly_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ElderlyProfileResponse:
    profile = await elderly_service.get_profile(
        db=db,
        profile_id=profile_id,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia dengan id {profile_id} tidak ditemukan.",
        )
    _, _, access_level = await require_elderly_access(profile_id, current_user, db)
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
    current_user: User = Depends(get_current_user),
) -> ElderlyProfileResponse:
    _, _ = await require_caregiver_owner(profile_id, current_user, db)
    profile = await elderly_service.update_profile(
        db=db,
        profile_id=profile_id,
        payload=payload,
        caregiver_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
) -> ElderlyProfileResponse:
    _, _ = await require_caregiver_owner(profile_id, current_user, db)
    profile = await elderly_service.deactivate_profile(
        db=db,
        profile_id=profile_id,
        caregiver_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
) -> None:
    _, _ = await require_caregiver_owner(profile_id, current_user, db)
    deleted = await elderly_service.delete_profile(
        db=db,
        profile_id=profile_id,
        caregiver_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil lansia {profile_id} tidak ditemukan atau bukan milik Anda.",
        )
