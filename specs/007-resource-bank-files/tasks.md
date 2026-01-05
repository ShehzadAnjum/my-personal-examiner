# Tasks: Resource Bank File Storage & Multi-Source Content Management

**Input**: Design documents from `/specs/007-resource-bank-files/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks included for >80% coverage requirement (Constitution mandate)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- **Exact file paths** included in descriptions

## Path Conventions

Project structure (from plan.md):
- Backend: `backend/src/` for source code
- Frontend: `frontend/` for Next.js 16 components (Phase 1 limited)
- Tests: `backend/tests/` (unit/ and integration/)
- Migrations: `backend/alembic/versions/`
- Resources: `backend/resources/` (gitignored local storage)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add Python dependencies to backend/pyproject.toml (PyPDF2 2.12+, pytesseract 0.3+, youtube-transcript-api 0.6+, boto3, Celery 5.3+, pyclamd, pdf2image)
- [X] T002 [P] Run `uv sync` to install new dependencies
- [X] T003 [P] Create backend/resources/ directory structure (syllabus/, past_papers/, textbooks/, user_uploads/, videos/, downloads/)
- [X] T004 [P] Add backend/resources/ to .gitignore to prevent accidental commits
- [X] T005 [P] Configure environment variables in backend/.env.example (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, YOUTUBE_API_KEY, SIGNING_SECRET_KEY, REDIS_URL, CLAMAV_SOCKET)
- [X] T006 Create backend/src/models/enums.py with ResourceType, Visibility, S3SyncStatus, AddedBy enums

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create Alembic migration 010_add_resource_tables.py with 4 tables (resources, syllabus_point_resources, explanation_resource_usage, student_resource_preferences) and ENUM types
- [X] T008 [P] Create Alembic migration 011_add_resource_indexes.py with 14 performance indexes (GIN index for search_vector, composite PKs, foreign keys)
- [ ] T009 Run Alembic migrations: `alembic upgrade head` **⚠️ PENDING: Requires PostgreSQL running**
- [X] T010 [P] Create backend/src/models/resource.py with Resource SQLModel class (19 fields per data-model.md)
- [X] T011 [P] Create backend/src/models/syllabus_point_resource.py with SyllabusPointResource SQLModel class
- [X] T012 [P] Create backend/src/models/explanation_resource_usage.py with ExplanationResourceUsage SQLModel class
- [X] T013 [P] Create backend/src/models/student_resource_preference.py with StudentResourcePreference SQLModel class
- [X] T014 [P] Create backend/src/schemas/resource_schemas.py with Pydantic request/response models (ResourceUploadRequest, ResourceResponse, ResourceListResponse)
- [X] T015 Configure Celery app in backend/src/tasks/celery_app.py with Redis broker, JSON serialization, timezone=UTC
- [X] T016 [P] Initialize ClamAV daemon and verify with `clamdscan --version` **⚠️ Verification script created, daemon check deferred**
- [X] T017 [P] Create backend/src/middleware/resource_permission.py with signed URL generation and verification functions (HMAC SHA-256)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Admin Initializes Official Resource Repository (Priority: P1) 🎯 MVP

**Goal**: Admin uploads Cambridge 9708 syllabus, stores locally with S3 backup, detects duplicates via signature

**Independent Test**: Upload syllabus PDF → verify stored in `backend/resources/syllabus/9708/`, S3 queued, DB record created with signature

### Implementation for User Story 1

- [X] T018 [P] [US1] Create backend/src/services/file_storage_service.py with functions: calculate_signature (SHA-256), save_file_to_local, get_file_path_for_resource
- [X] T019 [P] [US1] Create backend/src/tasks/s3_upload_task.py with Celery task: upload_to_s3_task (boto3 client, SSE-S3 encryption, 3 retries with exponential backoff per research.md)
- [X] T020 [US1] Implement virus scanning in backend/src/services/file_storage_service.py: scan_file_for_virus using pyclamd (scan after write, before DB commit)
- [X] T021 [US1] Create backend/src/routes/resources.py with POST /api/resources/upload endpoint (multipart file upload, validate file size <50MB, check quota, call scan, save, queue S3 upload)
- [X] T022 [US1] Add duplicate detection logic in upload endpoint (check signature exists in DB, reject with "Already exists" message per acceptance scenario)
- [X] T023 [US1] Implement S3 sync status tracking: update resource.s3_sync_status field on Celery task completion/failure
- [X] T024 [US1] Add error handling for S3 upload failures (log alert, mark status as failed, send admin notification per FR-043)

### Tests for User Story 1

- [X] T025 [P] [US1] Unit test: backend/tests/unit/test_file_storage_service.py (calculate_signature, save_file_to_local, scan_file_for_virus with mocked pyclamd)
- [X] T026 [P] [US1] Unit test: backend/tests/unit/test_s3_upload_task.py (mock boto3 client with moto, test retry logic, test SSE-S3 encryption)
- [X] T027 [P] [US1] Integration test: backend/tests/integration/test_resource_upload.py (end-to-end upload flow: POST multipart, verify file stored, DB record, S3 queued, signature duplicate detection)

**Checkpoint**: At this point, User Story 1 should be fully functional - admin can upload syllabus with S3 backup

---

## Phase 4: User Story 2 - System Auto-Syncs Cambridge Past Papers Daily (Priority: P1)

**Goal**: Daily 2AM job downloads new past papers from Cambridge, uses signature-based change detection, links mark schemes

**Independent Test**: Trigger sync job → mock Cambridge website → verify past papers downloaded to `backend/resources/past_papers/9708/{year}_{session}_qp_{paper}.pdf`, mark schemes linked

### Implementation for User Story 2

- [X] T028 [P] [US2] Create backend/src/services/sync_service.py with functions: scrape_cambridge_website, download_past_paper, link_mark_scheme
- [X] T029 [US2] Implement signature-based change detection in sync_service.py: compare SHA-256 hash, skip download if unchanged, update last_checked timestamp
- [X] T030 [US2] Implement past paper download logic: parse Cambridge website, extract year/session/paper metadata, save with naming convention `{year}_{session}_qp_{paper}.pdf`
- [X] T031 [US2] Implement mark scheme linking: download corresponding mark scheme, create Resource record with metadata.mark_scheme_id relationship (per FR-011)
- [X] T032 [P] [US2] Create backend/src/tasks/sync_task.py with Celery task: sync_cambridge_resources (scheduled daily 2AM via Celery Beat, 3 retries with 4-hour delay per research.md)
- [X] T033 [US2] Configure Celery Beat schedule in backend/src/tasks/celery_app.py: crontab(hour=2, minute=0) for daily sync
- [X] T034 [US2] Add sync failure handling: log failed sync, retry 3 times, alert admin if all retries fail (per edge case)
- [X] T035 [US2] Create backend/src/routes/resource_sync.py with POST /api/sync/trigger endpoint for manual sync (per contracts/sync.yaml)
- [X] T036 [US2] Implement GET /api/sync/status endpoint showing last_sync_date, sync_status (idle/running/success/failed), new_resources_count

### Tests for User Story 2

- [X] T037 [P] [US2] Unit test: backend/tests/unit/test_sync_service.py (mock Cambridge website with test PDFs, test signature detection, test mark scheme linking)
- [X] T038 [P] [US2] Integration test: backend/tests/integration/test_daily_sync.py (trigger Celery task, verify past papers downloaded, DB records created, mark schemes linked)

**Checkpoint**: At this point, User Stories 1 AND 2 work - syllabus uploaded manually, past papers sync automatically daily

---

## Phase 5: User Story 3 - Student Uploads Private Learning Resource (Priority: P2)

**Goal**: Student uploads PDF study notes, stores in student_id-scoped directory, sets visibility=private, queues for admin review

**Independent Test**: Student uploads "My Notes.pdf" → verify stored in `backend/resources/user_uploads/{student_id}/`, visibility=private, admin sees in pending dashboard, other students can't access

### Implementation for User Story 3

- [X] T039 [P] [US3] Extend file_storage_service.py: create_student_directory, validate_student_quota (100 resources per student per FR-050)
- [X] T040 [P] [US3] Create backend/src/services/pdf_extraction_service.py with extract_pdf_text (PyPDF2 native extraction + pytesseract OCR fallback per research.md #2)
- [X] T041 [US3] Implement OCR detection in pdf_extraction_service.py: if extracted text <100 chars, trigger OCR with pdf2image + pytesseract
- [X] T042 [US3] Create backend/src/tasks/ocr_task.py with Celery task: extract_text_task (background OCR for large PDFs, update resource.extracted_text field)
- [X] T043 [US3] Extend POST /api/resources/upload in routes/resources.py: check uploaded_by_student_id from JWT, set visibility=pending_review, enforce quota per FR-052 **⚠️ Already implemented in Phase 3**
- [X] T044 [US3] Add quota validation: query count of resources WHERE uploaded_by_student_id={student_id}, reject if >=100 with error message per FR-052 **⚠️ Already implemented in Phase 3**
- [X] T045 [US3] Implement DELETE /api/resources/{id} endpoint: allow students to delete own resources WHERE uploaded_by_student_id={student_id} AND admin_approved=false (per contracts/resources.yaml) **⚠️ Already implemented in Phase 3**

### Tests for User Story 3

- [X] T046 [P] [US3] Unit test: backend/tests/unit/test_pdf_extraction.py (test PyPDF2 extraction, test OCR fallback with mocked pytesseract, test 100-char threshold)
- [X] T047 [P] [US3] Unit test: backend/tests/unit/test_resource_quota.py (test quota enforcement, test error message when 100 reached)
- [X] T048 [P] [US3] Integration test: backend/tests/integration/test_student_upload.py (student uploads PDF, verify private visibility, verify quota enforcement, test delete endpoint)
- [X] T049 [P] [US3] Integration test: backend/tests/integration/test_multi_tenant_isolation.py (verify student A can't access student B's private resources, test visibility filters per FR-037)

**Checkpoint**: At this point, students can upload private notes with quota enforcement and multi-tenant isolation

---

## Phase 6: User Story 4 - Admin Reviews and Approves User-Uploaded Resources (Priority: P2)

**Goal**: Admin sees pending uploads, previews PDF, approves (visibility→public) or rejects (delete file+record), edits metadata

**Independent Test**: Create pending resource → admin views in dashboard → preview 3 pages → approve → verify visibility=public and other students can access

### Implementation for User Story 4

- [X] T050 [P] [US4] Create backend/src/routes/admin_resources.py with GET /api/admin/resources/pending endpoint (filter by visibility=pending_review, return list with student name, title, upload_date, file_size per contracts/admin.yaml)
- [X] T051 [P] [US4] Implement GET /api/admin/resources/{id}/preview endpoint: extract first 3 pages of PDF using PyPDF2, convert to base64 images, return as JSON array (per contracts/admin.yaml)
- [X] T052 [US4] Implement PUT /api/admin/resources/{id}/approve endpoint: update visibility=public, admin_approved=true, set approval_date timestamp (per FR-028, linear state machine FR-070)
- [X] T053 [US4] Implement PUT /api/admin/resources/{id}/reject endpoint: delete file from storage, delete DB record (per FR-029, linear state machine FR-071)
- [X] T054 [US4] Implement PUT /api/admin/resources/{id}/metadata endpoint: allow admin to edit title, description, metadata JSONB before approval (per FR-030)
- [X] T055 [US4] Add textbook excerpt extraction: admin provides page_range in metadata, extract pages, store in metadata.excerpt_location (per FR-031)
- [X] T056 [US4] Enforce state machine transitions: prevent visibility change from approved back to pending_review (one-way approval per FR-072)

### Tests for User Story 4

- [X] T057 [P] [US4] Unit test: backend/tests/unit/test_admin_service.py (test state transitions, test rejection deletes file+record)
- [X] T058 [P] [US4] Integration test: backend/tests/integration/test_admin_review.py (end-to-end approval workflow: pending → preview → approve → verify public, test reject deletes resource)

**Checkpoint**: At this point, admin can review and approve/reject user uploads with state machine enforcement

---

## Phase 7: User Story 5 - System Auto-Selects Best Resources for Topic Generation (Priority: P3)

**Goal**: When generating topic, system auto-selects most relevant resources based on relevance_score, allows manual override

**Independent Test**: Generate topic for 9708.5.1 → verify auto-selects syllabus (1.0 relevance), top 3 past papers (0.8-0.9), textbook chapter (if tagged), display quality scores as percentages

### Implementation for User Story 5

- [x] T059 [P] [US5] Create backend/src/services/resource_service.py with get_resources_for_syllabus_point (query SyllabusPointResource JOIN Resource, order by relevance_score DESC, limit 5 per FR-032)
- [x] T060 [US5] Implement auto-selection algorithm: calculate_relevance_score based on keyword matching, syllabus point ID, resource type (syllabus always 1.0 per US5 acceptance)
- [x] T061 [US5] Add resource usage tracking: create ExplanationResourceUsage records after topic generation with contribution_weight values (per FR-036)
- [x] T062 [US5] Extend existing topic generation endpoint to include selected resources in LLM prompt: syllabus learning outcomes, past paper texts, textbook excerpts with attribution (per FR-035)

### Tests for User Story 5

- [x] T063 [P] [US5] Unit test: backend/tests/unit/test_resource_service.py (test auto-selection algorithm, test relevance scoring, test usage tracking)
- [x] T064 [P] [US5] Integration test: backend/tests/integration/test_auto_selection.py (create resources with relevance scores, trigger auto-selection, verify top 5 returned in order)

**Checkpoint**: At this point, topic generation auto-selects best resources based on quality scores

---

## Phase 8: User Story 6 - Admin Tags Resources to Syllabus Points (Priority: P3)

**Goal**: Admin uses tagging interface to link resources to syllabus points with relevance scores, improves auto-selection

**Independent Test**: Admin searches "fiscal policy" → selects resource + syllabus point 9708.5.1 → sets relevance 95% → verify SyllabusPointResource record created, affects future auto-selections

### Implementation for User Story 6

- [x] T065 [P] [US6] Create backend/src/services/tagging_service.py with create_tag (insert SyllabusPointResource with relevance_score), search_resources (full-text search using tsvector)
- [x] T066 [P] [US6] Create backend/src/routes/resource_tagging.py with POST /api/resources/{id}/tag endpoint (create SyllabusPointResource link with relevance_score 0-1 per contracts/tagging.yaml)
- [x] T067 [US6] Implement GET /api/resources/search endpoint: full-text search using PostgreSQL tsvector, ts_rank for ranking, return results with relevance scores (per FR-047, FR-048, research.md #7)
- [x] T068 [US6] Implement GET /api/syllabus/{point_id}/resources endpoint: return resources linked to syllabus point ordered by relevance_score (per contracts/tagging.yaml)
- [x] T069 [US6] Add page_range metadata support: allow admin to specify textbook page ranges in metadata JSONB field when tagging (per FR-046)

### Tests for User Story 6

- [x] T070 [P] [US6] Unit test: backend/tests/unit/test_tagging_service.py (test tag creation, test relevance score validation 0-1, test full-text search with ts_rank)
- [x] T071 [P] [US6] Integration test: backend/tests/integration/test_manual_tagging.py (create tag, verify affects auto-selection, test search endpoint returns ranked results)

**Checkpoint**: At this point, admin can manually tag resources to syllabus points, improving auto-selection accuracy

---

## Phase 9: User Story 7 - System Extracts YouTube Transcript for Topic Generation (Priority: P3)

**Goal**: Admin adds YouTube URL, system extracts transcript via API, identifies timestamps, stores metadata, makes searchable

**Independent Test**: Admin pastes YouTube URL → system calls API → extracts transcript → parses timestamps → stores in metadata → includes excerpts in LLM prompts when relevant

### Implementation for User Story 7

- [x] T072 [P] [US7] Create backend/src/services/youtube_service.py with extract_youtube_transcript (youtube-transcript-api + YouTube Data API v3 per research.md #3)
- [x] T073 [US7] Implement YouTube metadata extraction: get video title, channel, duration, thumbnail via YouTube Data API v3, store in metadata JSONB
- [x] T074 [US7] Implement transcript timestamp parsing: identify keywords in transcript, extract matching timestamps with context (per US7 acceptance scenario 2)
- [x] T075 [US7] Add YouTube API quota management: track daily video count, limit to 10 videos/day in Phase 1, log warning if approaching quota
- [x] T076 [US7] Extend POST /api/resources/upload to accept source_url for YouTube links: validate YouTube URL format, call youtube_service, create Resource record with resource_type=video
- [x] T077 [US7] Add error handling for unavailable transcripts: graceful degradation, store video metadata only if transcript extraction fails (per research.md #3)

### Tests for User Story 7

- [x] T078 [P] [US7] Unit test: backend/tests/unit/test_youtube_service.py (mock youtube-transcript-api, test metadata extraction, test quota tracking, test transcript unavailable handling)
- [x] T079 [P] [US7] Integration test: backend/tests/integration/test_youtube_upload.py (upload YouTube URL, verify transcript extracted, metadata stored, searchable via full-text search)

**Checkpoint**: At this point, all 7 user stories complete - full Resource Bank MVP functionality implemented

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, compliance, and quality gates

- [x] T080 [P] Implement observability metrics endpoint GET /api/metrics: total resources, resources by visibility, S3 sync status, storage usage by student (per FR-063, FR-066)
- [x] T081 [P] Add comprehensive error logging: file upload failures, S3 sync failures, OCR failures, Cambridge unreachable with severity levels ERROR/WARNING/INFO (per FR-064)
- [x] T082 [P] Add security event logging: failed auth attempts, unauthorized access attempts, quota exceeded violations, admin actions with 1-year retention (per FR-065, FR-067)
- [x] T083 [P] Implement S3 outage handling: continue with local-only storage, queue failed uploads with status=pending_retry, batch retry when S3 recovers (per FR-054 to FR-057, edge case)
- [x] T084 [P] Add GET /api/sync/s3-status endpoint: show pending_uploads count, failed_uploads count, s3_online status (per contracts/sync.yaml)
- [x] T085 [P] Add POST /api/sync/retry-s3 endpoint: batch retry failed S3 uploads (per contracts/sync.yaml)
- [x] T086 [P] Implement signed URL generation for private downloads: integrate with download endpoint, 1-hour expiration (per FR-062, research.md #6)
- [ ] T087 Configure HTTPS enforcement for all API endpoints (per FR-058)
- [ ] T088 [P] Create frontend/app/(dashboard)/resources/page.tsx with resource browser for students (list public + own private resources)
- [ ] T089 [P] Create frontend/app/(dashboard)/resources/admin/page.tsx with admin review dashboard (pending list, preview, approve/reject buttons)
- [ ] T090 [P] Create frontend/components/ResourceUpload.tsx with file upload component (drag-drop, file size validation, progress indicator)
- [ ] T091 Run full test suite: `pytest backend/tests/ -v --cov=backend/src --cov-report=term-missing` and verify >80% coverage (Constitution requirement)
- [ ] T092 Run quickstart.md validation: follow setup steps, verify all services start (FastAPI, Celery worker, Celery Beat, Flower)
- [ ] T093 Code cleanup: remove debug print statements, organize imports, run linter (black, ruff)
- [ ] T094 Security hardening: validate all multi-tenant queries include student_id filter, verify signed URL HMAC implementation, check ClamAV integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US2 (P1): Can start after Foundational - No dependencies on other stories (can run parallel with US1)
  - US3 (P2): Depends on US1 (Resource model, file_storage_service, upload endpoint)
  - US4 (P2): Depends on US3 (pending resources exist for review)
  - US5 (P3): Depends on US1, US6 (needs resources with relevance scores)
  - US6 (P3): Depends on US1 (Resource model, tagging to existing resources)
  - US7 (P3): Depends on US1 (Resource model, extends upload endpoint)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2) ─┬─→ US1 (P1) ───┬─→ US3 (P2) ──→ US4 (P2)
                        │                │
                        ├─→ US2 (P1)     ├─→ US6 (P3) ──┐
                        │                │               ├─→ US5 (P3)
                        └────────────────┴─→ US7 (P3) ──┘
```

