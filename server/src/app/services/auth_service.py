"""
Authentication service for email/password registration and login.

This service handles:
- User registration with email + password
- User login verification
- Token refresh
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.database.enums import AuthProvider
from src.database.models.user import OAuthAccount, User


async def register_user(
    db: AsyncSession,
    payload: UserRegisterRequest,
) -> tuple[User, TokenResponse]:
    """
    Register a new user with email + password.
    
    Raises ValueError if email already exists.
    """
    email = payload.email.lower()
    
    existing_stmt = select(User).where(User.email == email)
    existing = await db.execute(existing_stmt)
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        full_name=payload.full_name,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        is_email_verified=False,
    )
    db.add(user)
    await db.flush()

    return user, _create_token_response(user)


async def authenticate_user(
    db: AsyncSession,
    payload: UserLoginRequest,
) -> tuple[User, TokenResponse]:
    """
    Authenticate user with email or username (treated as email).
    
    Raises ValueError if credentials invalid.
    """
    email = payload.email.lower()
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("Invalid email or password")

    if not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("User account is inactive")

    user.last_login_at = datetime.now(tz=timezone.utc)
    await db.flush()

    return user, _create_token_response(user)


async def refresh_access_token(
    db: AsyncSession,
    refresh_token: str,
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Raises ValueError if refresh token invalid.
    """
    payload = decode_token(refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise ValueError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise ValueError("Invalid token payload")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise ValueError("User not found or inactive")

    return _create_token_response(user)


def _create_token_response(user: User) -> TokenResponse:
    """Create token response for user."""
    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_refresh_token(subject=str(user.id)),
        token_type="bearer",
    )


async def get_user_by_id(
    db: AsyncSession,
    user_id: str,
) -> Optional[User]:
    """Get user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()