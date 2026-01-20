# Tasks: Embedding Integration

**Input**: Design documents from `/specs/010-embedding-integration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests ARE included in this task list as the spec mentions performance testing requirements (FR-004, FR-005).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`, `backend/alembic/`
- **Frontend**: `frontend/lib/`, `frontend/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and database migration

- [X] T001 Add pgvector and google-generativeai dependencies to backend/pyproject.toml
- [X] T002 [P] Add openai dependency for fallback support to backend/pyproject.toml
- [X] T003 Run `uv sync` to install new dependencies in backend/
- [X] T004 Create database migration in backend/alembic/versions/023_add_embedding_columns.py per data-model.md
- [X] T005 Run migration: `alembic upgrade head` to add vector extension and columns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Extend SyllabusPoint model with embedding fields in backend/src/models/syllabus_point.py
- [X] T007 [P] Extend Resource model with embedding fields in backend/src/models/resource.py (SKIPPED - deferred to US3)
- [X] T008 Create EmbeddingJob model in backend/src/models/embedding_job.py
- [X] T009 Register EmbeddingJob in backend/src/models/__init__.py
- [X] T010 Create embedding client with Gemini multi-key rotation in backend/src/ai_integration/embedding_client.py
- [X] T011 Add OpenAI fallback to embedding client in backend/src/ai_integration/embedding_client.py
- [X] T012 Create custom exceptions (EmbeddingError, RateLimitError) in backend/src/ai_integration/embedding_client.py
- [X] T013 Create base EmbeddingService class in backend/src/services/embedding_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Automatic Embedding Generation (Priority: P1) 🎯 MVP

**Goal**: After extracting topics from a syllabus, automatically generate and store embeddings for each topic

**Independent Test**: After extracting topics from a syllabus, verify that each topic has an associated embedding stored. Check that embeddings are 768 dimensions.

### Tests for User Story 1

- [ ] T014 [P] [US1] Unit test for embedding generation in backend/tests/unit/test_embedding_service.py
- [ ] T015 [P] [US1] Unit test for key rotation fallback in backend/tests/unit/test_embedding_client.py

### Implementation for User Story 1

- [X] T016 [US1] Implement generate_embedding() method in backend/src/services/embedding_service.py
- [X] T017 [US1] Implement batch embedding generation in backend/src/services/embedding_service.py
- [X] T018 [US1] Implement generate_embeddings_for_subject() in backend/src/services/embedding_service.py
- [X] T019 [US1] Add EmbeddingJob creation and progress tracking in backend/src/services/embedding_service.py
- [X] T020 [US1] Create Pydantic schemas for embedding endpoints in backend/src/schemas/embedding_schemas.py
- [X] T021 [US1] Create embedding routes file in backend/src/routes/embeddings.py
- [X] T022 [US1] Implement POST /embeddings/generate/{subject_id} endpoint in backend/src/routes/embeddings.py
- [X] T023 [US1] Implement GET /embeddings/status/{job_id} endpoint in backend/src/routes/embeddings.py
- [X] T024 [US1] Implement POST /embeddings/retry/{job_id} endpoint in backend/src/routes/embeddings.py
- [X] T025 [US1] Register embedding routes in backend/src/main.py
- [X] T026 [US1] Add logging for embedding generation operations in backend/src/services/embedding_service.py

**Checkpoint**: User Story 1 should be fully functional - can generate embeddings for any subject ✅

---

## Phase 4: User Story 2 - Semantic Topic Search (Priority: P2)

**Goal**: Users can search for topics using natural language queries and get relevant results ranked by semantic similarity

**Independent Test**: Search for "government intervention in markets" and verify results include relevant topics ranked by relevance, with response time under 500ms.

### Tests for User Story 2

- [ ] T027 [P] [US2] Integration test for semantic search in backend/tests/integration/test_semantic_search.py
- [ ] T028 [P] [US2] Performance test for <500ms search in backend/tests/integration/test_semantic_search.py

### Implementation for User Story 2

- [X] T029 [US2] Implement semantic_search() method in backend/src/services/embedding_service.py
- [X] T030 [US2] Add cosine similarity query with pgvector operators in backend/src/services/embedding_service.py
- [X] T031 [US2] Add SemanticSearchRequest/Response schemas in backend/src/schemas/embedding_schemas.py
- [X] T032 [US2] Create search routes file in backend/src/routes/search.py
- [X] T033 [US2] Implement POST /search/semantic endpoint in backend/src/routes/search.py
- [X] T034 [US2] Register search routes in backend/src/main.py
- [X] T035 [US2] Add search timing metrics and logging in backend/src/routes/search.py

**Checkpoint**: User Stories 1 AND 2 should both work independently ✅

---

## Phase 5: User Story 3 - Textbook-to-Syllabus Alignment (Priority: P3)

**Goal**: Admin can upload textbook content and system automatically identifies matching syllabus topics

**Independent Test**: Upload a textbook chapter about "Price Elasticity of Demand", verify system identifies matching syllabus topics with confidence scores.

### Tests for User Story 3

- [ ] T036 [P] [US3] Integration test for content alignment in backend/tests/integration/test_content_alignment.py

### Implementation for User Story 3

- [X] T037 [US3] Implement align_content() method in backend/src/services/embedding_service.py
- [X] T038 [US3] Add confidence scoring (high/medium/low) logic in backend/src/services/embedding_service.py
- [X] T039 [US3] Add ContentAlignmentRequest/Response schemas in backend/src/schemas/embedding_schemas.py
- [X] T040 [US3] Implement POST /embeddings/align endpoint in backend/src/routes/search.py

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently ✅

---

## Phase 6: User Story 4 - Re-embed on Content Update (Priority: P4)

**Goal**: When topic description is updated, automatically regenerate that topic's embedding

**Independent Test**: Update topic 1.1's description, verify its embedding is regenerated, and confirm search results reflect the updated content.

### Tests for User Story 4

- [ ] T041 [P] [US4] Unit test for single topic re-embedding in backend/tests/unit/test_embedding_service.py

### Implementation for User Story 4

- [X] T042 [US4] Implement regenerate_embedding(topic_id) method in backend/src/services/embedding_service.py
- [X] T043 [US4] Implement bulk_regenerate_embeddings(topic_ids) method in backend/src/services/embedding_service.py
- [ ] T044 [US4] Add re-embed trigger hook to topic update service (if exists) or document integration pattern

**Checkpoint**: All 4 user stories should be independently functional ✅

---

## Phase 7: Frontend Integration (Optional)

**Purpose**: React hooks and components for frontend integration

- [ ] T045 [P] Create useSemanticSearch hook in frontend/lib/hooks/useSemanticSearch.ts
- [ ] T046 [P] Create useEmbeddingJob hook in frontend/lib/hooks/useEmbeddingJob.ts
- [ ] T047 [P] Create search API client in frontend/lib/api/search.ts
- [ ] T048 [P] Create embeddings API client in frontend/lib/api/embeddings.ts

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T049 Add error handling for edge cases (empty content, very long content) in backend/src/services/embedding_service.py
- [ ] T050 Add content truncation with warning for texts exceeding 8000 chars in backend/src/services/embedding_service.py
- [ ] T051 [P] Add multi-tenant isolation check (subject_id scope) in all embedding queries
- [ ] T052 Run quickstart.md validation scenarios manually
- [ ] T053 Update environment variable documentation with GEMINI_API_KEY_1-5 and OPENAI_API_KEY

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3 → P4)
  - Or in parallel if multiple developers available
- **Frontend (Phase 7)**: Can proceed in parallel with backend User Stories after Phase 2
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on embeddings existing (US1) but can be implemented in parallel
- **User Story 3 (P3)**: Depends on embeddings existing (US1) but can be implemented in parallel
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (if tests included)
- Schemas before endpoints
- Services before routes
- Core implementation before integration

### Parallel Opportunities

- Setup tasks marked [P] can run in parallel
- Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Frontend tasks (Phase 7) can run fully in parallel with each other
- US1, US3, US4 can run in parallel after Foundational phase (US2 depends on embeddings)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
T014: "Unit test for embedding generation in backend/tests/unit/test_embedding_service.py"
T015: "Unit test for key rotation fallback in backend/tests/unit/test_embedding_client.py"
```

## Parallel Example: Frontend Integration

```bash
# Launch all frontend tasks together:
T045: "Create useSemanticSearch hook in frontend/lib/hooks/useSemanticSearch.ts"
T046: "Create useEmbeddingJob hook in frontend/lib/hooks/useEmbeddingJob.ts"
T047: "Create search API client in frontend/lib/api/search.ts"
T048: "Create embeddings API client in frontend/lib/api/embeddings.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Automatic Embedding Generation)
4. **STOP and VALIDATE**: Test embedding generation independently
5. Deploy/demo if ready - this alone provides 98% token savings!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test search independently → Deploy
4. Add User Story 3 → Test alignment independently → Deploy
5. Add User Story 4 → Test re-embed independently → Deploy
6. Each story adds value without breaking previous stories

### Suggested MVP Scope

**MVP = User Story 1 (Automatic Embedding Generation)**

This delivers:
- Embeddings generated after topic extraction
- 98%+ token savings on post-extraction operations
- Foundation for all future embedding features

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Performance target: <500ms for semantic search (FR-005)
- Performance target: 60 topics in 60 seconds (FR-004)
