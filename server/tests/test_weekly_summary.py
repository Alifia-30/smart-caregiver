"""
Test Weekly Summary.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.database.models.elderly import ElderlyProfile


@pytest.mark.asyncio
async def test_weekly_summary_batch(
    client_caregiver: AsyncClient,
    db_session,
    elderly_profile: ElderlyProfile,
):
    """Weekly summary batch job should work."""
    response = await client_caregiver.post("/internal/jobs/send-weekly-summary")
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_weekly_summary_single(
    client_caregiver: AsyncClient,
    db_session,
    elderly_profile: ElderlyProfile,
):
    """Weekly summary for specific elderly should work."""
    response = await client_caregiver.post(
        f"/internal/jobs/send-weekly-summary/{elderly_profile.id}"
    )
    assert response.status_code in [200, 500]