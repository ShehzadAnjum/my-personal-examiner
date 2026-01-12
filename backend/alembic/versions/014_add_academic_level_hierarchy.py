"""Add academic level hierarchy

Revision ID: 014_academic_level_hierarchy
Revises: 013_add_admin_setup_fields
Create Date: 2026-01-05

Feature: 008-academic-level-hierarchy

This migration restructures the database from a flat Subject model to a three-tier hierarchy:
Academic Level → Subject → Syllabus → Syllabus Point

Changes:
1. Creates academic_levels table (new)
2. Creates syllabi table (new)
3. Adds academic_level_id FK to subjects
4. Adds syllabus_id FK to syllabus_points
5. Migrates existing subject data to new structure
6. Removes deprecated columns from subjects
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "014_academic_level_hierarchy"
down_revision = "013_add_admin_setup_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade: Create hierarchy structure and migrate data
    """
    # 1. Create academic_levels table
    op.create_table(
        "academic_levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(10), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("exam_board", sa.String(100), nullable=False, server_default="Cambridge International"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("idx_academic_levels_code", "academic_levels", ["code"], unique=True)

    # 2. Create syllabi table
    op.create_table(
        "syllabi",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("year_range", sa.String(20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("syllabus_resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["syllabus_resource_id"], ["resources.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_syllabi_subject_id", "syllabi", ["subject_id"])
    op.create_index("idx_syllabi_code", "syllabi", ["code"])

    # 3. Add academic_level_id to subjects (nullable initially for migration)
    op.add_column(
        "subjects",
        sa.Column("academic_level_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 4. Add syllabus_id to syllabus_points (nullable initially for migration)
    op.add_column(
        "syllabus_points",
        sa.Column("syllabus_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 5. Data migration: Create default academic levels from existing subjects
    # This uses raw SQL for efficiency
    op.execute("""
        -- Create academic levels from distinct subject levels
        INSERT INTO academic_levels (id, name, code, exam_board, description, created_at, updated_at)
        SELECT DISTINCT
            gen_random_uuid(),
            CASE
                WHEN level = 'A' THEN 'A-Level'
                WHEN level = 'AS' THEN 'AS-Level'
                ELSE level || '-Level'
            END,
            level,
            COALESCE(exam_board, 'Cambridge International'),
            'Migrated from existing subjects',
            NOW(),
            NOW()
        FROM subjects
        WHERE level IS NOT NULL
        ON CONFLICT (code) DO NOTHING
    """)

    # If no academic levels created (empty subjects table), create default A-Level
    op.execute("""
        INSERT INTO academic_levels (id, name, code, exam_board, description, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            'A-Level',
            'A',
            'Cambridge International',
            'Cambridge International A-Level',
            NOW(),
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM academic_levels WHERE code = 'A')
    """)

    # 6. Update subjects with academic_level_id
    op.execute("""
        UPDATE subjects s
        SET academic_level_id = al.id
        FROM academic_levels al
        WHERE s.level = al.code
    """)

    # 7. Create syllabi from existing subject data
    op.execute("""
        INSERT INTO syllabi (id, subject_id, code, year_range, version, is_active, syllabus_resource_id, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            s.id,
            s.code,
            COALESCE(s.syllabus_year, '2023-2025'),
            1,
            true,
            s.syllabus_resource_id,
            NOW(),
            NOW()
        FROM subjects s
        WHERE s.code IS NOT NULL
    """)

    # 8. Update syllabus_points with syllabus_id
    op.execute("""
        UPDATE syllabus_points sp
        SET syllabus_id = syl.id
        FROM syllabi syl
        JOIN subjects s ON syl.subject_id = s.id
        WHERE sp.subject_id = s.id
    """)

    # 9. Add foreign key constraint for academic_level_id (after data migration)
    # First, handle any orphan subjects (shouldn't happen, but be safe)
    op.execute("""
        UPDATE subjects
        SET academic_level_id = (SELECT id FROM academic_levels WHERE code = 'A' LIMIT 1)
        WHERE academic_level_id IS NULL
    """)

    # Now we can make it NOT NULL and add FK
    op.alter_column("subjects", "academic_level_id", nullable=False)
    op.create_foreign_key(
        "fk_subjects_academic_level_id",
        "subjects",
        "academic_levels",
        ["academic_level_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("idx_subjects_academic_level_id", "subjects", ["academic_level_id"])

    # 10. Add FK for syllabus_id on syllabus_points
    # Handle orphan syllabus_points (shouldn't happen, but be safe)
    op.execute("""
        DELETE FROM syllabus_points WHERE syllabus_id IS NULL
    """)
    op.alter_column("syllabus_points", "syllabus_id", nullable=False)
    op.create_foreign_key(
        "fk_syllabus_points_syllabus_id",
        "syllabus_points",
        "syllabi",
        ["syllabus_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("idx_syllabus_points_syllabus_id", "syllabus_points", ["syllabus_id"])

    # 11. Drop deprecated columns from subjects
    # First drop the FK constraint on syllabus_resource_id
    # Check which constraint name exists (may vary between environments)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_subjects_syllabus_resource') THEN
                ALTER TABLE subjects DROP CONSTRAINT fk_subjects_syllabus_resource;
            ELSIF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'subjects_syllabus_resource_id_fkey') THEN
                ALTER TABLE subjects DROP CONSTRAINT subjects_syllabus_resource_id_fkey;
            END IF;
        END $$;
    """)

    # Keep subject_id on syllabus_points for now (for backward compatibility)
    # We'll keep both FKs during transition

    op.drop_column("subjects", "code")
    op.drop_column("subjects", "level")
    op.drop_column("subjects", "exam_board")
    op.drop_column("subjects", "syllabus_year")
    op.drop_column("subjects", "syllabus_resource_id")

    # Note: We keep subject_id on syllabus_points for backward compatibility
    # It can be removed in a future migration after all code is updated


def downgrade() -> None:
    """
    Downgrade: Restore flat structure
    """
    # 1. Add back columns to subjects
    op.add_column("subjects", sa.Column("code", sa.String(10), nullable=True))
    op.add_column("subjects", sa.Column("level", sa.String(10), nullable=True))
    op.add_column("subjects", sa.Column("exam_board", sa.String(50), nullable=True))
    op.add_column("subjects", sa.Column("syllabus_year", sa.String(20), nullable=True))
    op.add_column("subjects", sa.Column("syllabus_resource_id", postgresql.UUID(as_uuid=True), nullable=True))

    # 2. Restore data from syllabi and academic_levels
    op.execute("""
        UPDATE subjects s
        SET
            code = syl.code,
            level = al.code,
            exam_board = al.exam_board,
            syllabus_year = syl.year_range,
            syllabus_resource_id = syl.syllabus_resource_id
        FROM syllabi syl
        JOIN academic_levels al ON s.academic_level_id = al.id
        WHERE syl.subject_id = s.id AND syl.is_active = true
    """)

    # 3. Make columns NOT NULL
    op.alter_column("subjects", "code", nullable=False)
    op.alter_column("subjects", "level", nullable=False)
    op.alter_column("subjects", "syllabus_year", nullable=False)

    # 4. Drop FK and index on subjects.academic_level_id
    op.drop_index("idx_subjects_academic_level_id", table_name="subjects")
    op.drop_constraint("fk_subjects_academic_level_id", "subjects", type_="foreignkey")
    op.drop_column("subjects", "academic_level_id")

    # 5. Drop FK and index on syllabus_points.syllabus_id
    op.drop_index("idx_syllabus_points_syllabus_id", table_name="syllabus_points")
    op.drop_constraint("fk_syllabus_points_syllabus_id", "syllabus_points", type_="foreignkey")
    op.drop_column("syllabus_points", "syllabus_id")

    # 6. Drop syllabi table
    op.drop_index("idx_syllabi_code", table_name="syllabi")
    op.drop_index("idx_syllabi_subject_id", table_name="syllabi")
    op.drop_table("syllabi")

    # 7. Drop academic_levels table
    op.drop_index("idx_academic_levels_code", table_name="academic_levels")
    op.drop_table("academic_levels")

    # 8. Add back FK for syllabus_resource_id (use original constraint name)
    op.create_foreign_key(
        "fk_subjects_syllabus_resource",
        "subjects",
        "resources",
        ["syllabus_resource_id"],
        ["id"],
        ondelete="SET NULL",
    )
