"""Add mark_schemes table and update questions table for Phase II US1

Revision ID: 70253d04973d
Revises: 002_questions
Create Date: 2025-12-19

Phase II User Story 1: Upload & Storage
- Adds mark_schemes table for storing raw mark scheme text (AD-005: Minimal Extraction)
- Adds missing columns to questions table (paper_number, year, session, file_path)
- Updates syllabus_point_ids to use ARRAY[TEXT] instead of JSONB for better PostgreSQL support

Architecture Decisions:
- AD-005: Minimal mark scheme extraction (raw text in Phase II, parsing in Phase III)
- Questions and mark_schemes linked via source_paper identifier
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB


# revision identifiers, used by Alembic.
revision: str = '70253d04973d'
down_revision: Union[str, Sequence[str], None] = '002_questions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase II US1 schema additions

    Changes:
    1. ALTER questions table - add paper_number, year, session, file_path columns
    2. ALTER questions table - change syllabus_point_ids from JSONB to ARRAY[TEXT]
    3. CREATE mark_schemes table - store raw mark scheme text
    4. CREATE indexes on new columns
    """

    # ========================================================================
    # Update questions table - add missing columns
    # ========================================================================

    # Add paper_number column (extracted from source_paper)
    op.add_column('questions', sa.Column('paper_number', sa.Integer, nullable=True))

    # Add year column (exam year)
    op.add_column('questions', sa.Column('year', sa.Integer, nullable=True))

    # Add session column (exam session: MAY_JUNE, FEB_MARCH, OCT_NOV)
    op.add_column('questions', sa.Column('session', sa.String(20), nullable=True))

    # Add file_path column (path to original PDF)
    op.add_column('questions', sa.Column('file_path', sa.String(500), nullable=True))

    # Add check constraint for session validation
    op.create_check_constraint(
        'ck_questions_session',
        'questions',
        "session IN ('MAY_JUNE', 'FEB_MARCH', 'OCT_NOV') OR session IS NULL"
    )

    # ========================================================================
    # Update questions table - convert syllabus_point_ids to ARRAY[TEXT]
    # ========================================================================

    # Drop the old GIN index on JSONB first
    op.drop_index('idx_questions_syllabus_points', table_name='questions')

    # Add new temporary column for ARRAY[TEXT]
    op.add_column('questions', sa.Column('syllabus_point_ids_temp', ARRAY(sa.Text), nullable=True))

    # Migrate data from JSONB to ARRAY (handle empty arrays and null values)
    op.execute("""
        UPDATE questions
        SET syllabus_point_ids_temp = CASE
            WHEN syllabus_point_ids IS NULL THEN NULL
            WHEN syllabus_point_ids::text = '[]' THEN ARRAY[]::TEXT[]
            ELSE (
                SELECT ARRAY_AGG(elem::text)
                FROM jsonb_array_elements_text(syllabus_point_ids) AS elem
            )
        END
    """)

    # Drop old JSONB column
    op.drop_column('questions', 'syllabus_point_ids')

    # Rename temp column to final name
    op.alter_column('questions', 'syllabus_point_ids_temp', new_column_name='syllabus_point_ids')

    # Create GIN index on new ARRAY column (supports && and @> operators)
    op.execute("""
        CREATE INDEX idx_questions_syllabus_points
        ON questions USING GIN (syllabus_point_ids)
    """)

    # ========================================================================
    # Create mark_schemes table
    # ========================================================================

    op.create_table(
        'mark_schemes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('source_paper', sa.String(50), nullable=False, unique=True),
        sa.Column('mark_scheme_text', sa.Text, nullable=False),
        sa.Column('question_paper_filename', sa.String(100), nullable=False),
        sa.Column('paper_number', sa.Integer, nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('session', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Check constraint: Validate session
        sa.CheckConstraint("session IN ('MAY_JUNE', 'FEB_MARCH', 'OCT_NOV')", name='ck_mark_schemes_session')
    )

    # ========================================================================
    # Create indexes
    # ========================================================================

    # Questions table indexes (new columns)
    op.create_index('idx_questions_paper_number', 'questions', ['paper_number'])
    op.create_index('idx_questions_year', 'questions', ['year'])
    op.create_index('idx_questions_session', 'questions', ['session'])

    # Mark schemes table indexes
    op.create_index('idx_mark_schemes_subject_id', 'mark_schemes', ['subject_id'])
    op.create_index('idx_mark_schemes_source_paper', 'mark_schemes', ['source_paper'])
    op.create_index('idx_mark_schemes_year', 'mark_schemes', ['year'])
    op.create_index('idx_mark_schemes_session', 'mark_schemes', ['session'])


def downgrade() -> None:
    """
    Rollback Phase II US1 schema changes

    CAUTION: This will delete all mark scheme data.
    Questions table columns will be reverted.
    """

    # Drop mark_schemes indexes
    op.drop_index('idx_mark_schemes_session', table_name='mark_schemes')
    op.drop_index('idx_mark_schemes_year', table_name='mark_schemes')
    op.drop_index('idx_mark_schemes_source_paper', table_name='mark_schemes')
    op.drop_index('idx_mark_schemes_subject_id', table_name='mark_schemes')

    # Drop mark_schemes table
    op.drop_table('mark_schemes')

    # Drop questions table indexes (new columns)
    op.drop_index('idx_questions_session', table_name='questions')
    op.drop_index('idx_questions_year', table_name='questions')
    op.drop_index('idx_questions_paper_number', table_name='questions')

    # Revert syllabus_point_ids to JSONB
    op.drop_index('idx_questions_syllabus_points', table_name='questions')

    # Add temporary JSONB column
    op.add_column('questions', sa.Column('syllabus_point_ids_temp', JSONB, nullable=True))

    # Migrate data from ARRAY back to JSONB
    op.execute("""
        UPDATE questions
        SET syllabus_point_ids_temp = CASE
            WHEN syllabus_point_ids IS NULL THEN '[]'::jsonb
            WHEN array_length(syllabus_point_ids, 1) IS NULL THEN '[]'::jsonb
            ELSE to_jsonb(syllabus_point_ids)
        END
    """)

    # Drop ARRAY column
    op.drop_column('questions', 'syllabus_point_ids')

    # Rename temp column
    op.alter_column('questions', 'syllabus_point_ids_temp', new_column_name='syllabus_point_ids')

    # Recreate GIN index on JSONB
    op.execute("""
        CREATE INDEX idx_questions_syllabus_points
        ON questions USING GIN (syllabus_point_ids)
    """)

    # Drop check constraint
    op.drop_constraint('ck_questions_session', 'questions', type_='check')

    # Drop columns from questions table
    op.drop_column('questions', 'file_path')
    op.drop_column('questions', 'session')
    op.drop_column('questions', 'year')
    op.drop_column('questions', 'paper_number')
