# Data Model: Resource Bank File Storage

**Feature**: 007-resource-bank-files
**Date**: 2025-12-27
**ORM**: SQLModel 0.0.22+ (PostgreSQL 16)

---

## Overview

The Resource Bank data model consists of **4 primary tables** designed to store, manage, and track multi-source learning resources with multi-tenant isolation, relevance scoring, and usage tracking.

**Design Principles**:
- Multi-tenant isolation via `visibility` (public/private/pending) + `uploaded_by_student_id`
- JSONB metadata fields for flexible type-specific attributes
- Signature-based change detection (SHA-256 hashing)
- Linear state machine: uploaded → pending_review → approved OR rejected
- Composite primary keys for link tables (optimized joins)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Resource                                │
│  (Central entity for all learning materials)                     │
│                                                                   │
│  - id: UUID (PK)                                                  │
│  - resource_type: ENUM (syllabus, textbook, past_paper, etc.)    │
│  - title: TEXT                                                    │
│  - source_url: TEXT (nullable)                                    │
│  - file_path: TEXT                                                │
│  - uploaded_by_student_id: UUID (FK → students, nullable)         │
│  - admin_approved: BOOLEAN (default: false)                       │
│  - visibility: ENUM (public, private, pending_review)             │
│  - metadata: JSONB (flexible type-specific fields)                │
│  - signature: TEXT (SHA-256 hash)                                 │
│  - s3_url: TEXT (nullable)                                        │
│  - s3_sync_status: ENUM (pending, success, failed)                │
│  - last_synced_at: TIMESTAMP (nullable)                           │
│  - search_vector: TSVECTOR (computed from title + extracted_text)│
│  - created_at: TIMESTAMP                                          │
│  - updated_at: TIMESTAMP                                          │
└───────────────────────┬──────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌─────────────────────┐        ┌──────────────────────────────────┐
│ SyllabusPointResource│        │ ExplanationResourceUsage         │
│ (Link resources to   │        │ (Track resource usage)           │
│  syllabus points)    │        │                                  │
│                      │        │  - explanation_id: UUID (PK, FK) │
│  - syllabus_point_id │        │  - resource_id: UUID (PK, FK)    │
│  - resource_id (FK)  │        │  - contribution_weight: FLOAT    │
│  - relevance_score   │        │  - created_at: TIMESTAMP         │
│  - added_by: ENUM    │        └──────────────────────────────────┘
│  - PK: (syllabus, id)│
└─────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ StudentResourcePreference               │
│ (User-specific resource preferences)    │
│                                          │
│  - student_id: UUID (PK, FK)             │
│  - resource_id: UUID (PK, FK)            │
│  - enabled: BOOLEAN (default: true)      │
│  - priority: INT (for ordering)          │
│  - created_at: TIMESTAMP                 │
│  - updated_at: TIMESTAMP                 │
└──────────────────────────────────────────┘
```

---

## Table 1: `resources`

**Purpose**: Central storage for all learning materials (syllabus, past papers, textbooks, user uploads, YouTube links)

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique resource identifier |
| `resource_type` | ENUM | NOT NULL | Type: syllabus, textbook, past_paper, video, article, user_upload |
| `title` | TEXT | NOT NULL | Resource title (e.g., "9708 Syllabus 2024") |
| `source_url` | TEXT | NULLABLE | Original source URL (Cambridge website, YouTube, etc.) |
| `file_path` | TEXT | NOT NULL | Local file path (`backend/resources/...`) |
| `uploaded_by_student_id` | UUID | NULLABLE, FK → students | Student who uploaded (NULL for official resources) |
| `admin_approved` | BOOLEAN | NOT NULL, DEFAULT FALSE | Approval status (user uploads only) |
| `visibility` | ENUM | NOT NULL, DEFAULT 'pending_review' | Access control: public, private, pending_review |
| `metadata` | JSONB | NOT NULL, DEFAULT '{}' | Type-specific fields (page_range, chapter, video_duration, etc.) |
| `signature` | TEXT | NOT NULL, UNIQUE | SHA-256 hash for change detection |
| `s3_url` | TEXT | NULLABLE | S3 object URL (after background upload) |
| `s3_sync_status` | ENUM | NOT NULL, DEFAULT 'pending' | S3 upload status: pending, success, failed, pending_retry |
| `last_synced_at` | TIMESTAMP | NULLABLE | Last successful S3 upload timestamp |
| `extracted_text` | TEXT | NULLABLE | Full text from PDF parsing or OCR |
| `search_vector` | TSVECTOR | GENERATED | Computed: to_tsvector('english', title \|\| ' ' \|\| extracted_text) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Resource creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

### Indexes

```sql
CREATE INDEX idx_resource_type ON resources(resource_type);
CREATE INDEX idx_visibility ON resources(visibility);
CREATE INDEX idx_uploaded_by ON resources(uploaded_by_student_id);
CREATE INDEX idx_signature ON resources(signature);  -- Fast duplicate detection
CREATE INDEX idx_s3_sync_status ON resources(s3_sync_status);  -- Queue queries
CREATE INDEX idx_search_vector ON resources USING GIN(search_vector);  -- Full-text search
```

### State Machine

```
[UPLOAD] → pending_review (visibility='pending_review', admin_approved=false)
    │
    ├─ [APPROVE] → approved (visibility='public', admin_approved=true)
    │                 └─ TERMINAL STATE (no reversal)
    │
    └─ [REJECT] → deleted (file + DB record removed)
                   └─ TERMINAL STATE (no restoration, student can re-upload as new resource)
