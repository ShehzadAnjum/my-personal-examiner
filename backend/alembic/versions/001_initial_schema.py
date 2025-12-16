"""Initial schema: students, subjects, syllabus_points

Revision ID: 001_initial
Revises:
Create Date: 2025-12-16

Creates three tables:
- students (multi-tenant anchor entity)
- subjects (global, seeded with Economics 9708)
- syllabus_points (global, foreign key to subjects)

Constitutional Requirements:
- Principle V: Multi-tenant isolation (students table)
- Principle I & FR-014: Economics 9708 seeded
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID, TEXT


# revision identifiers, used by Alembic
revision: str = '001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial schema

    Tables created:
    1. students - Multi-tenant anchor entity
    2. subjects - Available A-Level subjects (global)
    3. syllabus_points - Learning objectives (global)
    """

    # Create students table (Multi-tenant anchor)
    op.create_table(
        'students',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column('email', sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('target_grades', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Create indexes on students
    op.create_index('idx_students_email', 'students', ['email'])
    op.create_index('idx_students_created_at', 'students', ['created_at'])

    # Create subjects table (Global)
    op.create_table(
        'subjects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('exam_board', sa.String(length=50), nullable=False, server_default='Cambridge International'),
        sa.Column('syllabus_year', sa.String(length=20), nullable=False),
    )

    # Create indexes on subjects
    op.create_index('idx_subjects_code', 'subjects', ['code'])
    op.create_index('uq_subjects_code_year', 'subjects', ['code', 'syllabus_year'], unique=True)

    # Create syllabus_points table (Global, FK to subjects)
    op.create_table(
        'syllabus_points',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False, index=True),
        sa.Column('code', sa.String(length=20), nullable=False, index=True),
        sa.Column('description', TEXT, nullable=False),
        sa.Column('topics', TEXT, nullable=True),
        sa.Column('learning_outcomes', TEXT, nullable=True),
    )

    # Create indexes on syllabus_points
    op.create_index('idx_syllabus_points_subject_id', 'syllabus_points', ['subject_id'])
    op.create_index('idx_syllabus_points_code', 'syllabus_points', ['code'])

    # Seed Economics 9708 (Constitutional Requirement - FR-014)
    economics_id = str(uuid4())
    op.execute(f"""
        INSERT INTO subjects (id, code, name, level, exam_board, syllabus_year)
        VALUES (
            '{economics_id}',
            '9708',
            'Economics',
            'A',
            'Cambridge International',
            '2023-2025'
        )
    """)


def downgrade() -> None:
    """
    Drop all tables

    CAUTION: This will delete all data in Phase I tables.
    """

    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('syllabus_points')
    op.drop_table('subjects')
    op.drop_table('students')
