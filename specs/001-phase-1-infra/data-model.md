# Phase 1: Data Model

**Feature**: 001-phase-1-infra (Core Infrastructure & Database)
**Date**: 2025-12-16
**Status**: Complete

## Overview

This document defines the database schema for Phase I, focusing on student authentication and subject management. All models follow multi-tenant isolation principles (Principle V).

---

## Entity 1: Student

**Purpose**: Represents a student user of the system (multi-tenant anchor entity)

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique student identifier |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Student email (login credential) |
| password_hash | String(255) | NOT NULL | bcrypt-hashed password (never plain text) |
| full_name | String(100) | NOT NULL | Student's full name |
| target_grades | JSON | NULLABLE | Target grades by subject, e.g., {"9708": "A*"} |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Account creation timestamp |
| updated_at | DateTime | NULLABLE | Last profile update timestamp |

**Relationships**:
- **Has Many**: Exams (future Phase II)
- **Has Many**: Attempts (future Phase III)
- **Has Many**: StudentProgress (future Phase III)

**Indexes**:
- `idx_students_email` (email) - Fast login lookups
- `idx_students_created_at` (created_at) - Chronological queries

**Validation Rules** (from spec FR-001 to FR-004):
- Email must match standard email format (RFC 5322)
- Password minimum 8 characters
- Password stored as bcrypt hash (work factor 12)
- Email must be unique (409 Conflict on duplicate registration)

**Multi-Tenant Role**: Student is the **anchor entity** for all user-scoped data. All queries for user-scoped tables must filter by student_id.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False, index=True, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    full_name: str = Field(nullable=False, max_length=100)
    target_grades: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)
```

---

## Entity 2: Subject

**Purpose**: Represents an A-Level subject available for study (system-managed, not user-created)

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique subject identifier |
| code | String(10) | NOT NULL, INDEX | Cambridge subject code (e.g., "9708") |
| name | String(100) | NOT NULL | Subject name (e.g., "Economics") |
| level | String(10) | NOT NULL | "AS" or "A" (A-Level) |
| exam_board | String(50) | NOT NULL, DEFAULT "Cambridge International" | Exam board name |
| syllabus_year | String(20) | NOT NULL | Syllabus version (e.g., "2023-2025") |

**Relationships**:
- **Has Many**: SyllabusPoints (learning objectives)
- **Has Many**: Questions (future Phase II)
- **Has Many**: Exams (future Phase II)

**Indexes**:
- `idx_subjects_code` (code) - Fast subject lookups
- `uq_subjects_code_year` (code, syllabus_year) - Unique constraint for versioning

**Validation Rules** (from spec FR-014 to FR-016):
- Code must match Cambridge format (4 digits)
- Level must be "AS" or "A"
- Economics 9708 seeded as initial subject

**Multi-Tenant Role**: Subject is **global** (not scoped to students). All students see same subjects.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, index=True, max_length=10)
    name: str = Field(nullable=False, max_length=100)
    level: str = Field(nullable=False, max_length=10)  # "AS" or "A"
    exam_board: str = Field(default="Cambridge International", nullable=False, max_length=50)
    syllabus_year: str = Field(nullable=False, max_length=20)  # "2023-2025"
```

---

## Entity 3: SyllabusPoint

**Purpose**: Represents a specific learning objective or topic within a subject syllabus

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique syllabus point identifier |
| subject_id | UUID | FK(subjects.id), NOT NULL, INDEX | Parent subject |
| code | String(20) | NOT NULL, INDEX | Syllabus code (e.g., "9708.1.1") |
| description | Text | NOT NULL | Learning objective description |
| topics | Text | NULLABLE | Comma-separated topics covered |
| learning_outcomes | Text | NULLABLE | Expected learning outcomes |

**Relationships**:
- **Belongs To**: Subject (parent subject)
- **Many-to-Many**: Questions (future Phase II) - via question.syllabus_point_ids JSON array

**Indexes**:
- `idx_syllabus_points_subject_id` (subject_id) - Fast subject-scoped queries
- `idx_syllabus_points_code` (code) - Fast code lookups

