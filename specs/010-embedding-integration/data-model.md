# Data Model: Embedding Integration

**Feature**: 010-embedding-integration
**Date**: 2026-01-21
**Spec**: [spec.md](./spec.md)

---

## Entity Extensions

### SyllabusPoint (Extended)

Extends existing `SyllabusPoint` model with embedding storage.

```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

class SyllabusPoint(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Embedding fields
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(768), nullable=True),
        description="768-dimension vector embedding for semantic search"
    )
    embedding_model: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Model used to generate embedding (e.g., 'gemini/text-embedding-004')"
    )
    embedded_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when embedding was generated"
    )
```

**Field Descriptions**:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| embedding | VECTOR(768) | Yes | 768-dimension embedding vector |
| embedding_model | VARCHAR(50) | Yes | Model identifier (e.g., "gemini/text-embedding-004") |
| embedded_at | TIMESTAMP | Yes | When embedding was generated |

**Embedding Text Composition**:
```python
def get_embedding_text(self) -> str:
    """Combine fields for embedding generation"""
    parts = [self.code, self.title]
    if self.description:
        parts.append(self.description)
    if self.learning_outcomes:
        parts.extend(self.learning_outcomes)
    return " | ".join(parts)
```

---

### Resource (Extended)

Extends existing `Resource` model for textbook/content alignment.

```python
class Resource(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Embedding fields
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(768), nullable=True),
        description="768-dimension vector embedding for content alignment"
    )
    embedding_model: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Model used to generate embedding"
    )
    embedded_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when embedding was generated"
    )
```

---

### EmbeddingJob (New)

Tracks bulk embedding generation jobs.

```python
from enum import Enum
from uuid import UUID, uuid4

class EmbeddingJobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some embeddings failed

class EmbeddingJob(SQLModel, table=True):
    __tablename__ = "embedding_job"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject_id: UUID = Field(foreign_key="subject.id", index=True)

    # Job metadata
    status: EmbeddingJobStatus = Field(default=EmbeddingJobStatus.PENDING)
    job_type: str = Field(max_length=50)  # "syllabus", "resource", "bulk_regenerate"

    # Progress tracking
    total_items: int = Field(default=0)
    completed_items: int = Field(default=0)
    failed_items: int = Field(default=0)

    # Timing
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Error tracking
    error_message: Optional[str] = Field(default=None)
    failed_item_ids: Optional[List[UUID]] = Field(default=None, sa_column=Column(ARRAY(UUID)))

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = Field(default=None, foreign_key="student.id")
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| subject_id | UUID | Subject being embedded (FK) |
| status | ENUM | Job status (pending/in_progress/completed/failed/partial) |
| job_type | VARCHAR(50) | Type of embedding job |
| total_items | INT | Total items to embed |
| completed_items | INT | Successfully embedded count |
| failed_items | INT | Failed embedding count |
| started_at | TIMESTAMP | Job start time |
| completed_at | TIMESTAMP | Job completion time |
| error_message | TEXT | Error details if failed |
| failed_item_ids | UUID[] | List of failed item IDs for retry |
| created_at | TIMESTAMP | Job creation time |
| created_by | UUID | User who triggered job (FK) |

---

## Database Migration

### Migration: 020_add_embedding_columns.py

```python
"""Add embedding columns to syllabus_point and resource tables

Revision ID: 020_add_embedding_columns
Revises: 019_fix_explanation_fk
Create Date: 2026-01-21
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = '020_add_embedding_columns'
down_revision = '019_fix_explanation_fk'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Add embedding columns to syllabus_point
    op.add_column('syllabus_point',
        sa.Column('embedding', Vector(768), nullable=True))
    op.add_column('syllabus_point',
        sa.Column('embedding_model', sa.String(50), nullable=True))
    op.add_column('syllabus_point',
        sa.Column('embedded_at', sa.DateTime(), nullable=True))

    # Add embedding columns to resource
    op.add_column('resource',
        sa.Column('embedding', Vector(768), nullable=True))
    op.add_column('resource',
        sa.Column('embedding_model', sa.String(50), nullable=True))
    op.add_column('resource',
        sa.Column('embedded_at', sa.DateTime(), nullable=True))

    # Create embedding_job table
    op.create_table('embedding_job',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('subject_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_items', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_items', sa.Integer(), nullable=False, default=0),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('failed_item_ids', sa.ARRAY(sa.UUID()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['student.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embedding_job_subject_id', 'embedding_job', ['subject_id'])
    op.create_index('ix_embedding_job_status', 'embedding_job', ['status'])

def downgrade() -> None:
    # Drop embedding_job table
    op.drop_index('ix_embedding_job_status', 'embedding_job')
    op.drop_index('ix_embedding_job_subject_id', 'embedding_job')
    op.drop_table('embedding_job')

    # Remove embedding columns from resource
    op.drop_column('resource', 'embedded_at')
    op.drop_column('resource', 'embedding_model')
    op.drop_column('resource', 'embedding')

    # Remove embedding columns from syllabus_point
    op.drop_column('syllabus_point', 'embedded_at')
    op.drop_column('syllabus_point', 'embedding_model')
    op.drop_column('syllabus_point', 'embedding')

    # Note: Not dropping pgvector extension as it may be used elsewhere
```

---

## Relationships

```
┌─────────────────┐       ┌─────────────────┐
│     Subject     │       │     Student     │
│                 │       │                 │
│  id (PK)        │       │  id (PK)        │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ 1:N                     │ 1:N
         ▼                         │
┌─────────────────┐                │
│  SyllabusPoint  │                │
│                 │                │
│  id (PK)        │                │
│  subject_id (FK)│                │
│  embedding      │◄───────────────┘
│  embedding_model│     (created_by)
│  embedded_at    │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   EmbeddingJob  │
│                 │
│  id (PK)        │
│  subject_id (FK)│
│  status         │
│  total_items    │
│  completed_items│
└─────────────────┘
```

---

## Indexes

| Table | Index | Columns | Type | Purpose |
|-------|-------|---------|------|---------|
| syllabus_point | (future) | embedding | HNSW | Fast similarity search |
| embedding_job | ix_embedding_job_subject_id | subject_id | B-tree | Filter by subject |
| embedding_job | ix_embedding_job_status | status | B-tree | Find pending jobs |

**Note**: Vector index on `syllabus_point.embedding` deferred until performance testing shows need (>500ms queries).

---

## Constraints

1. **Embedding dimensions**: Must be exactly 768 floats
2. **Embedding model format**: `provider/model-name` (e.g., "gemini/text-embedding-004")
3. **Subject scope**: Embeddings are scoped to subject via `subject_id`
4. **Nullable embeddings**: Topics can exist without embeddings (pre-generation or failed)
