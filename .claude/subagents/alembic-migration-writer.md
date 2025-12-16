# Alembic Migration Writer Subagent

**Parent Agent**: Database Integrity

**Task**: Generate database migrations from SQLModel changes with forward and rollback

**Inputs**:
- Database schema changes (new tables, columns, constraints)
- Migration description
- Dependencies on previous migrations

**Outputs**:
- Alembic migration file (`backend/alembic/versions/###_description.py`)
- Forward migration (`upgrade()` function)
- Rollback migration (`downgrade()` function)

**Pattern**:
```python
"""Add students and subjects tables

Revision ID: 001_initial_schema
Revises: None
Create Date: 2025-12-16 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create students and subjects tables."""

    # Students table
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('target_grades', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('email', name='uq_students_email'),
    )

    # Create indexes
    op.create_index('idx_students_email', 'students', ['email'])
    op.create_index('idx_students_created_at', 'students', ['created_at'])

    # Subjects table (global, not multi-tenant)
    op.create_table(
        'subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('code', sa.String(length=10), nullable=False),  # e.g., "9708"
        sa.Column('name', sa.String(length=100), nullable=False),  # e.g., "Economics"
        sa.Column('level', sa.String(length=10), nullable=False),  # "AS" or "A"
        sa.Column('exam_board', sa.String(length=50), nullable=False, server_default='Cambridge International'),
        sa.Column('syllabus_year', sa.String(length=20), nullable=False),  # e.g., "2023-2025"
        sa.UniqueConstraint('code', 'syllabus_year', name='uq_subjects_code_year'),
    )

    op.create_index('idx_subjects_code', 'subjects', ['code'])

    # Seed initial data (Economics 9708)
    op.execute("""
        INSERT INTO subjects (id, code, name, level, exam_board, syllabus_year)
        VALUES (
            gen_random_uuid(),
            '9708',
            'Economics',
            'A',
            'Cambridge International',
            '2023-2025'
        )
    """)

def downgrade() -> None:
    """Drop students and subjects tables."""

    op.drop_index('idx_subjects_code', table_name='subjects')
    op.drop_table('subjects')

    op.drop_index('idx_students_created_at', table_name='students')
    op.drop_index('idx_students_email', table_name='students')
    op.drop_table('students')
```

**Multi-Tenant Table Migration**:
```python
def upgrade() -> None:
    """Add exams table (multi-tenant)."""

    op.create_table(
        'exams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_type', sa.String(length=20), nullable=False),  # "mock", "practice"
        sa.Column('total_marks', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Foreign keys
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='RESTRICT'),
    )

    # Multi-tenant index (CRITICAL for query performance)
    op.create_index('idx_student_exams', 'exams', ['student_id', 'created_at'])

def downgrade() -> None:
    """Drop exams table."""

    op.drop_index('idx_student_exams', table_name='exams')
    op.drop_table('exams')
```

**Running Migrations**:
```bash
# Generate migration automatically from models
cd backend
uv run alembic revision --autogenerate -m "add students table"

# Apply migration
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current version
uv run alembic current
```

**When to Use**: Creating database migrations, schema changes, adding indexes
