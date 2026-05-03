"""
Dashboard Service — business logic for dashboard overview and health trends.

Responsibilities:
  1. Get dashboard overview for the current user (caregiver's elderly or viewer's elderly)
  2. Get health trends data for a specific elderly person (7d or 30d range)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.core.auth import get_viewer_access_elderly_ids
from src.app.schemas.dashboard import (
    DashboardElderlyItem,
    DashboardOverviewResponse,
    HealthTrendDataPoint,
    HealthTrendsParameterSummary,
    HealthTrendsResponse,
    HealthTrendsSummary,
)
from src.database.enums import ElderlyStatus
from src.database.models.elderly import ElderlyProfile
from src.database.models.health import HealthRecord


async def get_dashboard_overview(
    user: "User",  # Forward reference to avoid circular import
    db: AsyncSession,
) -> DashboardOverviewResponse:
    """
    Get dashboard overview for the current user.

    Caregivers see all their elderly profiles (status=ACTIVE).
    Viewers see all elderly they have accepted access to.

    Returns:
        DashboardOverviewResponse with list of elderly and their latest health status.
    """
    elderly_ids: list[uuid.UUID] = []

    caregiver_stmt = (
        select(ElderlyProfile.id)
        .where(
            ElderlyProfile.caregiver_id == user.id,
            ElderlyProfile.status == ElderlyStatus.ACTIVE,
        )
    )
    caregiver_result = await db.execute(caregiver_stmt)
    caregiver_ids = [row[0] for row in caregiver_result.fetchall()]
    elderly_ids.extend(caregiver_ids)

    viewer_ids = await get_viewer_access_elderly_ids(user, db)
    elderly_ids.extend(viewer_ids)

    if not elderly_ids:
        return DashboardOverviewResponse(total=0, elderly=[])

    elderly_ids = list(set(elderly_ids))

    elderly_stmt = (
        select(ElderlyProfile)
        .where(
            ElderlyProfile.id.in_(elderly_ids),
            ElderlyProfile.status == ElderlyStatus.ACTIVE,
        )
    )
    elderly_result = await db.execute(elderly_stmt)
    elderly_profiles = elderly_result.scalars().all()

    latest_record_subquery = (
        select(
            HealthRecord.elderly_id,
            func.max(HealthRecord.recorded_at).label("max_recorded_at"),
        )
        .where(HealthRecord.elderly_id.in_(elderly_ids))
        .group_by(HealthRecord.elderly_id)
        .subquery()
    )

    latest_record_stmt = (
        select(HealthRecord)
        .join(
            latest_record_subquery,
            (HealthRecord.elderly_id == latest_record_subquery.c.elderly_id)
            & (HealthRecord.recorded_at == latest_record_subquery.c.max_recorded_at),
        )
    )
    latest_result = await db.execute(latest_record_stmt)
    latest_records = {r.elderly_id: r for r in latest_result.scalars().all()}

    elderly_items = []
    for elderly in elderly_profiles:
        latest_record = latest_records.get(elderly.id)
        mobility = elderly.mobility_level
        if hasattr(mobility, 'value'):
            mobility = mobility.value

        health_status = latest_record.health_status if latest_record else None
        if health_status and hasattr(health_status, 'value'):
            health_status = health_status.value

        elderly_items.append(
            DashboardElderlyItem(
                elderly_id=elderly.id,
                full_name=elderly.full_name,
                age=elderly.age,
                gender=elderly.gender,
                photo_url=elderly.photo_url,
                mobility_level=mobility,
                latest_health_status=health_status,
                latest_recorded_at=latest_record.recorded_at if latest_record else None,
            )
        )

    elderly_items.sort(key=lambda x: x.full_name)

    return DashboardOverviewResponse(total=len(elderly_items), elderly=elderly_items)


async def get_health_trends(
    elderly_id: uuid.UUID,
    range: str,
    db: AsyncSession,
) -> HealthTrendsResponse:
    """
    Get health trends for a specific elderly person.

    Args:
        elderly_id: UUID of the elderly profile
        range: "7d" or "30d"

    Returns:
        HealthTrendsResponse with data points per date and summary statistics.
    """
    if range not in ("7d", "30d"):
        raise ValueError("Range must be '7d' or '30d'")

    days = 7 if range == "7d" else 30
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    stmt = (
        select(HealthRecord)
        .where(
            HealthRecord.elderly_id == elderly_id,
            HealthRecord.recorded_at >= start_date,
        )
        .order_by(HealthRecord.recorded_at)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    records_by_date: dict[date, HealthRecord] = {}
    for record in records:
        record_date = record.recorded_at.date()
        if record_date not in records_by_date:
            records_by_date[record_date] = record

    data_points = []
    all_values: dict[str, list[float]] = {
        "systolic_bp": [],
        "diastolic_bp": [],
        "blood_sugar": [],
        "heart_rate": [],
        "body_temperature": [],
        "body_weight": [],
        "cholesterol": [],
        "uric_acid": [],
        "spo2_level": [],
    }

    for record_date in sorted(records_by_date.keys()):
        record = records_by_date[record_date]
        data_points.append(
            HealthTrendDataPoint(
                date=record_date,
                systolic_bp=record.systolic_bp,
                diastolic_bp=record.diastolic_bp,
                blood_sugar=record.blood_sugar,
                heart_rate=record.heart_rate,
                body_temperature=record.body_temperature,
                body_weight=record.body_weight,
                cholesterol=record.cholesterol,
                uric_acid=record.uric_acid,
                spo2_level=record.spo2_level,
            )
        )

        if record.systolic_bp is not None:
            all_values["systolic_bp"].append(record.systolic_bp)
        if record.diastolic_bp is not None:
            all_values["diastolic_bp"].append(record.diastolic_bp)
        if record.blood_sugar is not None:
            all_values["blood_sugar"].append(record.blood_sugar)
        if record.heart_rate is not None:
            all_values["heart_rate"].append(record.heart_rate)
        if record.body_temperature is not None:
            all_values["body_temperature"].append(record.body_temperature)
        if record.body_weight is not None:
            all_values["body_weight"].append(record.body_weight)
        if record.cholesterol is not None:
            all_values["cholesterol"].append(record.cholesterol)
        if record.uric_acid is not None:
            all_values["uric_acid"].append(record.uric_acid)
        if record.spo2_level is not None:
            all_values["spo2_level"].append(record.spo2_level)

    def _build_summary(values: list[float]) -> Optional[HealthTrendsParameterSummary]:
        if not values:
            return None
        return HealthTrendsParameterSummary(
            min=min(values),
            max=max(values),
            avg=sum(values) / len(values),
            count=len(values),
        )

    summary = HealthTrendsSummary(
        systolic_bp=_build_summary(all_values["systolic_bp"]),
        diastolic_bp=_build_summary(all_values["diastolic_bp"]),
        blood_sugar=_build_summary(all_values["blood_sugar"]),
        heart_rate=_build_summary(all_values["heart_rate"]),
        body_temperature=_build_summary(all_values["body_temperature"]),
        body_weight=_build_summary(all_values["body_weight"]),
        cholesterol=_build_summary(all_values["cholesterol"]),
        uric_acid=_build_summary(all_values["uric_acid"]),
        spo2_level=_build_summary(all_values["spo2_level"]),
    )

    return HealthTrendsResponse(
        elderly_id=elderly_id,
        range=range,
        data=data_points,
        summary=summary,
    )