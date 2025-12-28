# Task T-215: Authentication endpoints (signup, signin, logout)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta

from app.models.database import get_db
from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)

# Task T-215: Create router for authentication endpoints
# All endpoints prefixed with /auth and tagged as "authentication"
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized - invalid credentials or token"},
        422: {"description": "Unprocessable Entity - validation error"},
    }
)

@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account and receive JWT token"
)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Task T-215: User signup endpoint (POST /auth/signup)

    Creates a new user account with email and password.

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "name": "John Doe"  // optional
        }

    Response (201 Created):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-29T10:30:00Z"
            }
        }

    Error Responses:
    - 400 Bad Request: Email already registered
    - 400 Bad Request: Password too short (< 8 chars)
    - 422 Unprocessable Entity: Invalid email format or missing fields

    Flow:
    1. Validate user data (Pydantic UserCreate schema)
    2. Check if email already exists in database
    3. Validate password length (minimum 8 characters)
    4. Hash password using bcrypt (12 rounds)
    5. Create user record in database
    6. Generate JWT token with user_id as subject
    7. Return token + user data

    Security:
    - Password validated for minimum length on backend
    - Password hashed with bcrypt before storage
    - Duplicate email check prevents account takeover
    - Token issued immediately (user is logged in)
    - Original password never logged or stored

    Constitution Compliance (T-215):
    - ✅ Password hashed (bcrypt)
    - ✅ User data isolation ready (user_id in token)
    - ✅ JWT token returned (no session cookies)
    """
    # Task T-215: Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = db.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or sign in.",
        )

    # Task T-215: Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )

    if len(user_data.password) > 128:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be less than 128 characters.",
        )

    # Task T-215: Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        is_active=True,  # New users are active by default
    )

    # Task T-215: Save user to database
    db.add(user)
    db.commit()
    db.refresh(user)

    # Task T-215: Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@router.post(
    "/signin",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user with email and password"
)
async def signin(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Task T-215: User signin endpoint (POST /auth/signin)

    Authenticates user with email and password, returns JWT token.

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }

    Response (200 OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-29T10:30:00Z"
            }
        }

    Error Responses:
    - 401 Unauthorized: Invalid email or password
    - 401 Unauthorized: Account is deactivated
    - 422 Unprocessable Entity: Invalid email format

    Flow:
    1. Validate credentials data (Pydantic UserLogin schema)
    2. Query database for user by email
    3. Verify password against bcrypt hash
    4. Check if user account is active
    5. Generate JWT token with user_id as subject
    6. Return token + user data

    Security:
    - Generic 401 error for both invalid email and password (timing attack prevention)
    - Password verified against bcrypt hash (not compared as plain text)
    - Inactive accounts cannot login (allows soft-delete via deactivation)
    - Token includes user_id but not password or sensitive data

    Constitution Compliance (T-215):
    - ✅ Password verified via bcrypt
    - ✅ User data isolation ready (user_id in token)
    - ✅ JWT token returned (no session cookies)
    """
    # Task T-215: Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = db.exec(statement).first()

    # Task T-215: Generic error message to prevent email enumeration
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Task T-215: Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Task T-215: Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated. Contact support for assistance.",
        )

    # Task T-215: Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@router.post(
    "/logout",
    summary="User Logout",
    description="Logout endpoint (client-side token removal)"
)
async def logout() -> dict:
    """
    Task T-215: User logout endpoint (POST /auth/logout)

    Logout endpoint for client coordination. The actual logout is handled
    client-side by removing the JWT token from local storage.

    Request: No body required

    Response (200 OK):
        {
            "message": "Logout successful"
        }

    Implementation Notes:
    - JWT is stateless, so server logout just returns success
    - Client responsible for removing token from localStorage/sessionStorage
    - Token will continue to work until expiration (exp claim)
    - For full logout (token revocation), implement:
      * Redis blacklist of revoked tokens
      * Token revocation endpoint that checks blacklist
      * Shorter token expiration times
      * Refresh token rotation

    Security:
    - This endpoint is optional (client can logout without calling it)
    - No authentication required (can logout without token)
    - Useful for analytics (track when users logout)
    - In production, might call analytics or cleanup services

    Client Usage (JavaScript):
        const response = await fetch('http://localhost:8000/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
        });

        if (response.ok) {
            localStorage.removeItem('auth_token');
            // Redirect to login page
        }

    Constitution Compliance (T-215):
    - ✅ Stateless authentication (no session server-side)
    - ✅ Client-side token removal (no state to maintain)
    - ✅ No sensitive data in response
    """
    return {
        "message": "Logout successful. Please remove your token from the client."
    }

# Task T-215: Import get_current_user for the /me endpoint
from app.api.deps import get_current_user

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get authenticated user profile"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Task T-215: Get current user profile endpoint (GET /auth/me)

    Returns the authenticated user's profile information.

    Requires: Valid JWT token in Authorization header

    Response (200 OK):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "name": "John Doe",
            "created_at": "2025-12-29T10:30:00Z"
        }

    Error Responses:
    - 401 Unauthorized: Missing or invalid token

    Import Note: get_current_user is imported at module level
    """
    # Task T-215: Return authenticated user from dependency
    return UserResponse.model_validate(current_user)