**Validation Rules** (from spec FR-017):
- Code must match pattern: `{subject_code}.{section}.{subsection}`
- subject_id must reference existing Subject

**Multi-Tenant Role**: SyllabusPoint is **global** (not scoped to students). All students see same syllabus.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional

class SyllabusPoint(SQLModel, table=True):
    __tablename__ = "syllabus_points"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject_id: UUID = Field(foreign_key="subjects.id", nullable=False, index=True)
    code: str = Field(nullable=False, index=True, max_length=20)
    description: str = Field(nullable=False, sa_column=Column(Text))
    topics: Optional[str] = Field(default=None, sa_column=Column(Text))
    learning_outcomes: Optional[str] = Field(default=None, sa_column=Column(Text))
```

---

## Entity Relationship Diagram

```
┌─────────────────┐
│    Student      │ (Multi-tenant anchor)
│─────────────────│
│ id (PK)         │
│ email (UNIQUE)  │
│ password_hash   │
│ full_name       │
│ target_grades   │
│ created_at      │
└─────────────────┘
        │
        │ (No relationships in Phase I)
        │ (Phase II will add: Has Many → Exams)
        ↓

┌─────────────────┐
│    Subject      │ (Global, not multi-tenant)
│─────────────────│
│ id (PK)         │
│ code            │
│ name            │
│ level           │
│ exam_board      │
│ syllabus_year   │
└─────────────────┘
        │
        │ Has Many
        ↓
┌─────────────────┐
│ SyllabusPoint   │ (Global, not multi-tenant)
│─────────────────│
│ id (PK)         │
│ subject_id (FK) │
│ code            │
│ description     │
│ topics          │
│ learning_outcomes│
└─────────────────┘
```

---

## Database Schema SQL (for reference)

```sql
-- Students table (multi-tenant anchor)
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    target_grades JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_created_at ON students(created_at);

-- Subjects table (global)
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    level VARCHAR(10) NOT NULL,
    exam_board VARCHAR(50) NOT NULL DEFAULT 'Cambridge International',
    syllabus_year VARCHAR(20) NOT NULL,
    CONSTRAINT uq_subjects_code_year UNIQUE (code, syllabus_year)
);

CREATE INDEX idx_subjects_code ON subjects(code);

-- Seed Economics 9708
INSERT INTO subjects (code, name, level, exam_board, syllabus_year)
VALUES ('9708', 'Economics', 'A', 'Cambridge International', '2023-2025');

-- Syllabus points table (global)
CREATE TABLE syllabus_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    topics TEXT,
    learning_outcomes TEXT
);

CREATE INDEX idx_syllabus_points_subject_id ON syllabus_points(subject_id);
CREATE INDEX idx_syllabus_points_code ON syllabus_points(code);
```

---

## State Transitions

**Student Account States**:
1. **Created** → Student registers via `POST /api/auth/register`
2. **Authenticated** → Student logs in via `POST /api/auth/login`, receives JWT
3. **Updated** → Student updates profile via `PATCH /api/students/me`

No soft deletes in Phase I (account deletion deferred to Phase V).

---

## Validation Summary

**Constitutional Compliance**:
- ✅ **Principle V (Multi-Tenant Isolation)**: Student table is anchor, all future user-scoped tables will have student_id FK
- ✅ **Principle I (Subject Accuracy)**: Subject.syllabus_year tracks Cambridge versions
- ✅ **Principle III (Syllabus Sync)**: SyllabusPoint.code allows mapping questions to curriculum

**Spec Requirements Met**:
- ✅ FR-001 to FR-013: Student data management
- ✅ FR-014 to FR-017: Subject management
- ✅ FR-018 to FR-021: Data persistence & integrity
- ✅ All success criteria (SC-001 to SC-015) supported by schema

---

## Next Phase

Phase 1 design complete. Ready for:
1. **API Contracts**: Define OpenAPI schema for endpoints
2. **Quickstart**: Setup instructions for development environment
