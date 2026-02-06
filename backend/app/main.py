"""
Task T-202: FastAPI application entry point
Task T003/T005: Throttling middleware and metrics logging

Phase II Backend - Full-stack todo application with:
- Better Auth JWT validation (EdDSA/JWKS)
- SQLModel ORM with PostgreSQL (Neon)
- User-scoped data isolation
- RESTful API endpoints
- Stateless throttling and request logging
"""

"""
Task T-202: FastAPI application entry point
Task T003/T005: Throttling middleware and metrics logging

Phase II Backend - Full-stack todo application with:
- Better Auth JWT validation (EdDSA/JWKS)
- SQLModel ORM with PostgreSQL (Neon)
- User-scoped data isolation
- RESTful API endpoints
- Stateless throttling and request logging
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import ThrottlingMiddleware
from app.models.database import init_db
from app.api.todos import router as todos_router


# Flag to track if database has been initialized (for idempotent startup)
_db_initialized = False


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

    # Startup: Initialize database tables (only once)
    if not _db_initialized:
        init_db()
        _db_initialized = True

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

# Task T003/T005: Throttling and metrics middleware (stateless)
app.add_middleware(ThrottlingMiddleware)

# Task T-216: Register Todo CRUD endpoints
app.include_router(todos_router)


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
