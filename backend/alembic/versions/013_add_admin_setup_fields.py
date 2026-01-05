"""Add admin setup fields to subjects and generated_explanations

Revision ID: 013_add_admin_setup_fields
Revises: 1322c004525c
Create Date: 2026-01-05

Feature: Admin-First Topic & Explanation Generation System

Changes:
1. subjects table:
   - Add setup_status (VARCHAR) - tracks admin setup wizard progress
   - Add syllabus_resource_id (UUID FK) - links to uploaded syllabus PDF

2. generated_explanations table:
   - Add archived (BOOLEAN) - for v2+ relinking during syllabus regeneration
   - Add archive_reason (VARCHAR) - reason for archiving
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "013_add_admin_setup_fields"
down_revision = "1322c004525c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add setup_status to subjects
    op.add_column(
        "subjects",
        sa.Column(
            "setup_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
    )

    # Add syllabus_resource_id to subjects
    op.add_column(
        "subjects",
        sa.Column(
            "syllabus_resource_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Add foreign key constraint for syllabus_resource_id
    op.create_foreign_key(
        "fk_subjects_syllabus_resource",
        "subjects",
        "resources",
        ["syllabus_resource_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add archived field to generated_explanations
    op.add_column(
        "generated_explanations",
        sa.Column(
            "archived",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    # Add archive_reason field to generated_explanations
    op.add_column(
        "generated_explanations",
        sa.Column(
            "archive_reason",
            sa.String(length=500),
            nullable=True,
        ),
    )

    # Add index for finding non-archived explanations
    op.create_index(
        "idx_explanation_archived",
        "generated_explanations",
        ["archived"],
        postgresql_where=sa.text("archived = false"),
    )


def downgrade() -> None:
    # Remove index
    op.drop_index("idx_explanation_archived", table_name="generated_explanations")

    # Remove archive fields from generated_explanations
    op.drop_column("generated_explanations", "archive_reason")
    op.drop_column("generated_explanations", "archived")

    # Remove foreign key and columns from subjects
    op.drop_constraint("fk_subjects_syllabus_resource", "subjects", type_="foreignkey")
    op.drop_column("subjects", "syllabus_resource_id")
    op.drop_column("subjects", "setup_status")
