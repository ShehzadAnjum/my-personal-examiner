"""Add improvement_plans table for Phase III Reviewer Agent

Revision ID: 005_improve
Revises: 004_study
Create Date: 2025-12-20

Phase III AI Teaching Roles - Reviewer Agent Schema:
- Creates improvement_plans table for storing student weakness analysis
- Links weaknesses (AO1/AO2/AO3) to actionable improvement tasks
- Tracks progress on action items with completion status

Architecture Decisions:
- AD-006: JSONB for flexible weakness categorization (AO1/AO2/AO3 structure adapts per subject)
- Linked to attempts table for traceability

Constitutional Requirements:
- Principle VI: Constructive Feedback (action_items provide concrete steps for improvement)
- Principle V: Multi-tenant isolation (student_id FK with CASCADE DELETE)
- Principle VII: >80% test coverage (table designed for testability)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic
revision: str = '005_improve'
down_revision: Union[str, Sequence[str], None] = '004_study'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase III Reviewer Agent schema additions

    Changes:
    1. CREATE improvement_plans table - weakness analysis and action items
    2. CREATE indexes - GIN indexes on JSONB, B-tree on student_id and attempt_id
    """

    # Ensure uuid-ossp extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ========================================================================
    # T011: Create improvement_plans table
    # ========================================================================

    op.create_table(
        'improvement_plans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attempt_id', UUID(as_uuid=True), sa.ForeignKey('attempts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('weaknesses', JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('action_items', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('progress', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
    )

    # Create indexes
    op.create_index('idx_improvement_plans_student', 'improvement_plans', ['student_id'])
    op.create_index('idx_improvement_plans_attempt', 'improvement_plans', ['attempt_id'])

    # GIN indexes on JSONB fields for fast weakness/action queries
    op.create_index(
        'idx_improvement_plans_weaknesses',
        'improvement_plans',
        ['weaknesses'],
        postgresql_using='gin'
    )

    op.create_index(
        'idx_improvement_plans_action_items',
        'improvement_plans',
        ['action_items'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Rollback Phase III Reviewer Agent schema

    CAUTION: This will delete all improvement plan data.
    """

    # Drop indexes first
    op.drop_index('idx_improvement_plans_action_items', table_name='improvement_plans')
    op.drop_index('idx_improvement_plans_weaknesses', table_name='improvement_plans')
    op.drop_index('idx_improvement_plans_attempt', table_name='improvement_plans')
    op.drop_index('idx_improvement_plans_student', table_name='improvement_plans')

    # Drop table
    op.drop_table('improvement_plans')
