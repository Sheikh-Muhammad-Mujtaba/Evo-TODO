# Task T-210: Database connection configuration and session management
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Task T-210: Create engine with connection pool
# NullPool disables connection pooling (useful for development with sqlite)
# For production PostgreSQL, use QueuePool (default) with pool_size and max_overflow
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging (development only)
    future=True,  # Use SQLAlchemy 2.0 style
    # Use NullPool for development, QueuePool for production
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
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
