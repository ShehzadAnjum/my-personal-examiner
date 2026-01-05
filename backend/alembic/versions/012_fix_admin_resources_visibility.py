"""Fix admin-uploaded resources visibility

Revision ID: 012_fix_admin_resources
Revises: 011_add_resource_indexes
Create Date: 2026-01-05

Data fix: Auto-approve all admin-uploaded resources that were created
before the auto-approval logic was implemented.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '012_fix_admin_resources'
down_revision: Union[str, None] = '011_add_resource_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Auto-approve all resources that:
    1. Have uploaded_by_student_id that is an admin
    2. Are currently pending_review
    3. Should have been auto-approved
    """
    # Update resources uploaded by admins to be auto-approved
    op.execute("""
        UPDATE resources r
        SET
            admin_approved = true,
            visibility = 'public'
        FROM students s
        WHERE
            r.uploaded_by_student_id = s.id
            AND s.is_admin = true
            AND r.admin_approved = false
            AND r.visibility = 'pending_review';
    """)

    # Also update admin-uploaded resources where uploaded_by_student_id is NULL
    # but the resource type suggests it was admin-uploaded (not user_upload)
    op.execute("""
        UPDATE resources
        SET
            admin_approved = true,
            visibility = 'public'
        WHERE
            uploaded_by_student_id IS NULL
            AND resource_type != 'user_upload'
            AND admin_approved = false
            AND visibility = 'pending_review';
    """)


def downgrade() -> None:
    """
    No downgrade - this is a data fix for inconsistent state.
    We don't want to revert auto-approvals.
    """
    pass
