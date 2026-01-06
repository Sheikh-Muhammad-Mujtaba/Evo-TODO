# Vercel Python Serverless Function Entry Point
# Wraps FastAPI app for Vercel deployment

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings
from app.models.database import init_db
from app.api.todos import router as todos_router

# Flag to track if database has been initialized
_db_initialized = False

# Create FastAPI app
app = FastAPI(
    title="Evo-TODO API",
    description="Phase II: Full-stack todo application with Better Auth JWT (EdDSA/JWKS)",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on first request (idempotent)
@app.on_event("startup")
async def startup_event():
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
        except Exception as e:
            print(f"DB init warning: {e}")

# Register Todo CRUD endpoints
app.include_router(todos_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Vercel"""
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Evo-TODO API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

# Vercel ASGI handler
handler = app
