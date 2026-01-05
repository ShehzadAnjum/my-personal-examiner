# Tasks: Resource Bank

**Input**: Design documents from `/specs/006-resource-bank/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Branch**: `006-resource-bank`
**Date**: 2025-12-26

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment setup, and shared dependencies

- [x] T001 Add `cryptography` package to backend dependencies in `backend/pyproject.toml`
- [x] T002 [P] Create cache directory structure `backend/cache/resources/explanations/`
- [x] T003 [P] Add ENCRYPTION_KEY to environment variables template in `backend/.env.example`
- [x] T004 [P] Create shared enums module `backend/src/models/enums.py` with GeneratedByType, LLMProvider, MasteryLevel, PersonalizationStyle enums

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and services that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [x] T005 [P] Create GeneratedExplanation model in `backend/src/models/generated_explanation.py` per data-model.md
- [x] T006 [P] Create StudentLearningPath model in `backend/src/models/student_learning_path.py` per data-model.md
- [x] T007 [P] Create StudentLLMConfig model in `backend/src/models/student_llm_config.py` per data-model.md
- [x] T008 Add `is_admin` boolean field to existing Student model in `backend/src/models/student.py`
- [x] T009 Export new models in `backend/src/models/__init__.py`
- [x] T010 Generate Alembic migration for new tables: `alembic revision --autogenerate -m "add_resource_bank_tables"`
- [x] T011 Run migration and verify tables created: `alembic upgrade head`

### Core Services

- [x] T012 Create llm_key_service.py with encrypt/decrypt functions using Fernet in `backend/src/services/llm_key_service.py`
- [x] T013 [P] Create cache_service.py with save/get/delete/list operations in `backend/src/services/cache_service.py`
- [x] T014 Create resource_service.py with CRUD operations in `backend/src/services/resource_service.py`

### Pydantic Schemas

- [x] T015 [P] Create resource schemas in `backend/src/schemas/resource_schemas.py` per contracts/resources-api.yaml
- [x] T016 [P] Create learning path schemas in `backend/src/schemas/learning_path_schemas.py` per contracts/learning-path-api.yaml

**Checkpoint**: Foundation ready - all models, core services, and schemas in place

---

## Phase 3: User Story 1 - View Shared Topic Explanation (Priority: P1)

**Goal**: Students can view admin-generated explanations instantly from cache/database

**Independent Test**: Navigate to a topic with v1 explanation, verify it loads within 2 seconds

### Implementation for User Story 1

- [x] T017 [US1] Implement `get_explanation()` in resource_service.py with cache-first retrieval pattern
- [x] T018 [US1] Implement `get_from_cache()` and `save_to_cache()` in cache_service.py with signature validation
- [x] T019 [US1] Create GET `/resources/explanations/{syllabus_point_id}` endpoint in `backend/src/routes/resources.py`
- [x] T020 [US1] Handle cache miss: fetch from DB, cache locally, return response
- [x] T021 [US1] Handle no explanation: return 404 with "pending admin generation" message
- [x] T022 [P] [US1] Create API client function `getExplanation()` in `frontend/lib/api/resources.ts`
- [x] T023 [P] [US1] Create `useResourceExplanation` hook in `frontend/lib/hooks/useResourceExplanation.tsx`
- [x] T024 [US1] Update teaching page `frontend/app/(dashboard)/teaching/[topicId]/page.tsx` to use resource bank

**Checkpoint**: Students can view v1 explanations - core value delivered

---

## Phase 4: User Story 2 - Admin Generates Baseline Content (Priority: P1)

**Goal**: Admin can generate v1 explanations for topics using system LLM credentials

**Independent Test**: Admin logs in, generates explanation for topic, verify all students can view it

### Implementation for User Story 2

- [x] T025 [US2] Create admin auth middleware checking `is_admin=true` in `backend/src/middleware/admin_auth.py`
- [x] T026 [US2] Implement `generate_v1_explanation()` in resource_service.py integrating with LLM orchestrator
- [x] T027 [US2] Create POST `/admin/resources/generate-v1` endpoint in `backend/src/routes/resources.py`
- [x] T028 [US2] Implement signature generation using SHA-256 hash of content + timestamp
- [x] T029 [US2] Create POST `/admin/resources/{id}/regenerate` endpoint for v1 regeneration
- [x] T030 [US2] Add admin-only "Generate Explanation" button to teaching page (visible only when `is_admin=true`)
- [x] T031 [P] [US2] Create admin API client functions in `frontend/lib/api/resources.ts`

**Checkpoint**: Admin can populate resource bank with v1 content

---

## Phase 5: User Story 3 - Student Configures Personal LLM Keys (Priority: P2)

**Goal**: Students can securely store their own API keys for personalized generation

**Independent Test**: Student adds API key, verify encrypted in DB, only last 4 chars shown

### Implementation for User Story 3

- [ ] T032 [US3] Implement `save_api_key()` with AES-256 encryption in llm_key_service.py
- [ ] T033 [US3] Implement `get_api_key_status()` returning masked key hint in llm_key_service.py
- [ ] T034 [US3] Implement `delete_api_key()` in llm_key_service.py
- [ ] T035 [US3] Create GET `/student/llm-config` endpoint in `backend/src/routes/resources.py`
- [ ] T036 [US3] Create POST `/student/llm-config` endpoint with key encryption
- [ ] T037 [US3] Create DELETE `/student/llm-config/{provider}` endpoint
- [ ] T038 [P] [US3] Create LLMConfigForm component in `frontend/components/settings/LLMConfigForm.tsx`
- [ ] T039 [US3] Create Settings page with LLM configuration section in `frontend/app/(dashboard)/settings/page.tsx`
- [ ] T040 [P] [US3] Create API client functions for LLM config in `frontend/lib/api/resources.ts`

**Checkpoint**: Students can securely store their API keys

---

## Phase 6: User Story 4 - Student Generates Personalized Version (Priority: P2)

**Goal**: Students with API keys can generate v2+ personalized explanations in 5 styles

**Independent Test**: Student with API key generates "Simpler" version, verify v2 created with their key

### Implementation for User Story 4

- [ ] T041 [US4] Implement `decrypt_api_key()` for runtime LLM calls in llm_key_service.py
- [ ] T042 [US4] Implement `generate_personalized_explanation()` with 5 distinct style prompts in resource_service.py
- [ ] T043 [US4] Create style-specific LLM prompts (Simpler, More Detailed, More Examples, Exam-Focused, Visual) in `backend/src/prompts/personalization_prompts.py`
- [ ] T044 [US4] Create POST `/resources/explanations/{syllabus_point_id}/generate` endpoint
- [ ] T045 [US4] Implement rate limiting (10/hour/student) with monitoring in resource_service.py
- [ ] T046 [US4] Create GET `/resources/explanations/{syllabus_point_id}/versions` endpoint
- [ ] T047 [P] [US4] Create VersionSwitcher component in `frontend/components/teaching/VersionSwitcher.tsx`
- [ ] T048 [US4] Add personalization UI to teaching page with style selector and generate button
- [ ] T049 [P] [US4] Create API client functions for personalized generation in `frontend/lib/api/resources.ts`

**Checkpoint**: Students can create personalized versions using their own API keys

---

## Phase 7: User Story 5 - Track Learning Progress (Priority: P2)

**Goal**: System automatically tracks views, time spent, and mastery level per student

**Independent Test**: View topic, verify view_count increments and time_spent accumulates

### Implementation for User Story 5

- [ ] T050 [US5] Create learning_path_service.py with tracking logic in `backend/src/services/learning_path_service.py`
- [ ] T051 [US5] Implement `track_view()` with mastery auto-progression logic
- [ ] T052 [US5] Implement `track_time_spent()` accumulating seconds on page leave
- [ ] T053 [US5] Implement mastery transition rules (views 3+ → familiar, time 10+ min → familiar)
- [ ] T054 [US5] Create POST `/learning-path/track-view` endpoint in `backend/src/routes/learning_path.py`
- [ ] T055 [US5] Create POST `/learning-path/track-time` endpoint
- [ ] T056 [US5] Create GET `/learning-path` endpoint with filtering and pagination
- [ ] T057 [US5] Create GET `/learning-path/summary` endpoint for dashboard stats
- [ ] T058 [US5] Create PATCH `/learning-path/{syllabus_point_id}` for manual mastery override
- [ ] T059 [P] [US5] Create useLearningPath hook in `frontend/lib/hooks/useLearningPath.tsx`
- [ ] T060 [P] [US5] Create API client functions in `frontend/lib/api/learning-path.ts`
- [ ] T061 [US5] Add view tracking on page load and time tracking on page leave to teaching page
- [ ] T062 [US5] Create learning progress dashboard component showing mastery distribution

**Checkpoint**: Learning progress is tracked and displayed to students

---

## Phase 8: User Story 6 - Sync Cache with Database (Priority: P3)

**Goal**: Local file cache stays synchronized with database using signature comparison

**Independent Test**: Modify record in DB, trigger sync, verify local cache updates

### Implementation for User Story 6

- [ ] T063 [US6] Create sync_service.py with signature comparison in `backend/src/services/sync_service.py`
- [ ] T064 [US6] Implement `check_sync_status()` comparing DB and cache signatures
- [ ] T065 [US6] Implement `sync_from_database()` fetching stale/missing entries
- [ ] T066 [US6] Create GET `/resources/sync-status` endpoint in resources.py
- [ ] T067 [US6] Create POST `/resources/sync` endpoint triggering sync
- [ ] T068 [US6] Add startup sync hook in `backend/src/main.py` lifespan event
- [ ] T069 [US6] Implement cache index.json for quick signature lookups

**Checkpoint**: Cache automatically stays in sync with database

---

## Phase 9: User Story 7 - Bookmark Favorite Topics (Priority: P3)

**Goal**: Students can bookmark topics for quick access during revision

**Independent Test**: Bookmark topic, verify it appears in student's bookmarks list only

### Implementation for User Story 7

- [ ] T070 [US7] Implement bookmark operations in learning_path_service.py
- [ ] T071 [US7] Create GET `/learning-path/bookmarks` endpoint
- [ ] T072 [US7] Create POST `/learning-path/{syllabus_point_id}/bookmark` endpoint
- [ ] T073 [US7] Create DELETE `/learning-path/{syllabus_point_id}/bookmark` endpoint
- [ ] T074 [P] [US7] Add bookmark button to teaching page explanation header
- [ ] T075 [US7] Create "My Bookmarks" section in learning dashboard

**Checkpoint**: Students can bookmark and access favorite topics

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Quality, performance, and documentation improvements

- [ ] T076 [P] Add comprehensive error handling for LLM API failures (fallback to cache)
- [ ] T077 [P] Add request logging for all resource bank endpoints
- [ ] T078 Implement monitoring alerts for rate limit violations
- [ ] T079 [P] Add loading states and skeleton UI to all resource bank components
- [ ] T080 Performance optimization: lazy loading for explanation content
- [ ] T081 [P] Update README with resource bank feature documentation
- [ ] T082 Run quickstart.md validation checklist
- [ ] T083 Security audit: verify API keys never appear in logs or responses

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────────┐
                                                                   │
Phase 2 (Foundational) ◄──────────────────────────────────────────┘
    │
    ├──► Phase 3 (US1: View Explanations) ──► MVP CHECKPOINT
    │
    ├──► Phase 4 (US2: Admin Generate) ──────► Depends on US1 models
    │
    ├──► Phase 5 (US3: LLM Config) ──────────► Independent
    │         │
    │         └──► Phase 6 (US4: Personalize) ◄── Depends on US3
    │
    ├──► Phase 7 (US5: Learning Path) ───────► Independent
    │
    ├──► Phase 8 (US6: Sync) ────────────────► Depends on US1 cache
    │
    └──► Phase 9 (US7: Bookmarks) ───────────► Depends on US5 model
              │
              └──► Phase 10 (Polish) ◄─────── After all stories
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 | Foundational only | - |
| US2 | US1 (models) | US3, US5 |
| US3 | Foundational only | US1, US2, US5 |
| US4 | US3 (LLM config) | US5, US6, US7 |
| US5 | Foundational only | US1, US2, US3 |
| US6 | US1 (cache service) | US4, US5, US7 |
| US7 | US5 (learning path model) | US4, US6 |

### Parallel Opportunities per Phase

**Phase 2 (Foundational)**:
```bash
# Models can be created in parallel:
T005, T006, T007, T008 → All model files are independent

