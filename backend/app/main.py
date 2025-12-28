"""
Task T-202: FastAPI application entry point

Phase II Backend - Full-stack todo application with:
- JWT authentication with shared secret
- SQLModel ORM with PostgreSQL
- User-scoped data isolation
- RESTful API endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Task T-202: Create FastAPI app instance
app = FastAPI(
    title="Evo-TODO API",
    description="Phase II: Full-stack todo application with JWT authentication",
    version="1.0.0",
)

# Task T-202: CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task T-202: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker Compose healthchecks"""
    return {"status": "healthy"}

# Task T-215: Auth endpoints will be registered here
# Task T-216: Todo CRUD endpoints will be registered here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
