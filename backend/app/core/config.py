"""
Task T-202: Configuration and settings for Phase II backend

Phase II Constitution Compliance:
- All configuration from environment variables (security)
- JWT configuration with shared secret
- Database URL for PostgreSQL connection
- CORS for frontend communication
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Task T-202: Application settings from environment variables"""

    # JWT Configuration (Task T-213)
    JWT_SECRET_KEY: str = "your-256-bit-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days

    # Database Configuration (Task T-210)
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
