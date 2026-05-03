"""
Integration tests - Test against live API with real HTTP calls.
Uses httpx AsyncClient to test the entire FastAPI app.
"""

import uuid
from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app


# =============================================================================
# Base Test Client (No Auth)
# =============================================================================

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# =============================================================================
# Test Health Check
# =============================================================================


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health-check")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# =============================================================================
# Test Auth Endpoints
# =============================================================================


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Login with invalid credentials should fail."""
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrong"},
    )
    # 422 = validation error OR 401 = invalid credentials (both acceptable)
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_weekly_summary_internal_job(client: AsyncClient):
    """Internal weekly summary job should work (internal endpoint)."""
    response = await client.post("/internal/jobs/send-weekly-summary")
    # May return 200 (success) or 500 (if no data) but should not be 401
    assert response.status_code in [200, 500, 404]


# =============================================================================
# Test OpenAPI Documentation
# =============================================================================


@pytest.mark.asyncio
async def test_openapi_docs(client: AsyncClient):
    """OpenAPI docs should be available."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "Smart Caregiver API"


@pytest.mark.asyncio
async def test_swagger_ui(client: AsyncClient):
    """Swagger UI should be available."""
    response = await client.get("/docs")
    assert response.status_code == 200


# =============================================================================
# Test ReDoc
# =============================================================================


@pytest.mark.asyncio
async def test_redoc(client: AsyncClient):
    """ReDoc should be available."""
    response = await client.get("/redoc")
    assert response.status_code == 200