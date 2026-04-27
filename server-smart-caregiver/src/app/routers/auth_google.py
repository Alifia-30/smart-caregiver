"""
Google OAuth 2.0 FastAPI router.

Endpoints:
    GET  /auth/google/login     → redirect to Google consent screen
    GET  /auth/google/callback  → handle Google redirect, return JWT tokens
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.oauth_google import (
    build_google_auth_url,
    exchange_code_for_tokens,
    fetch_google_user_info,
    generate_oauth_state,
    get_or_create_google_user,
    issue_tokens_for_user,
)
from src.database.session import get_db

router = APIRouter(prefix="/auth/google", tags=["auth"])

# In production store state in Redis with short TTL (5 min).
# This in-memory set is fine for single-process dev only.
_pending_states: set[str] = set()


@router.get("/login")
async def google_login() -> RedirectResponse:
    """
    Step 1: Redirect the user to Google's OAuth consent screen.
    The 'state' parameter prevents CSRF attacks.
    """
    state = generate_oauth_state()
    _pending_states.add(state)
    auth_url = build_google_auth_url(state=state)
    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Step 2: Google redirects here after user grants permission.
    - Validate state (CSRF check)
    - Exchange code → Google tokens
    - Fetch Google user profile
    - Upsert User + OAuthAccount in DB
    - Return our JWT tokens
    """
    # CSRF check
    if state not in _pending_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state.",
        )
    _pending_states.discard(state)

    # Exchange code for Google tokens
    try:
        google_tokens = await exchange_code_for_tokens(code=code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange code with Google.",
        )

    # Fetch profile
    try:
        google_profile = await fetch_google_user_info(
            access_token=google_tokens["access_token"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch Google user profile.",
        )

    # Upsert user in database
    user = await get_or_create_google_user(
        db=db,
        google_profile=google_profile,
        google_tokens=google_tokens,
    )

    return issue_tokens_for_user(user)
