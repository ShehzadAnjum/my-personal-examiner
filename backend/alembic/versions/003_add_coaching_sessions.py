"""Add coaching_sessions table for Phase III Coach Agent

Revision ID: 003_coaching_sessions
Revises: 002b_attempts
Create Date: 2025-12-20

Phase III AI Teaching Roles - Coach Agent Schema:
- Creates coaching_sessions table for tracking tutoring sessions
- Stores JSONB session transcripts (array of {role, content, timestamp} objects)
- Tracks session outcomes (in_progress, resolved, needs_more_help, refer_to_teacher)

Architecture Decisions:
- AD-003: JSONB for flexible conversation storage (Socratic questioning is dynamic)
- JSONB with GIN indexes for fast containment queries

Constitutional Requirements:
- Principle V: Multi-tenant isolation (student_id FK with CASCADE DELETE)
- Principle VII: >80% test coverage (table designed for testability)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic
revision: str = '003_coaching'
down_revision: Union[str, Sequence[str], None] = '002b_attempts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase III Coach Agent schema additions

    Changes:
    1. CREATE coaching_sessions table - track tutoring sessions
    2. CREATE indexes - GIN index on JSONB transcript, B-tree on student_id
    """

    # Ensure uuid-ossp extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ========================================================================
    # T009: Create coaching_sessions table
    # ========================================================================

    op.create_table(
        'coaching_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(500), nullable=False),
        sa.Column('struggle_description', sa.Text, nullable=True),
        sa.Column('session_transcript', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('outcome', sa.String(50), nullable=False, server_default="'in_progress'"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Check constraint: Validate outcome enum
        sa.CheckConstraint(
            "outcome IN ('in_progress', 'resolved', 'needs_more_help', 'refer_to_teacher')",
            name='ck_coaching_sessions_outcome'
        )
    )

    # Create indexes
    op.create_index('idx_coaching_sessions_student', 'coaching_sessions', ['student_id'])
    op.create_index('idx_coaching_sessions_created', 'coaching_sessions', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # GIN index on session_transcript for JSONB queries
    op.create_index(
        'idx_coaching_sessions_transcript',
        'coaching_sessions',
        ['session_transcript'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Rollback Phase III Coach Agent schema

    CAUTION: This will delete all coaching session data.
    """

    # Drop indexes first
    op.drop_index('idx_coaching_sessions_transcript', table_name='coaching_sessions')
    op.drop_index('idx_coaching_sessions_created', table_name='coaching_sessions')
    op.drop_index('idx_coaching_sessions_student', table_name='coaching_sessions')

    # Drop table
    op.drop_table('coaching_sessions')