**Critical Path**: Foundational → US1 → US3 → US4 (Admin can upload, students can upload, admin can review)

**MVP Scope**: Foundational + US1 + US2 (Official resources synced, foundation for student uploads)

### Within Each User Story

1. Implementation tasks before tests (tests verify completed implementation)
2. Models before services
3. Services before endpoints
4. Core implementation before integration
5. Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All tasks except T001→T002 can run in parallel
- **Foundational (Phase 2)**: T010-T014 (models) in parallel, T007-T008 (migrations) sequential
- **User Stories**: US1 and US2 (both P1) can run in parallel after Foundational
- **Tests within story**: All test tasks marked [P] can run in parallel
- **Models within story**: All model tasks marked [P] can run in parallel
- **Polish (Phase 10)**: T080-T090 can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# After T009 (migrations run), launch all models in parallel:
Task T010: "Create backend/src/models/resource.py"
Task T011: "Create backend/src/models/syllabus_point_resource.py"
Task T012: "Create backend/src/models/explanation_resource_usage.py"
Task T013: "Create backend/src/models/student_resource_preference.py"
Task T014: "Create backend/src/schemas/resource_schemas.py"
```

## Parallel Example: User Story 1

```bash
# Launch all service foundation tasks in parallel:
Task T018: "Create backend/src/services/file_storage_service.py"
Task T019: "Create backend/src/tasks/s3_upload_task.py"

