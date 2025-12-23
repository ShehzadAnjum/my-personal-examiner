"""Add study_plans table for Phase III Planner Agent

Revision ID: 004_study
Revises: 003_coaching
Create Date: 2025-12-20

Phase III AI Teaching Roles - Planner Agent Schema:
- Creates study_plans table for storing personalized study schedules
- Uses SuperMemo 2 (SM-2) spaced repetition algorithm with easiness factors
- Implements contextual interleaving (max 3 related topics per day)
- Stores JSONB schedule (day-by-day with intervals) and easiness_factors (EF per topic)

Architecture Decisions:
- AD-004: SM-2 algorithm for evidence-based spaced repetition
- AD-005: JSONB for flexible schedule storage (days, activities, intervals adapt dynamically)

Constitutional Requirements:
- Principle V: Multi-tenant isolation (student_id FK with CASCADE DELETE)
- Principle VII: >80% test coverage (table designed for testability)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic
revision: str = '004_study'
down_revision: Union[str, Sequence[str], None] = '003_coaching'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase III Planner Agent schema additions

    Changes:
    1. CREATE study_plans table - personalized n-day study schedules
    2. CREATE indexes - GIN indexes on JSONB, B-tree on student_id and status
    """

    # Ensure uuid-ossp extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ========================================================================
    # T010: Create study_plans table
    # ========================================================================

    op.create_table(
        'study_plans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('exam_date', sa.Date, nullable=False),
        sa.Column('total_days', sa.Integer, nullable=False),
        sa.Column('hours_per_day', sa.Float, nullable=False),
        sa.Column('schedule', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('easiness_factors', JSONB, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default="'active'"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Check constraints
        sa.CheckConstraint('total_days > 0', name='ck_study_plans_total_days'),
        sa.CheckConstraint('hours_per_day > 0 AND hours_per_day <= 24', name='ck_study_plans_hours_per_day'),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'abandoned')",
            name='ck_study_plans_status'
        )
    )

    # Create indexes
    op.create_index('idx_study_plans_student', 'study_plans', ['student_id'])
    op.create_index('idx_study_plans_status', 'study_plans', ['status'])
    op.create_index('idx_study_plans_exam_date', 'study_plans', ['exam_date'])

    # GIN indexes on JSONB fields for fast queries
    op.create_index(
        'idx_study_plans_schedule',
        'study_plans',
        ['schedule'],
        postgresql_using='gin'
    )

    op.create_index(
        'idx_study_plans_easiness_factors',
        'study_plans',
        ['easiness_factors'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Rollback Phase III Planner Agent schema

    CAUTION: This will delete all study plan data.
    """

    # Drop indexes first
    op.drop_index('idx_study_plans_easiness_factors', table_name='study_plans')
    op.drop_index('idx_study_plans_schedule', table_name='study_plans')
    op.drop_index('idx_study_plans_exam_date', table_name='study_plans')
    op.drop_index('idx_study_plans_status', table_name='study_plans')
    op.drop_index('idx_study_plans_student', table_name='study_plans')

    # Drop table
    op.drop_table('study_plans')
