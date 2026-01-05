# Tasks: Academic Level Hierarchy

**Feature**: 008-academic-level-hierarchy
**Generated**: 2026-01-05
**Source**: spec.md, plan.md, data-model.md, contracts/openapi.yaml

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 47 |
| User Stories | 5 |
| Parallelizable | 18 |
| Setup/Foundation | 12 |
| MVP Scope | US1 + US2 + US3 (P1 stories) |

---

## Phase 1: Setup (Foundation)

**Goal**: Initialize project structure and database migration infrastructure

- [x] T001 Create database backup script in backend/scripts/backup_before_hierarchy.sh
- [x] T002 [P] Create AcademicLevel model in backend/src/models/academic_level.py
- [x] T003 [P] Create Syllabus model in backend/src/models/syllabus.py
- [x] T004 [P] Create Pydantic schemas in backend/src/schemas/academic_level_schemas.py
- [x] T005 [P] Create Pydantic schemas in backend/src/schemas/syllabus_schemas.py
- [x] T006 Update model exports in backend/src/models/__init__.py

---

## Phase 2: Database Migration (Foundational - Blocking)

**Goal**: Migrate database schema from flat Subject to three-tier hierarchy
**Blocker**: Must complete before any user story implementation

- [x] T007 Create Alembic migration 014_add_academic_level_hierarchy.py in backend/alembic/versions/
- [x] T008 Modify Subject model: add academic_level_id FK, remove level/exam_board in backend/src/models/subject.py
- [x] T009 Modify SyllabusPoint model: change subject_id to syllabus_id FK in backend/src/models/syllabus_point.py
- [x] T010 Update schema exports in backend/src/schemas/__init__.py
- [x] T011 Run and verify migration with alembic upgrade head
- [x] T012 Create seed data script for default academic levels in backend/scripts/seed_academic_levels.py

---

## Phase 3: User Story 1 - Admin Creates Academic Level (P1)

**Goal**: Admin can create academic levels (like "A-Level", "IGCSE") to organize subjects
**Independent Test**: Create academic level via API, verify it appears in list
**Dependencies**: Phase 2 complete

### Backend Implementation

- [x] T013 [US1] Create hierarchy_service.py with create_academic_level() in backend/src/services/hierarchy_service.py
- [x] T014 [US1] Add list_academic_levels() to hierarchy_service.py in backend/src/services/hierarchy_service.py
- [x] T015 [US1] Add get_academic_level() to hierarchy_service.py in backend/src/services/hierarchy_service.py
- [x] T016 [P] [US1] Create academic_levels router with GET /api/academic-levels in backend/src/routes/academic_levels.py
- [x] T017 [P] [US1] Add POST /api/academic-levels endpoint (admin only) in backend/src/routes/academic_levels.py
- [x] T018 [P] [US1] Add GET /api/academic-levels/{id} endpoint in backend/src/routes/academic_levels.py
- [x] T019 [US1] Register academic_levels router in backend/src/main.py

### Frontend Implementation

- [x] T020 [P] [US1] Create academic-levels API client in frontend/lib/api/academic-levels.ts
- [x] T021 [P] [US1] Create useAcademicLevels hook in frontend/lib/hooks/useAcademicLevels.ts
- [x] T022 [US1] Create academic levels list page in frontend/app/(dashboard)/admin/setup/academic-levels/page.tsx
- [ ] T023 [US1] Add "No academic levels" empty state to teaching page in frontend/app/(dashboard)/teaching/page.tsx (DEFERRED to US4)
- [x] T024 [US1] Update admin dashboard to show academic levels count in frontend/app/(dashboard)/admin/page.tsx

### Acceptance Verification

- [ ] T025 [US1] Verify: Admin can create academic level with name/code via UI
- [ ] T026 [US1] Verify: Duplicate code prevention works (409 error)
- [ ] T027 [US1] Verify: Academic levels list displays with subject counts

---

## Phase 4: User Story 2 - Admin Creates Subject Under Academic Level (P1)

**Goal**: Admin can create subjects under a specific academic level
**Independent Test**: Select academic level, create subject, verify it appears under that level
**Dependencies**: US1 complete

### Backend Implementation

- [x] T028 [US2] Add create_subject_for_level() to hierarchy_service.py in backend/src/services/hierarchy_service.py (done in Phase 3)
- [x] T029 [US2] Add list_subjects_for_level() to hierarchy_service.py in backend/src/services/hierarchy_service.py (done in Phase 3)
- [x] T030 [P] [US2] Add GET /api/academic-levels/{id}/subjects endpoint in backend/src/routes/academic_levels.py (done in Phase 3)
- [x] T031 [P] [US2] Add POST /api/academic-levels/{id}/subjects endpoint in backend/src/routes/academic_levels.py (done in Phase 3)
- [x] T032 [US2] Update GET /api/subjects to accept ?academic_level_id filter in backend/src/routes/subjects.py

### Frontend Implementation

- [x] T033 [US2] Update useSubjects hook to accept academic_level_id filter in frontend/lib/hooks/useSubjects.ts
- [x] T034 [US2] Create subject creation page under academic level in frontend/app/(dashboard)/admin/setup/subjects/page.tsx
- [x] T035 [P] [US2] Create HierarchySelector component (level dropdown) in frontend/components/admin/HierarchySelector.tsx

### Acceptance Verification

- [ ] T036 [US2] Verify: Admin can create subject under selected academic level
- [ ] T037 [US2] Verify: Duplicate subject name under same level prevented
- [ ] T038 [US2] Verify: Academic level detail shows all subjects

---

## Phase 5: User Story 3 - Admin Uploads Syllabus for Subject (P1)

**Goal**: Admin can upload syllabus PDF for a specific subject
**Independent Test**: Select subject, upload syllabus with code/year, verify topics extracted
**Dependencies**: US2 complete

### Backend Implementation

- [x] T039 [US3] Add create_syllabus_for_subject() to hierarchy_service.py in backend/src/services/hierarchy_service.py
- [x] T040 [US3] Add list_syllabi_for_subject() to hierarchy_service.py in backend/src/services/hierarchy_service.py
- [x] T041 [P] [US3] Add GET /api/subjects/{id}/syllabi endpoint in backend/src/routes/subjects.py
- [x] T042 [P] [US3] Add POST /api/subjects/{id}/syllabi endpoint in backend/src/routes/subjects.py
- [x] T043 [US3] Update admin_setup.py to use new hierarchy (subject → syllabus) in backend/src/routes/admin_setup.py

### Frontend Implementation

- [x] T044 [US3] Update syllabus upload page to select subject first in frontend/app/(dashboard)/admin/setup/syllabus/page.tsx
- [x] T045 [US3] Add syllabus list to subject detail view in frontend components

### Acceptance Verification

- [ ] T046 [US3] Verify: Admin can upload syllabus with code/year_range
- [ ] T047 [US3] Verify: Syllabus appears under subject with topic count

---

## Phase 6: User Story 4 - Student Navigates Hierarchy (P2)

**Goal**: Students see content organized by hierarchy in teaching page
**Independent Test**: View teaching page, see breadcrumb with academic level > subject > syllabus
**Dependencies**: US3 complete (content exists)

### Backend Implementation

- [x] T048 [US4] Add GET /api/hierarchy endpoint for full tree in backend/src/routes/academic_levels.py
- [x] T049 [US4] Update GET /api/topics to accept syllabus_id parameter in backend/src/routes/syllabus.py

### Frontend Implementation

- [x] T050 [US4] Update teaching page to show hierarchy breadcrumb in frontend/app/(dashboard)/teaching/page.tsx
- [x] T051 [US4] Update DashboardHeader to show dynamic hierarchy in frontend/components/layout/DashboardHeader.tsx
- [x] T052 [US4] Update TopicBrowser to accept syllabus context in frontend/components/teaching/TopicBrowser.tsx

### Acceptance Verification

- [ ] T053 [US4] Verify: Teaching page shows "A-Level > Economics > 9708" breadcrumb
- [ ] T054 [US4] Verify: Header shows dynamic subject from hierarchy

---

## Phase 7: User Story 5 - Admin Manages Hierarchy (P3)

