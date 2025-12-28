# Task T-214: FastAPI dependencies for authentication and database access
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID

from app.core.security import decode_access_token
from app.models.database import get_db
from app.models.user import User
from jose import JWTError

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
    Task T-214: FastAPI dependency to extract and validate JWT token

    This dependency extracts the JWT token from the Authorization header,
    validates the signature, and returns the authenticated User object.

    Usage in protected routes:
        @router.get("/todos")
        async def get_todos(current_user: User = Depends(get_current_user)):
            # current_user is the authenticated User from JWT
            todos = db.query(Todo).filter(Todo.user_id == current_user.id).all()
            return todos

    Flow:
    1. Extract token from "Authorization: Bearer <token>" header
    2. Decode JWT and extract user_id (sub claim)
    3. Query database for User with that ID
    4. Verify user is active (is_active=True)
    5. Return User object for use in route

    Error Responses:
    - 401 Unauthorized: Missing/malformed Authorization header
    - 401 Unauthorized: Invalid/expired JWT token
    - 401 Unauthorized: User ID not found in token
    - 401 Unauthorized: User doesn't exist in database
    - 401 Unauthorized: User account is deactivated

    Security Features:
    - Token signature verified using JWT_SECRET_KEY
    - Token expiration verified
    - User existence verified (token claims not trusted alone)
    - User active status verified (allows account deactivation)
    - No password stored/compared (JWT-based)
    """
    token = credentials.credentials

    try:
        # Task T-214: Decode JWT and extract claims
        payload = decode_access_token(token)

        # Extract user_id from "sub" (subject) claim
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (missing user ID)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Task T-214: Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (invalid user ID format)",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        # Task T-214: Token signature or expiration invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Task T-214: Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Task T-214: Verify user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
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
    Task T-214: Extract user ID directly from Authorization header (low-level)

    This is a lower-level dependency for cases where you need just the user ID
    without full database lookup. Not recommended for most endpoints.

    Args:
        authorization: Authorization header value

    Returns:
        User UUID if valid token, None if no token or invalid

    Example:
        @router.get("/user-id")
        async def get_user_id(user_id: Optional[UUID] = Depends(get_user_id_from_header)):
            return {"user_id": user_id}

    Security Note: This does NOT verify the user still exists or is active.
    Only use for informational endpoints or combine with get_current_user
    for protected operations.
    """
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            return None

        return UUID(user_id_str)
    except (ValueError, JWTError):
        return None