```

### Sample Metadata JSONB

```json
// For textbooks
{
  "page_range": "245-267",
  "chapter": 12,
  "isbn": "978-0198748908",
  "excerpt_location": "textbooks/9708/excerpts/chapter12.pdf"
}

// For videos
{
  "video_duration": "PT15M32S",  // ISO 8601 duration
  "channel": "EconPlusDal",
  "thumbnail_url": "https://...",
  "transcript_timestamps": [
    {"time": "2:30", "text": "Definition of fiscal policy..."},
    {"time": "5:45", "text": "Examples of fiscal policy..."}
  ]
}

// For past papers
{
  "year": 2023,
  "session": "May/June",
  "paper": 2,
  "mark_scheme_id": "uuid-of-linked-mark-scheme"
}
```

---

## Table 2: `syllabus_point_resources`

**Purpose**: Link resources to specific syllabus points with relevance scoring for auto-selection

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `syllabus_point_id` | UUID | PRIMARY KEY, FK → syllabus_points | Syllabus learning outcome ID (e.g., 9708.5.1) |
| `resource_id` | UUID | PRIMARY KEY, FK → resources | Resource ID |
| `relevance_score` | FLOAT | NOT NULL, CHECK (relevance_score BETWEEN 0 AND 1) | Relevance 0-1 (1.0 = perfect match) |
| `added_by` | ENUM | NOT NULL | Who created link: system, admin, student |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Link creation timestamp |

### Composite Primary Key

```sql
PRIMARY KEY (syllabus_point_id, resource_id)
```

**Rationale**: Prevents duplicate links, optimizes joins on syllabus_point_id (most common query pattern)

### Indexes

```sql
CREATE INDEX idx_relevance_score ON syllabus_point_resources(relevance_score DESC);  -- Auto-selection sorting
CREATE INDEX idx_added_by ON syllabus_point_resources(added_by);  -- Filter by source
```

### Sample Data

```
syllabus_point_id                | resource_id                  | relevance_score | added_by
---------------------------------|------------------------------|-----------------|---------
uuid-9708.5.1                    | uuid-syllabus-9708           | 1.0             | system
uuid-9708.5.1                    | uuid-past-paper-2023-q3      | 0.9             | admin
uuid-9708.5.1                    | uuid-textbook-chapter12      | 0.95            | admin
uuid-9708.5.1                    | uuid-youtube-fiscal-policy   | 0.7             | student
```

---

## Table 3: `explanation_resource_usage`

**Purpose**: Track which resources were used to generate each topic explanation (for analytics and attribution)

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `explanation_id` | UUID | PRIMARY KEY, FK → generated_explanations | Explanation ID (from Feature 006) |
| `resource_id` | UUID | PRIMARY KEY, FK → resources | Resource ID |
| `contribution_weight` | FLOAT | NOT NULL, CHECK (contribution_weight BETWEEN 0 AND 1) | How much this resource influenced explanation |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Usage tracking timestamp |

### Composite Primary Key

```sql
PRIMARY KEY (explanation_id, resource_id)
```

**Rationale**: One explanation can use multiple resources, prevents duplicate tracking

### Indexes

```sql
CREATE INDEX idx_explanation_usage ON explanation_resource_usage(explanation_id);  -- List resources for explanation
CREATE INDEX idx_resource_usage ON explanation_resource_usage(resource_id);  -- Find explanations using resource
```

### Sample Data

```
explanation_id                   | resource_id                  | contribution_weight
---------------------------------|------------------------------|--------------------
uuid-explanation-fiscal-policy   | uuid-syllabus-9708           | 0.5   (50% from syllabus)
uuid-explanation-fiscal-policy   | uuid-past-paper-2023-q3      | 0.3   (30% from past paper)
uuid-explanation-fiscal-policy   | uuid-textbook-chapter12      | 0.2   (20% from textbook)
```

---

## Table 4: `student_resource_preferences`

**Purpose**: User-specific resource preferences for personalized learning (enable/disable resources, set priority)

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `student_id` | UUID | PRIMARY KEY, FK → students | Student ID |
| `resource_id` | UUID | PRIMARY KEY, FK → resources | Resource ID |
| `enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether student wants to use this resource |
| `priority` | INT | NOT NULL, DEFAULT 0 | Ordering preference (higher = more important) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Preference creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

