# Stage 1: Builder
FROM python:3.11-slim-buster as builder

WORKDIR /app

# Install uv (or pip, depending on preference)
RUN pip install uv

# Copy only the pyproject.toml and uv.lock to leverage caching
COPY ../pyproject.toml ../uv.lock ./

# Install dependencies using uv
RUN uv sync --system --no-setup-py

# Stage 2: Runner
FROM python:3.11-slim-buster as runner

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Copy the shared app directory
COPY ../app/ ./app/

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the FastAPI application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]