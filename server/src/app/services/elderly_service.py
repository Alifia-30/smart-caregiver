"""
Elderly Profile Service — business logic layer.

REQ-002: Caregiver creates elderly profile
REQ-003: Multiple profiles per caregiver

Operations:
  create_profile       → insert new ElderlyProfile row
  get_profile          → fetch single profile (with ownership check)
  list_profiles        → paginated list for one caregiver
  update_profile       → partial update (PATCH semantics)
  deactivate_profile   → soft-delete (status = INACTIVE)
  delete_profile       → hard-delete (permanent, use with caution)
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import desc, func as sql_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.elderly import (
    ElderlyProfileCreate,
    ElderlyProfileListResponse,
    ElderlyProfileResponse,
    ElderlyProfileSummary,
    ElderlyProfileUpdate,
)
from src.database.enums import ElderlyStatus
from src.database.models.elderly import ElderlyProfile


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_response(profile: ElderlyProfile) -> ElderlyProfileResponse:
    return ElderlyProfileResponse.model_validate(profile)


def _to_summary(profile: ElderlyProfile) -> ElderlyProfileSummary:
    return ElderlyProfileSummary.model_validate(profile)


# ── Service functions ──────────────────────────────────────────────────────────

async def create_profile(
    db: AsyncSession,
    payload: ElderlyProfileCreate,
    caregiver_id: uuid.UUID,
) -> ElderlyProfileResponse:
    """Create a new elderly profile owned by caregiver_id.

    REQ-002: Any authenticated caregiver can create a profile.
    REQ-003: A caregiver can own multiple profiles (no limit enforced here).

    Args:
        db:           Async database session.
        payload:      Validated request body.
        caregiver_id: UUID of the authenticated caregiver.

    Returns:
        The newly created profile.
    """
    profile = ElderlyProfile(
        caregiver_id=caregiver_id,
        full_name=payload.full_name,
        age=payload.age,
        gender=payload.gender,
        photo_url=payload.photo_url,
        medical_history=payload.medical_history,
        physical_condition=payload.physical_condition,
        mobility_level=payload.mobility_level,
        hobbies_interests=payload.hobbies_interests,
        allergies=payload.allergies,
        emergency_contact_name=payload.emergency_contact_name,
        emergency_contact_phone=payload.emergency_contact_phone,
        status=ElderlyStatus.ACTIVE,
    )
    db.add(profile)
    await db.flush()   # get the generated id without committing yet
    await db.refresh(profile)
    return _to_response(profile)


async def get_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    caregiver_id: Optional[uuid.UUID] = None,
) -> Optional[ElderlyProfileResponse]:
    """Fetch a single elderly profile by id.

    If caregiver_id is provided, the result is filtered to only return
    profiles belonging to that caregiver (ownership check).

    Returns:
        ElderlyProfileResponse or None if not found / not owned.
    """
    query = select(ElderlyProfile).where(ElderlyProfile.id == profile_id)
    if caregiver_id is not None:
        query = query.where(ElderlyProfile.caregiver_id == caregiver_id)

    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    return _to_response(profile) if profile else None


async def list_profiles(
    db: AsyncSession,
    caregiver_id: uuid.UUID,
    status: Optional[ElderlyStatus] = None,
    limit: int = 20,
    offset: int = 0,
) -> ElderlyProfileListResponse:
    """Return paginated elderly profiles for one caregiver.

    REQ-003: Returns ALL profiles belonging to this caregiver.

    Args:
        db:           Async database session.
        caregiver_id: UUID of the authenticated caregiver.
        status:       Optional filter (active | inactive | critical).
        limit:        Page size (max 100).
        offset:       Skip N records.

    Returns:
        ElderlyProfileListResponse with total count and page of summaries.
    """
    base_filter = ElderlyProfile.caregiver_id == caregiver_id
    if status is not None:
        base_filter = base_filter & (ElderlyProfile.status == status)

    # Total count
    count_result = await db.execute(
        select(sql_func.count()).select_from(ElderlyProfile).where(base_filter)
    )
    total = count_result.scalar_one()

    # Page
    rows_result = await db.execute(
        select(ElderlyProfile)
        .where(base_filter)
        .order_by(desc(ElderlyProfile.created_at))
        .limit(limit)
        .offset(offset)
    )
    profiles = rows_result.scalars().all()

    return ElderlyProfileListResponse(
        total=total,
        profiles=[_to_summary(p) for p in profiles],
    )


async def update_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    payload: ElderlyProfileUpdate,
    caregiver_id: uuid.UUID,
) -> Optional[ElderlyProfileResponse]:
    """Partially update an elderly profile (only provided fields are changed).

    Only the owning caregiver can update a profile.

    Returns:
        Updated ElderlyProfileResponse or None if not found / not owned.
    """
    result = await db.execute(
        select(ElderlyProfile).where(
            ElderlyProfile.id == profile_id,
            ElderlyProfile.caregiver_id == caregiver_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return None

    # Apply only the fields explicitly set in the payload (exclude_unset=True)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.flush()
    await db.refresh(profile)
    return _to_response(profile)


async def deactivate_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    caregiver_id: uuid.UUID,
) -> Optional[ElderlyProfileResponse]:
    """Soft-delete: set status = INACTIVE.

    The profile and all its health records are preserved.
    Only the owning caregiver can deactivate a profile.

    Returns:
        Updated profile or None if not found / not owned.
    """
    result = await db.execute(
        select(ElderlyProfile).where(
            ElderlyProfile.id == profile_id,
            ElderlyProfile.caregiver_id == caregiver_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return None

    profile.status = ElderlyStatus.INACTIVE
    await db.flush()
    await db.refresh(profile)
    return _to_response(profile)


async def delete_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    caregiver_id: uuid.UUID,
) -> bool:
    """Hard-delete an elderly profile (permanent, cascades to all child data).

    ⚠️  This will permanently delete all health records, schedules,
    recommendations, and invitations linked to this profile.

    Returns:
        True if deleted, False if not found / not owned.
    """
    result = await db.execute(
        select(ElderlyProfile).where(
            ElderlyProfile.id == profile_id,
            ElderlyProfile.caregiver_id == caregiver_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return False

    await db.delete(profile)
    await db.flush()
    return True
