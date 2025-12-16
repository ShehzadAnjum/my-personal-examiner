# Phase 0: Research & Technology Decisions

**Feature**: 001-phase-1-infra (Core Infrastructure & Database)
**Date**: 2025-12-16
**Status**: Complete

## Overview

This document records technology choices, best practices research, and architectural decisions for Phase I infrastructure. All decisions align with constitutional requirements and CLAUDE.md locked technology stack.

---

## Decision 1: ORM Choice - SQLModel

**Decision**: Use SQLModel 0.0.22+ as the ORM

**Rationale**:
1. **Constitutional Lock**: CLAUDE.md mandates SQLModel (not SQLAlchemy, not Prisma)
2. **Pydantic Integration**: Native Pydantic v2 support for request/response validation
3. **Type Safety**: Full Python type hints, catches errors at IDE/mypy stage
4. **FastAPI Compatibility**: Created by same author (Sebastián Ramírez), seamless integration
5. **SQLAlchemy Core**: Built on SQLAlchemy 2.0, inherits mature query engine

**Alternatives Considered**:
- **SQLAlchemy Core**: More verbose, no automatic Pydantic schema generation
- **Tortoise ORM**: Async-first but less mature, no Pydantic integration
- **Prisma (Python)**: Requires Node.js for schema management, adds toolchain complexity

**Best Practices**:
```python
# Multi-tenant pattern (MANDATORY)
from sqlmodel import SQLModel, Field
from uuid import UUID

class Exam(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", index=True)  # CRITICAL
```

**References**:
- Official docs: https://sqlmodel.tiangolo.com/
- Multi-tenant patterns: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/back-populates/

---

## Decision 2: Authentication - JWT with Better Auth Patterns

**Decision**: Implement JWT (JSON Web Tokens) authentication with 24-hour expiration

**Rationale**:
1. **Stateless**: No server-side session storage required, scales horizontally
2. **Industry Standard**: OAuth2 + JWT widely supported by frontend frameworks
3. **Mobile-Friendly**: Works seamlessly with future mobile apps (Phase V+)
4. **Neon Compatibility**: No Redis/session store required (reduces infrastructure)

**Alternatives Considered**:
- **Session-based auth**: Requires Redis/session store, adds infrastructure
- **OAuth2 (Google/GitHub)**: Overkill for MVP, students need simple email/password
- **Magic links**: Poor UX for students taking timed exams

**Implementation Approach**:
- Use `python-jose` for JWT encoding/decoding
- Use `passlib` with bcrypt for password hashing
- Token payload: `{"sub": "<student_id>", "exp": "<expiration>"}`
- Token expiration: 24 hours (configurable via environment)

**Security Measures**:
- Passwords hashed with bcrypt (work factor 12)
- JWT secret stored in environment variable (never committed)
- HTTPS enforced in production (Vercel/Railway default)
- No password in JWT payload (only student_id)

**Best Practices**:
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(student_id: str, expires_delta: timedelta = timedelta(hours=24)):
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({"sub": student_id, "exp": expire}, SECRET_KEY, algorithm="HS256")
```

**References**:
- FastAPI security docs: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- JWT best practices: https://tools.ietf.org/html/rfc7519

---

## Decision 3: Database - PostgreSQL 16 via Neon

**Decision**: Use Neon managed PostgreSQL 16

**Rationale**:
1. **Constitutional Lock**: CLAUDE.md mandates PostgreSQL via Neon
2. **Serverless PostgreSQL**: Auto-scales, pay-per-use pricing for MVP
3. **Branch-per-PR**: Database branching for testing (Phase II+)
4. **Connection Pooling**: Built-in pooling handles FastAPI concurrent connections
5. **Zero Ops**: No manual backups, updates, or scaling

**Alternatives Considered**:
- **Self-hosted PostgreSQL**: Requires DevOps effort, increases complexity
- **Railway PostgreSQL**: Lock-in to Railway, migration harder
- **Supabase**: Includes unnecessary features (Auth, Storage), over-engineered for MVP

**Configuration**:
```python
# backend/src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str  # From .env: postgresql://user:pass@neon.tech/dbname
    database_pool_size: int = 10
    database_max_overflow: int = 20

# backend/src/database.py
from sqlmodel import create_engine, Session

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=False,  # True for debugging SQL
)
```

**Best Practices**:
- Use connection pooling (default 10 connections)
- Enable SSL in production (`?sslmode=require`)
- Store connection string in `.env` (never commit)
- Use Alembic for migrations (never manual ALTER TABLE)

**References**:
- Neon docs: https://neon.tech/docs/introduction
- SQLModel + PostgreSQL: https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/

---

## Decision 4: Migrations - Alembic

**Decision**: Use Alembic 1.13+ for database schema versioning

**Rationale**:
1. **Industry Standard**: De facto Python migration tool, used by SQLAlchemy ecosystem
2. **Rollback Support**: Every migration has `upgrade()` and `downgrade()` functions
3. **Team Collaboration**: Migration files in git, no manual schema sync
4. **SQLModel Compatible**: Works seamlessly with SQLModel table definitions

**Alternatives Considered**:
- **Manual SQL scripts**: Error-prone, no rollback, hard to track
- **SQLModel auto-create**: No version control, unsafe for production
- **Flyway**: Java-based, adds JVM dependency

**Migration Workflow**:
```bash
# Generate migration from model changes
cd backend
uv run alembic revision --autogenerate -m "add students table"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

