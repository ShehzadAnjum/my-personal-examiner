"""merge_heads_before_resource_bank

Revision ID: 7b8e00fbe2d1
Revises: 008_pointer, 4ac52e7be851
Create Date: 2025-12-26 01:54:36.375777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b8e00fbe2d1'
down_revision: Union[str, Sequence[str], None] = ('008_pointer', '4ac52e7be851')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
