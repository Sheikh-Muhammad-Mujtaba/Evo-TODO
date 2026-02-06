# Dockerfile for MCP Server

# ---- Builder Stage ----
FROM python:3.13 as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY ../pyproject.toml ../uv.lock ./

# Install dependencies into a virtual environment
RUN uv venv && uv sync --no-cache

# ---- Final Stage ----
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /.venv

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy only the necessary code
COPY ../app/ ./app/
COPY mcp_server/ mcp_server/

# Expose port 8000 (standard for uvicorn)
EXPOSE 8000

# Start MCP server using uvicorn
CMD ["uvicorn", "mcp_server.server:mcp_host_app", "--host", "0.0.0.0", "--port", "8000"]
