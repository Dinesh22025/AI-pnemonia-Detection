"""
Database connection configuration using SQLAlchemy.
Supports PostgreSQL with SQLite fallback for local development.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

load_dotenv()

# Force SQLite for local development
DATABASE_URL = "sqlite:///./pneumovision.db"

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.
    Ensures proper cleanup after request completion.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables.
    This function is called lazily to handle database initialization
    after the engine is created.
    """
    from sqlalchemy import create_engine as _create_engine
    engine = _create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "False").lower() == "true",
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)
    return engine


def drop_db():
    """Drop all tables - use with caution."""
    from sqlalchemy import create_engine as _create_engine
    engine = _create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.drop_all(bind=engine)
