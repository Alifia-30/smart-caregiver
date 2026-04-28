"""
Health Service — business logic layer for health records and fuzzy analysis.

Responsibilities:
  1. Create a HealthRecord from a validated request payload.
  2. Run fuzzy analysis synchronously in a thread-pool executor so the
     async event loop is never blocked by CPU-bound skfuzzy computations.
  3. Persist fuzzy scores and derived health_status back to the record.
  4. Provide query helpers (list by elderly, latest record, single record).
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.fuzzy.engine import FuzzyAnalysisResult, run_fuzzy_analysis
from src.app.schemas.health import (
    FuzzyModuleSchema,
    FuzzyResultSchema,
    HealthRecordCreate,
    HealthRecordResponse,
    HealthRecordSummary,
)
from src.database.enums import HealthStatus
from src.database.models.health import HealthRecord


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fuzzy_status_to_health_status(fuzzy_status: str) -> HealthStatus:
    """Map fuzzy engine output string → HealthStatus enum value."""
    mapping = {
        "Normal": HealthStatus.NORMAL,
        "Warning": HealthStatus.WARNING,
        "Critical": HealthStatus.CRITICAL,
    }
    return mapping.get(fuzzy_status, HealthStatus.NORMAL)


def _build_fuzzy_response(result: FuzzyAnalysisResult) -> FuzzyResultSchema:
    """Convert a FuzzyAnalysisResult into the Pydantic response schema."""

    cardio_schema: Optional[FuzzyModuleSchema] = None
    if result.cardio:
        cardio_schema = FuzzyModuleSchema(
            score=result.cardio.score,
            status=result.cardio.status,
            parameters={
                "blood_pressure": result.cardio.bp_status,
                "heart_rate": result.cardio.hr_status,
                "spo2": result.cardio.spo2_status,
            },
        )

    metabolic_schema: Optional[FuzzyModuleSchema] = None
    if result.metabolic:
        metabolic_schema = FuzzyModuleSchema(
            score=result.metabolic.score,
            status=result.metabolic.status,
            parameters={
                "blood_sugar": result.metabolic.sugar_status,
                "cholesterol": result.metabolic.chol_status,
                "uric_acid": result.metabolic.uric_status,
                "body_weight": result.metabolic.weight_status,
            },
        )

    infection_schema: Optional[FuzzyModuleSchema] = None
    if result.infection:
        infection_schema = FuzzyModuleSchema(
            score=result.infection.score,
            status=result.infection.status,
            parameters={
                "body_temperature": result.infection.temp_status,
                "spo2": result.infection.spo2_status,
            },
        )

    return FuzzyResultSchema(
        cardiovascular=cardio_schema,
        metabolic=metabolic_schema,
        infection=infection_schema,
        final_score=result.final_score,
        final_status=result.final_status,
    )


def _record_to_response(
    record: HealthRecord,
    fuzzy_result: Optional[FuzzyAnalysisResult] = None,
) -> HealthRecordResponse:
    """Build a HealthRecordResponse from a SQLAlchemy model instance."""
    fuzzy_schema = _build_fuzzy_response(fuzzy_result) if fuzzy_result else None

    return HealthRecordResponse(
        id=record.id,
        elderly_id=record.elderly_id,
        recorded_by=record.recorded_by,
        recorded_at=record.recorded_at,
        created_at=record.created_at,
        systolic_bp=record.systolic_bp,
        diastolic_bp=record.diastolic_bp,
        blood_sugar=record.blood_sugar,
        heart_rate=record.heart_rate,
        body_temperature=record.body_temperature,
        body_weight=record.body_weight,
        cholesterol=record.cholesterol,
        uric_acid=record.uric_acid,
        spo2_level=record.spo2_level,
        daily_notes=record.daily_notes,
        complaints=record.complaints,
        health_status=record.health_status,
        cardio_score=record.cardio_score,
        metabolic_score=record.metabolic_score,
        infection_score=record.infection_score,
        fuzzy_final_score=record.fuzzy_final_score,
        fuzzy_analysis=fuzzy_schema,
    )


async def _run_fuzzy_async(record: HealthRecord) -> FuzzyAnalysisResult:
    """Run the CPU-bound fuzzy analysis in a thread-pool executor.

    This prevents blocking the async event loop during skfuzzy computation.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: run_fuzzy_analysis(
            systolic_bp=record.systolic_bp,
            heart_rate=record.heart_rate,
            spo2_level=record.spo2_level,
            blood_sugar=record.blood_sugar,
            cholesterol=record.cholesterol,
            uric_acid=record.uric_acid,
            body_weight=record.body_weight,
            body_temperature=record.body_temperature,
        ),
    )
    return result


# ── Public service functions ───────────────────────────────────────────────────

