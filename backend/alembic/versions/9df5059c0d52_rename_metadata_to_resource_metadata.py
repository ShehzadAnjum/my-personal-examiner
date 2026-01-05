"""rename_metadata_to_resource_metadata

Revision ID: 9df5059c0d52
Revises: 011_add_resource_indexes
Create Date: 2025-12-27 15:41:46.074355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9df5059c0d52'
down_revision: Union[str, Sequence[str], None] = '011_add_resource_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename metadata column to resource_metadata (avoid SQLAlchemy reserved name)
    op.alter_column('resources', 'metadata', new_column_name='resource_metadata')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert column name back to metadata
    op.alter_column('resources', 'resource_metadata', new_column_name='metadata')
