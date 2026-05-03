"""
Internal Jobs Router — for manual trigger of background tasks.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services import summary_service
from src.database.session import get_db

router = APIRouter(prefix="/internal/jobs", tags=["internal-jobs"])


@router.post(
    "/send-weekly-summary",
    status_code=status.HTTP_200_OK,
    summary="Manually trigger weekly summary generation",
    description="Processes weekly summaries for all active elderly profiles and sends notifications.",
)
async def trigger_weekly_summary(
    db: AsyncSession = Depends(get_db),
):
    # In a real app, this should be protected by an API key or internal network check
    sent_count = await summary_service.process_all_weekly_summaries(db)
    return {"status": "success", "notifications_sent": sent_count}


@router.post(
    "/send-weekly-summary/{elderly_id}",
    status_code=status.HTTP_200_OK,
    summary="Trigger weekly summary for a specific elderly",
)
async def trigger_weekly_summary_single(
    elderly_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    sent_count = await summary_service.send_weekly_summary_notifications(db, elderly_id)
    return {"status": "success", "notifications_sent": sent_count}