# After implementation, launch all tests in parallel:
Task T025: "Unit test: test_file_storage_service.py"
Task T026: "Unit test: test_s3_upload_task.py"
Task T027: "Integration test: test_resource_upload.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup → Dependencies installed
2. Complete Phase 2: Foundational → Database ready, models created
3. Complete Phase 3: User Story 1 → Admin can upload syllabus with S3 backup
4. Complete Phase 4: User Story 2 → Daily sync downloads past papers automatically
5. **STOP and VALIDATE**: Test US1 + US2 independently, verify syllabus + past papers stored
6. Deploy/demo if ready

**Estimated Effort**: ~15 hours (Phase 1-4 only)

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Database → ~5 hours
2. **MVP** (Phase 3-4): US1 + US2 → ~10 hours → **DEPLOY** (Official resources synced)
3. **Student Uploads** (Phase 5-6): US3 + US4 → ~10 hours → **DEPLOY** (Students can upload, admin reviews)
4. **Advanced Features** (Phase 7-9): US5 + US6 + US7 → ~15 hours → **DEPLOY** (Auto-selection, tagging, YouTube)
5. **Polish** (Phase 10): Metrics, logging, frontend → ~10 hours → **DEPLOY** (Production-ready)

**Total Estimated Effort**: ~50 hours (matches plan.md estimate of 40-55 hours)

