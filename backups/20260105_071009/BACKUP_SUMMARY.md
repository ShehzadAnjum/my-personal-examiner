# Backup Summary

**Created**: Mon Jan  5 07:10:09 PKT 2026
**Timestamp**: 20260105_071009
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
```bash
psql "$DATABASE_URL" < "/home/anjum/dev/my_personal_examiner/backups/20260105_071009/full_database.sql"
```

## Notes
- Run localStorage backup in browser BEFORE clearing frontend cache
- Keep this backup until new setup is verified working
