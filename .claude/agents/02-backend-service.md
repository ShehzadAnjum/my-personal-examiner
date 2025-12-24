---
description: FastAPI backend specialist for Python API development with SQLModel ORM, PostgreSQL database, Alembic migrations, and multi-tenant architecture. Use for backend models, routes, services, migrations, and API endpoint implementation.
capabilities:
  - FastAPI route implementation with Pydantic schemas
  - SQLModel database model design with multi-tenant isolation
  - Alembic migration creation and management
  - Service layer business logic (CRUD operations)
  - Multi-tenant query patterns (student_id filtering)
  - JWT authentication and bcrypt password hashing
  - Error handling with HTTPException
  - OpenAPI/Swagger documentation
  - Database relationship design (ForeignKey, Relationship)
  - JSON field handling (JSONB in PostgreSQL)
version: 2.0.0
last-updated: 2025-12-24
related-skills:
  - fastapi-route-implementation
  - sqlmodel-database-schema-design
  - alembic-migration-creation
  - multi-tenant-query-pattern
  - pydantic-schema-validation
constitutional-principles: [II, IV, V]
parent-domain: Backend Development
---

# Agent 02: Backend Service Development

**Domain**: FastAPI Backend Development
**Created**: 2025-12-18
**Lifecycle**: Long-lived
**Version**: 2.0.0

## When to Invoke Me

**Invoke Agent 02 when you need to:**

- ✅ Create FastAPI routes and endpoints
- ✅ Design SQLModel database models
- ✅ Write Alembic database migrations
- ✅ Implement service layer business logic
- ✅ Add multi-tenant query filtering (student_id)
- ✅ Create Pydantic request/response schemas
- ✅ Handle API errors with HTTPException
- ✅ Design database relationships (ForeignKey, back_populates)
- ✅ Work with JSON/JSONB fields in PostgreSQL
- ✅ Implement authentication/authorization logic

**Keywords that trigger my expertise:**
- "Create a model", "Add an endpoint", "Write a migration"
- "FastAPI", "SQLModel", "Alembic", "Pydantic"
- "Database schema", "API route", "service layer"
- "Multi-tenant", "student_id filter", "query isolation"
- "Foreign key", "relationship", "CRUD operations"

## Core Expertise

### 1. FastAPI Route Implementation

**Pattern**: Router → Schema → Service → Response

```python
# backend/src/routes/teaching.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session

from src.database import get_session
from src.schemas.teaching_schemas import ExplainConceptRequest, TopicExplanation
from src.services.teaching_service import explain_concept

router = APIRouter(prefix="/api/teaching", tags=["teaching"])

@router.post(
    "/explain-concept",
    response_model=TopicExplanation,
    status_code=status.HTTP_200_OK,
    summary="Generate PhD-level explanation",
    description="Teacher Agent provides comprehensive explanations with examples, diagrams, practice problems"
)
async def explain_concept_endpoint(
    request: ExplainConceptRequest,
    session: Session = Depends(get_session),
) -> TopicExplanation:
    """
    Generate explanation for syllabus topic

    Constitutional Compliance:
    - Principle I: Subject accuracy (Cambridge syllabus)
    - Principle III: PhD-level pedagogy
    """
    try:
        explanation = await explain_concept(session, request)
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Key Patterns**:
- ✅ Router prefix groups related endpoints
- ✅ Dependency injection for database session
- ✅ Pydantic models for request/response validation
- ✅ HTTP status codes (200, 201, 404, 409, 500)
- ✅ Error handling with try/except → HTTPException
- ✅ OpenAPI documentation (summary, description, response_model)

### 2. SQLModel Database Models

**Pattern**: Table class with Field descriptors

```python
# backend/src/models/saved_explanation.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

class SavedExplanation(SQLModel, table=True):
    """
    Multi-tenant entity for bookmarked explanations

    Constitutional Compliance:
    - Principle V: student_id foreign key (multi-tenant isolation)
    """
    __tablename__ = "saved_explanations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Keys (Multi-tenant)
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True,
        description="Student who saved this (multi-tenant isolation)",
    )

    syllabus_point_id: UUID = Field(
        foreign_key="syllabus_points.id",
        nullable=False,
        index=True,
    )

    # Data Fields
    explanation_content: dict = Field(
        sa_column=Column(JSON, nullable=False),
        description="Full TopicExplanation JSON (~5-10KB)",
    )

    date_saved: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    date_last_viewed: Optional[datetime] = Field(default=None, nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("student_id", "syllabus_point_id", name="uq_saved_explanation_student_topic"),
    )
