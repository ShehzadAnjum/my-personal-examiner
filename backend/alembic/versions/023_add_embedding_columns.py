"""Add embedding columns to syllabus_points and create embedding_jobs table

Revision ID: 023_add_embedding_columns
Revises: 022_add_assessment_model
Create Date: 2026-01-21

Feature: 010-embedding-integration

This migration:
1. Enables pgvector extension for vector storage
2. Adds embedding columns to syllabus_points table:
   - embedding: VECTOR(768) for semantic search
   - embedding_model: VARCHAR(50) for model version tracking
   - embedded_at: TIMESTAMP for freshness tracking
3. Creates embedding_jobs table for bulk embedding generation tracking

Constitutional Requirements:
- Embeddings scoped to subject/syllabus for multi-tenant isolation - Principle V
- Embeddings regenerated when syllabus updated - Principle III
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "023_add_embedding_columns"
down_revision = "022_add_assessment_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Enable pgvector and add embedding columns to syllabus_points,
    create embedding_jobs table for tracking bulk operations.
    """
    # Enable pgvector extension (requires superuser on Neon - already available)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding columns to syllabus_points
    op.add_column(
        "syllabus_points",
        sa.Column(
            "embedding",
            postgresql.ARRAY(sa.Float()),
            nullable=True,
            comment="768-dimension vector embedding for semantic search (stored as float array, cast to vector for queries)"
        )
    )
    op.add_column(
        "syllabus_points",
        sa.Column(
            "embedding_model",
            sa.String(50),
            nullable=True,
            comment="Model used to generate embedding (e.g., 'gemini/text-embedding-004')"
        )
    )
    op.add_column(
        "syllabus_points",
        sa.Column(
            "embedded_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when embedding was generated"
        )
    )

    # Create embedding_jobs table for tracking bulk embedding generation
    op.create_table(
        "embedding_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
            comment="Job status: pending, in_progress, completed, failed, partial"
        ),
        sa.Column(
            "job_type",
            sa.String(50),
            nullable=False,
            comment="Type: syllabus, resource, bulk_regenerate"
        ),
        sa.Column(
            "total_items",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total items to embed"
        ),
        sa.Column(
            "completed_items",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Successfully embedded count"
        ),
        sa.Column(
            "failed_items",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Failed embedding count"
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Job start time"
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Job completion time"
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Error details if failed"
        ),
        sa.Column(
            "failed_item_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
            comment="IDs of failed items for retry"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="SET NULL"),
            nullable=True,
            comment="User who triggered job"
        ),
    )

    # Create index for status (subject_id index already created via index=True in table definition)
    op.execute("CREATE INDEX IF NOT EXISTS ix_embedding_jobs_status ON embedding_jobs (status)")


def downgrade() -> None:
    """
    Drop embedding_jobs table and embedding columns from syllabus_points.
    """
    # Drop indexes
    op.drop_index("ix_embedding_jobs_status", table_name="embedding_jobs")
    op.drop_index("ix_embedding_jobs_subject_id", table_name="embedding_jobs")

    # Drop embedding_jobs table
    op.drop_table("embedding_jobs")

    # Remove embedding columns from syllabus_points
    op.drop_column("syllabus_points", "embedded_at")
    op.drop_column("syllabus_points", "embedding_model")
    op.drop_column("syllabus_points", "embedding")

    # Note: Not dropping pgvector extension as it may be used elsewhere
