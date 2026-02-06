import logging
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from mcp_server.mcp_app import mcp_app_instance
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create a FastAPI app instance to host the MCP server as HTTP
# Note: FastMCP's streamable_http_app() manages its own session lifecycle
mcp_host_app = FastAPI(
    title="Todo MCP Host",
    description="Hosts the Todo MCP Server instance via HTTP",
    version="1.0.0",
)

# Add CORS middleware to allow frontend communication
mcp_host_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list, # From shared settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Mcp-Session-Id"], # Expose Mcp-Session-Id for browser clients
)

# Mount the FastMCP application under the /mcp path
# This exposes the JSON-RPC endpoint for MCP clients at http://localhost:8001/mcp
mcp_host_app.mount("/mcp", mcp_app_instance.streamable_http_app())

@mcp_host_app.get("/health")
async def health_check():
    """Health check endpoint for the MCP server."""
    return {"status": "healthy", "service": "Todo MCP Host (FastMCP)"}

if __name__ == "__main__":
    uvicorn.run(mcp_host_app, host="0.0.0.0", port=8001)