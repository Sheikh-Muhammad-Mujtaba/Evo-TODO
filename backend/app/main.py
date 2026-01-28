"""
Task T-202: FastAPI application entry point

Phase II Backend - Full-stack todo application with:
- Better Auth JWT validation (EdDSA/JWKS)
- SQLModel ORM with PostgreSQL (Neon)
- User-scoped data isolation
- RESTful API endpoints
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.database import init_db
from app.api.todos import router as todos_router
from app.schemas.chat import ChatRequest
from app.agents.chat_agent import get_agent_response, get_initialized_triage_agent
from agents import Agent
from agents.mcp import MCPServerStreamableHttp
from typing import Optional

# Flag to track if database has been initialized (for idempotent startup)
_db_initialized = False
_triage_agent: Optional[Agent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Task T-210: Application lifecycle - database initialization

    On startup: Create all database tables (idempotent - only runs once)
    On shutdown: Cleanup (if needed)

    For Vercel serverless: Only initializes once, not on every cold start.
    Multiple concurrent invocations are safe due to idempotent table creation.
    """
    global _db_initialized
    global _triage_agent

    # Startup: Initialize database tables (only once)
    if not _db_initialized:
        init_db()
        _db_initialized = True
    
    # Initialize the MCP HTTP server and the triage agent
    # The MCP server should be running separately on port 8001
    try:
        print(f"[INFO] Attempting to connect to MCP server at {settings.MCP_SERVER_URL}/mcp")
        async with MCPServerStreamableHttp(
            name="TodoMCP",
            params={
                "url": settings.MCP_SERVER_URL + "/mcp",
            },
            cache_tools_list=True,
        ) as mcp_server:
            print("[INFO] Successfully connected to MCP server")
            _triage_agent = await get_initialized_triage_agent(mcp_server)
            yield
    except Exception as e:
        print(f"[WARNING] Failed to connect to MCP server: {str(e)}")
        print("[INFO] Application will continue without MCP server functionality")
        print("[INFO] Make sure to start the MCP server separately:")
        print(f"[INFO]   cd backend && python -m mcp_server.server")
        yield



# Task T-202: Create FastAPI app instance
app = FastAPI(
    title="Evo-TODO API",
    description="Phase II: Full-stack todo application with Better Auth JWT (EdDSA/JWKS)",
    version="1.0.0",
    lifespan=lifespan,
)

# Task T-202: CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task T-216: Register Todo CRUD endpoints
app.include_router(todos_router)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the agent.
    
    Parameters:
    - message: The user's message
    - user_id: The user's ID (required)
    - conversation_id: The conversation ID (auto-generated if not provided)
    """
    if _triage_agent is None:
        raise RuntimeError("Triage agent not initialized.")
    
    # Validate that conversation_id is not None
    if request.conversation_id is None:
        raise ValueError("conversation_id cannot be None")
    
    response = await get_agent_response(
        triage_agent=_triage_agent,
        user_input=request.message,
        user_id=request.user_id,
        conversation_id=request.conversation_id,
    )
    return {"response": response, "conversation_id": request.conversation_id}


# Task T-202: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker Compose healthchecks"""
    return {"status": "healthy"}


# Task T-202: Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Evo-TODO API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
