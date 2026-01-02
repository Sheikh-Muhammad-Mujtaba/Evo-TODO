# Task T-212: Todo Pydantic schemas for API request/response validation
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class TodoCreate(BaseModel):
    """
    Task T-212: Schema for creating a new todo (POST /api/todos)

    Fields:
    - title: Required todo title (1-500 characters)
    - description: Optional longer description (0-2000 characters)

    User ID is automatically extracted from JWT token (not in request body).

    Validation:
    - title: Must be non-empty after stripping whitespace
    - title: Max 500 characters
    - description: Max 2000 characters (optional)

    Example:
        POST /api/todos
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread from Whole Foods"
        }
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Todo title (1-500 characters, required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Todo description (0-2000 characters, optional)"
    )

    class Config:
        """Task T-212: Pydantic config"""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread from Whole Foods"
            }
        }

class TodoUpdate(BaseModel):
    """
    Task T-212: Schema for updating todo fields (PUT /api/todos/{id})

    Fields:
    - title: New title (optional, None means no change)
    - description: New description (optional, None means no change)

    At least one field must be provided (validated in endpoint).

    Partial Update Example:
        PUT /api/todos/550e8400-e29b-41d4-a716-446655440000
        {
            "title": "Buy groceries at Trader Joe's"
        }
    """
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated todo title (optional, leave None to keep current)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated todo description (optional, leave None to keep current)"
    )

    class Config:
        """Task T-212: Pydantic config"""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries at Trader Joe's",
                "description": None
            }
        }

class TodoToggle(BaseModel):
    """
    Task T-212: Schema for toggling todo completion status (PATCH /api/todos/{id})

    Fields:
    - is_complete: New completion status (true/false)

    Example:
        PATCH /api/todos/550e8400-e29b-41d4-a716-446655440000
        {
            "is_complete": true
        }
    """
    is_complete: bool = Field(
        ...,
        description="Completion status (true = completed, false = pending)"
    )

    class Config:
        """Task T-212: Pydantic config"""
        json_schema_extra = {
            "example": {
                "is_complete": True
            }
        }

class TodoResponse(BaseModel):
    """
    Task T-212: Schema for todo data in API responses

    Fields:
    - id: Todo UUID (unique identifier)
    - user_id: Owner user UUID (for debugging, not exposed to frontend)
    - title: Todo title
    - description: Optional description
    - is_complete: Completion status
    - created_at: Creation timestamp (UTC)
    - updated_at: Last modification timestamp (UTC)

    This schema is returned by all todo endpoints (GET, POST, PUT, PATCH).

    Security: user_id is included in response for debugging but frontend
    should NEVER allow user to see other users' todos due to API filtering.

    Example Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "w2PYO9wq2FGP2fR111aTZkbPWD5ZyJPC",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "is_complete": false,
            "created_at": "2025-12-29T10:30:00Z",
            "updated_at": "2025-12-29T10:30:00Z"
        }
    """
    id: UUID = Field(
        ...,
        description="Todo unique identifier (UUID)"
    )
    user_id: str = Field(
        ...,
        description="Owner user ID (for API validation only, not shown in frontend)"
    )
    title: str = Field(
        ...,
        description="Todo title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Todo description (optional)"
    )
    is_complete: bool = Field(
        ...,
        description="Completion status"
    )
    created_at: datetime = Field(
        ...,
        description="UTC timestamp when todo was created"
    )
    updated_at: datetime = Field(
        ...,
        description="UTC timestamp of last update"
    )

    class Config:
        """Task T-212: Pydantic ORM mode for SQLModel conversion"""
        from_attributes = True  # Allow conversion from SQLModel instances
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "w2PYO9wq2FGP2fR111aTZkbPWD5ZyJPC",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_complete": False,
                "created_at": "2025-12-29T10:30:00Z",
                "updated_at": "2025-12-29T10:30:00Z"
            }
        }

class TodoListResponse(BaseModel):
    """
    Task T-212: Schema for paginated todo list responses (GET /api/todos)

    Fields:
    - todos: Array of TodoResponse objects
    - total: Total count of todos matching the filter

    Example Response:
        {
            "todos": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "title": "Buy groceries",
                    "is_complete": false,
                    ...
                }
            ],
            "total": 42
        }

    Pagination: Frontend can use skip/limit query parameters:
        GET /api/todos?skip=0&limit=10
    """
    todos: list[TodoResponse] = Field(
        default_factory=list,
        description="Array of todo items"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total count of todos (for pagination)"
    )

    class Config:
        """Task T-212: Pydantic config"""
        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "w2PYO9wq2FGP2fR111aTZkbPWD5ZyJPC",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_complete": False,
                        "created_at": "2025-12-29T10:30:00Z",
                        "updated_at": "2025-12-29T10:30:00Z"
                    }
                ],
                "total": 42
            }
        }

class TodoBulkDelete(BaseModel):
    """
    Task T-212: Schema for bulk delete operation (future use)

    Fields:
    - ids: List of todo IDs to delete

    This schema is for future DELETE /api/todos endpoint (not in Phase II).
    """
    ids: list[UUID] = Field(
        ...,
        min_items=1,
        description="Array of todo IDs to delete (minimum 1)"
    )

    class Config:
        """Task T-212: Pydantic config"""
        json_schema_extra = {
            "example": {
                "ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001"
                ]
            }
        }
