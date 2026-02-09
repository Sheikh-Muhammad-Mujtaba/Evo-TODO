# Dockerfile for MCP Server

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files (context is ./backend)
COPY pyproject.toml ./

# Install dependencies
RUN uv venv && \
    uv pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlmodel \
    pydantic-settings \
    pydantic[email] \
    "psycopg[binary,pool]" \
    httpx \
    "PyJWT[crypto]" \
    mcp \
    starlette

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code (context is ./backend)
COPY app/ ./app/
COPY mcp_server/ ./mcp_server/

# Expose port 8000
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start MCP server
CMD ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