# Schemas can be created in parallel:
T015, T016 → Different schema files
```

**Phase 3-9 (User Stories)**:
```bash
# Frontend tasks marked [P] can run parallel to backend:
Backend: T017-T021 (service + routes)
Frontend: T022, T023 (API client + hook)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (BLOCKS all stories)
3. Complete Phase 3: US1 - View Explanations
4. Complete Phase 4: US2 - Admin Generate
5. **STOP and VALIDATE**: Admin can generate, students can view
6. Deploy/demo MVP

### Incremental Delivery

| Increment | Stories | Value Delivered |
|-----------|---------|-----------------|
| MVP | US1 + US2 | View & generate explanations |
| v1.1 | + US3, US4 | Personalization with student keys |
| v1.2 | + US5 | Learning progress tracking |
| v1.3 | + US6, US7 | Sync + bookmarks |
| v2.0 | + Polish | Production-ready |

---

## Summary

| Phase | Tasks | Parallelizable |
|-------|-------|----------------|
| Setup | 4 | 3 |
| Foundational | 12 | 6 |
| US1 (P1) | 8 | 3 |
| US2 (P1) | 7 | 1 |
| US3 (P2) | 9 | 3 |
| US4 (P2) | 9 | 2 |
| US5 (P2) | 13 | 2 |
| US6 (P3) | 7 | 0 |
| US7 (P3) | 6 | 1 |
| Polish | 8 | 5 |
| **TOTAL** | **83** | **26** |

**MVP Scope**: Phases 1-4 (31 tasks) → US1 + US2 complete
**Full Feature**: All 83 tasks across 10 phases
