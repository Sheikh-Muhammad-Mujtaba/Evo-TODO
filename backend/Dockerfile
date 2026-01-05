# Task T-204: FastAPI backend Docker image

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY pyproject.toml .

# Task T-204: Install Python dependencies via uv
RUN pip install uv && uv sync

# Copy application code
COPY . .

# Task T-204: Expose port 8000
EXPOSE 8000

# Task T-204: Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Task T-204: Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
