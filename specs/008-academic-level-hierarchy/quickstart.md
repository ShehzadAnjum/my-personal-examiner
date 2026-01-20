# Quick Start: Academic Level Hierarchy

**Feature**: 008-academic-level-hierarchy
**Date**: 2026-01-05

---

## Overview

This feature restructures the database from a flat `Subject` model to a three-tier hierarchy:

```
Academic Level → Subject → Syllabus → Syllabus Points
```

---

## Getting Started

### Prerequisites

1. Backend running on `localhost:8000`
2. PostgreSQL database accessible
3. Admin user authenticated

### Running the Migration

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "add_academic_level_hierarchy"

# Run migration
alembic upgrade head
```

### Testing the API

```bash
# List academic levels (empty initially)
curl http://localhost:8000/api/academic-levels

# Create an academic level (requires admin auth)
curl -X POST http://localhost:8000/api/academic-levels \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "A-Level",
    "code": "A",
    "description": "Cambridge International A-Level",
    "exam_board": "Cambridge International"
  }'

# Create a subject under the level
curl -X POST http://localhost:8000/api/academic-levels/<level-id>/subjects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Economics"
  }'

# Create a syllabus for the subject
curl -X POST http://localhost:8000/api/subjects/<subject-id>/syllabi \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "code": "9708",
    "year_range": "2023-2025"
  }'

# Get full hierarchy
curl http://localhost:8000/api/hierarchy
```

---

## Admin Setup Flow

### Step 1: Create Academic Level

Navigate to `/admin/setup/academic-levels` and create your first academic level:

- **Name**: A-Level
- **Code**: A
- **Exam Board**: Cambridge International

### Step 2: Create Subject

Navigate to `/admin/setup/subjects?level_id=<id>` and create a subject:

- **Name**: Economics

### Step 3: Upload Syllabus

Navigate to `/admin/setup/syllabus?subject_id=<id>` and upload:

- **Code**: 9708
- **Year Range**: 2023-2025
- **PDF**: Cambridge syllabus document

---

## Key Files

### Backend

| File | Purpose |
|------|---------|
| `backend/src/models/academic_level.py` | AcademicLevel model |
| `backend/src/models/syllabus.py` | Syllabus model |
| `backend/src/routes/academic_levels.py` | API endpoints |
| `backend/alembic/versions/014_*.py` | Migration script |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/app/(dashboard)/admin/setup/academic-levels/page.tsx` | Step 1 UI |
| `frontend/lib/hooks/useAcademicLevels.ts` | Data fetching hook |
| `frontend/lib/api/academic-levels.ts` | API client |

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/unit/test_academic_level.py -v
pytest tests/integration/test_hierarchy.py -v
```

### Frontend Tests

```bash
cd frontend
pnpm test -- --grep "academic level"
```

---

## Rollback

If you need to rollback:

```bash
cd backend
alembic downgrade -1
```

This will:
1. Restore `subject_id` column on syllabus_points
2. Drop `syllabi` table
3. Drop `academic_levels` table
4. Restore original columns on `subjects`

---

## Common Issues

### Migration fails with FK violation

**Cause**: Existing syllabus_points reference subjects that don't map cleanly.

**Solution**: Run data cleanup script before migration:

```bash
python scripts/prepare_hierarchy_migration.py
```

### "No academic levels configured" shows in UI

**Cause**: Database was reset but new hierarchy not seeded.

**Solution**: Create academic level via admin setup or API.

### Subjects don't appear under level

**Cause**: Subjects not linked to academic_level_id.

**Solution**: Run migration again or manually update:

```sql
UPDATE subjects SET academic_level_id = '<level-uuid>' WHERE academic_level_id IS NULL;
```

---

## Next Steps

After completing this feature:

1. Run `/sp.tasks` to generate task list
2. Implement backend models and routes
3. Create frontend wizard pages
4. Run tests and verify migration
5. Update documentation
