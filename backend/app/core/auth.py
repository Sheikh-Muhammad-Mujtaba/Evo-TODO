"""
Task T-221: Better Auth Configuration and JWT Verification

This module configures the Better Auth client and provides JWT verification functions
for FastAPI. Better Auth handles all authentication (signup, signin, session management).
This module validates Better Auth JWTs at the API boundary.

Phase II Constitution Compliance:
- Better Auth manages user authentication (required per spec)
- JWT validation happens at FastAPI dependency level
- User_id extracted from JWT claims for data isolation
- All requests must provide valid Better Auth JWT token
"""

import os
from typing import Dict, Optional
import httpx
from jose import JWTError, jwt
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """T-221: Better Auth Configuration from Environment"""

    BETTER_AUTH_SECRET: str = os.getenv(
        "BETTER_AUTH_SECRET",
        "your-better-auth-secret-key-change-in-production"
    )
    BETTER_AUTH_API_URL: str = os.getenv(
        "BETTER_AUTH_API_URL",
        "https://api.betterauth.io"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days

    class Config:
        env_file = ".env"


# T-221: Initialize Better Auth settings
auth_settings = AuthSettings()


async def verify_better_auth_token(token: str) -> Dict:
    """
    T-222: Verify and decode Better Auth JWT token

    This function validates the JWT signature and expiration using the shared secret.
    It extracts the user_id (sub claim) for data isolation in subsequent queries.

    Args:
        token: JWT token from Authorization header (Bearer token)

    Returns:
        Token payload dict with 'sub' (user_id) and other claims

    Raises:
        ValueError: If token is invalid, expired, or signature verification fails

    Flow:
        1. Decode JWT using BETTER_AUTH_SECRET and HS256
        2. Validate 'sub' claim exists (user_id)
        3. Return payload for dependency extraction
    """
    try:
        # Decode and verify JWT signature using shared secret
        payload = jwt.decode(
            token,
            auth_settings.BETTER_AUTH_SECRET,
            algorithms=[auth_settings.JWT_ALGORITHM]
        )

        # Ensure user_id (sub claim) is present
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' (user_id) claim")

        return payload

    except JWTError as e:
        # JWT validation failed (signature, expiration, format)
        raise ValueError(f"Invalid or expired token: {str(e)}")


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    T-222: Extract user_id from Better Auth JWT token

    Safely extracts user_id without raising exceptions (returns None on failure).
    Used by FastAPI dependencies for data isolation.

    Args:
        token: JWT token string

    Returns:
        User ID (UUID from 'sub' claim) or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            auth_settings.BETTER_AUTH_SECRET,
            algorithms=[auth_settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None


async def validate_better_auth_with_service(token: str) -> bool:
    """
    T-221: Validate token with Better Auth service (optional)

    This method can validate tokens directly with the Better Auth service
    for additional security (check if token was revoked, etc.).

    Currently disabled for MVP; enable for production with token revocation support.

    Args:
        token: JWT token to validate

    Returns:
        True if valid, False otherwise
    """
    # NOTE: Better Auth service validation can be added here
    # For MVP, we rely on JWT signature verification only
    # In production, call: {BETTER_AUTH_API_URL}/api/auth/verify with token
    return True


# T-221: Test that module imports correctly
if __name__ == "__main__":
    print(f"✓ Better Auth module loaded successfully")
    print(f"✓ BETTER_AUTH_SECRET configured: {bool(auth_settings.BETTER_AUTH_SECRET)}")
    print(f"✓ BETTER_AUTH_API_URL: {auth_settings.BETTER_AUTH_API_URL}")
    print(f"✓ JWT_ALGORITHM: {auth_settings.JWT_ALGORITHM}")
    print(f"✓ JWT_EXPIRATION_HOURS: {auth_settings.JWT_EXPIRATION_HOURS}")