### Parallel Team Strategy

With 2 developers after Foundational phase:

- **Developer A**: US1 → US3 → US5 (Resource upload flow)
- **Developer B**: US2 → US4 → US6 → US7 (Sync + admin workflows)

Stories integrate via shared Resource model (completed in Foundational phase).

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] to [US7] labels map tasks to user stories for traceability
- Each user story should be independently completable and testable
- Tests verify >80% coverage (Constitution requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Multi-tenant isolation validated via test_multi_tenant_isolation.py (T049)
- S3 outage handling ensures graceful degradation (T083)
- Signed URLs enforce private resource access control (T086)

---

**Total Tasks**: 94
**MVP Tasks (US1 + US2)**: 27 tasks (Phase 1-4)
**Full Feature Tasks**: 94 tasks (all 7 user stories + polish)

**Parallel Opportunities Identified**: 42 tasks marked [P] can run in parallel with other tasks in same phase

**Independent Test Criteria**:
- US1: Upload syllabus → verify file + DB + S3 queued
- US2: Trigger sync → verify past papers downloaded with signatures
- US3: Student uploads → verify private visibility + quota
- US4: Admin approves → verify visibility→public transition
- US5: Generate topic → verify auto-selected resources
- US6: Admin tags → verify relevance score affects auto-selection
- US7: Add YouTube → verify transcript extracted

**MVP Scope Recommendation**: Foundational + US1 + US2 (Official resources synced and stored)

**Ready for /sp.implement** ✅
