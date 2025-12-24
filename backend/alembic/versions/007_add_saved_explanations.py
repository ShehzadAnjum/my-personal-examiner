"""Add saved_explanations table for Phase IV Teaching Page

Revision ID: 007_saved
Revises: 006_confidence
Create Date: 2025-12-23

Feature: 005-teaching-page (User Story 3 - Bookmark Explanations)
- Creates saved_explanations table for storing bookmarked explanations
- Links students to syllabus topics with full explanation content
- Prevents duplicate bookmarks per student+topic
- Multi-tenant isolation via student_id foreign key

Architecture Decisions:
- AD-007: JSONB for explanation_content (full TopicExplanation JSON ~5-10KB)
- Unique constraint on (student_id, syllabus_point_id) prevents duplicate bookmarks
- Indexes on student_id and syllabus_point_id for multi-tenant queries

Constitutional Requirements:
- Principle V: Multi-tenant isolation (student_id FK with CASCADE DELETE)
- Principle VI: Constructive Feedback (preserve AI-generated teaching quality in JSON)
- FR-012: Prevent duplicate bookmarks per student+topic
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic
revision: str = '007_saved'
down_revision: Union[str, Sequence[str], None] = '006_confidence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase IV Teaching Page schema additions

    Changes:
    1. CREATE saved_explanations table - bookmarked explanations
    2. CREATE unique constraint - prevent duplicate bookmarks per student+topic
    3. CREATE indexes - student_id, syllabus_point_id for multi-tenant queries
    """

    # Ensure uuid-ossp extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ========================================================================
    # T006: Create saved_explanations table
    # ========================================================================

    op.create_table(
        'saved_explanations',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('uuid_generate_v4()'),
            nullable=False
        ),
        sa.Column(
            'student_id',
            UUID(as_uuid=True),
            sa.ForeignKey('students.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'syllabus_point_id',
            UUID(as_uuid=True),
            sa.ForeignKey('syllabus_points.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'explanation_content',
            JSONB,
            nullable=False,
            comment='Full TopicExplanation JSON (definition, examples, practice, etc.)'
        ),
        sa.Column(
            'date_saved',
            sa.DateTime,
            nullable=False,
            server_default=sa.text('NOW()')
        ),
        sa.Column(
            'date_last_viewed',
            sa.DateTime,
            nullable=True
        ),
        # Unique constraint: prevent duplicate bookmarks per student+topic
        sa.UniqueConstraint(
            'student_id',
            'syllabus_point_id',
            name='uq_saved_explanation_student_topic'
        ),
    )

    # Create indexes for multi-tenant queries
    op.create_index(
        'idx_saved_explanations_student',
        'saved_explanations',
        ['student_id']
    )

    op.create_index(
        'idx_saved_explanations_syllabus_point',
        'saved_explanations',
        ['syllabus_point_id']
    )

    # GIN index on explanation_content for future search within bookmarks
    op.create_index(
        'idx_saved_explanations_content',
        'saved_explanations',
        ['explanation_content'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Rollback Phase IV Teaching Page schema

    CAUTION: This will delete all saved explanation data.
    """

    # Drop indexes first
    op.drop_index('idx_saved_explanations_content', table_name='saved_explanations')
    op.drop_index('idx_saved_explanations_syllabus_point', table_name='saved_explanations')
    op.drop_index('idx_saved_explanations_student', table_name='saved_explanations')

    # Drop table (unique constraint drops automatically with table)
    op.drop_table('saved_explanations')
