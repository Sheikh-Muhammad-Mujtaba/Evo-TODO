# Task T-222: FastAPI dependencies for Better Auth JWT validation (Official JWT Plugin)
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID

from app.core.auth import verify_better_auth_token, get_user_id_from_token
from app.core.jwks_client import JWKSFetchError
from app.models.database import get_db
from app.models.user import User
from jwt.exceptions import InvalidTokenError

# Task T-214: HTTP Bearer security scheme for API documentation
# This registers the Bearer authentication in FastAPI's OpenAPI (Swagger) UI
security = HTTPBearer(
    description="JWT token in Authorization header. Format: Bearer <token>"
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Task T-222: FastAPI dependency to validate Better Auth JWT token (Official Plugin)

    This dependency extracts the Better Auth JWT token from the Authorization header,
    validates it using EdDSA/Ed25519 keys from the JWKS endpoint, and returns the
    authenticated User object from the database.

    Uses official Better Auth JWT plugin architecture:
    - EdDSA/Ed25519 asymmetric verification (not HS256 symmetric)
    - JWKS endpoint for public key retrieval
    - Issuer/audience claim validation
    - Automatic key rotation via kid

    Usage in protected routes:
        @router.get("/todos")
        async def get_todos(current_user: User = Depends(get_current_user)):
            # current_user is the authenticated User from Better Auth JWT
            todos = db.query(Todo).filter(Todo.user_id == current_user.id).all()
            return todos

    Flow:
    1. Extract token from "Authorization: Bearer <token>" header
    2. Verify token signature and expiration with JWKS endpoint (EdDSA)
    3. Validate issuer and audience claims
    4. Extract user_id from token's 'sub' (subject) claim
    5. Query database for User with that ID (defense in depth)
    6. Verify user is active (is_active=True)
    7. Return User object for use in route

    Error Responses:
    - 401 Unauthorized: Missing/malformed Authorization header
    - 401 Unauthorized: Invalid/expired Better Auth JWT token
    - 401 Unauthorized: Invalid issuer or audience
    - 401 Unauthorized: User ID not found in token claims
    - 401 Unauthorized: User doesn't exist in database
    - 401 Unauthorized: User account is deactivated
    - 503 Service Unavailable: JWKS endpoint unreachable (Better Auth service down)

    Security Features (T-222):
    - Token signature verified using Ed25519 public key from JWKS (asymmetric)
    - Token expiration verified via JWT exp claim
    - Issuer/audience validated against configured values
    - User existence verified in database (token claims not trusted alone)
    - User active status verified (allows account deactivation)
    - Data isolation enforced: All queries filter by user_id
    """
    token = credentials.credentials

    try:
        # Task T-222: Verify Better Auth JWT signature and expiration (EdDSA/JWKS)
        payload = await verify_better_auth_token(token)

        # Extract user_id from "sub" (subject) claim
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Task T-222: Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWKSFetchError:
        # Better Auth service (JWKS endpoint) is unavailable
        # Return 503 instead of 401 to indicate temporary service issue
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable",
        )

    except ValueError:
        # Token signature or expiration invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Task T-222: Fetch user from database (defense in depth)
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Task T-222: Verify user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Task T-214: Optional authentication dependency

    This dependency allows routes to work with OR without authentication.
    Returns None if no valid token, returns User if valid token.

    Usage:
        @router.get("/todos")
        async def get_todos(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                # User is authenticated
                todos = db.query(Todo).filter(Todo.user_id == current_user.id).all()
            else:
                # User is not authenticated, can show public todos or empty list
                todos = []
            return todos

    Returns:
        User object if valid token provided, None otherwise (never raises 401)

    Use Cases:
    - Public endpoints with optional personalization
    - Reading public user profiles
    - Feed endpoints that show more to authenticated users
    """
    if credentials is None:
        # No Authorization header provided
        return None

    try:
        # Task T-214: Use same validation as get_current_user
        return await get_current_user(credentials, db)
    except HTTPException:
        # Token is invalid, return None instead of raising
        return None

def get_user_id_from_header(
    authorization: Optional[str] = Header(None)
) -> Optional[UUID]:
    """
    Task T-222: Extract user ID directly from Authorization header (low-level)

    This is a lower-level dependency for cases where you need just the user ID
    without full database lookup. Uses Better Auth JWT validation.

    Args:
        authorization: Authorization header value

    Returns:
        User UUID if valid Better Auth token, None if no token or invalid

    Example:
        @router.get("/user-id")
        async def get_user_id(user_id: Optional[UUID] = Depends(get_user_id_from_header)):
            return {"user_id": user_id}

    Security Note (T-222): This does NOT verify the user still exists or is active.
    Only use for informational endpoints or combine with get_current_user
    for protected operations. Always use get_current_user for data modification.
    """
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        user_id_str = get_user_id_from_token(token)

        if user_id_str is None:
            return None

        return UUID(user_id_str)
    except (ValueError, JWTError):
        return None
