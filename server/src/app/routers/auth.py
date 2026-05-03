"""
Authentication Router.

Endpoints:
- POST /auth/register     → Register with email + password
- POST /auth/login       → Login with email + password
- POST /auth/refresh    → Refresh access token
- GET  /auth/me        → Get current user profile

Also integrates with Google OAuth from auth_google.py.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.auth import get_current_user
from src.app.schemas.auth import (
    MessageResponse,
    TokenResponse,
    TokenRefreshRequest,
    UserLoginRequest,
    UserMeResponse,
    UserRegisterRequest,
    UserResponse,
)
from src.app.services import auth_service
from src.database.models.user import User
from src.database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new account with email + password",
    description=(
        "Creates a new user account with email and password authentication. "
        "Returns JWT access and refresh tokens upon successful registration."
    ),
)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user with email + password."""
    try:
        user, tokens = await auth_service.register_user(db=db, payload=payload)
        await db.commit()
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email + password (form-data)",
    description=(
        "Authenticates user with email and password. "
        "Returns JWT access and refresh tokens upon successful login. "
        "Use form-data content type."
    ),
)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login with email + password (form-data format)."""
    try:
        payload = UserLoginRequest(email=form_data.username, password=form_data.password)
        user, tokens = await auth_service.authenticate_user(db=db, payload=payload)
        await db.commit()
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login with email + password (JSON)",
    description=(
        "Authenticates user with email and password. "
        "Returns JWT access and refresh tokens upon successful login. "
        "Use JSON content type with 'email' and 'password' fields."
    ),
)
async def login_json(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login with email + password (JSON format)."""
    try:
        user, tokens = await auth_service.authenticate_user(db=db, payload=payload)
        await db.commit()
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description=(
        "Use refresh token to obtain new access token. "
        "Both access and refresh tokens are returned."
    ),
)
async def refresh(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        tokens = await auth_service.refresh_access_token(db=db, refresh_token=payload.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserMeResponse:
    """Get current authenticated user profile."""
    return current_user