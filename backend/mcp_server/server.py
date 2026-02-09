import logging
import uvicorn
import contextlib
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

# Use absolute imports from backend root
from mcp_server.mcp_app import mcp_app_instance
from app.core.config import settings

logger = logging.getLogger(__name__)

# CRITICAL: MCP SDK requires proper lifespan management for SSE transport
# The session_manager must be running for the MCP server to accept connections
# We use stateless_http=False (SSE) in mcp_app.py, so this is REQUIRED.

@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """
    Lifespan context manager that starts the MCP session manager.
    This is CRITICAL for SSE transport (stateless_http=False) to work properly.
    """
    logger.info("Starting MCP session manager...")
    async with mcp_app_instance.session_manager.run():
        logger.info("MCP session manager running.")
        yield
    logger.info("MCP session manager stopped.")

async def health_check(request):
    """Health check endpoint for the MCP server."""
    return JSONResponse({"status": "healthy", "service": "Todo MCP Host (MCP SDK/SSE)"})

# Create Starlette app with the lifespan and routes
# Mount the MCP server at root (/) so the MCP endpoint is at /mcp (the default path)
# By mounting at root, the streamable_http_app's default /mcp endpoint is directly accessible
app = Starlette(
    routes=[
        Route("/api/health", health_check),  # Move health to /api/health to avoid conflict
        Mount("/", app=mcp_app_instance.streamable_http_app()),
    ],
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],  # Required for browser-based MCP clients
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)