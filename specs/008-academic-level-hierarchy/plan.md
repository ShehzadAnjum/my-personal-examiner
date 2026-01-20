# Implementation Plan: Academic Level Hierarchy

**Branch**: `008-academic-level-hierarchy` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-academic-level-hierarchy/spec.md`

---

## Summary

Restructure the database from a flat `Subject` model to a three-tier hierarchy: **Academic Level → Subject → Syllabus**. This enables the system to support multiple qualification types (A-Level, O-Level, IGCSE, IB) without being Cambridge-specific. Syllabus points will be linked to syllabi instead of subjects.

---

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5.7+
**Primary Dependencies**: FastAPI 0.115+, SQLModel, Next.js 16+, React 19, TanStack Query 5.62+
**Storage**: PostgreSQL 16 (Neon Serverless)
**Testing**: pytest 8.3+ (backend), Jest 29+ (frontend)
**Target Platform**: Web application (Vercel deployment)
**Project Type**: Web (backend + frontend)
**Performance Goals**: API response <200ms, page load <2s
**Constraints**: Multi-tenant data isolation, backward compatibility with existing data
**Scale/Scope**: Single-user MVP, 1 admin, extensible to multiple academic levels

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I: Subject Accuracy | ✅ PASS | Hierarchy enables accurate mapping to Cambridge structure |
| III: Syllabus Sync | ✅ PASS | Syllabus entity now has dedicated version tracking |
| IV: Spec-Driven | ✅ PASS | Spec created via /sp.specify, plan via /sp.plan |
| V: Multi-Tenant Isolation | ✅ PASS | Global entities (not student-scoped), no isolation change |
| VII: Phase Boundaries | ✅ PASS | Feature scoped, includes migration strategy |
| IX: SpecKitPlus | ✅ PASS | Following /sp.* workflow |
| XIV: UI Discoverability | ✅ PASS | Admin setup wizard will have clickable navigation |

**Gate Result**: PASSED - No violations

---

## Project Structure

### Documentation (this feature)

```text
specs/008-academic-level-hierarchy/
├── plan.md              # This file
├── research.md          # Phase 0: Best practices research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Quick start guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml     # OpenAPI schema
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── academic_level.py      # NEW: Academic level model
│   │   ├── subject.py             # MODIFY: Remove level/exam_board, add FK
│   │   ├── syllabus.py            # NEW: Syllabus model
│   │   └── syllabus_point.py      # MODIFY: Change FK from subject to syllabus
│   ├── routes/
│   │   ├── academic_levels.py     # NEW: CRUD endpoints
│   │   ├── subjects.py            # MODIFY: Scoped to academic level
│   │   └── admin_setup.py         # MODIFY: Three-step wizard
│   └── services/
│       └── hierarchy_service.py   # NEW: Hierarchy management
└── alembic/
    └── versions/
        └── 014_add_academic_level_hierarchy.py  # Migration

frontend/
├── app/(dashboard)/
│   ├── admin/
│   │   └── setup/
│   │       ├── academic-levels/   # NEW: Step 1 - Academic level creation
│   │       ├── subjects/          # MODIFY: Step 2 - Subject under level
│   │       └── syllabus/          # MODIFY: Step 3 - Syllabus for subject
│   └── teaching/
│       └── page.tsx               # MODIFY: Show hierarchy breadcrumb
├── components/
│   └── admin/
│       └── HierarchySelector.tsx  # NEW: Dropdown chain component
└── lib/
    ├── api/
    │   └── academic-levels.ts     # NEW: API client
    └── hooks/
        ├── useAcademicLevels.ts   # NEW: Fetch hook
        └── useSubjects.ts         # MODIFY: Accept academic_level_id filter
```

**Structure Decision**: Web application pattern (backend + frontend). No new directories needed beyond creating new model/route/component files within existing structure.

---

## Complexity Tracking

> No violations requiring justification. Schema change is straightforward migration.

---

## Migration Strategy

### Data Transformation

1. **Create AcademicLevel table** with default "A-Level" (code="A", exam_board="Cambridge International")
2. **Create Syllabus table** - move `code`, `syllabus_year` from Subject
3. **Update Subject** - add `academic_level_id` FK, keep `name` only
4. **Update SyllabusPoint** - change FK from `subject_id` to `syllabus_id`
5. **Migrate existing data**:
   - Extract unique (code, syllabus_year, exam_board) → create Syllabus records
   - Link SyllabusPoints to new Syllabus records
   - Update Subject to reference AcademicLevel

### Rollback Plan

- Migration includes `downgrade()` function
- Data backup required before running migration
- Can revert by removing FKs and restoring original columns

---

## API Design Overview

### New Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/academic-levels` | List all academic levels |
| POST | `/api/academic-levels` | Create academic level (admin) |
| GET | `/api/academic-levels/{id}` | Get level with subjects |
| PUT | `/api/academic-levels/{id}` | Update level (admin) |
| DELETE | `/api/academic-levels/{id}` | Delete level if empty (admin) |
| GET | `/api/academic-levels/{id}/subjects` | List subjects under level |
| POST | `/api/academic-levels/{id}/subjects` | Create subject under level |
| GET | `/api/subjects/{id}/syllabi` | List syllabi for subject |
| POST | `/api/subjects/{id}/syllabi` | Create syllabus (admin upload) |

