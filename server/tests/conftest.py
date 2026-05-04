"""
Test fixtures and configuration.
Simpler approach: just use different fixture names.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.database.session import AsyncSessionLocal, get_db
from src.database.models.user import User
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.health import HealthRecord
from src.database.models.schedule import Schedule
from src.database.models.recommendation import AIActivityRecommendation
from src.database.enums import (
    HealthStatus,
    InvitationStatus,
    ScheduleType,
    RecurrenceType,
    RecommendationStatus,
)
from src.app.core.security import create_access_token
from src.main import app


# =============================================================================
# Override get_db
# =============================================================================

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async def override_get_db():
        async with AsyncSessionLocal() as db:
            yield db
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# =============================================================================
# Test Client Fixture
# =============================================================================

@pytest_asyncio.fixture
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# =============================================================================
# Seed Data Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def caregiver_user(db_session) -> User:
    user = User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="caregiver@test.com",
        hashed_password="$2b$12$dummy_hash_for_testing",
        full_name="Test Caregiver",
        is_active=True,
    )
    db_session.add(user)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return user


@pytest_asyncio.fixture
async def viewer_user(db_session) -> User:
    user = User(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        email="viewer@test.com",
        hashed_password="$2b$12$dummy_hash_for_testing",
        full_name="Test Viewer",
        is_active=True,
    )
    db_session.add(user)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return user


@pytest_asyncio.fixture
async def other_user(db_session) -> User:
    user = User(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        email="other@test.com",
        hashed_password="$2b$12$dummy_hash",
        full_name="Other User",
        is_active=True,
    )
    db_session.add(user)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return user


@pytest_asyncio.fixture
async def elderly_profile(db_session, caregiver_user) -> ElderlyProfile:
    elderly = ElderlyProfile(
        id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        caregiver_id=caregiver_user.id,
        full_name="Budi Test",
        age=75,
        gender="male",
        mobility_level="assisted",
    )
    db_session.add(elderly)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return elderly


@pytest_asyncio.fixture
async def viewer_invitation(db_session, elderly_profile, viewer_user) -> ViewerInvitation:
    invitation = ViewerInvitation(
        id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        elderly_id=elderly_profile.id,
        viewer_id=viewer_user.id,
        invited_by=elderly_profile.caregiver_id,
        email="viewer@test.com",
        token="test-token-seed",
        status=InvitationStatus.ACCEPTED,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return invitation


@pytest_asyncio.fixture
async def health_records(db_session, elderly_profile, caregiver_user) -> list:
    records = []
    for i in range(7):
        record = HealthRecord(
            elderly_id=elderly_profile.id,
            recorded_by=caregiver_user.id,
            systolic_bp=120.0 + i,
            diastolic_bp=80.0,
            blood_sugar=100.0 + i * 5,
            heart_rate=75.0,
            body_temperature=36.5 + (i * 0.1),
            health_status=HealthStatus.NORMAL,
            recorded_at=datetime.now(timezone.utc) - timedelta(days=i),
        )
        db_session.add(record)
        records.append(record)
    
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    
    return records


@pytest_asyncio.fixture
async def recommendation(db_session, elderly_profile) -> AIActivityRecommendation:
    rec = AIActivityRecommendation(
        id=uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"),
        elderly_id=elderly_profile.id,
        activity_name="Senam Kursi",
        category="physical",
        description="Latihan fisik untuk lansia",
        status=RecommendationStatus.PENDING,
    )
    db_session.add(rec)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return rec


@pytest_asyncio.fixture
async def schedule(db_session, elderly_profile) -> Schedule:
    sched = Schedule(
        id=uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
        elderly_id=elderly_profile.id,
        title="Minum Obat Pagi",
        schedule_type=ScheduleType.MEDICATION,
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=2),
        recurrence_type=RecurrenceType.DAILY,
        is_active=True,
    )
    db_session.add(sched)
    try:
        await db_session.commit()
    except:
        await db_session.rollback()
    return sched


# =============================================================================
# Auth Token Fixtures - generate from user fixture
# =============================================================================

@pytest_asyncio.fixture
async def caregiver_token(caregiver_user: User) -> str:
    return create_access_token(subject=str(caregiver_user.id))


@pytest_asyncio.fixture
async def viewer_token(viewer_user: User) -> str:
    return create_access_token(subject=str(viewer_user.id))


@pytest_asyncio.fixture
async def other_token(other_user: User) -> str:
    return create_access_token(subject=str(other_user.id))


# =============================================================================
# Client with Auth - different naming to avoid conflicts
# =============================================================================

@pytest_asyncio.fixture
async def client_caregiver(http_client, caregiver_token):
    """Client with caregiver auth - set headers directly."""
    http_client.headers["Authorization"] = f"Bearer {caregiver_token}"
    return http_client


@pytest_asyncio.fixture
async def client_viewer(http_client, viewer_token):
    """Client with viewer auth."""
    http_client.headers["Authorization"] = f"Bearer {viewer_token}"
    return http_client


@pytest_asyncio.fixture
async def client_other(http_client, other_token):
    """Client with other user auth."""
    http_client.headers["Authorization"] = f"Bearer {other_token}"
    return http_client