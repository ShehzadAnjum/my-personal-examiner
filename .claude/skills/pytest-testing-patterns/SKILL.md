---
name: pytest-testing-patterns
description: pytest testing patterns for unit tests, mocks, fixtures, and SQLModel testing. Use when writing backend tests, test fixtures, or test utilities.
---

# Skill: Pytest Testing Patterns

**Type**: Testing Infrastructure
**Created**: 2025-12-18
**Domain**: Unit & Integration Testing
**Parent Agent**: 07-Testing-Quality

## Overview
Pytest testing patterns for FastAPI + SQLModel applications with >80% coverage target.

## Common Patterns

### Conftest (Fixtures)
```python
# tests/conftest.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from src.database import get_session
from src.main import app

@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """FastAPI test client with DB override"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Unit Test Pattern
```python
# tests/unit/test_student_service.py
from src.services.student_service import create_student
from src.schemas.student import RegisterRequest

def test_create_student_success(session: Session):
    """Test student creation with valid data"""
    data = RegisterRequest(
        email="test@example.com",
        password="SecurePass123",
        full_name="Test Student"
    )

    student = create_student(session, data)

    assert student.email == "test@example.com"
    assert student.full_name == "Test Student"
    assert student.password_hash != "SecurePass123"  # Should be hashed
```

### Integration Test Pattern (API)
```python
# tests/integration/test_auth_routes.py
def test_register_endpoint_success(client: TestClient):
    """Test POST /api/auth/register with valid data"""
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "SecurePass123",
        "full_name": "New Student"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "password" not in data  # Never expose password

def test_register_endpoint_duplicate_email(client: TestClient):
    """Test duplicate email returns 409"""
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "Pass123",
        "full_name": "First"
    })

    response = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "Pass456",
        "full_name": "Second"
    })

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()
```

### Parametrize Pattern
```python
@pytest.mark.parametrize("password,expected_error", [
    ("short", "at least 8 characters"),
    ("nouppercase123", "uppercase letter"),
    ("NOLOWERCASE123", "lowercase letter"),
    ("NoDigitsHere", "digit"),
])
def test_password_validation(password: str, expected_error: str):
    """Test password validation rules"""
    with pytest.raises(ValueError, match=expected_error):
        RegisterRequest(email="test@test.com", password=password)
```

### Async Pattern
```python
@pytest.mark.asyncio
async def test_async_marking_engine():
    """Test async marking with AI"""
    result = await mark_answer_async(
        question_id=uuid4(),
        student_answer="Supply increases...",
        marking_scheme={"max_marks": 8}
    )

    assert 0 <= result.marks_awarded <= 8
```

## Coverage Requirements

### Run with Coverage
```bash
uv run pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Target: >80%
```bash
# Check coverage passes threshold
uv run pytest --cov=src --cov-fail-under=80
```

## Constitutional Compliance

**Principle VII**: Phase Boundaries Are Hard Gates
- ✅ >80% coverage required before phase completion
- ✅ All critical paths tested (auth, multi-tenant, marking)

**Principle V**: Multi-Tenant Isolation
- ✅ Test data isolation between students
- ✅ Verify student_id filtering in all queries

**Usage:** 0 times (will use 30+ times)
**Version**: 1.0.0 | **Last Updated**: 2025-12-18