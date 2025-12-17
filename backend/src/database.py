"""
Database Connection and Session Management

SQLModel engine configuration and session factory.
Provides database session dependency for FastAPI routes.

Constitutional Requirement: Multi-tenant isolation enforced at query level.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.pool import NullPool, QueuePool
from sqlmodel import Session, create_engine

from src.config import get_settings

# Lazy engine creation - only create when first accessed
_engine = None


def get_engine():
    """Get or create database engine (lazy initialization for serverless)"""
    global _engine
    if _engine is None:
        settings = get_settings()
        # Database engine configuration
        # Uses connection pooling in production, NullPool in testing
        if settings.is_production:
            _engine = create_engine(
                settings.database_url_str,
                echo=False,  # Don't log SQL queries in production
                pool_pre_ping=True,  # Verify connections before using
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
            )
        else:
            _engine = create_engine(
                settings.database_url_str,
                echo=settings.debug,  # Log SQL queries in debug mode
                poolclass=NullPool,  # No pooling in development
            )
    return _engine




def get_session() -> Generator[Session, None, None]:
    """
    Database session dependency

    Creates a new SQLModel session for each request.
    Automatically commits on success, rolls back on error.

    Yields:
        Session: SQLModel database session

    Example:
        >>> from fastapi import Depends
        >>> from src.database import get_session
        >>>
        >>> @app.get("/students")
        >>> def list_students(session: Session = Depends(get_session)):
        >>>     students = session.exec(select(Student)).all()
        >>>     return students
    """
    with Session(get_engine()) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


def init_db() -> None:
    """
    Initialize database

    Creates all tables defined in SQLModel models.
    Used in development and testing. In production, use Alembic migrations.

    Note:
        This function is NOT used in Phase I. Alembic migrations handle
        schema creation (Constitutional Requirement: Principle VII).
    """
    from sqlmodel import SQLModel

    # Import all models to register them with SQLModel
    from src.models.student import Student  # noqa: F401
    from src.models.subject import Subject  # noqa: F401
    from src.models.syllabus_point import SyllabusPoint  # noqa: F401

    SQLModel.metadata.create_all(get_engine())


def drop_db() -> None:
    """
    Drop all database tables

    DANGEROUS: Used only in testing.
    Never call in production.
    """
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(get_engine())
