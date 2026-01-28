from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Unique conversation ID. Auto-generated if not provided."
    )
    user_id: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID
