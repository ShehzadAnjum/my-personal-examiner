"""add resource bank tables

Revision ID: 009_resource_bank
Revises: 7b8e00fbe2d1
Create Date: 2025-12-26

Feature: 006-resource-bank
Adds:
- generated_explanations table (shared topic explanations)
- student_learning_paths table (per-student progress tracking)
- student_llm_configs table (encrypted API key storage)
- is_admin column to students table
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision: str = "009_resource_bank"
down_revision: Union[str, None] = "7b8e00fbe2d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_admin column to students
    op.add_column(
        "students",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
    )

    # 2. Create student_llm_configs table
    op.create_table(
        "student_llm_configs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("api_key_encrypted", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("usage_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("usage_reset_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("usage_this_month >= 0", name="ck_llmconfig_usage_positive"),
    )
    op.create_index(
        "ix_student_llm_configs_student_id",
        "student_llm_configs",
        ["student_id"],
    )
    op.create_index(
        "idx_llmconfig_student_provider",
        "student_llm_configs",
        ["student_id", "provider"],
        unique=True,
    )
    op.create_index(
        "idx_llmconfig_student_active",
        "student_llm_configs",
        ["student_id"],
        postgresql_where=sa.text("is_active = true"),
    )

    # 3. Create generated_explanations table
    op.create_table(
        "generated_explanations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("syllabus_point_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("generated_by", sa.String(length=50), nullable=False),
        sa.Column("generator_student_id", sa.UUID(), nullable=True),
        sa.Column("llm_provider", sa.String(length=50), nullable=False),
        sa.Column("llm_model", sa.String(length=100), nullable=False),
        sa.Column("token_cost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_rating", sa.Float(), nullable=True),
        sa.Column("signature", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["syllabus_point_id"], ["syllabus_points.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["generator_student_id"], ["students.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("version >= 1", name="ck_explanation_version_positive"),
        sa.CheckConstraint(
            "quality_rating IS NULL OR (quality_rating >= 0 AND quality_rating <= 5)",
            name="ck_explanation_quality_rating_range",
        ),
        sa.CheckConstraint(
            "(generated_by = 'system' AND generator_student_id IS NULL) OR "
            "(generated_by = 'student' AND generator_student_id IS NOT NULL)",
            name="ck_explanation_generator_consistency",
        ),
    )
    op.create_index(
        "ix_generated_explanations_syllabus_point_id",
        "generated_explanations",
        ["syllabus_point_id"],
    )
    op.create_index(
        "idx_explanation_syllabus_version",
        "generated_explanations",
        ["syllabus_point_id", "version"],
        unique=True,
    )
    op.create_index(
        "idx_explanation_generator",
        "generated_explanations",
        ["generator_student_id"],
        postgresql_where=sa.text("generator_student_id IS NOT NULL"),
    )
    op.create_index(
        "idx_explanation_signature",
        "generated_explanations",
        ["signature"],
    )

    # 4. Create student_learning_paths table
    op.create_table(
        "student_learning_paths",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("syllabus_point_id", sa.UUID(), nullable=False),
        sa.Column("explanation_id", sa.UUID(), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "total_time_spent_seconds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("last_viewed_at", sa.DateTime(), nullable=True),
        sa.Column("preferred_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_bookmarked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "mastery_level",
            sa.String(length=50),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["syllabus_point_id"], ["syllabus_points.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["explanation_id"], ["generated_explanations.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("view_count >= 0", name="ck_learningpath_view_count_positive"),
        sa.CheckConstraint(
            "total_time_spent_seconds >= 0",
            name="ck_learningpath_time_spent_positive",
        ),
        sa.CheckConstraint(
            "preferred_version >= 1",
            name="ck_learningpath_preferred_version_positive",
        ),
    )
    op.create_index(
        "ix_student_learning_paths_student_id",
        "student_learning_paths",
        ["student_id"],
    )
    op.create_index(
        "ix_student_learning_paths_syllabus_point_id",
        "student_learning_paths",
        ["syllabus_point_id"],
    )
    op.create_index(
        "idx_learningpath_student_syllabus",
        "student_learning_paths",
        ["student_id", "syllabus_point_id"],
        unique=True,
    )
    op.create_index(
        "idx_learningpath_student_bookmarked",
        "student_learning_paths",
        ["student_id"],
        postgresql_where=sa.text("is_bookmarked = true"),
    )
    op.create_index(
        "idx_learningpath_student_mastery",
        "student_learning_paths",
        ["student_id", "mastery_level"],
    )


def downgrade() -> None:
    # Drop tables in reverse order (due to FK dependencies)
    op.drop_table("student_learning_paths")
    op.drop_table("generated_explanations")
    op.drop_table("student_llm_configs")

    # Remove is_admin column
    op.drop_column("students", "is_admin")
