"""
Google OAuth 2.0 integration service.

Libraries needed:
    pip install authlib httpx python-jose[cryptography] passlib[bcrypt]

Flow:
    1. Frontend redirects user to /auth/google/login
    2. Google redirects back to /auth/google/callback?code=...&state=...
    3. We exchange code → tokens → fetch user profile from Google
    4. Upsert User + OAuthAccount
    5. Return our own JWT access + refresh tokens
"""

import secrets
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.core.config import settings
from src.app.core.security import create_access_token, create_refresh_token
from src.database.models.user import OAuthAccount, User
from src.database.enums import AuthProvider


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


# ── OAuth state helpers (CSRF protection) ────────────────────────────────────

def generate_oauth_state() -> str:
    """Generate a secure random state token for CSRF protection."""
    return secrets.token_urlsafe(32)


def build_google_auth_url(state: str) -> str:
    """Return the Google OAuth authorization URL."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",       # request refresh_token
        "prompt": "consent",            # force consent screen to always get refresh_token
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


# ── Token exchange ────────────────────────────────────────────────────────────

async def exchange_code_for_tokens(code: str) -> dict:
    """Exchange authorization code for Google access/refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_google_user_info(access_token: str) -> dict:
    """Fetch user profile from Google using access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


# ── User upsert ───────────────────────────────────────────────────────────────

async def get_or_create_google_user(
    db: AsyncSession,
    google_profile: dict,
    google_tokens: dict,
) -> User:
    """
    Upsert logic:
        1. Look up OAuthAccount by (provider=google, provider_user_id=sub).
        2. Found → update tokens, return linked user.
        3. Not found → check if email already exists in users table.
            a. Exists  → link new OAuthAccount to existing user.
            b. New user → create User + OAuthAccount.
    """
    provider_uid = google_profile["sub"]
    email = google_profile.get("email", "").lower()
    name = google_profile.get("name", "")
    avatar = google_profile.get("picture")

    token_expires_at: Optional[datetime] = None
    if expires_in := google_tokens.get("expires_in"):
        token_expires_at = datetime.now(tz=timezone.utc).replace(
            second=datetime.now(tz=timezone.utc).second + int(expires_in)
        )

    # 1. Look up existing OAuth account
    stmt = (
        select(OAuthAccount)
        .where(
            OAuthAccount.provider == AuthProvider.GOOGLE,
            OAuthAccount.provider_user_id == provider_uid,
        )
        .options(selectinload(OAuthAccount.user))
    )
    result = await db.execute(stmt)
    oauth_account: Optional[OAuthAccount] = result.scalar_one_or_none()

    if oauth_account:
        # 2. Update tokens
        oauth_account.access_token = google_tokens.get("access_token")
        oauth_account.refresh_token = google_tokens.get("refresh_token") or oauth_account.refresh_token
        oauth_account.token_expires_at = token_expires_at
        oauth_account.provider_avatar_url = avatar
        user = oauth_account.user
        user.last_login_at = datetime.now(tz=timezone.utc)
        if not user.avatar_url:
            user.avatar_url = avatar
        await db.flush()
        return user

    # 3. No OAuth account — check if email exists
    existing_user_stmt = select(User).where(User.email == email)
    existing_result = await db.execute(existing_user_stmt)
    user: Optional[User] = existing_result.scalar_one_or_none()

    if not user:
        # 3b. Brand new user
        user = User(
            email=email,
            full_name=name,
            avatar_url=avatar,
            is_email_verified=True,    # Google verified the email
            last_login_at=datetime.now(tz=timezone.utc),
        )
        db.add(user)
        await db.flush()  # populate user.id

    # 3a or 3b — create the OAuth account link
    new_oauth = OAuthAccount(
        user_id=user.id,
        provider=AuthProvider.GOOGLE,
        provider_user_id=provider_uid,
        access_token=google_tokens.get("access_token"),
        refresh_token=google_tokens.get("refresh_token"),
        token_expires_at=token_expires_at,
        provider_email=email,
        provider_name=name,
        provider_avatar_url=avatar,
    )
    db.add(new_oauth)
    user.last_login_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return user


# ── JWT issuance ──────────────────────────────────────────────────────────────

def issue_tokens_for_user(user: User) -> dict:
    """Issue our own JWT access + refresh tokens after successful OAuth."""
    return {
        "access_token": create_access_token(subject=str(user.id)),
        "refresh_token": create_refresh_token(subject=str(user.id)),
        "token_type": "bearer",
    }