### Composite Primary Key

```sql
PRIMARY KEY (student_id, resource_id)
```

**Rationale**: One student can have multiple preferences, prevents duplicate entries

### Indexes

```sql
CREATE INDEX idx_student_preferences ON student_resource_preferences(student_id);  -- Fast student lookup
CREATE INDEX idx_priority ON student_resource_preferences(priority DESC);  -- Sorting by priority
```

### Sample Data

```
student_id                       | resource_id                  | enabled | priority
---------------------------------|------------------------------|---------|----------
uuid-student-alice               | uuid-textbook-chapter12      | true    | 10   (highest priority)
uuid-student-alice               | uuid-youtube-fiscal-policy   | false   | 0    (disabled)
uuid-student-bob                 | uuid-past-paper-2023-q3      | true    | 5    (medium priority)
```

---

## SQLModel Implementation (Python)

### Resource Model

```python
from sqlmodel import SQLModel, Field, Column, Enum
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy import Computed
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
import uuid

class ResourceType(str, PyEnum):
    SYLLABUS = "syllabus"
    TEXTBOOK = "textbook"
    PAST_PAPER = "past_paper"
    VIDEO = "video"
    ARTICLE = "article"
    USER_UPLOAD = "user_upload"

class Visibility(str, PyEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    PENDING_REVIEW = "pending_review"

class S3SyncStatus(str, PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PENDING_RETRY = "pending_retry"

class Resource(SQLModel, table=True):
    __tablename__ = "resources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    resource_type: ResourceType = Field(sa_column=Column(Enum(ResourceType), nullable=False))
    title: str = Field(max_length=500, nullable=False, index=True)
    source_url: Optional[str] = Field(default=None, max_length=2000)
    file_path: str = Field(nullable=False, max_length=1000)
    uploaded_by_student_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="students.id",
        index=True
    )
    admin_approved: bool = Field(default=False, nullable=False)
    visibility: Visibility = Field(
        default=Visibility.PENDING_REVIEW,
        sa_column=Column(Enum(Visibility), nullable=False, index=True)
    )
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    signature: str = Field(nullable=False, unique=True, max_length=64, index=True)  # SHA-256
    s3_url: Optional[str] = Field(default=None, max_length=2000)
    s3_sync_status: S3SyncStatus = Field(
        default=S3SyncStatus.PENDING,
        sa_column=Column(Enum(S3SyncStatus), nullable=False, index=True)
    )
    last_synced_at: Optional[datetime] = Field(default=None)
    extracted_text: Optional[str] = Field(default=None)  # From PDF/OCR
    search_vector: Optional[str] = Field(
        sa_column=Column(
            'search_vector',
            TSVECTOR,
            Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, ''))")
        )
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### SyllabusPointResource Model

```python
class AddedBy(str, PyEnum):
    SYSTEM = "system"
    ADMIN = "admin"
    STUDENT = "student"

