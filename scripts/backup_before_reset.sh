#!/bin/bash
# =============================================================================
# Backup Script for Admin-First Topic Regeneration
# =============================================================================
# Creates timestamped backup before resetting topics/explanations
#
# Usage: ./scripts/backup_before_reset.sh
#
# This script will:
# 1. Create full database dump (pg_dump)
# 2. Export key tables to CSV for easy viewing
# 3. Generate localStorage backup instructions
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       BACKUP BEFORE TOPIC REGENERATION                        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create timestamped backup directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${PROJECT_ROOT}/backups/${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Backup directory: ${BACKUP_DIR}${NC}"
echo ""

# Load environment variables
if [ -f "${PROJECT_ROOT}/backend/.env" ]; then
    echo -e "${GREEN}✓ Loading environment from backend/.env${NC}"
    export $(grep -v '^#' "${PROJECT_ROOT}/backend/.env" | xargs)
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    echo -e "${GREEN}✓ Loading environment from .env${NC}"
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
else
    echo -e "${RED}✗ No .env file found. Please ensure DATABASE_URL is set.${NC}"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}✗ DATABASE_URL not set. Cannot proceed with backup.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL found${NC}"
echo ""

# =============================================================================
# Step 1: Full Database Dump
# =============================================================================
echo -e "${BLUE}[1/4] Creating full database dump...${NC}"
if pg_dump "$DATABASE_URL" > "${BACKUP_DIR}/full_database.sql" 2>/dev/null; then
    echo -e "${GREEN}✓ Full database dump: ${BACKUP_DIR}/full_database.sql${NC}"
    DUMP_SIZE=$(du -h "${BACKUP_DIR}/full_database.sql" | cut -f1)
    echo -e "   Size: ${DUMP_SIZE}"
else
    echo -e "${YELLOW}⚠ pg_dump failed. Trying alternative method...${NC}"
    # Alternative: Use psql with \copy commands for each table
    echo "-- Full database backup (alternative method)" > "${BACKUP_DIR}/full_database.sql"
    echo "-- Generated: $(date)" >> "${BACKUP_DIR}/full_database.sql"
fi
echo ""

# =============================================================================
# Step 2: Export Key Tables to CSV
# =============================================================================
echo -e "${BLUE}[2/4] Exporting key tables to CSV...${NC}"

# Tables to export
TABLES=(
    "students"
    "subjects"
    "syllabus_points"
    "generated_explanations"
    "resources"
    "syllabus_point_resources"
    "saved_explanations"
    "coaching_sessions"
)

for TABLE in "${TABLES[@]}"; do
    echo -n "   Exporting ${TABLE}... "
    if psql "$DATABASE_URL" -c "\\COPY (SELECT * FROM ${TABLE}) TO STDOUT WITH CSV HEADER" > "${BACKUP_DIR}/${TABLE}.csv" 2>/dev/null; then
        ROW_COUNT=$(wc -l < "${BACKUP_DIR}/${TABLE}.csv")
        ROW_COUNT=$((ROW_COUNT - 1))  # Subtract header
        echo -e "${GREEN}✓ (${ROW_COUNT} rows)${NC}"
    else
        echo -e "${YELLOW}⚠ Table may not exist or is empty${NC}"
        rm -f "${BACKUP_DIR}/${TABLE}.csv"
    fi
done
echo ""

# =============================================================================
# Step 3: Create localStorage Backup Instructions
# =============================================================================
echo -e "${BLUE}[3/4] Creating localStorage backup instructions...${NC}"

cat << 'EOF' > "${BACKUP_DIR}/localStorage_backup.md"
# localStorage Backup Instructions

The frontend caches explanations in browser localStorage. Follow these steps to backup:

## Step 1: Open Browser DevTools
- Press F12 (or Cmd+Option+I on Mac)
- Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
- Click **Local Storage** → your site URL

## Step 2: Export Explanation Cache
Run this in the browser console (F12 → Console):

