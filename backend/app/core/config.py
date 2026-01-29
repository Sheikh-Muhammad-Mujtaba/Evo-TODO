"""
Task T-202/T-221: Configuration and settings for Phase II backend

Phase II Constitution Compliance:
- All configuration from environment variables (security)
- Better Auth configuration for JWT validation (Task T-221, Official JWT Plugin)
- EdDSA/JWKS verification (not HS256 shared secret)
- Database URL for PostgreSQL/Neon connection
- CORS for frontend communication
"""

from functools import lru_cache
from typing import Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Task T-202/T-221: Application settings from environment variables"""

    # Better Auth Configuration (Task T-221, Official JWT Plugin with EdDSA/JWKS)
    BETTER_AUTH_URL: str = "http://localhost:3000"
    BETTER_AUTH_JWKS_URL: str = ""  # Computed from BETTER_AUTH_URL if empty
    BETTER_AUTH_ISSUER: str = ""    # Defaults to BETTER_AUTH_URL if empty
    BETTER_AUTH_AUDIENCE: str = ""  # Defaults to BETTER_AUTH_URL if empty

    # JWKS Cache Configuration
    JWKS_CACHE_LIFESPAN: int = 300  # 5 minutes
    JWKS_CACHE_MAX_KEYS: int = 16

    # Database Configuration (Task T-210/T-223)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/evo_todo"

    # CORS Configuration (comma-separated string converted to list)
    CORS_ORIGINS: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    MODEL_NAME: str = "gemini/gemini-pro"

    # MCP Server Configuration
    MCP_SERVER_URL: str = "http://localhost:8001"
    # Internal secret for MCP server authentication (agent -> MCP server trust)
    MCP_INTERNAL_SECRET: str = "mcp-internal-secret-change-in-production"

    model_config = ConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list"""
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def __init__(self, **data):
        """Initialize settings and compute derived URLs"""
        super().__init__(**data)

        # Compute derived URLs if not explicitly set
        if not self.BETTER_AUTH_JWKS_URL:
            self.BETTER_AUTH_JWKS_URL = f"{self.BETTER_AUTH_URL}/api/auth/jwks"
        if not self.BETTER_AUTH_ISSUER:
            self.BETTER_AUTH_ISSUER = self.BETTER_AUTH_URL
        if not self.BETTER_AUTH_AUDIENCE:
            self.BETTER_AUTH_AUDIENCE = self.BETTER_AUTH_URL


@lru_cache()
def get_settings() -> Settings:
    """Task T-202: Get cached settings instance"""
    return Settings()


# Task T-202: Export settings
settings = get_settings()