class SyllabusPointResource(SQLModel, table=True):
    __tablename__ = "syllabus_point_resources"

    syllabus_point_id: uuid.UUID = Field(
        foreign_key="syllabus_points.id",
        primary_key=True
    )
    resource_id: uuid.UUID = Field(
        foreign_key="resources.id",
        primary_key=True
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        nullable=False,
        index=True
    )
    added_by: AddedBy = Field(sa_column=Column(Enum(AddedBy), nullable=False, index=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### ExplanationResourceUsage Model

```python
class ExplanationResourceUsage(SQLModel, table=True):
    __tablename__ = "explanation_resource_usage"

    explanation_id: uuid.UUID = Field(
        foreign_key="generated_explanations.id",
        primary_key=True
    )
    resource_id: uuid.UUID = Field(
        foreign_key="resources.id",
        primary_key=True
    )
    contribution_weight: float = Field(
        ge=0.0,
        le=1.0,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### StudentResourcePreference Model

```python
class StudentResourcePreference(SQLModel, table=True):
    __tablename__ = "student_resource_preferences"

    student_id: uuid.UUID = Field(
        foreign_key="students.id",
        primary_key=True,
        index=True
    )
    resource_id: uuid.UUID = Field(
        foreign_key="resources.id",
        primary_key=True
    )
    enabled: bool = Field(default=True, nullable=False)
    priority: int = Field(default=0, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

## Alembic Migrations

### Migration 010: Create Tables

```python
"""Add resource bank tables

Revision ID: 010_add_resource_tables
Revises: 009_...
Create Date: 2025-12-27
"""

def upgrade():
    # Create ENUM types
    op.execute("""
        CREATE TYPE resourcetype AS ENUM ('syllabus', 'textbook', 'past_paper', 'video', 'article', 'user_upload');
        CREATE TYPE visibility AS ENUM ('public', 'private', 'pending_review');
        CREATE TYPE s3syncstatus AS ENUM ('pending', 'success', 'failed', 'pending_retry');
        CREATE TYPE addedby AS ENUM ('system', 'admin', 'student');
    """)

    # Create resources table
    op.create_table(
        'resources',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('resource_type', sa.Enum('syllabus', 'textbook', 'past_paper', 'video', 'article', 'user_upload', name='resourcetype'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source_url', sa.String(2000), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('uploaded_by_student_id', postgresql.UUID(), nullable=True),
        sa.Column('admin_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('visibility', sa.Enum('public', 'private', 'pending_review', name='visibility'), nullable=False, server_default='pending_review'),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('signature', sa.String(64), nullable=False),
        sa.Column('s3_url', sa.String(2000), nullable=True),
        sa.Column('s3_sync_status', sa.Enum('pending', 'success', 'failed', 'pending_retry', name='s3syncstatus'), nullable=False, server_default='pending'),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('search_vector', TSVECTOR, Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, ''))")),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by_student_id'], ['students.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('signature')
    )

    # Create other tables (syllabus_point_resources, explanation_resource_usage, student_resource_preferences)
    # ... (similar patterns)

def downgrade():
    op.drop_table('student_resource_preferences')
    op.drop_table('explanation_resource_usage')
    op.drop_table('syllabus_point_resources')
    op.drop_table('resources')
    op.execute("DROP TYPE IF EXISTS addedby, s3syncstatus, visibility, resourcetype")
```

### Migration 011: Add Performance Indexes

```python
"""Add resource indexes for performance

Revision ID: 011_add_resource_indexes
Revises: 010_add_resource_tables
Create Date: 2025-12-27
"""

def upgrade():
    # Resources table indexes
    op.create_index('idx_resource_type', 'resources', ['resource_type'])
    op.create_index('idx_visibility', 'resources', ['visibility'])
    op.create_index('idx_uploaded_by', 'resources', ['uploaded_by_student_id'])
    op.create_index('idx_signature', 'resources', ['signature'])
    op.create_index('idx_s3_sync_status', 'resources', ['s3_sync_status'])
    op.execute("CREATE INDEX idx_search_vector ON resources USING GIN(search_vector)")

    # SyllabusPointResource indexes
    op.create_index('idx_relevance_score', 'syllabus_point_resources', [sa.text('relevance_score DESC')])
    op.create_index('idx_added_by', 'syllabus_point_resources', ['added_by'])

    # ExplanationResourceUsage indexes
    op.create_index('idx_explanation_usage', 'explanation_resource_usage', ['explanation_id'])
    op.create_index('idx_resource_usage', 'explanation_resource_usage', ['resource_id'])

    # StudentResourcePreference indexes
    op.create_index('idx_student_preferences', 'student_resource_preferences', ['student_id'])
    op.create_index('idx_priority', 'student_resource_preferences', [sa.text('priority DESC')])

def downgrade():
    # Drop all indexes in reverse order
    # ...
```

---

## Multi-Tenant Isolation Queries

### Example 1: List Public + Private Resources for Student

```python
def get_resources_for_student(student_id: uuid.UUID, session: Session):
    return session.exec(
        select(Resource)
        .where(
            or_(
                Resource.visibility == Visibility.PUBLIC,
                and_(
                    Resource.visibility == Visibility.PRIVATE,
                    Resource.uploaded_by_student_id == student_id
                )
            )
        )
        .order_by(Resource.created_at.desc())
    ).all()
```

### Example 2: Admin Pending Review Query

```python
def get_pending_resources(session: Session):
    return session.exec(
        select(Resource)
        .where(Resource.visibility == Visibility.PENDING_REVIEW)
        .order_by(Resource.created_at.desc())
    ).all()
```

### Example 3: Auto-Select Resources by Relevance

```python
def get_resources_for_syllabus_point(syllabus_point_id: uuid.UUID, limit: int = 5):
    return session.exec(
        select(Resource)
        .join(SyllabusPointResource)
        .where(SyllabusPointResource.syllabus_point_id == syllabus_point_id)
        .order_by(SyllabusPointResource.relevance_score.desc())
        .limit(limit)
    ).all()
```

---

## Summary

**Tables**: 4 (resources, syllabus_point_resources, explanation_resource_usage, student_resource_preferences)
**Indexes**: 14 (optimized for common queries)
**State Machine**: Linear approval workflow (pending_review → approved/rejected)
**Multi-Tenant**: Visibility + uploaded_by_student_id filtering
**Performance**: GIN index for full-text search, composite PKs for joins

✅ **Data model complete** - Ready for API contract generation.

---

**Next**: Generate OpenAPI contracts in `contracts/` directory.