**Goal**: Admin can edit and delete academic levels and subjects
**Independent Test**: Edit academic level name, verify change persists
**Dependencies**: US1, US2 complete

### Backend Implementation

- [x] T055 [US5] Add update_academic_level() to hierarchy_service.py in backend/src/services/hierarchy_service.py
- [x] T056 [US5] Add delete_academic_level() with RESTRICT check in backend/src/services/hierarchy_service.py
- [x] T057 [P] [US5] Add PUT /api/academic-levels/{id} endpoint in backend/src/routes/academic_levels.py
- [x] T058 [P] [US5] Add DELETE /api/academic-levels/{id} endpoint in backend/src/routes/academic_levels.py

### Frontend Implementation

- [x] T059 [US5] Add edit modal to academic levels page in frontend/app/(dashboard)/admin/setup/academic-levels/page.tsx
- [x] T060 [US5] Add delete button with confirmation dialog in frontend components

### Acceptance Verification

- [ ] T061 [US5] Verify: Admin can edit academic level name
- [ ] T062 [US5] Verify: Delete prevented when level has subjects (400 error)
- [ ] T063 [US5] Verify: Delete works when level is empty

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Remove hardcoded references, ensure backward compatibility

- [x] T064 Remove all hardcoded "Economics 9708" strings from frontend components
- [x] T065 Update localStorage cache keys to include hierarchy context in frontend/lib/hooks/useTopics.ts
- [x] T066 Add cache invalidation when hierarchy changes in frontend/app/(dashboard)/admin/page.tsx
- [x] T067 Update admin setup wizard to follow 3-step flow (Level → Subject → Syllabus)

---

## Dependencies Graph

```
Phase 1: Setup
    │
    ▼
Phase 2: Migration (BLOCKING)
    │
    ▼
Phase 3: US1 - Create Academic Level
    │
    ├───────────────────────────┐
    ▼                           ▼
Phase 4: US2 - Create Subject   Phase 7: US5 - Manage (partial)
    │
    ▼
Phase 5: US3 - Upload Syllabus
    │
    ├───────────────────────────┐
    ▼                           ▼
Phase 6: US4 - Navigation       Phase 7: US5 - Manage (full)
    │
    ▼
Phase 8: Polish
```

---

## Parallel Execution Opportunities

### Within Phase 1 (Setup)
```
T002 (AcademicLevel model) ║ T003 (Syllabus model) ║ T004 (AL schemas) ║ T005 (Syllabus schemas)
```

### Within Phase 3 (US1)
```
T016 (GET /levels) ║ T017 (POST /levels) ║ T018 (GET /levels/{id})
T020 (API client) ║ T021 (useAcademicLevels hook)
```

### Within Phase 4 (US2)
```
T030 (GET subjects) ║ T031 (POST subjects) ║ T035 (HierarchySelector)
```

### Within Phase 5 (US3)
```
T041 (GET syllabi) ║ T042 (POST syllabi)
```

### Within Phase 7 (US5)
```
T057 (PUT level) ║ T058 (DELETE level)
```

---

## MVP Scope (Recommended)

**Phases 1-5 (US1 + US2 + US3)** deliver core value:
- Admin can create complete hierarchy
- Database properly restructured
- Setup wizard guides through 3 steps

**Defer to next iteration**:
- Phase 6 (US4): Student navigation enhancements
- Phase 7 (US5): Edit/delete management
- Phase 8: Polish

---

## Implementation Strategy

1. **Start with migration** (Phase 2) - most risk, earliest feedback
2. **Implement vertically** - complete each user story end-to-end before moving to next
3. **Test independently** - each story has clear acceptance criteria
4. **Parallel where possible** - multiple developers can work on different routes/components
5. **Defer polish** - hardcoded string removal can happen last

---

## Success Criteria Mapping

| Success Criterion | Tasks |
|-------------------|-------|
| SC-001: Hierarchy in <5 min | T022, T034, T044, T067 |
| SC-002: No hardcoded "Economics 9708" | T064 |
| SC-003: Empty state displayed | T023 |
| SC-004: Backward compatibility | T007, T009, T011 |
| SC-005: 3-step wizard | T067 |
| SC-006: Breadcrumb navigation | T050, T051 |
