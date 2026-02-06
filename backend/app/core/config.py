"""
Configuration and settings for Phase II backend (Shared)
Structured logging configuration

Phase II Constitution Compliance:
- All configuration from environment variables (security)
- Better Auth configuration for JWT validation (Official JWT Plugin)
- EdDSA/JWKS verification (not HS256 shared secret)
- Database URL for PostgreSQL/Neon connection
- CORS for frontend communication
- Structured logging
- Gemini API configuration for agent service
- MCP Server configuration for inter-service communication
"""

from functools import lru_cache
import logging
import logging.config
import json
from datetime import datetime
from typing import Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for production logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        return json.dumps(log_entry)


def configure_logging(environment: str = "development", debug: bool = True) -> None:
    """
    Configure structured logging based on environment.

    - Development: Human-readable format with DEBUG level
    - Production: JSON structured format with INFO level
    """
    log_level = logging.DEBUG if debug else logging.INFO

    if environment == "production":
        # Production: JSON structured logging
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logging.root.handlers = [handler]
        logging.root.setLevel(log_level)
    else:
        # Development: Human-readable logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class Settings(BaseSettings):
    """Application settings from environment variables for shared backend services"""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Better Auth Configuration (from todo-service)
    BETTER_AUTH_URL: str = "http://localhost:3000"
    BETTER_AUTH_JWKS_URL: str = ""  # Computed from BETTER_AUTH_URL if empty
    BETTER_AUTH_ISSUER: str = ""    # Defaults to BETTER_AUTH_URL if empty
    BETTER_AUTH_AUDIENCE: str = ""  # Defaults to BETTER_AUTH_URL if empty

    # JWKS Cache Configuration (from todo-service)
    JWKS_CACHE_LIFESPAN: int = 300  # 5 minutes
    JWKS_CACHE_MAX_KEYS: int = 16

    # Database Configuration (from todo-service)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/evo_todo"

    # CORS Configuration (from todo-service)
    CORS_ORIGINS: str = "http://localhost:3000"

    # Gemini API Configuration (from agent-service)
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    MODEL_NAME: str = "gemini-2.5-flash" # Using agent-service's model name, as it appears more specific

    # MCP Server Configuration (from both, consolidating to localhost default for local dev)
    # Note: This should be the base URL only, endpoint path will be appended in code
    MCP_SERVER_URL: str = "http://localhost:8001"
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
    """Get cached settings instance"""
    return Settings()


# Export settings
settings = get_settings()

# Initialize structured logging
configure_logging(settings.ENVIRONMENT, settings.DEBUG)

logger = logging.getLogger(__name__)

logger.debug(f"MCP_SERVER_URL: {settings.MCP_SERVER_URL}")
logger.debug(f"MCP_INTERNAL_SECRET (first 8 chars): {settings.MCP_INTERNAL_SECRET[:8]}...")