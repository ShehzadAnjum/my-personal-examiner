---
name: sqlmodel-database-schema-design
description: SQLModel database schema design with multi-tenant patterns, relationships, and PostgreSQL best practices. Use when designing database models, migrations, or query patterns.
---


# Skill: SQLModel Database Schema Design

**Type**: Backend Development Expertise
**Created**: 2025-12-18
**Domain**: Database Architecture
**Parent Agent**: 02-Backend-Service

## Overview
Design multi-tenant database schemas using SQLModel (Pydantic + SQLAlchemy) for My Personal Examiner project, ensuring constitutional compliance with multi-tenant isolation.

## Constitutional Requirements
- **Principle IV**: SQLModel MANDATORY (constitutional lock - no raw SQLAlchemy ORM)
- **Principle V**: Multi-tenant isolation - every table must support student_id filtering
- All models must use Pydantic for validation

## Prerequisites
- SQLModel 0.0.22+ installed
- PostgreSQL 16+ database
- Understanding of Pydantic Field validators
- UUID for primary keys

## Standard Pattern

### 1. Basic Table Model
```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    """
    Multi-tenant anchor entity.

    Constitutional Principle V: Student is the primary tenant entity.
    All student-scoped tables must reference this via student_id.
    """
    __tablename__ = "students"

    # Primary Key (always UUID)
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Unique constraints
    email: str = Field(unique=True, nullable=False, index=True, max_length=255)

    # Required fields
    password_hash: str = Field(nullable=False, max_length=255)
    full_name: str = Field(nullable=False, max_length=100)

    # Optional fields
    target_grades: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps (auto-managed)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
```

### 2. Reference Data Table (No Multi-Tenancy)
```python
class Subject(SQLModel, table=True):
    """Reference data - shared across all students"""
    __tablename__ = "subjects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(unique=True, nullable=False, max_length=10)  # e.g., "9708"
    name: str = Field(nullable=False, max_length=255)
    level: str = Field(nullable=False, max_length=10)  # "AS" or "A"
    exam_board: str = Field(nullable=False, max_length=100)
    syllabus_year: str = Field(nullable=False, max_length=20)  # "2023-2025"
```

### 3. Multi-Tenant Table (Student-Scoped)
```python
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Exam(SQLModel, table=True):
    """
    Student-scoped entity.

    Constitutional Principle V: MUST filter by student_id in all queries.
    """
    __tablename__ = "exams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Multi-tenant anchor (MANDATORY for student-scoped tables)
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True  # Critical for query performance
    )

    # Foreign key to reference data
    subject_id: UUID = Field(foreign_key="subjects.id", nullable=False)

    # Table-specific fields
    exam_type: str = Field(nullable=False, max_length=50)
    paper_number: int = Field(nullable=False)
    total_marks: int = Field(nullable=False)
    duration: int = Field(nullable=False)  # minutes
    status: str = Field(default="pending", max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. JSONB Fields for Flexible Data
```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject_id: UUID = Field(foreign_key="subjects.id")

    # JSONB for complex structured data
    marking_scheme: dict = Field(
        sa_column=Column(JSONB),
        nullable=False
    )
    # Example marking_scheme structure:
    # {
    #   "levels": {
    #     "L3": {"marks": "7-8", "descriptor": "Thorough, perceptive..."},
    #     "L2": {"marks": "4-6", "descriptor": "Sound, mostly accurate..."}
    #   },
    #   "mark_allocation": {
    #     "AO1_knowledge": 4,
    #     "AO2_application": 2,
    #     "AO3_evaluation": 2
    #   }
    # }

    topics: list[str] = Field(default=[], sa_column=Column(JSONB))
    syllabus_point_ids: list[UUID] = Field(default=[], sa_column=Column(JSONB))
```

### 5. Array Fields (PostgreSQL-specific)
```python
from sqlalchemy.dialects.postgresql import ARRAY


class AttemptedQuestion(SQLModel, table=True):
    __tablename__ = "attempted_questions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    attempt_id: UUID = Field(foreign_key="attempts.id")
    question_id: UUID = Field(foreign_key="questions.id")

    # Array field for weaknesses
    weaknesses: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String(100)))
    )
    # Example: ["insufficient_evaluation", "lacks_diagram", "weak_conclusion"]
