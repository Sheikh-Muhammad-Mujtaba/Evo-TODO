"""
Task T-221: Better Auth JWT Verification (Official JWT Plugin Architecture)

This module verifies Better Auth JWTs using:
- EdDSA/Ed25519 asymmetric keys from JWKS endpoint
- Issuer and audience claim validation
- Key ID (kid) based key selection with automatic refresh on rotation
- Automatic JWKS caching with 5-minute TTL

The official Better Auth JWT plugin uses:
- Algorithm: EdDSA with Ed25519 curve (asymmetric)
- Key source: JWKS endpoint at /api/auth/jwks
- Token structure: HS256 -> EdDSA, shared secret -> JWKS endpoint
- Claims required: sub (user_id), iss (issuer), aud (audience), exp (expiration)

Phase II Constitution Compliance:
- Better Auth manages user authentication (required per spec)
- JWT validation at FastAPI dependency level (Task T-222)
- User_id extracted from JWT claims for data isolation (Task T-224)
- All requests must provide valid Better Auth JWT token
"""

import logging
from typing import Dict, Optional

import jwt
from jwt import PyJWKClient, PyJWKClientError
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    DecodeError,
)

from app.core.config import settings
from app.core.jwks_client import (
    get_jwks_client,
    refresh_jwks_cache,
    JWKSFetchError,
    JWKSKeyNotFoundError,
)

logger = logging.getLogger(__name__)


async def verify_better_auth_token(token: str) -> Dict:
    """
    Task T-221: Verify and decode Better Auth JWT token using JWKS.

    This function validates the JWT using EdDSA/Ed25519 public keys from
    the Better Auth JWKS endpoint. It performs full JWT verification including
    signature validation, claim validation, and key rotation handling.

    Verification Flow:
    1. Get JWKS client (uses cached instance with 5-min TTL)
    2. Extract signing key from JWKS based on kid in JWT header
    3. Verify JWT signature using Ed25519 public key
    4. Validate issuer (iss) claim matches BETTER_AUTH_ISSUER
    5. Validate audience (aud) claim matches BETTER_AUTH_AUDIENCE
    6. Validate expiration (exp) claim
    7. Extract and verify 'sub' (subject/user_id) claim is present
    8. Return token payload for downstream use

    Key Rotation Handling:
    If a JWT has a kid (key ID) not found in the cached JWKS:
    - First attempt: Use cached JWKS
    - If kid not found: Refresh JWKS cache from endpoint
    - Second attempt: Try again with fresh JWKS
    - If still not found: Raise ValueError (401 Unauthorized)

    Args:
        token (str): JWT token from Authorization header (without "Bearer " prefix)

    Returns:
        Dict: Token payload containing:
            - 'sub': User ID (UUID string)
            - 'iss': Issuer URL
            - 'aud': Audience URL
            - 'exp': Expiration timestamp
            - Additional claims from Better Auth

    Raises:
        ValueError: If token is invalid, expired, or verification fails
            - "Token has expired" → ExpiredSignatureError
            - "Invalid token audience" → InvalidAudienceError
            - "Invalid token issuer" → InvalidIssuerError
            - "Invalid token format" → DecodeError
            - "Token missing 'sub' (user_id) claim" → Missing sub claim
            - "Token signing key not found in JWKS" → kid not in JWKS after refresh
            - "Token verification failed" → Other unexpected errors

    Security Notes:
    - Signature verification uses Ed25519 public key from JWKS (asymmetric)
    - Token is never trusted without signature verification
    - Claims are validated against configured issuer/audience
    - Issuer/audience mismatch indicates token from different service
    - User_id extraction is safe for subsequent database queries

    Example:
        >>> token = "eyJhbGciOiJFZERTQSIsImtpZCI6ImtleS0xIn0.eyJzdWIi..."
        >>> payload = await verify_better_auth_token(token)
        >>> user_id = payload["sub"]  # e.g., "550e8400-e29b-41d4-a716-446655440000"
    """
    try:
        # Get JWKS client (uses cached instance, singleton pattern)
        jwks_client = get_jwks_client()

        # Extract signing key from JWKS based on kid in JWT header
        # This will fail if kid is not in the cached JWKS
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
        except PyJWKClientError as e:
            # Key not found in cache - try refreshing JWKS cache once
            logger.warning(f"Key not found in JWKS cache, refreshing: {e}")
            refresh_jwks_cache()
            jwks_client = get_jwks_client()

            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
            except PyJWKClientError as e:
                logger.error(f"Key still not found after JWKS refresh: {e}")
                raise ValueError("Token signing key not found in JWKS")

        # Verify and decode JWT with full claim validation
        # Uses Ed25519 public key from JWKS endpoint
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],  # Better Auth JWT plugin default algorithm
            audience=settings.BETTER_AUTH_AUDIENCE,
            issuer=settings.BETTER_AUTH_ISSUER,
            options={
                "verify_signature": True,   # Verify Ed25519 signature
                "verify_exp": True,         # Verify expiration
                "verify_aud": True,         # Verify audience claim
                "verify_iss": True,         # Verify issuer claim
                "require": ["sub", "exp", "iss", "aud"],  # Required claims
            }
        )

        # Ensure user_id (sub claim) is present
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' (user_id) claim")

        logger.debug(f"Token verified for user: {user_id[:8]}...")
        return payload

    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise ValueError("Token has expired")

    except InvalidAudienceError:
        logger.warning(f"Invalid audience claim, expected: {settings.BETTER_AUTH_AUDIENCE}")
        raise ValueError("Invalid token audience")

    except InvalidIssuerError:
        logger.warning(f"Invalid issuer claim, expected: {settings.BETTER_AUTH_ISSUER}")
        raise ValueError("Invalid token issuer")

    except DecodeError as e:
        logger.warning(f"Token decode failed: {e}")
        raise ValueError("Invalid token format")

    except InvalidTokenError as e:
        logger.warning(f"Token validation failed: {e}")
        raise ValueError(f"Invalid token: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise ValueError("Token verification failed")


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Task T-222: Extract user_id from Better Auth JWT token (synchronous version).

    Safely extracts user_id from the 'sub' claim without raising exceptions.
    Does NOT verify signature or claims - use only for non-critical extraction.

    This function is useful for:
    - Extracting user_id before authentication (for logging/diagnostics)
    - Fallback paths where authentication failure is acceptable
    - Non-critical use cases where unverified extraction is acceptable

    WARNING: Do NOT use this for authentication or authorization decisions.
    Always use verify_better_auth_token() for protected operations.

    Args:
        token (str): JWT token string

    Returns:
        Optional[str]: User ID (UUID string from 'sub' claim) or None if invalid

    Example:
        >>> token = "eyJhbGciOiJFZERTQSIsImtpZCI6ImtleS0xIn0..."
        >>> user_id = get_user_id_from_token(token)
        >>> if user_id:
        ...     logger.info(f"Request from user: {user_id}")
        ... else:
        ...     logger.info("Request with invalid token")

    Security Note:
        This function does NOT verify the signature. It only decodes
        the JWT without verification. Use verify_better_auth_token()
        for any security-critical operations.
    """
    try:
        # Decode without verification (unsafe extraction only)
        unverified = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return unverified.get("sub")
    except Exception:
        return None
