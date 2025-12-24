"""
Test Configuration and Fixtures

Provides shared fixtures for unit, integration, and E2E tests.

Constitutional Requirements:
- Test database isolated from production - Principle V
- Test data cleared after each test (no cross-contamination)
- Multi-tenant isolation tested rigorously
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.database import get_session
from src.main import app


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    """
    Create in-memory SQLite engine for testing

    Uses StaticPool to maintain single connection across threads.
    Database is recreated for each test (clean slate).

    Yields:
        Engine: SQLAlchemy engine with test database
    """
    # In-memory SQLite database (fast, isolated)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Single connection for in-memory DB
    )

    # Create all tables with checkfirst=True to avoid "already exists" errors
    # This is needed because some tests reimport models multiple times
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except Exception:
        # If creation fails, clear metadata and try again
        SQLModel.metadata.clear()
        SQLModel.metadata.create_all(engine, checkfirst=True)

    yield engine

    # Clean up after test
    try:
        SQLModel.metadata.drop_all(engine)
    except Exception:
        pass  # Ignore drop errors
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    """
    Create test database session

    Each test gets a fresh session with empty database.
    Rollback happens automatically after test completes.

    Args:
        engine: Test database engine (from engine_fixture)

    Yields:
        Session: SQLModel session for test
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="db_session")
def db_session_fixture(engine):
    """
    Alias for session fixture (for integration tests compatibility)

    Each test gets a fresh session with empty database.
    Rollback happens automatically after test completes.

    Args:
        engine: Test database engine (from engine_fixture)

    Yields:
        Session: SQLModel session for test
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create FastAPI test client with database override

    Overrides get_session dependency to use test database.
    All API requests in tests use this test database.

    Args:
        session: Test database session (from session_fixture)

    Yields:
        TestClient: FastAPI test client
    """

    def get_session_override():
        """Override get_session to return test session"""
        return session

    # Override FastAPI dependency
    app.dependency_overrides[get_session] = get_session_override

    # Create test client
    client = TestClient(app)

    yield client

    # Clear overrides after test
    app.dependency_overrides.clear()


# Test data factories


@pytest.fixture
def sample_student_data():
    """
    Sample student registration data for tests

    Returns:
        dict: Valid registration request data
    """
    return {
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test Student",
    }


@pytest.fixture
def sample_student_data_2():
    """
    Second sample student (for multi-tenant isolation tests)

    Returns:
        dict: Valid registration request data (different email)
    """
    return {
        "email": "student2@example.com",
        "password": "SecurePass456",
        "full_name": "Second Student",
    }