### Modified Endpoints

| Endpoint | Change |
|----------|--------|
| `GET /api/subjects` | Add `?academic_level_id=` filter |
| `POST /api/admin/setup/upload-syllabus` | Associate with subject, not create subject |
| `GET /api/topics` | Accept `syllabus_id` instead of `subject_code` |

---

## Frontend UI Flow

### Admin Setup Wizard (Updated)

```
Step 1: Academic Level
┌────────────────────────────────────────┐
│ Create Academic Level                   │
│                                         │
│ Name: [A-Level              ]           │
│ Code: [A                    ]           │
│ Exam Board: [Cambridge International]   │
│ Description: [Advanced Level...]        │
│                                         │
│ [Cancel] [Create & Next →]              │
└────────────────────────────────────────┘

Step 2: Subject
┌────────────────────────────────────────┐
│ Create Subject under A-Level            │
│                                         │
│ Name: [Economics            ]           │
│                                         │
│ [← Back] [Create & Next →]              │
└────────────────────────────────────────┘

Step 3: Syllabus Upload
┌────────────────────────────────────────┐
│ Upload Syllabus for Economics           │
│                                         │
│ Code: [9708                 ]           │
│ Year Range: [2023-2025      ]           │
│ PDF: [Choose file...        ]           │
│                                         │
│ [← Back] [Upload & Extract Topics]      │
└────────────────────────────────────────┘
```

### Teaching Page Header

```
Before: "PhD-Level Economics Explanations"
After:  "PhD-Level A-Level > Economics > 9708 Explanations"
        (with breadcrumb navigation)
```

### Empty State

```
When no academic levels:
┌────────────────────────────────────────┐
│         No Academic Levels             │
│                                         │
│ Create your first academic level to    │
│ start organizing subjects.              │
│                                         │
│ [Create Academic Level →]               │
└────────────────────────────────────────┘
```

---

## Research Questions (Phase 0)

1. **Best pattern for hierarchical data in SQLModel** - Adjacency list vs nested sets
2. **Cascade delete behavior** - What happens when deleting academic level with subjects?
3. **Backward compatibility** - How to handle existing syllabus_points FKs during migration?
4. **Frontend routing** - Best pattern for multi-step wizard state management

---

## Success Criteria (from spec)

- [ ] SC-001: Admin can create hierarchy in under 5 minutes
- [ ] SC-002: All hardcoded "Economics 9708" references removed
- [ ] SC-003: "No academic levels configured" state displays correctly
- [ ] SC-004: Existing data continues to work after migration
- [ ] SC-005: Setup wizard guides through 3-step creation
- [ ] SC-006: Breadcrumbs show full hierarchy

---

## Files to Create/Modify

### Backend (New)
- `backend/src/models/academic_level.py`
- `backend/src/models/syllabus.py`
- `backend/src/routes/academic_levels.py`
- `backend/src/services/hierarchy_service.py`
- `backend/alembic/versions/014_add_academic_level_hierarchy.py`

### Backend (Modify)
- `backend/src/models/subject.py`
- `backend/src/models/syllabus_point.py`
- `backend/src/models/__init__.py`
- `backend/src/routes/admin_setup.py`
- `backend/src/routes/subjects.py`
- `backend/src/routes/teaching.py`

### Frontend (New)
- `frontend/app/(dashboard)/admin/setup/academic-levels/page.tsx`
- `frontend/components/admin/HierarchySelector.tsx`
- `frontend/lib/api/academic-levels.ts`
- `frontend/lib/hooks/useAcademicLevels.ts`

### Frontend (Modify)
- `frontend/app/(dashboard)/teaching/page.tsx`
- `frontend/app/(dashboard)/admin/page.tsx`
- `frontend/components/layout/DashboardHeader.tsx`
- `frontend/components/teaching/TopicBrowser.tsx`
- `frontend/lib/hooks/useSubjects.ts`

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Migration corrupts data | Low | High | Full backup before migration, test on dev first |
| FK constraint violations | Medium | Medium | Careful ordering in migration, rollback plan |
| UI breaks during transition | Low | Medium | Feature flag, gradual rollout |
| Performance regression | Low | Low | Add indexes on new FKs |

---

## Estimated Effort

| Phase | Tasks | Complexity |
|-------|-------|------------|
| Phase 0: Research | 4 questions | Low |
| Phase 1: Data Model | 2 new models, 2 modified | Medium |
| Phase 2: API Contracts | 9 new endpoints | Medium |
| Phase 3: Migration | 1 migration script | Medium |
| Phase 4: Backend | Routes, services | Medium |
| Phase 5: Frontend | Wizard pages, components | Medium |
| Phase 6: Testing | Unit + integration | Medium |

**Total**: ~40-50 tasks estimated
