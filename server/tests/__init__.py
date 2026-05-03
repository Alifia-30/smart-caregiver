"""
Test fixtures and configuration.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.base import Base
from src.database.models.user import User
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.health import HealthRecord
from src.database.models.notification import Notification
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
from src.database.session import get_db


# =============================================================================
# SQLAlchemy Test Engine (SQLite in-memory)
# =============================================================================

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables for testing."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables after testing."""
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    create_tables()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        drop_tables()


# =============================================================================
# Override get_db to use test DB
# =============================================================================

def override_get_db():
    """Override FastAPI dependency to use test DB."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# =============================================================================
# Async Test Client
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def client() -> Generator[AsyncClient, None, None]:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# =============================================================================
# Test Users Fixtures
# =============================================================================


@pytest.fixture
def caregiver_user(db_session: Session) -> User:
    """Create a test caregiver user."""
    user = User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="caregiver@test.com",
        hashed_password="$2b$12$dummy_hash_for_testing",
        full_name="Test Caregiver",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def viewer_user(db_session: Session) -> User:
    """Create a test viewer user."""
    user = User(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        email="viewer@test.com",
        hashed_password="$2b$12$dummy_hash_for_testing",
        full_name="Test Viewer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


# =============================================================================
# Test Elderly Profile Fixture
# =============================================================================


@pytest.fixture
def elderly_profile(db_session: Session, caregiver_user: User) -> ElderlyProfile:
    """Create a test elderly profile."""
    elderly = ElderlyProfile(
        id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        caregiver_id=caregiver_user.id,
        full_name="Budi Santoso",
        age=75,
        gender="male",
        mobility_level="assisted",
    )
    db_session.add(elderly)
    db_session.commit()
    return elderly


# =============================================================================
# Viewer Invitation Fixture
# =============================================================================


@pytest.fixture
def viewer_invitation(
    db_session: Session,
    elderly_profile: ElderlyProfile,
    viewer_user: User,
) -> None:
    """Create accepted viewer invitation."""
    invitation = ViewerInvitation(
        id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        elderly_id=elderly_profile.id,
        viewer_id=viewer_user.id,
        invited_by=elderly_profile.caregiver_id,
        email="viewer@test.com",
        token="test-token-123",
        status=InvitationStatus.ACCEPTED,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()


# =============================================================================
# Auth Tokens Fixtures
# =============================================================================


@pytest.fixture
def caregiver_token(caregiver_user: User) -> str:
    """Generate access token for caregiver."""
    return create_access_token(
        data={"sub": str(caregiver_user.id), "type": "access"}
    )


@pytest.fixture
def viewer_token(viewer_user: User) -> str:
    """Generate access token for viewer."""
    return create_access_token(
        data={"sub": str(viewer_user.id), "type": "access"}
    )


# =============================================================================
# Authorized Client Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def auth_client(
    client: AsyncClient,
    caregiver_token: str,
) -> AsyncClient:
    """Client with caregiver authentication."""
    client.headers["Authorization"] = f"Bearer {caregiver_token}"
    return client


@pytest_asyncio.fixture
async def viewer_client(
    client: AsyncClient,
    viewer_token: str,
) -> AsyncClient:
    """Client with viewer authentication."""
    client.headers["Authorization"] = f"Bearer {viewer_token}"
    return client


# =============================================================================
# Health Record Fixture
# =============================================================================


@pytest.fixture
def health_record(
    db_session: Session,
    elderly_profile: ElderlyProfile,
    caregiver_user: User,
) -> HealthRecord:
    """Create a test health record."""
    record = HealthRecord(
        id=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        elderly_id=elderly_profile.id,
        recorded_by=caregiver_user.id,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        blood_sugar=100.0,
        heart_rate=75.0,
        body_temperature=36.5,
        health_status=HealthStatus.NORMAL,
        recorded_at=datetime.now(timezone.utc),
    )
    db_session.add(record)
    db_session.commit()
    return record


# =============================================================================
# Schedule Fixture
# =============================================================================


@pytest.fixture
def schedule(
    db_session: Session,
    elderly_profile: ElderlyProfile,
) -> Schedule:
    """Create a test schedule."""
    schedule = Schedule(
        id=uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
        elderly_id=elderly_profile.id,
        title="Minum Obat Pagi",
        schedule_type=ScheduleType.MEDICATION,
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
        recurrence=RecurrenceType.DAILY,
        is_active=True,
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule


# =============================================================================
# Recommendation Fixture
# =============================================================================


@pytest.fixture
def recommendation(
    db_session: Session,
    elderly_profile: ElderlyProfile,
) -> AIActivityRecommendation:
    """Create a test recommendation."""
    rec = AIActivityRecommendation(
        id=uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"),
        elderly_id=elderly_profile.id,
        title="Senam Chairs",
        description="Latihan duduk untuk mobilitas",
        category="physical",
        status=RecommendationStatus.PENDING,
    )
    db_session.add(rec)
    db_session.commit()
    return rec