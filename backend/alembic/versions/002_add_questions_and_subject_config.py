"""Add questions, exams, subject config for Phase II

Revision ID: 002_questions
Revises: 001_initial
Create Date: 2025-12-18

Phase II Question Bank & Exam Generation Schema:
- Adds JSONB config columns to subjects table (marking_config, extraction_patterns, paper_templates)
- Creates questions table for storing extracted questions with JSONB syllabus tags and marking schemes
- Creates exams table for generated practice/timed exams
- Creates pdf_extraction_logs table for audit trail

Architecture Decisions:
- AD-001: JSONB + Resource Files for subject configuration
- AD-002: Generic extraction framework (config-driven, not subject-specific)
- JSONB with GIN indexes for fast containment queries

Constitutional Requirements:
- Principle VII: >80% test coverage (tables designed for testability)
- Principle V: Multi-tenant isolation (exams.student_id for future filtering)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic
revision: str = '002_questions'
down_revision: Union[str, Sequence[str], None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase II schema additions

    Changes:
    1. ALTER subjects table - add JSONB config columns
    2. CREATE questions table - store extracted questions
    3. CREATE exams table - store generated exams
    4. CREATE pdf_extraction_logs table - audit trail
    5. CREATE indexes - GIN indexes on JSONB, B-tree on scalars
    """

    # Enable uuid-ossp extension for uuid_generate_v4() function
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ========================================================================
    # T006: Add JSONB columns to subjects table
    # ========================================================================

    # Add marking_config JSONB column (e.g., level descriptors for Economics)
    op.add_column('subjects', sa.Column('marking_config', JSONB, nullable=True))

    # Add extraction_patterns JSONB column (e.g., question delimiters, marks patterns)
    op.add_column('subjects', sa.Column('extraction_patterns', JSONB, nullable=True))

    # Add paper_templates JSONB column (e.g., Paper 1/2/3 structures)
    op.add_column('subjects', sa.Column('paper_templates', JSONB, nullable=True))

    # Create GIN indexes on JSONB columns for fast queries
    op.create_index(
        'idx_subjects_marking_config',
        'subjects',
        ['marking_config'],
        postgresql_using='gin'
    )

    op.create_index(
        'idx_subjects_extraction_patterns',
        'subjects',
        ['extraction_patterns'],
        postgresql_using='gin'
    )

    # ========================================================================
    # T007: Create questions table
    # ========================================================================

    op.create_table(
        'questions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('syllabus_point_ids', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('question_text', sa.Text, nullable=False),
        sa.Column('max_marks', sa.Integer, nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('source_paper', sa.String(100), nullable=False),
        sa.Column('question_number', sa.Integer, nullable=False),
        sa.Column('marking_scheme', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=True),

        # Unique constraint: Prevent duplicate questions from same paper
        sa.UniqueConstraint('subject_id', 'source_paper', 'question_number', name='uq_questions_subject_paper_number'),

        # Check constraint: Difficulty must be valid enum value
        sa.CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name='ck_questions_difficulty')
    )

    # ========================================================================
    # T008: Create exams table
    # ========================================================================

    op.create_table(
        'exams',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('student_id', UUID(as_uuid=True), sa.ForeignKey('students.id'), nullable=True),  # Nullable for teacher-generated templates
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('exam_type', sa.String(20), nullable=False),
        sa.Column('paper_number', sa.Integer, nullable=True),
        sa.Column('question_ids', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('total_marks', sa.Integer, nullable=False),
        sa.Column('duration', sa.Integer, nullable=False),  # Duration in minutes
        sa.Column('status', sa.String(20), nullable=False, server_default="'PENDING'"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Check constraints: Validate enum values
        sa.CheckConstraint("exam_type IN ('PRACTICE', 'TIMED', 'FULL_PAPER')", name='ck_exams_exam_type'),
        sa.CheckConstraint("status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED')", name='ck_exams_status')
    )

    # ========================================================================
    # T009: Create pdf_extraction_logs table
    # ========================================================================

    op.create_table(
        'pdf_extraction_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),  # SHA256 hash
        sa.Column('subject_id', UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=True),  # Nullable if parsing fails
        sa.Column('extraction_status', sa.String(20), nullable=False),
        sa.Column('questions_extracted', sa.Integer, nullable=False, server_default='0'),
        sa.Column('errors', JSONB, nullable=True),
        sa.Column('processed_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Check constraint: Validate extraction status
        sa.CheckConstraint("extraction_status IN ('SUCCESS', 'FAILED', 'PARTIAL')", name='ck_pdf_logs_status')
    )

    # ========================================================================
    # T010: Create indexes
    # ========================================================================

    # Questions table indexes
    op.create_index('idx_questions_subject_id', 'questions', ['subject_id'])
    op.create_index('idx_questions_difficulty', 'questions', ['difficulty'])
    op.create_index('idx_questions_source_paper', 'questions', ['source_paper'])

    # GIN index on syllabus_point_ids for JSONB containment queries (@> operator)
    op.create_index(
        'idx_questions_syllabus_points',
        'questions',
        ['syllabus_point_ids'],
        postgresql_using='gin'
    )

    # Exams table indexes
    op.create_index('idx_exams_student_id', 'exams', ['student_id'])
    op.create_index('idx_exams_subject_id', 'exams', ['subject_id'])
    op.create_index('idx_exams_created_at', 'exams', ['created_at'])

    # PDF extraction logs indexes
    op.create_index('idx_pdf_logs_file_hash', 'pdf_extraction_logs', ['file_hash'])
    op.create_index('idx_pdf_logs_subject_id', 'pdf_extraction_logs', ['subject_id'])
    op.create_index('idx_pdf_logs_processed_at', 'pdf_extraction_logs', ['processed_at'])


def downgrade() -> None:
    """
    Rollback Phase II schema

    CAUTION: This will delete all Phase II data (questions, exams, extraction logs).
    Subject config JSONB columns will be removed.
    """

    # Drop indexes first
    # Questions indexes
    op.drop_index('idx_questions_syllabus_points', table_name='questions')
    op.drop_index('idx_questions_source_paper', table_name='questions')
    op.drop_index('idx_questions_difficulty', table_name='questions')
    op.drop_index('idx_questions_subject_id', table_name='questions')

    # Exams indexes
    op.drop_index('idx_exams_created_at', table_name='exams')
    op.drop_index('idx_exams_subject_id', table_name='exams')
    op.drop_index('idx_exams_student_id', table_name='exams')

    # PDF logs indexes
    op.drop_index('idx_pdf_logs_processed_at', table_name='pdf_extraction_logs')
    op.drop_index('idx_pdf_logs_subject_id', table_name='pdf_extraction_logs')
    op.drop_index('idx_pdf_logs_file_hash', table_name='pdf_extraction_logs')

    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('pdf_extraction_logs')
    op.drop_table('exams')
    op.drop_table('questions')

    # Drop GIN indexes on subjects table
    op.drop_index('idx_subjects_extraction_patterns', table_name='subjects')
    op.drop_index('idx_subjects_marking_config', table_name='subjects')

    # Drop JSONB columns from subjects table
    op.drop_column('subjects', 'paper_templates')
    op.drop_column('subjects', 'extraction_patterns')
    op.drop_column('subjects', 'marking_config')