async def create_health_record(
    db: AsyncSession,
    payload: HealthRecordCreate,
    recorded_by: Optional[uuid.UUID] = None,
) -> HealthRecordResponse:
    """Create a health record, run fuzzy analysis, and persist everything.

    Steps:
      1. Insert the HealthRecord row with raw vitals.
      2. Flush to get a database-assigned id without committing.
      3. Run fuzzy analysis in thread pool.
      4. Write scores + health_status back to the same row.
      5. Commit once — the session dependency in get_db() handles this.

    Args:
        db:          Async database session (from FastAPI dependency).
        payload:     Validated request body.
        recorded_by: UUID of the authenticated user creating this record.

    Returns:
        HealthRecordResponse with full fuzzy analysis embedded.
    """
    record = HealthRecord(
        elderly_id=payload.elderly_id,
        recorded_by=recorded_by,
        recorded_at=payload.recorded_at,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        heart_rate=payload.heart_rate,
        spo2_level=payload.spo2_level,
        blood_sugar=payload.blood_sugar,
        cholesterol=payload.cholesterol,
        uric_acid=payload.uric_acid,
        body_weight=payload.body_weight,
        body_temperature=payload.body_temperature,
        daily_notes=payload.daily_notes,
        complaints=payload.complaints,
        health_status=HealthStatus.NORMAL,   # will be overwritten below
    )

    db.add(record)
    await db.flush()   # populate record.id without committing

    # ── Fuzzy analysis ─────────────────────────────────────────────────────────
    fuzzy_result = await _run_fuzzy_async(record)

    # ── Persist fuzzy scores back to the row ───────────────────────────────────
    record.cardio_score     = fuzzy_result.cardio.score     if fuzzy_result.cardio     else None
    record.metabolic_score  = fuzzy_result.metabolic.score  if fuzzy_result.metabolic  else None
    record.infection_score  = fuzzy_result.infection.score  if fuzzy_result.infection  else None
    record.fuzzy_final_score = fuzzy_result.final_score
    record.health_status     = _fuzzy_status_to_health_status(fuzzy_result.final_status)

    # Session is committed by the get_db() dependency after this function returns
    return _record_to_response(record, fuzzy_result)


async def get_health_record(
    db: AsyncSession,
    record_id: uuid.UUID,
) -> Optional[HealthRecordResponse]:
    """Fetch a single health record by id.

    Fuzzy scores are read from stored columns (no recomputation).

    Returns:
        HealthRecordResponse or None if not found.
    """
    result = await db.execute(
        select(HealthRecord).where(HealthRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return _record_to_response(record)


async def reanalyze_health_record(
    db: AsyncSession,
    record_id: uuid.UUID,
) -> Optional[HealthRecordResponse]:
    """Re-run fuzzy analysis for an existing record and update stored scores.

    Useful if the fuzzy membership functions are updated and scores need
    to be recalculated for historical records.

    Returns:
        Updated HealthRecordResponse or None if not found.
    """
    result = await db.execute(
        select(HealthRecord).where(HealthRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None

    fuzzy_result = await _run_fuzzy_async(record)

    record.cardio_score      = fuzzy_result.cardio.score    if fuzzy_result.cardio    else None
    record.metabolic_score   = fuzzy_result.metabolic.score if fuzzy_result.metabolic else None
    record.infection_score   = fuzzy_result.infection.score if fuzzy_result.infection else None
    record.fuzzy_final_score = fuzzy_result.final_score
    record.health_status     = _fuzzy_status_to_health_status(fuzzy_result.final_status)

    return _record_to_response(record, fuzzy_result)


async def list_health_records(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[HealthRecordResponse]]:
    """Return paginated health records for one elderly person.

    Records are ordered newest-first.

    Returns:
        (total_count, list_of_records)
    """
    from sqlalchemy import func as sql_func

    count_result = await db.execute(
        select(sql_func.count()).select_from(HealthRecord).where(
            HealthRecord.elderly_id == elderly_id
        )
    )
    total = count_result.scalar_one()

    rows_result = await db.execute(
        select(HealthRecord)
        .where(HealthRecord.elderly_id == elderly_id)
        .order_by(desc(HealthRecord.recorded_at))
        .limit(limit)
        .offset(offset)
    )
    records = rows_result.scalars().all()
    return total, [_record_to_response(r) for r in records]


async def get_latest_health_record(
    db: AsyncSession,
    elderly_id: uuid.UUID,
) -> Optional[HealthRecordSummary]:
    """Return the most recent health record summary for one elderly person.

    Returns:
        HealthRecordSummary or None if no records exist.
    """
    result = await db.execute(
        select(HealthRecord)
        .where(HealthRecord.elderly_id == elderly_id)
        .order_by(desc(HealthRecord.recorded_at))
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return HealthRecordSummary.model_validate(record)
