"""Add resource bank tables

Revision ID: 010_add_resource_tables
Revises: 009_resource_bank
Create Date: 2025-12-27

Feature: 007-resource-bank-files
Tables: resources, syllabus_point_resources, explanation_resource_usage, student_resource_preferences
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010_add_resource_tables'
down_revision: Union[str, None] = '009_resource_bank'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types (safely, ignoring if they already exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE resourcetype AS ENUM ('syllabus', 'textbook', 'past_paper', 'video', 'article', 'user_upload');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE visibility AS ENUM ('public', 'private', 'pending_review');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE s3syncstatus AS ENUM ('pending', 'success', 'failed', 'pending_retry');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE addedby AS ENUM ('system', 'admin', 'student');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create resources table (using create_type=False to prevent automatic ENUM creation)
    op.create_table(
        'resources',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('resource_type', postgresql.ENUM('syllabus', 'textbook', 'past_paper', 'video', 'article', 'user_upload', name='resourcetype', create_type=False), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source_url', sa.String(2000), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('uploaded_by_student_id', postgresql.UUID(), nullable=True),
        sa.Column('admin_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('visibility', postgresql.ENUM('public', 'private', 'pending_review', name='visibility', create_type=False), nullable=False, server_default='pending_review'),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('signature', sa.String(64), nullable=False),
        sa.Column('s3_url', sa.String(2000), nullable=True),
        sa.Column('s3_sync_status', postgresql.ENUM('pending', 'success', 'failed', 'pending_retry', name='s3syncstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR, sa.Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, ''))")),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by_student_id'], ['students.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('signature', name='uq_resource_signature')
    )

    # Create syllabus_point_resources table
    op.create_table(
        'syllabus_point_resources',
        sa.Column('syllabus_point_id', postgresql.UUID(), nullable=False),
        sa.Column('resource_id', postgresql.UUID(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('added_by', postgresql.ENUM('system', 'admin', 'student', name='addedby', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('syllabus_point_id', 'resource_id'),
        sa.ForeignKeyConstraint(['syllabus_point_id'], ['syllabus_points.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.CheckConstraint('relevance_score >= 0 AND relevance_score <= 1', name='ck_relevance_score_range')
    )

    # Create explanation_resource_usage table
    op.create_table(
        'explanation_resource_usage',
        sa.Column('explanation_id', postgresql.UUID(), nullable=False),
        sa.Column('resource_id', postgresql.UUID(), nullable=False),
        sa.Column('contribution_weight', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('explanation_id', 'resource_id'),
        sa.ForeignKeyConstraint(['explanation_id'], ['generated_explanations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.CheckConstraint('contribution_weight >= 0 AND contribution_weight <= 1', name='ck_contribution_weight_range')
    )

    # Create student_resource_preferences table
    op.create_table(
        'student_resource_preferences',
        sa.Column('student_id', postgresql.UUID(), nullable=False),
        sa.Column('resource_id', postgresql.UUID(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('student_id', 'resource_id'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('student_resource_preferences')
    op.drop_table('explanation_resource_usage')
    op.drop_table('syllabus_point_resources')
    op.drop_table('resources')
    op.execute("DROP TYPE IF EXISTS addedby")
    op.execute("DROP TYPE IF EXISTS s3syncstatus")
    op.execute("DROP TYPE IF EXISTS visibility")
    op.execute("DROP TYPE IF EXISTS resourcetype")
