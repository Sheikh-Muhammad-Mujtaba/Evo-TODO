from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from app.agents.chat_agent import get_initialized_orchestrator_agent, get_agent_response
from agents.mcp import MCPServerStreamableHttp
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None
    user_id: str

@router.post("/{user_id}")
async def chat_endpoint(user_id: str, request_data: ChatRequest, http_request: Request):
    conversation_id = request_data.conversation_id or uuid4()

    # Get the authorization header
    authorization = http_request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]

    # Create MCP connection with per-request headers (updated SDK pattern)
    async with MCPServerStreamableHttp(
        name="Todo MCP Server Client",
        params={
            "url": f"{settings.MCP_SERVER_URL}/mcp",
            "headers": {
                "X-User-ID": user_id,
                "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
                "Authorization": f"Bearer {token}",
            },
        },
        cache_tools_list=True,
    ) as mcp_server:
        try:
            orchestrator_agent = await get_initialized_orchestrator_agent(mcp_server)
            assistant_response = await get_agent_response(
                orchestrator_agent,
                request_data.message,
                user_id,
                conversation_id,
            )
            return {
                "response": assistant_response,
                "conversation_id": str(conversation_id),
            }
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
