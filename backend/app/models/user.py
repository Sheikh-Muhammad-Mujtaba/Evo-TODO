# Task T-208: SQLModel User entity with database schema
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, DateTime, Boolean, Index

class User(SQLModel, table=True):
    """
    Task T-208: User model for SQLModel ORM

    Maps to 'users' table with fields:
    - id: UUID primary key (auto-generated)
    - email: Unique email address (indexed for login queries)
    - password_hash: Bcrypt hashed password (never stored in plain text)
    - name: Optional user display name
    - is_active: Boolean for account deactivation without deletion
    - created_at: UTC timestamp for account creation
    - updated_at: UTC timestamp for last modification

    Security: Password stored as hash only. All queries filtered by user_id
    for data isolation (constitution requirement).
    """
    __tablename__ = "users"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier (UUID v4)"
    )

    # Authentication Fields
    email: str = Field(
        unique=True,
        nullable=False,
        index=True,
        max_length=255,
        description="User email (unique, indexed for login)"
    )

    password_hash: str = Field(
        nullable=False,
        max_length=255,
        description="Bcrypt hashed password (never plain text)"
    )

    # Profile Fields
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name (optional)"
    )

    # Account Status
    is_active: bool = Field(
        default=True,
        description="Account active status (true = active, false = deactivated)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="UTC timestamp when user was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="UTC timestamp of last update"
    )

    # Task T-208: No table arguments needed for users table
    # (email unique constraint and id index handled by Field definitions)

    def __repr__(self) -> str:
        """Task T-208: String representation for debugging"""
        return f"User(id={self.id}, email={self.email}, is_active={self.is_active})"
