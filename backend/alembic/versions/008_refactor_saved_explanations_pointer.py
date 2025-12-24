"""refactor saved_explanations to pointer-based bookmarks

Revision ID: 008
Revises: 007
Create Date: 2025-12-24

Changes:
- Drop explanation_content column (JSON) from saved_explanations table
- Architecture change: Store only syllabus_point_id reference (pointer-based bookmarks)
- Explanation content now cached in browser localStorage only
- Reduces database storage and eliminates content duplication

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_pointer'
down_revision = '007_saved'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Drop explanation_content column from saved_explanations.

    WARNING: This will delete all existing saved explanation content!
    Users will need to regenerate explanations after this migration.
    """
    # Drop the explanation_content column
    op.drop_column('saved_explanations', 'explanation_content')


def downgrade() -> None:
    """
    Re-add explanation_content column (but data will be lost).

    NOTE: This only recreates the column structure, not the data!
    """
    # Re-add the explanation_content column
    op.add_column(
        'saved_explanations',
        sa.Column(
            'explanation_content',
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default='{}'  # Default empty JSON object for existing rows
        )
    )