```

## Common Patterns

### Pattern 1: Composite Indexes
```python
from sqlalchemy import Index


class SyllabusPoint(SQLModel, table=True):
    __tablename__ = "syllabus_points"
    __table_args__ = (
        # Composite index for common query pattern
        Index('ix_syllabus_subject_code', 'subject_id', 'code'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject_id: UUID = Field(foreign_key="subjects.id")
    code: str = Field(nullable=False, max_length=50)  # e.g., "9708.1.1"
```

### Pattern 2: Check Constraints
```python
class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Constrain difficulty to 1-5 range
    difficulty: int = Field(
        nullable=False,
        sa_column_kwargs={"check": "difficulty BETWEEN 1 AND 5"}
    )
```

### Pattern 3: Soft Deletes
```python
class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)

    # Soft delete pattern
    deleted_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
```

## Multi-Tenant Isolation Checklist

**For EVERY student-scoped table:**
- [ ] Has `student_id UUID` field
- [ ] `student_id` has foreign key to `students.id`
- [ ] `student_id` has index for performance
- [ ] `student_id` is NOT NULL
- [ ] All queries will include `WHERE student_id = ?`

## Migration Generation

After creating models, generate Alembic migration:
```bash
cd backend
uv run alembic revision --autogenerate -m "create students and subjects tables"
uv run alembic upgrade head
```

## Common Pitfalls

### ❌ Wrong: Using Integer Primary Keys
```python
class Student(SQLModel, table=True):
    id: int = Field(primary_key=True)  # WRONG - use UUID
```

### ✅ Correct: UUID Primary Keys
```python
class Student(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
```

---

### ❌ Wrong: Missing student_id Index
```python
class Exam(SQLModel, table=True):
    student_id: UUID = Field(foreign_key="students.id")  # Missing index
```

### ✅ Correct: Indexed student_id
```python
class Exam(SQLModel, table=True):
    student_id: UUID = Field(
        foreign_key="students.id",
        index=True  # REQUIRED for performance
    )
```

---

### ❌ Wrong: Nullable student_id (Security Violation)
```python
class Exam(SQLModel, table=True):
    student_id: Optional[UUID] = Field(foreign_key="students.id")  # DANGEROUS
```

### ✅ Correct: Non-nullable student_id
```python
class Exam(SQLModel, table=True):
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False  # Constitutional requirement
    )
```

---

### ❌ Wrong: Using SQLAlchemy ORM Directly
```python
from sqlalchemy.orm import DeclarativeBase, Mapped

class Student(DeclarativeBase):  # WRONG - violates constitutional lock
    ...
```

### ✅ Correct: Always Use SQLModel
```python
from sqlmodel import SQLModel

class Student(SQLModel, table=True):  # Constitutional requirement
    ...
```

## Testing Schema

```python
# tests/unit/test_models.py
import pytest
from uuid import UUID
from src.models.student import Student


def test_student_model_creates_with_uuid():
    student = Student(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test Student"
    )
    assert isinstance(student.id, UUID)
    assert student.email == "test@example.com"


def test_student_email_uniqueness(session):
    # Create first student
    student1 = Student(email="test@example.com", ...)
    session.add(student1)
    session.commit()

    # Try to create duplicate
    student2 = Student(email="test@example.com", ...)
    session.add(student2)

    with pytest.raises(IntegrityError):
        session.commit()
```

## Constitutional Compliance

**Principle IV**: SQLModel MANDATORY
- ✅ Always use `SQLModel` base class
- ❌ Never use raw SQLAlchemy `DeclarativeBase`

**Principle V**: Multi-Tenant Isolation
- ✅ Every student-scoped table has `student_id`
- ✅ `student_id` is indexed for performance
- ✅ `student_id` is NOT NULL
- ✅ All queries filter by `student_id`

## Version History

- **1.1.0** (2025-12-24): Restructured to /SKILL.md format with YAML frontmatter, added capabilities list
- **1.0.0** (2025-12-18): Initial skill creation

**Usage Frequency**: Used 3 times in Phase I (students, subjects, syllabus_points), will use 10+ times in Phases II-V (questions, exams, attempts, feedback, etc.)