**Best Practices**:
- Always review auto-generated migrations before applying
- Test rollback locally before production deployment
- Include data migrations when changing columns with data
- Use meaningful migration descriptions

**References**:
- Alembic docs: https://alembic.sqlalchemy.org/en/latest/
- SQLModel + Alembic: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#alembic-migrations

---

## Decision 5: Testing Framework - pytest

**Decision**: Use pytest 8.3+ with pytest-cov for coverage

**Rationale**:
1. **Python Standard**: Most popular testing framework in Python ecosystem
2. **Fixtures**: Reusable test setup (database sessions, test clients)
3. **Async Support**: pytest-asyncio handles FastAPI async routes
4. **Coverage**: pytest-cov integrates coverage.py for >80% target

**Test Structure**:
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests (models, services)
├── integration/         # API endpoint tests (routes + database)
└── e2e/                 # User journey tests (multi-endpoint flows)
```

**Fixture Pattern**:
```python
# tests/conftest.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient

@pytest.fixture(name="db_session")
def db_session_fixture():
    # Create in-memory SQLite for tests (faster than PostgreSQL)
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    # Override get_db dependency with test database
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
```

**Best Practices**:
- Use in-memory SQLite for unit tests (faster)
- Use PostgreSQL (test database) for integration tests
- Mock external services (email, AI APIs)
- Aim for >80% coverage (constitutional requirement)

**References**:
- pytest docs: https://docs.pytest.org/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/

---

## Decision 6: Dependency Management - UV

**Decision**: Use UV 0.5+ as Python package manager

**Rationale**:
1. **Constitutional Lock**: CLAUDE.md mandates UV (not pip, not Poetry)
2. **10-100x Faster**: Rust-based, dramatically faster than pip/Poetry
3. **Lock File**: `uv.lock` ensures reproducible installs
4. **Compatible**: Works with standard `pyproject.toml`, easy migration

**Configuration**:
```toml
# backend/pyproject.toml
[project]
name = "my-personal-examiner-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "alembic>=1.13.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.9",
    "psycopg2-binary>=2.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.7.0",
    "mypy>=1.11.0",
]
```

**Workflow**:
```bash
# Install dependencies
uv sync

# Add new dependency
uv add fastapi

# Run with UV
uv run pytest
uv run uvicorn src.main:app --reload
```

**References**:
- UV docs: https://docs.astral.sh/uv/
- pyproject.toml spec: https://packaging.python.org/en/latest/specifications/pyproject-toml/

---

## Decision 7: Multi-Tenant Security Pattern

**Decision**: Filter all user-scoped queries by `student_id` from JWT

**Rationale**:
1. **Constitutional Requirement**: Principle V mandates sacred multi-tenant isolation
2. **Zero Trust**: Every query explicitly filters, no implicit access
3. **Database-Level**: Foreign keys + indexes enforce isolation at DB layer
4. **JWT-Based**: student_id from token, not request parameter (prevents tampering)

**Implementation**:
```python
# Dependency: Extract student_id from JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Student:
    student_id = verify_token(token)  # Raises 401 if invalid
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Route: Filter by current user's ID
@router.get("/exams")
def get_exams(current_user: Student = Depends(get_current_user), db: Session = Depends(get_db)):
    # MANDATORY: Filter by current_user.id
    exams = db.exec(select(Exam).where(Exam.student_id == current_user.id)).all()
    return exams
```

**Enforcement**:
- Pre-commit hook: grep for unfiltered `.all()` queries
- Unit test: `test_student_cannot_access_other_student_data()`
- Code review: Every route using user-scoped models must filter by student_id

**References**:
- Multi-tenant patterns: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#orm-queryguide-query-filters
- FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/

---

## Summary

All technology choices aligned with constitutional requirements and CLAUDE.md locked stack. No NEEDS CLARIFICATION items remain. Phase 1 design can proceed.

**Key Takeaways**:
1. SQLModel + FastAPI + Alembic + pytest = proven, mature stack
2. JWT authentication = industry standard, stateless, mobile-ready
3. Neon PostgreSQL = zero-ops, serverless, cost-effective for MVP
4. Multi-tenant security enforced at every layer (DB, API, tests)
5. UV package manager = 10-100x faster than pip/Poetry

**Next Phase**: Phase 1 - Design data models, API contracts, quickstart guide
