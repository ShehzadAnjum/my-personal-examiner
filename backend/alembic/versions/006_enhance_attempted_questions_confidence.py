"""Enhance attempted_questions with confidence scoring for Phase III Marker Agent

Revision ID: 006_confidence
Revises: 005_improve
Create Date: 2025-12-20

Phase III AI Teaching Roles - Marker Agent Schema Enhancement:
- Adds confidence_score field (0-100) to attempted_questions
- Adds needs_review boolean flag (<70% confidence triggers manual review)
- Adds reviewed_by and reviewed_at for human examiner review tracking

Architecture Decisions:
- AD-007: 6-signal confidence heuristic (<70% threshold for manual review)
- Enables quality assurance through manual review queue

Constitutional Requirements:
- Principle II: A* Standard (confidence scoring ensures quality control)
- Principle VII: >80% test coverage (fields designed for testability)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic
revision: str = '006_confidence'
down_revision: Union[str, Sequence[str], None] = '005_improve'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase III Marker Agent schema enhancements

    Changes:
    1. ALTER attempted_questions - add confidence scoring fields
    2. CREATE index - on needs_review for manual review queue
    """

    # ========================================================================
    # T012: Enhance attempted_questions with confidence scoring
    # ========================================================================

    # Add confidence_score column (0-100 scale)
    op.add_column('attempted_questions', sa.Column('confidence_score', sa.Integer, nullable=True))

    # Add needs_review flag (true if confidence < 70%)
    op.add_column('attempted_questions', sa.Column('needs_review', sa.Boolean, nullable=False, server_default='false'))

    # Add reviewed_by (human examiner who reviewed low-confidence marks)
    op.add_column('attempted_questions', sa.Column('reviewed_by', UUID(as_uuid=True), sa.ForeignKey('students.id'), nullable=True))

    # Add reviewed_at timestamp
    op.add_column('attempted_questions', sa.Column('reviewed_at', sa.DateTime, nullable=True))

    # Add check constraint for confidence_score range
    op.create_check_constraint(
        'ck_attempted_questions_confidence_score',
        'attempted_questions',
        'confidence_score BETWEEN 0 AND 100'
    )

    # Create index on needs_review for manual review queue queries
    op.create_index('idx_attempted_questions_needs_review', 'attempted_questions', ['needs_review'])


def downgrade() -> None:
    """
    Rollback Phase III Marker Agent confidence scoring enhancements

    CAUTION: This will remove all confidence scoring data.
    """

    # Drop index first
    op.drop_index('idx_attempted_questions_needs_review', table_name='attempted_questions')

    # Drop check constraint
    op.drop_constraint('ck_attempted_questions_confidence_score', 'attempted_questions', type_='check')

    # Drop columns in reverse order
    op.drop_column('attempted_questions', 'reviewed_at')
    op.drop_column('attempted_questions', 'reviewed_by')
    op.drop_column('attempted_questions', 'needs_review')
    op.drop_column('attempted_questions', 'confidence_score')
