"""merge_phase_ii_and_phase_iii_migrations

Revision ID: 4ac52e7be851
Revises: 006_attempted_questions_confidence, 70253d04973d
Create Date: 2025-12-20 06:12:06.769674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ac52e7be851'
down_revision: Union[str, Sequence[str], None] = ('006_confidence', '70253d04973d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
