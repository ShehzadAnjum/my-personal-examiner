#!/bin/bash
# =============================================================================
# Reset Script for Admin-First Topic Regeneration
# =============================================================================
# Clears regenerable data while preserving user data.
#
# IMPORTANT: Run backup_before_reset.sh FIRST!
#
# Usage: ./scripts/reset_for_admin_setup.sh
#
# This script will:
# 1. Verify backup exists
# 2. Clear syllabus_points (will regenerate from syllabus)
# 3. Clear generated_explanations v1 (will regenerate by admin)
# 4. Clear syllabus_point_resources (will retag)
# 5. Reset subjects.setup_status to 'pending'
#
# PRESERVED:
# - students (user accounts)
# - student_llm_configs (API keys)
# - resources (uploaded files)
# - saved_explanations (bookmarks)
# - coaching_sessions (tutoring history)
# - attempts, attempted_questions (exam performance)
# - generated_explanations v2+ (student work - archived if unlinked)
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       RESET FOR ADMIN-FIRST TOPIC REGENERATION                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check for backup
BACKUP_DIR="${PROJECT_ROOT}/backups"
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ERROR: No backup found!                                      ║${NC}"
    echo -e "${RED}║                                                               ║${NC}"
    echo -e "${RED}║  Please run backup_before_reset.sh first:                     ║${NC}"
    echo -e "${RED}║    ./scripts/backup_before_reset.sh                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi

LATEST_BACKUP=$(ls -td "$BACKUP_DIR"/*/ 2>/dev/null | head -1)
echo -e "${GREEN}✓ Found backup: ${LATEST_BACKUP}${NC}"
echo ""

# Load environment variables
if [ -f "${PROJECT_ROOT}/backend/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/backend/.env" | xargs)
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
else
    echo -e "${RED}✗ No .env file found. Cannot proceed.${NC}"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}✗ DATABASE_URL not set. Cannot proceed.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL found${NC}"
echo ""

# Confirmation
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  WARNING: This will clear the following data:                 ║${NC}"
echo -e "${YELLOW}║                                                               ║${NC}"
echo -e "${YELLOW}║  - syllabus_points (all rows)                                 ║${NC}"
echo -e "${YELLOW}║  - generated_explanations (v1 only, v2+ archived)             ║${NC}"
echo -e "${YELLOW}║  - syllabus_point_resources (all rows)                        ║${NC}"
echo -e "${YELLOW}║  - subjects.setup_status → 'pending'                          ║${NC}"
echo -e "${YELLOW}║                                                               ║${NC}"
echo -e "${YELLOW}║  User data will be PRESERVED.                                 ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

read -p "Type 'RESET' to confirm: " CONFIRM
if [ "$CONFIRM" != "RESET" ]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Starting reset...${NC}"
echo ""

# =============================================================================
# Step 1: Archive v2+ explanations that will lose their topic links
# =============================================================================
echo -e "${BLUE}[1/5] Archiving v2+ explanations (preserving student work)...${NC}"
psql "$DATABASE_URL" -c "
UPDATE generated_explanations
SET archived = true,
    archive_reason = 'Archived during syllabus reset on $(date +%Y-%m-%d)'
WHERE version > 1
  AND archived = false;
" 2>/dev/null || echo "  (No v2+ explanations to archive)"
echo -e "${GREEN}✓ v2+ explanations archived${NC}"
echo ""

# =============================================================================
# Step 2: Delete v1 explanations (will regenerate by admin)
# =============================================================================
echo -e "${BLUE}[2/5] Deleting v1 explanations (will regenerate)...${NC}"
V1_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM generated_explanations WHERE version = 1;" 2>/dev/null | xargs)
psql "$DATABASE_URL" -c "
DELETE FROM generated_explanations WHERE version = 1;
" 2>/dev/null || echo "  (No v1 explanations to delete)"
echo -e "${GREEN}✓ Deleted ${V1_COUNT:-0} v1 explanations${NC}"
echo ""

# =============================================================================
# Step 3: Clear syllabus_point_resources (will retag after syllabus)
# =============================================================================
echo -e "${BLUE}[3/5] Clearing syllabus_point_resources (will retag)...${NC}"
SPR_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM syllabus_point_resources;" 2>/dev/null | xargs)
psql "$DATABASE_URL" -c "
DELETE FROM syllabus_point_resources;
" 2>/dev/null || echo "  (No mappings to delete)"
echo -e "${GREEN}✓ Deleted ${SPR_COUNT:-0} resource-topic mappings${NC}"
echo ""

# =============================================================================
# Step 4: Clear syllabus_points (will regenerate from uploaded syllabus)
# =============================================================================
echo -e "${BLUE}[4/5] Clearing syllabus_points (will regenerate from syllabus)...${NC}"
SP_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM syllabus_points;" 2>/dev/null | xargs)
psql "$DATABASE_URL" -c "
DELETE FROM syllabus_points;
" 2>/dev/null || echo "  (No topics to delete)"
echo -e "${GREEN}✓ Deleted ${SP_COUNT:-0} syllabus points${NC}"
echo ""

# =============================================================================
# Step 5: Reset subjects.setup_status to 'pending'
# =============================================================================
echo -e "${BLUE}[5/5] Resetting subject setup status to 'pending'...${NC}"
psql "$DATABASE_URL" -c "
UPDATE subjects
SET setup_status = 'pending',
    syllabus_resource_id = NULL;
" 2>/dev/null || echo "  (No subjects to reset)"
echo -e "${GREEN}✓ Subjects reset to pending${NC}"
echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RESET COMPLETE                             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  - v2+ explanations: Archived (preserved)"
echo "  - v1 explanations: Deleted (${V1_COUNT:-0} rows)"
echo "  - Resource mappings: Deleted (${SPR_COUNT:-0} rows)"
echo "  - Syllabus points: Deleted (${SP_COUNT:-0} rows)"
echo "  - Subjects: Reset to 'pending'"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Login as admin"
echo "  2. Go to /admin/setup"
echo "  3. Upload syllabus PDF"
echo "  4. Review and confirm topics"
echo "  5. Generate v1 explanations"
echo ""
echo -e "${GREEN}Backup location: ${LATEST_BACKUP}${NC}"
echo ""
