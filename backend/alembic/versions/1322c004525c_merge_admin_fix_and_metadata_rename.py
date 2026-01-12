"""merge_admin_fix_and_metadata_rename

Revision ID: 1322c004525c
Revises: 012_fix_admin_resources, 9df5059c0d52
Create Date: 2026-01-05 02:07:34.958024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1322c004525c'
down_revision: Union[str, Sequence[str], None] = ('012_fix_admin_resources', '9df5059c0d52')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
