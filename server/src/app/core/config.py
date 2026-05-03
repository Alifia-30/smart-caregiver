"""
Application configuration using pydantic-settings.
All sensitive values come from environment variables / .env file.

pip install pydantic-settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "CaregiverApp"
    DEBUG: bool = False

    # ── Database (Neon PostgreSQL) ────────────────────────────────────────────
    # Format: postgresql+asyncpg://user:password@host/dbname
    DATABASE_URL: str
    DB_ECHO: bool = False

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str                        # openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Google OAuth ──────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str               # e.g. https://yourapp.com/auth/google/callback

    # ── GROQ (AI Recommendations) ────────────────────────────────────────────────
    GROQ_API_KEY: str = ""

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()  # type: ignore[call-arg]
