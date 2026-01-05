"""Add resource indexes for performance

Revision ID: 011_add_resource_indexes
Revises: 010_add_resource_tables
Create Date: 2025-12-27

Feature: 007-resource-bank-files
Indexes: 14 performance indexes for fast queries
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '011_add_resource_indexes'
down_revision: Union[str, None] = '010_add_resource_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Resources table indexes
    op.create_index('idx_resource_type', 'resources', ['resource_type'])
    op.create_index('idx_visibility', 'resources', ['visibility'])
    op.create_index('idx_uploaded_by', 'resources', ['uploaded_by_student_id'])
    op.create_index('idx_signature', 'resources', ['signature'])
    op.create_index('idx_s3_sync_status', 'resources', ['s3_sync_status'])
    op.create_index('idx_title', 'resources', ['title'])
    
    # Full-text search GIN index
    op.execute("CREATE INDEX idx_search_vector ON resources USING GIN(search_vector)")

    # SyllabusPointResource indexes
    op.create_index('idx_relevance_score', 'syllabus_point_resources', [sa.text('relevance_score DESC')])
    op.create_index('idx_added_by', 'syllabus_point_resources', ['added_by'])
    op.create_index('idx_spr_resource_id', 'syllabus_point_resources', ['resource_id'])

    # ExplanationResourceUsage indexes
    op.create_index('idx_explanation_usage', 'explanation_resource_usage', ['explanation_id'])
    op.create_index('idx_resource_usage', 'explanation_resource_usage', ['resource_id'])

    # StudentResourcePreference indexes
    op.create_index('idx_student_preferences', 'student_resource_preferences', ['student_id'])
    op.create_index('idx_priority', 'student_resource_preferences', [sa.text('priority DESC')])


def downgrade() -> None:
    # Drop StudentResourcePreference indexes
    op.drop_index('idx_priority', 'student_resource_preferences')
    op.drop_index('idx_student_preferences', 'student_resource_preferences')

    # Drop ExplanationResourceUsage indexes
    op.drop_index('idx_resource_usage', 'explanation_resource_usage')
    op.drop_index('idx_explanation_usage', 'explanation_resource_usage')

    # Drop SyllabusPointResource indexes
    op.drop_index('idx_spr_resource_id', 'syllabus_point_resources')
    op.drop_index('idx_added_by', 'syllabus_point_resources')
    op.drop_index('idx_relevance_score', 'syllabus_point_resources')

    # Drop Resources indexes
    op.drop_index('idx_search_vector', 'resources')
    op.drop_index('idx_title', 'resources')
    op.drop_index('idx_s3_sync_status', 'resources')
    op.drop_index('idx_signature', 'resources')
    op.drop_index('idx_uploaded_by', 'resources')
    op.drop_index('idx_visibility', 'resources')
    op.drop_index('idx_resource_type', 'resources')
