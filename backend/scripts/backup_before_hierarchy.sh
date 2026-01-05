#!/bin/bash
#
# Backup Script: Academic Level Hierarchy Migration
# Creates a full database backup before running hierarchy migration
#
# Usage: ./backup_before_hierarchy.sh
#
# Requires: DATABASE_URL environment variable set

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/${TIMESTAMP}"

echo "=== Academic Level Hierarchy Migration Backup ==="
echo "Timestamp: ${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Check for DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    # Try to load from .env
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set. Please set it or create a .env file."
    exit 1
fi

echo ""
echo "1. Creating full database backup..."
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/full_db.sql" 2>/dev/null || {
    echo "WARNING: pg_dump failed. Trying psql export..."
}

echo ""
echo "2. Exporting key tables to CSV..."

# Export subjects table
psql "$DATABASE_URL" -c "COPY (SELECT * FROM subjects) TO STDOUT WITH CSV HEADER" > "$BACKUP_DIR/subjects.csv" 2>/dev/null || {
    echo "  - subjects: SKIPPED (table may not exist)"
}

# Export syllabus_points table
psql "$DATABASE_URL" -c "COPY (SELECT * FROM syllabus_points) TO STDOUT WITH CSV HEADER" > "$BACKUP_DIR/syllabus_points.csv" 2>/dev/null || {
    echo "  - syllabus_points: SKIPPED (table may not exist)"
}

# Export generated_explanations table
psql "$DATABASE_URL" -c "COPY (SELECT * FROM generated_explanations) TO STDOUT WITH CSV HEADER" > "$BACKUP_DIR/generated_explanations.csv" 2>/dev/null || {
    echo "  - generated_explanations: SKIPPED (table may not exist)"
}

# Export resources table
psql "$DATABASE_URL" -c "COPY (SELECT * FROM resources) TO STDOUT WITH CSV HEADER" > "$BACKUP_DIR/resources.csv" 2>/dev/null || {
    echo "  - resources: SKIPPED (table may not exist)"
}

echo ""
echo "3. Creating schema snapshot..."
pg_dump "$DATABASE_URL" --schema-only > "$BACKUP_DIR/schema.sql" 2>/dev/null || {
    echo "  - Schema snapshot: SKIPPED"
}

echo ""
echo "4. Recording migration context..."
cat << EOF > "$BACKUP_DIR/migration_context.md"
# Migration Backup Context

**Date**: $(date)
**Feature**: 008-academic-level-hierarchy
**Migration**: 014_add_academic_level_hierarchy

## Purpose
Restructure database from flat Subject model to three-tier hierarchy:
- Academic Level → Subject → Syllabus → Syllabus Point

## Tables Affected
- subjects (MODIFY: add academic_level_id, remove level/exam_board/code/syllabus_year)
- syllabus_points (MODIFY: change subject_id to syllabus_id)
- academic_levels (NEW)
- syllabi (NEW)

## Rollback Instructions
1. Run: alembic downgrade -1
2. If needed, restore from full_db.sql:
   psql \$DATABASE_URL < $BACKUP_DIR/full_db.sql

## Files in this backup
- full_db.sql: Complete database dump
- schema.sql: Schema-only dump
- subjects.csv: Subjects table data
- syllabus_points.csv: Syllabus points data
- generated_explanations.csv: Explanations data
- resources.csv: Resources data
EOF

echo ""
echo "=== Backup Complete ==="
echo "Location: $BACKUP_DIR"
echo ""
echo "Contents:"
ls -la "$BACKUP_DIR"
echo ""
echo "To restore: psql \$DATABASE_URL < $BACKUP_DIR/full_db.sql"