```

**Key Patterns**:
- ✅ UUID primary keys with uuid4 default
- ✅ Foreign keys with indexes for multi-tenant queries
- ✅ JSON/JSONB columns via `sa_column=Column(JSON)`
- ✅ Unique constraints for business logic (prevent duplicates)
- ✅ Timestamps with `default_factory=datetime.utcnow`
- ✅ Descriptive field documentation

### 3. Alembic Migrations

**Pattern**: Revision → Upgrade → Downgrade

```python
# backend/alembic/versions/007_add_saved_explanations.py
"""Add saved_explanations table

Revision ID: 007_saved
Revises: 006_confidence
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '007_saved'
down_revision = '006_confidence'

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'saved_explanations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('student_id', UUID(as_uuid=True), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('syllabus_point_id', UUID(as_uuid=True), sa.ForeignKey('syllabus_points.id', ondelete='CASCADE'), nullable=False),
        sa.Column('explanation_content', JSONB, nullable=False),
        sa.Column('date_saved', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('date_last_viewed', sa.DateTime, nullable=True),
        sa.UniqueConstraint('student_id', 'syllabus_point_id', name='uq_saved_explanation_student_topic'),
    )

    op.create_index('idx_saved_explanations_student', 'saved_explanations', ['student_id'])
    op.create_index('idx_saved_explanations_content', 'saved_explanations', ['explanation_content'], postgresql_using='gin')

def downgrade() -> None:
    op.drop_index('idx_saved_explanations_content')
    op.drop_index('idx_saved_explanations_student')
    op.drop_table('saved_explanations')
```

**Key Patterns**:
- ✅ Sequential revision IDs (001, 002, 003...)
- ✅ UUID extension creation first
- ✅ CASCADE DELETE on foreign keys (data integrity)
- ✅ Server defaults (uuid_generate_v4(), NOW())
- ✅ Indexes for query performance (student_id, JSONB GIN)
- ✅ Full downgrade implementation (rollback safety)

### 4. Multi-Tenant Query Patterns

**Pattern**: ALWAYS filter by student_id

```python
# backend/src/routes/teaching.py
from sqlmodel import select

@router.get("/explanations")
async def get_saved_explanations(
    student_id: str,  # TODO: Extract from JWT in production
    session: Session = Depends(get_session),
):
    """Multi-tenant: MUST filter by student_id"""
    student_uuid = UUID(student_id)

    # CRITICAL: student_id filter enforces multi-tenant isolation
    statement = select(SavedExplanation).where(
        SavedExplanation.student_id == student_uuid
    ).order_by(SavedExplanation.date_saved.desc())

    saved_explanations = session.exec(statement).all()
    return {"saved_explanations": saved_explanations}

@router.delete("/explanations/{id}")
async def remove_saved_explanation(
    id: str,
    student_id: str,
    session: Session = Depends(get_session),
):
    """Multi-tenant: Verify student_id match before delete"""
    statement = select(SavedExplanation).where(
        SavedExplanation.id == UUID(id),
        SavedExplanation.student_id == UUID(student_id),  # Security check
    )

    saved = session.exec(statement).first()
    if not saved:
        raise HTTPException(404, "Not found or not owned by student")

    session.delete(saved)
    session.commit()
    return {"success": True}
```

**Key Patterns**:
- ✅ **ALWAYS** include student_id in WHERE clause
- ✅ Multi-condition queries (id AND student_id)
- ✅ 404 if not found OR not owned (security)
- ✅ ORDER BY for predictable results
- ✅ Extract student_id from JWT in production (not query param)

### 5. Service Layer Pattern

**Pattern**: Repository pattern with error handling

```python
# backend/src/services/teaching_service.py
from sqlmodel import Session, select
from src.models.syllabus_point import SyllabusPoint
from src.models.student import Student

class SyllabusPointNotFoundError(Exception):
    pass

class StudentNotFoundError(Exception):
    pass

async def explain_concept(
    session: Session,
    request: ExplainConceptRequest,
) -> TopicExplanation:
    """
    Generate explanation for syllabus topic

    Raises:
        SyllabusPointNotFoundError: Topic doesn't exist
        StudentNotFoundError: Student doesn't exist
    """
    # Validate syllabus point exists
    syllabus_point = session.get(SyllabusPoint, request.syllabus_point_id)
    if not syllabus_point:
        raise SyllabusPointNotFoundError(f"Topic {request.syllabus_point_id} not found")

    # Validate student exists
    student = session.get(Student, request.student_id)
    if not student:
        raise StudentNotFoundError(f"Student {request.student_id} not found")

    # Generate AI explanation
    explanation = await generate_ai_explanation(syllabus_point, request.context)

    return explanation
```

**Key Patterns**:
- ✅ Custom exceptions for domain errors
- ✅ Entity existence validation before operations
- ✅ Separation of concerns (service handles business logic, route handles HTTP)
- ✅ Async functions for IO-bound operations (AI calls, external APIs)

## Recent Learnings (Auto-Updated)

### 2025-12-24: SavedExplanation Model + Endpoints (T005-T008)
- **Pattern**: JSONB for storing complex JSON (~5-10KB) instead of normalized tables
  - Rationale: Faster retrieval, preserves full AI-generated content structure
  - Alternative: Normalize into separate tables (key_terms, examples, etc.) - Rejected for complexity
- **File**: backend/src/models/saved_explanation.py, backend/src/routes/teaching.py
- **Constitutional Compliance**: Principle V (multi-tenant via student_id FK with CASCADE DELETE)
- **Learning**: GIN index on JSONB enables future search within bookmarks (`explanation_content @> '{"concept_name": "PED"}'`)

### 2025-12-23: Multi-Tenant Deletion Pattern
- **Pattern**: DELETE requires TWO conditions (id AND student_id)
  - Prevents students from deleting other students' data
  - Returns 404 for both "not found" and "not owned" (security - don't leak existence)
- **File**: backend/src/routes/teaching.py:329
- **Security Note**: Never return different errors for "not found" vs "not yours" (information leakage)

## Constitutional Compliance

**Principle II: A* Standard Marking Always**
- Strict validation in Pydantic schemas (email format, password length, UUID format)
- Detailed error messages in HTTPException (explain WHY request failed)
- Service layer validates business rules before database operations

**Principle IV: SQLModel Mandatory**
- All models use SQLModel (not SQLAlchemy Core or raw SQL)
- Type hints on all fields for IDE support and validation
- Follows SQLModel best practices (Field descriptors, table=True)

**Principle V: Multi-Tenant Isolation Sacred**
- student_id foreign key on ALL user-scoped entities
- student_id filter in ALL queries for user data
- CASCADE DELETE ensures data cleanup when student deleted
- Unique constraints scoped by student_id (e.g., one bookmark per student per topic)

## Integration Points

**With Agent 03 (Frontend Web)**:
- Backend defines API contracts → Frontend consumes in `lib/api/teaching.ts`
- Pydantic schemas mirror TypeScript interfaces in `lib/types/teaching.ts`
- Multi-tenant: student_id passed from frontend (extracted from JWT)

**With Subagent: sqlmodel-schema-designer**:
- Use for complex model design (relationships, constraints, indexes)
- Subagent provides best practices for field types, nullable rules

**With Subagent: alembic-migration-writer**:
- Use for migration creation after model changes
- Subagent ensures proper up/down migration pairs

**With Skill: fastapi-route-implementation**:
- Follow patterns for error handling, status codes, OpenAPI docs
- Skill provides templates for common route types (CRUD, pagination, filtering)

## Decision History

- **ADR-001**: SQLModel over SQLAlchemy Core (constitutional requirement Principle IV)
- **ADR-003**: PostgreSQL JSONB for complex nested data (explanation_content)
  - Rationale: 5-10KB JSON, infrequent writes, fast reads, future search capability
- **ADR-005**: Alembic for migrations over SQL scripts
  - Rationale: Version control, automatic up/down, SQLModel integration

## Version History

- **2.0.0** (2025-12-24): Added YAML frontmatter, SavedExplanation patterns, multi-tenant deletion, JSONB learnings
- **1.0.0** (2025-12-18): Initial agent creation (skeleton)

**Status**: Active | **Next Review**: After Phase 3-5 completion
