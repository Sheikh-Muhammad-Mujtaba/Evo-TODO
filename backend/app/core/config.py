"""
Task T-202/T-221: Configuration and settings for Phase II backend

Phase II Constitution Compliance:
- All configuration from environment variables (security)
- Better Auth configuration for JWT validation (Task T-221)
- Database URL for PostgreSQL/Neon connection
- CORS for frontend communication
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Task T-202/T-221: Application settings from environment variables"""

    # Better Auth Configuration (Task T-221)
    BETTER_AUTH_SECRET: str = "your-better-auth-secret-key-change-in-production"
    BETTER_AUTH_API_URL: str = "https://api.betterauth.io"

    # JWT Configuration (from Better Auth JWT plugin)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days

    # Database Configuration (Task T-210/T-223)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/evo_todo"

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Task T-202: Get cached settings instance"""
    return Settings()


# Task T-202: Export settings
settings = get_settings()
