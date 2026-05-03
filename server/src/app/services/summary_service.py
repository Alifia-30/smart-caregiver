"""
Weekly Summary Service — business logic for periodic health summaries.

Responsibilities:
  1. Generate weekly health summaries for an elderly person
  2. Send summary notifications to caregiver and viewers
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.notification_service import create_notification
from src.database.enums import HealthStatus, NotificationType, InvitationStatus
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.health import HealthRecord


async def generate_weekly_summary(
    db: AsyncSession,
    elderly_id: uuid.UUID,
) -> Optional[dict]:
    """
    Generate health summary for the last 7 days.
    
    Args:
        db: Database session
        elderly_id: UUID of the elderly profile
        
    Returns:
        Dictionary containing summary data or None if no records found
    """
    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()
    
    if not elderly:
        return None

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)

    # Fetch health records for the last 7 days
    stmt = (
        select(HealthRecord)
        .where(
            and_(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.recorded_at >= start_date,
            )
        )
        .order_by(HealthRecord.recorded_at)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return None

    # Calculate statistics
    total_records = len(records)
    status_counts = {
        HealthStatus.NORMAL: 0,
        HealthStatus.WARNING: 0,
        HealthStatus.NEEDS_ATTENTION: 0,
        HealthStatus.CRITICAL: 0,
    }
    
    param_values = {
        "systolic_bp": [],
        "diastolic_bp": [],
        "blood_sugar": [],
        "heart_rate": [],
        "body_temperature": [],
        "spo2_level": [],
    }

    for record in records:
        # Status count
        status = record.health_status
        if status in status_counts:
            status_counts[status] += 1
        
        # Collect values for averages
        if record.systolic_bp is not None: param_values["systolic_bp"].append(record.systolic_bp)
        if record.diastolic_bp is not None: param_values["diastolic_bp"].append(record.diastolic_bp)
        if record.blood_sugar is not None: param_values["blood_sugar"].append(record.blood_sugar)
        if record.heart_rate is not None: param_values["heart_rate"].append(record.heart_rate)
        if record.body_temperature is not None: param_values["body_temperature"].append(record.body_temperature)
        if record.spo2_level is not None: param_values["spo2_level"].append(record.spo2_level)

    averages = {}
    for param, values in param_values.items():
        if values:
            averages[param] = sum(values) / len(values)
        else:
            averages[param] = None

    # Construct summary message body
    status_summary = "Records: {0}. ".format(total_records)
    alert_count = status_counts[HealthStatus.WARNING] + status_counts[HealthStatus.NEEDS_ATTENTION] + status_counts[HealthStatus.CRITICAL]
    status_summary += "Status: {0} Normal, {1} Alerts.".format(status_counts[HealthStatus.NORMAL], alert_count)

    return {
        "elderly_id": str(elderly_id),
        "elderly_name": elderly.full_name,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "total_records": total_records,
        "status_counts": {k.value: v for k, v in status_counts.items()},
        "averages": averages,
        "body_summary": status_summary
    }


async def send_weekly_summary_notifications(
    db: AsyncSession,
    elderly_id: uuid.UUID,
) -> int:
    """
    Generate and send weekly summary notifications to caregiver and viewers.
    
    Args:
        db: Database session
        elderly_id: UUID of the elderly profile
        
    Returns:
        Number of notifications sent
    """
    summary = await generate_weekly_summary(db, elderly_id)
    if not summary:
        return 0

    elderly_stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    elderly_result = await db.execute(elderly_stmt)
    elderly = elderly_result.scalar_one_or_none()
    
    if not elderly:
        return 0

    # Collect recipients: caregiver + accepted viewers
    recipient_ids = [elderly.caregiver_id]
    
    viewers_stmt = select(ViewerInvitation).where(
        and_(
            ViewerInvitation.elderly_id == elderly_id,
            ViewerInvitation.status == InvitationStatus.ACCEPTED,
        )
    )
    viewers_result = await db.execute(viewers_stmt)
    viewers = viewers_result.scalars().all()
    
    for viewer in viewers:
        if viewer.viewer_id:
            recipient_ids.append(viewer.viewer_id)

    title = "Weekly Summary: {0}".format(elderly.full_name)
    body = "Here is the health summary for {0} from the past 7 days. {1}".format(elderly.full_name, summary['body_summary'])
    
    sent_count = 0
    for recipient_id in recipient_ids:
        await create_notification(
            db=db,
            recipient_id=recipient_id,
            notification_type=NotificationType.WEEKLY_SUMMARY,
            title=title,
            body=body,
            elderly_id=elderly_id,
            payload={**summary, "elderly_id": str(elderly_id), "recipient_id": str(recipient_id)}
        )
        sent_count += 1
    
    await db.flush()
    return sent_count


async def process_all_weekly_summaries(db: AsyncSession) -> int:
    """
    Internal job to process weekly summaries for all active elderly profiles.
    """
    stmt = select(ElderlyProfile.id).where(ElderlyProfile.status == "active")
    result = await db.execute(stmt)
    elderly_ids = result.scalars().all()
    
    total_sent = 0
    for eid in elderly_ids:
        total_sent += await send_weekly_summary_notifications(db, eid)
    
    return total_sent