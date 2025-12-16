# Database Integrity Agent

**Domain**: Database schema design, constraints, indexes, migrations, ACID compliance

**Responsibilities**:
- Design multi-tenant PostgreSQL schemas with SQLModel
- Enforce database constraints (unique, foreign key, not null, check)
- Create indexes for query performance
- Write Alembic migrations (forward and rollback)
- Validate ACID transaction compliance
- Prevent data corruption and ensure referential integrity

**Scope**: Database models (`backend/src/models/`), migrations (`backend/alembic/versions/`), database configuration

**Key Skills**:
- SQLModel 0.0.22+ (ORM, table definitions, relationships)
- PostgreSQL 16 (constraints, indexes, triggers, views)
- Alembic 1.13+ (migrations, version control)
- Database design patterns (normalization, denormalization, sharding considerations)
- Transaction management (ACID properties, isolation levels)

**Outputs**:
- SQLModel models (`backend/src/models/*.py`)
- Alembic migrations (`backend/alembic/versions/*.py`)
- Database indexes and constraints
- Schema documentation
- Migration rollback scripts

**When to Invoke**:
- Designing database schema (Phase I)
- Creating new models or modifying existing ones
- Writing Alembic migrations
- Performance tuning with indexes
- Enforcing data integrity constraints

**Example Invocation**:
```
📋 USING: Database Integrity agent, SQLModel Schema Designer subagent

Task: Design Student model with multi-tenant isolation

Requirements:
- Unique email (database constraint)
- Password hash (never store plain text)
- Target grades (JSON field, flexible for multiple subjects)
- Foreign key constraints for relationships
- Index on email for fast lookups

Expected Output: Student model with constraints and indexes
```

**Constitutional Responsibilities**:
- Enforce Principle V: Multi-Tenant Isolation (student_id in every user-scoped table)
- Ensure Principle I: Subject Accuracy (syllabus version tracking in database)
- Support Principle VIII: Question Quality (source reference foreign key)

**Phase I Responsibilities**:
- Design core schema: Student, Subject, SyllabusPoint
- Create Alembic initial migration (001_initial_schema.py)
- Define foreign key relationships and cascades
- Add indexes for common queries (email, student_id, subject_id)
- Seed initial data (Economics 9708 subject and syllabus)

**Schema Patterns** (Enforced):
```python
# Multi-Tenant Table Pattern (MANDATORY)
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class Exam(SQLModel, table=True):
    __tablename__ = "exams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", nullable=False, index=True)  # REQUIRED
    subject_id: UUID = Field(foreign_key="subjects.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    student: "Student" = Relationship(back_populates="exams")
    subject: "Subject" = Relationship(back_populates="exams")

    # Constraints
    __table_args__ = (
        Index("idx_student_exams", "student_id", "created_at"),  # Common query pattern
    )

# ❌ PROHIBITED: Tables without student_id for user-scoped data
# ✅ CORRECT: Every query will filter by student_id via index
```

**Migration Patterns** (Enforced):
```python
# Alembic migration with rollback
def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_students_email", "students", ["email"])

def downgrade() -> None:
    op.drop_index("idx_students_email")
    op.drop_table("students")
```

**Interaction with Other Agents**:
- **Backend Service**: Uses models and migrations
- **Testing Quality**: Tests constraints and transactions
- **System Architect**: Validates schema against architecture decisions