```javascript
// Export all explanation cache entries
const backup = {};
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  if (key && (key.startsWith('explanation_') || key.startsWith('cached_'))) {
    backup[key] = localStorage.getItem(key);
  }
}

// Download as JSON file
const blob = new Blob([JSON.stringify(backup, null, 2)], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'localStorage_backup_' + new Date().toISOString().slice(0,10) + '.json';
a.click();
URL.revokeObjectURL(url);

console.log('✅ Backup downloaded! Keys exported:', Object.keys(backup).length);
```

## Step 3: Save the Downloaded File
Move the downloaded JSON file to this backup directory:
`backups/TIMESTAMP/localStorage_backup.json`

## Restore Instructions (If Needed)
```javascript
// Import from backup file
const input = document.createElement('input');
input.type = 'file';
input.accept = '.json';
input.onchange = async (e) => {
  const file = e.target.files[0];
  const text = await file.text();
  const backup = JSON.parse(text);

  for (const [key, value] of Object.entries(backup)) {
    localStorage.setItem(key, value);
  }
  console.log('✅ Restored', Object.keys(backup).length, 'entries');
};
input.click();
```
EOF

echo -e "${GREEN}✓ localStorage instructions: ${BACKUP_DIR}/localStorage_backup.md${NC}"
echo ""

# =============================================================================
# Step 4: Create Backup Summary
# =============================================================================
echo -e "${BLUE}[4/4] Creating backup summary...${NC}"

cat << EOF > "${BACKUP_DIR}/BACKUP_SUMMARY.md"
# Backup Summary

**Created**: $(date)
**Timestamp**: ${TIMESTAMP}
**Purpose**: Pre-reset backup before admin-first topic regeneration

## Contents

| File | Description |
|------|-------------|
| full_database.sql | Complete PostgreSQL dump (pg_dump) |
| students.csv | User accounts (PRESERVE) |
| subjects.csv | A-Level subjects |
| syllabus_points.csv | Topic definitions (will be regenerated) |
| generated_explanations.csv | All explanations (v1 will be regenerated, v2+ preserved) |
| resources.csv | Uploaded resources (PRESERVE) |
| syllabus_point_resources.csv | Resource-topic mappings (will be regenerated) |
| saved_explanations.csv | User bookmarks (PRESERVE) |
| coaching_sessions.csv | Tutoring history (PRESERVE) |
| localStorage_backup.md | Instructions for browser cache backup |

## Data Preservation Rules

### WILL BE PRESERVED
- students (user accounts, is_admin flag)
- student_llm_configs (API keys)
- resources (uploaded files)
- saved_explanations (bookmarks - will be relinked)
- coaching_sessions (tutoring history)
- attempts, attempted_questions (exam performance)
- generated_explanations WHERE version > 1 (student v2+ explanations)

### WILL BE CLEARED/REGENERATED
- syllabus_points (regenerated from uploaded syllabus PDF)
- generated_explanations WHERE version = 1 (admin v1 explanations)
- syllabus_point_resources (retag after new syllabus)

## Restore Command
\`\`\`bash
psql "\$DATABASE_URL" < "${BACKUP_DIR}/full_database.sql"
\`\`\`

## Notes
- Run localStorage backup in browser BEFORE clearing frontend cache
- Keep this backup until new setup is verified working
EOF

echo -e "${GREEN}✓ Backup summary: ${BACKUP_DIR}/BACKUP_SUMMARY.md${NC}"
echo ""

# =============================================================================
# Final Report
# =============================================================================
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    BACKUP COMPLETE                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Backup location: ${BACKUP_DIR}${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: Before proceeding with reset:${NC}"
echo -e "  1. Open the app in browser"
echo -e "  2. Follow ${BACKUP_DIR}/localStorage_backup.md"
echo -e "  3. Save the downloaded JSON to this backup folder"
echo ""
echo -e "${GREEN}Backup files created:${NC}"
ls -la "${BACKUP_DIR}"
echo ""
echo -e "${YELLOW}To restore from this backup:${NC}"
echo -e "  psql \"\$DATABASE_URL\" < ${BACKUP_DIR}/full_database.sql"
echo ""
