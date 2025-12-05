# -*- coding: utf-8 -*-
"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database file path
DATABASE_PATH = DATA_DIR / "vision_security.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with SQLite-specific configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for ORM models
Base = declarative_base()


def init_db():
    """Initialize database by creating all tables.
    
    This function should be called on application startup to ensure
    all database tables are created. It's safe to call multiple times
    as it will only create tables that don't already exist.
    """
    # Import models to register them with Base.metadata
    try:
        from models.camera import Camera  # noqa: F401
        from models.ai_settings import AISettings  # noqa: F401
    except ImportError:
        from src.models.camera import Camera  # noqa: F401
        from src.models.ai_settings import AISettings  # noqa: F401
    
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session dependency for FastAPI.
    
    This function is used as a dependency in FastAPI route handlers
    to provide a database session. The session is automatically closed
    after the request is completed.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
