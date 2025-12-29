# Task T-210/T-223: Database connection configuration and session management
# Task T-223: Neon PostgreSQL serverless support
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings

# Task T-223: Create engine with Neon-optimized connection pooling
# For Neon Serverless PostgreSQL, we need:
# - Smaller pool size (serverless scales, don't hold connections)
# - Connection timeout for idle connections
# - Proper pool pre-ping to detect stale connections
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging (development only)
    future=True,  # Use SQLAlchemy 2.0 style
    # Task T-223: Neon-specific pooling configuration
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else QueuePool,
    # Task T-223: Serverless optimizations
    pool_size=2,  # Reduce for serverless (scales on-demand)
    max_overflow=3,  # Small overflow for temporary spikes
    pool_pre_ping=True,  # Verify connections before use (Neon important)
    pool_recycle=300,  # Recycle connections after 5 mins (Neon timeout)
    connect_args={"connect_timeout": 10},  # Connect timeout for Neon
)

def get_db():
    """
    Task T-210: Dependency for getting database session in FastAPI routes

    Usage in FastAPI route:
        @app.get("/todos")
        async def get_todos(db: Session = Depends(get_db)):
            todos = db.query(Todo).filter(Todo.user_id == current_user.id).all()
            return todos

    FastAPI automatically closes the session after the request completes.
    """
    with Session(engine) as session:
        yield session

def init_db():
    """
    Task T-210: Initialize database tables (create_all)

    Call this once on application startup:
        @app.on_event("startup")
        def on_startup():
            init_db()

    Creates all tables defined in SQLModel models (User, Todo).
    Safe to call multiple times (idempotent - only creates missing tables).

    In production, use Alembic for migrations instead of create_all.
    """
    SQLModel.metadata.create_all(engine)

def drop_db():
    """
    Task T-210: Drop all database tables (DESTRUCTIVE - development only)

    WARNING: This deletes all tables and data. Only use for testing/cleanup.
    """
    SQLModel.metadata.drop_all(engine)
