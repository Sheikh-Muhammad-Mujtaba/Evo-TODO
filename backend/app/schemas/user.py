# Task T-211: User Pydantic schemas for API request/response validation
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    """
    Task T-211: Schema for user signup/registration requests

    Fields:
    - email: Valid email address (Pydantic EmailStr validates format)
    - password: Plain text password (validated on backend: min 8 chars)
    - name: Optional display name

    This schema is used in POST /auth/signup to validate incoming data.
    """
    email: EmailStr = Field(
        ...,
        description="User email address (must be unique and valid)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (8-128 characters, will be hashed with bcrypt)"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name (optional)"
    )

    class Config:
        """Task T-211: Pydantic config for schema"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "name": "John Doe"
            }
        }

class UserLogin(BaseModel):
    """
    Task T-211: Schema for user signin/login requests

    Fields:
    - email: Email address for lookup
    - password: Plain text password for verification

    This schema is used in POST /auth/signin to validate credentials.
    """
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    password: str = Field(
        ...,
        description="User password (will be compared against bcrypt hash)"
    )

    class Config:
        """Task T-211: Pydantic config for schema"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }

class UserResponse(BaseModel):
    """
    Task T-211: Schema for user data in API responses

    Fields:
    - id: User UUID (never None in response)
    - email: User email address
    - name: Optional display name
    - created_at: Account creation timestamp

    Security Note: password_hash is NOT included in responses (never leaked to client).

    This schema is used in authentication responses and protected endpoints.
    """
    id: UUID = Field(
        ...,
        description="User unique identifier (UUID)"
    )
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    name: Optional[str] = Field(
        default=None,
        description="User display name"
    )
    created_at: datetime = Field(
        ...,
        description="UTC timestamp when account was created"
    )

    class Config:
        """Task T-211: Pydantic ORM mode for SQLModel conversion"""
        from_attributes = True  # Allow conversion from SQLModel instances
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-29T10:30:00Z"
            }
        }

class TokenResponse(BaseModel):
    """
    Task T-211: Schema for authentication token response

    Fields:
    - access_token: JWT token to include in Authorization header
    - token_type: Always "bearer" (HTTP Bearer scheme)
    - user: Full UserResponse object with user data

    This schema is returned by POST /auth/signup and POST /auth/signin endpoints.

    Client Usage:
        Authorization: Bearer <access_token>
    """
    access_token: str = Field(
        ...,
        description="JWT access token for protected endpoints"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer' for HTTP Bearer scheme)"
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user data"
    )

    class Config:
        """Task T-211: Pydantic config for schema"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "created_at": "2025-12-29T10:30:00Z"
                }
            }
        }

class UserUpdate(BaseModel):
    """
    Task T-211: Schema for updating user profile (future use)

    Fields:
    - name: New display name (optional, leave None to keep current)
    - email: New email address (optional, would require re-verification)

    This schema is for future PUT /users/{id} endpoint (not in Phase II).
    """
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Updated display name"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Updated email address (would need re-verification)"
    )

    class Config:
        """Task T-211: Pydantic config for schema"""
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": None
            }
        }
