---
description: "Atomic implementation tasks for Phase II Question Bank & Exam Generation"
---

# Tasks: Phase II - Question Bank & Exam Generation (Generic Framework)

**Input**: Design documents from `/specs/002-question-bank/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Included for >80% coverage compliance (Constitutional Principle VII). Tests written during implementation, not TDD approach per spec.

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- All paths use `backend/` prefix per plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure and dependency setup for Phase II

- [ ] T001 Create directory structure: backend/src/question_extractors/, backend/resources/subjects/9708/
- [ ] T002 Add pdfplumber==0.11.0 and pypdf==4.3.1 to backend/pyproject.toml dependencies
- [ ] T003 [P] Create backend/resources/subjects/9708/README.md documenting Economics as reference template
- [ ] T004 [P] Download 10+ Economics 9708 sample PDFs to backend/resources/subjects/9708/sample_papers/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Alembic migration backend/alembic/versions/002_add_questions_and_subject_config.py
- [ ] T006 Add JSONB columns to subjects table: marking_config, extraction_patterns, paper_templates with GIN indexes
- [ ] T007 Create questions table with fields: id, subject_id, syllabus_point_ids (JSONB), question_text, max_marks, difficulty, source_paper, question_number, marking_scheme (JSONB), unique constraint on (subject_id, source_paper, question_number)
- [ ] T008 [P] Create exams table with fields: id, student_id, subject_id, exam_type, paper_number, question_ids (JSONB), total_marks, duration, status
- [ ] T009 [P] Create pdf_extraction_logs table with fields: id, filename, file_hash, subject_id, extraction_status, questions_extracted, errors (JSONB), processed_at
- [ ] T010 Create indexes: idx_questions_subject_id, idx_questions_difficulty, idx_questions_syllabus_points (GIN), idx_questions_source_paper, idx_exams_student_id, idx_exams_subject_id, idx_pdf_logs_file_hash
- [ ] T011 Apply migration: uv run alembic upgrade head
- [ ] T012 Manually create Economics 9708 JSONB configs and save to backend/resources/subjects/9708/marking_config.json (level descriptors L1-L4)
- [ ] T013 [P] Manually create backend/resources/subjects/9708/extraction_patterns.yaml (question delimiters, marks patterns)
- [ ] T014 [P] Manually create backend/resources/subjects/9708/paper_templates.json (Paper 1/2/3 structures)
- [ ] T015 Create Python script backend/scripts/seed_economics_config.py to insert Economics 9708 configs into database subjects table
- [ ] T016 Run seed script: uv run python backend/scripts/seed_economics_config.py

**Checkpoint**: Foundation ready - database schema complete, Economics 9708 config seeded

---

## Phase 3: User Story 3 - Cambridge Filename Parsing (Priority: P1, No Dependencies)

**Goal**: Parse Cambridge PDF filenames to extract subject code, year, session, paper type, paper number

**Independent Test**: Test with 10+ Cambridge filename formats and verify correct metadata extraction without database

### Implementation for User Story 3

- [ ] T017 [US3] Create backend/src/question_extractors/__init__.py
- [ ] T018 [US3] Implement CambridgeFilenameParser class in backend/src/question_extractors/cambridge_parser.py with regex pattern and parse() method
- [ ] T019 [US3] Add session code mapping (s→MAY_JUNE, m→FEB_MARCH, w→OCT_NOV) and year conversion (2-digit to 4-digit)
- [ ] T020 [US3] Add InvalidFilenameFormatError exception for non-Cambridge formats
- [ ] T021 [US3] Return structured ParsedFilename dataclass with subject_code, year, session, paper_type, paper_number, variant fields

### Tests for User Story 3

- [ ] T022 [P] [US3] Unit test for standard format in backend/tests/unit/test_cambridge_parser.py: 9708_s22_qp_31.pdf
- [ ] T023 [P] [US3] Unit test for mark scheme: 9708_w21_ms_32.pdf
- [ ] T024 [P] [US3] Unit test for variant: 9708_s22_qp_31_v2.pdf
- [ ] T025 [P] [US3] Unit test for different sessions: 9706_m23_qp_42.pdf
- [ ] T026 [P] [US3] Unit test for invalid format: random_economics_questions.pdf should raise InvalidFilenameFormatError

**Checkpoint**: Filename parsing working with 100% accuracy for Cambridge format (NFR-007)

---

## Phase 4: User Story 4 - PDF Question Extraction (Priority: P1, Depends on US3)

**Goal**: Extract individual questions from Economics 9708 PDFs using subject config patterns

**Independent Test**: Extract questions from 5 Economics 9708 PDFs and verify all questions extracted with correct marks (>95% accuracy per NFR-006)

### Implementation for User Story 4

- [ ] T027 [P] [US4] Create GenericExtractor class in backend/src/question_extractors/generic_extractor.py that reads patterns from subject.extraction_patterns JSONB
- [ ] T028 [P] [US4] Create extraction utility functions in backend/src/question_extractors/extraction_patterns.py for regex matching
- [ ] T029 [US4] Implement extract_text() method in GenericExtractor using pdfplumber with PyPDF2 fallback
- [ ] T030 [US4] Implement extract_questions() method that splits text by question_delimiter from config, extracts question numbers and marks
- [ ] T031 [US4] Implement _parse_question() helper that concatenates multi-page questions, filters headers/footers, handles subparts
- [ ] T032 [US4] Implement _calculate_difficulty() using heuristic: 1-12 marks=easy, 13-20=medium, 21-30=hard (per research.md)
- [ ] T033 [US4] Add header/footer filtering logic to remove "Cambridge International", page numbers, standard footer text

### Tests for User Story 4

- [ ] T034 [P] [US4] Unit test GenericExtractor with mock Economics config in backend/tests/unit/test_generic_extractor.py
- [ ] T035 [P] [US4] Integration test extracting from real Economics Paper 3 PDF (3 essay questions, 25 marks each) in backend/tests/integration/test_economics_extraction.py
- [ ] T036 [P] [US4] Integration test for Paper 2 (data response with tables)
- [ ] T037 [P] [US4] Test multi-page question handling
- [ ] T038 [P] [US4] Test subpart aggregation (1(a) + 1(b) + 1(c) = total marks)

**Checkpoint**: Extraction achieves >95% accuracy for Economics 9708 standard format (NFR-006)

---

## Phase 5: User Story 5 - Mark Scheme Extraction & Matching (Priority: P2, Depends on US1)

**Goal**: Extract marking criteria from mark scheme PDFs and match to questions

**Independent Test**: Upload question paper + mark scheme, verify 100% match rate and marking_scheme JSONB populated

### Implementation for User Story 5

- [ ] T039 [US5] Create MarkSchemeExtractor class in backend/src/question_extractors/mark_scheme_extractor.py
- [ ] T040 [US5] Implement extract_mark_schemes() method that extracts Economics level descriptors (L1-L4) from PDF text
- [ ] T041 [US5] Parse level descriptor format: "Level 4: 18-25 marks - Sophisticated analysis..."
- [ ] T042 [US5] Extract keywords, model answer points, acceptable answers from mark scheme text
- [ ] T043 [US5] Build marking_scheme JSONB structure: {version, rubric_type, levels[], keywords[], model_answer_points[], acceptable_answers[][]}
- [ ] T044 [US5] Implement match_to_questions() method that queries questions by (subject_code, year, session, paper_number) tuple
- [ ] T045 [US5] Update questions.marking_scheme JSONB field with extracted data

### Tests for User Story 5

- [ ] T046 [P] [US5] Unit test MarkSchemeExtractor parsing in backend/tests/unit/test_mark_scheme_extractor.py
- [ ] T047 [P] [US5] Integration test: upload 9708_s22_qp_31.pdf then 9708_s22_ms_31.pdf, verify automatic matching in backend/tests/integration/test_mark_scheme_matching.py
- [ ] T048 [P] [US5] Test retroactive matching (mark scheme uploaded before question paper)
- [ ] T049 [P] [US5] Test cross-subject isolation (9706 mark scheme doesn't match 9708 questions)

**Checkpoint**: Mark scheme extraction and matching achieves 100% match rate for standard format (SC-003)

---

## Phase 6: User Story 1 - Manual Question Upload & Storage (Priority: P1, Depends on US3+US4)

**Goal**: Allow teachers to upload Cambridge PDFs and store extracted questions in database

**Independent Test**: Upload single Economics PDF, verify questions stored in database with complete metadata

### Models for User Story 1

- [ ] T050 [P] [US1] Create Question model in backend/src/models/question.py with SQLModel fields matching schema
- [ ] T051 [P] [US1] Create Exam model in backend/src/models/exam.py with SQLModel fields
- [ ] T052 [P] [US1] Create PDFExtractionLog model in backend/src/models/pdf_extraction_log.py
- [ ] T053 [P] [US1] Update Subject model in backend/src/models/subject.py to add marking_config, extraction_patterns, paper_templates JSONB fields

### Schemas for User Story 1

- [ ] T054 [P] [US1] Create QuestionResponse, QuestionCreate Pydantic schemas in backend/src/schemas/question_schemas.py
- [ ] T055 [P] [US1] Create PDFUploadResponse schema with extracted_count, errors fields
- [ ] T056 [P] [US1] Update SubjectResponse schema in backend/src/schemas/subject_schemas.py to include config fields

### Services for User Story 1

- [ ] T057 [US1] Create QuestionService in backend/src/services/question_service.py with create_question(), get_question_by_id(), check_duplicate() methods
- [ ] T058 [US1] Implement SubjectConfigService in backend/src/services/subject_config_service.py to load JSONB config + resource files
- [ ] T059 [US1] Create PDFProcessingService in backend/src/services/pdf_processing_service.py that orchestrates: parse filename → extract questions → save to DB → log extraction

### API Endpoints for User Story 1

- [ ] T060 [US1] Create POST /api/questions/upload endpoint in backend/src/routes/questions.py
- [ ] T061 [US1] Implement file validation (PDF only, <10MB per NFR-010)
- [ ] T062 [US1] Calculate file hash (SHA256) and check pdf_extraction_logs for duplicates
- [ ] T063 [US1] Parse filename using CambridgeFilenameParser, return 400 if invalid format
- [ ] T064 [US1] Load subject config from database, extract questions using GenericExtractor
- [ ] T065 [US1] Save extracted questions to database with source_paper metadata, handle 409 Conflict for duplicates per unique constraint
- [ ] T066 [US1] Create pdf_extraction_logs record with SUCCESS/FAILED status and error JSONB
- [ ] T067 [US1] Return 201 with {extracted_count, questions: [...], warnings: [...]}
- [ ] T068 [US1] Create GET /api/questions/{id} endpoint returning single question with marking scheme
- [ ] T069 [US1] Register routes in backend/src/main.py

### Tests for User Story 1

- [ ] T070 [P] [US1] Unit test QuestionService CRUD operations in backend/tests/unit/test_question_service.py
- [ ] T071 [P] [US1] Integration test POST /api/questions/upload with valid Economics PDF in backend/tests/integration/test_question_routes.py
- [ ] T072 [P] [US1] Test malformed PDF returns 400 Bad Request
- [ ] T073 [P] [US1] Test duplicate question returns 409 Conflict
- [ ] T074 [P] [US1] Test non-Cambridge filename returns 400 with specific error
- [ ] T075 [P] [US1] Test GET /api/questions/{id} returns complete question object

**Checkpoint**: Teachers can upload Economics PDFs and see extracted questions in database within 30 seconds with >95% accuracy (SC-001)

---

## Phase 7: User Story 2 - Question Bank Search & Filtering (Priority: P2, Depends on US1)

**Goal**: Enable searching question bank by subject, topic, difficulty, year range

**Independent Test**: With 20+ questions stored, test search queries and verify correct filtering within 500ms

### Schemas for User Story 2

- [ ] T076 [P] [US2] Create QuestionSearchRequest schema in backend/src/schemas/question_schemas.py with filters: subject_id, syllabus_points, difficulty, year_min, year_max, marks_min, marks_max
- [ ] T077 [P] [US2] Create PaginatedQuestionResponse schema with results[], total_count, page, per_page, total_pages

### Services for User Story 2

- [ ] T078 [US2] Implement search_questions() method in QuestionService with SQLModel query builder
- [ ] T079 [US2] Add filter by subject_id (WHERE subject_id = ?)
- [ ] T080 [US2] Add filter by syllabus_points using JSONB containment (WHERE syllabus_point_ids @> ?)
- [ ] T081 [US2] Add filter by difficulty (WHERE difficulty = ?)
- [ ] T082 [US2] Add filter by year range (extract year from source_paper, WHERE year BETWEEN ? AND ?)
- [ ] T083 [US2] Add filter by marks range (WHERE max_marks BETWEEN ? AND ?)
- [ ] T084 [US2] Implement pagination with offset/limit, return 20 results per page
- [ ] T085 [US2] Sort results by year descending (newest first)

### API Endpoints for User Story 2

- [ ] T086 [US2] Create GET /api/questions endpoint in backend/src/routes/questions.py
- [ ] T087 [US2] Parse query parameters: subject_id, syllabus_points (comma-separated), difficulty, year_min, year_max, marks_min, marks_max, page, per_page
- [ ] T088 [US2] Call QuestionService.search_questions() with filters
- [ ] T089 [US2] Return 200 OK with paginated results, empty array if no matches (not 404)

### Tests for User Story 2

- [ ] T090 [P] [US2] Unit test search_questions() with various filter combinations in backend/tests/unit/test_question_service.py
- [ ] T091 [P] [US2] Integration test GET /api/questions with syllabus_points filter in backend/tests/integration/test_question_routes.py
- [ ] T092 [P] [US2] Test pagination returns correct page metadata
- [ ] T093 [P] [US2] Test no results returns empty array with total_count=0
- [ ] T094 [P] [US2] Performance test: 500+ questions, search returns within 500ms (NFR-002)

**Checkpoint**: Question search returns results within 500ms for 500+ questions (SC-005)

---

## Phase 8: User Story 7 - Syllabus Point Tagging (Priority: P3, Depends on US1)

**Goal**: Allow manual tagging of questions with syllabus points

**Independent Test**: Tag 20 questions, verify tags stored in syllabus_point_ids JSONB array

### Schemas for User Story 7

- [ ] T095 [P] [US7] Create SyllabusPointTagRequest schema in backend/src/schemas/question_schemas.py with syllabus_point_ids array
- [ ] T096 [P] [US7] Create SyllabusResponse schema for hierarchical syllabus structure

### Services for User Story 7

- [ ] T097 [US7] Implement update_syllabus_tags() method in QuestionService
- [ ] T098 [US7] Validate syllabus point IDs exist in syllabus_points table before updating
- [ ] T099 [US7] Update questions.syllabus_point_ids JSONB field
- [ ] T100 [US7] Implement get_syllabus_hierarchy() method in SubjectConfigService that queries syllabus_points with parent_code for hierarchical structure

### API Endpoints for User Story 7

- [ ] T101 [US7] Create PATCH /api/questions/{id}/tags endpoint in backend/src/routes/questions.py
- [ ] T102 [US7] Validate request body has syllabus_point_ids array
- [ ] T103 [US7] Call QuestionService.update_syllabus_tags(), return 400 if invalid syllabus point IDs
- [ ] T104 [US7] Return 200 OK with updated question
- [ ] T105 [US7] Create GET /api/subjects/{id}/syllabus endpoint in backend/src/routes/subjects.py
- [ ] T106 [US7] Return hierarchical syllabus JSON structure: [{code, name, children: [...]}, ...]

### Tests for User Story 7

- [ ] T107 [P] [US7] Unit test update_syllabus_tags() in backend/tests/unit/test_question_service.py
- [ ] T108 [P] [US7] Integration test PATCH /api/questions/{id}/tags in backend/tests/integration/test_question_routes.py
- [ ] T109 [P] [US7] Test invalid syllabus point ID returns 400
- [ ] T110 [P] [US7] Integration test GET /api/subjects/{id}/syllabus returns hierarchical structure in backend/tests/integration/test_subject_routes.py

**Checkpoint**: Syllabus tagging working, questions filterable by syllabus points

---

## Phase 9: User Story 6 - Intelligent Exam Generation (Priority: P3, Depends on US1+US2+US7)

**Goal**: Generate custom exams matching syllabus coverage, difficulty distribution, total marks

**Independent Test**: With 100+ tagged questions, generate exam with criteria and verify distribution within ±10%

### Schemas for User Story 6

- [ ] T111 [P] [US6] Create ExamGenerationRequest schema in backend/src/schemas/exam_schemas.py with subject_id, syllabus_points[], difficulty_distribution {easy, medium, hard}, total_marks, paper_type, student_id
- [ ] T112 [P] [US6] Create ExamResponse schema with id, questions[], total_marks, duration, status

### Services for User Story 6

- [ ] T113 [US6] Create ExamGenerationService in backend/src/services/exam_generation_service.py
- [ ] T114 [US6] Implement generate_exam() method with weighted random selection algorithm from research.md
- [ ] T115 [US6] Filter question candidates by subject_id, syllabus_points, exclude previously attempted questions for student
- [ ] T116 [US6] Validate sufficient questions exist to meet criteria, raise InsufficientQuestionsError if not
- [ ] T117 [US6] Group candidates by difficulty (easy, medium, hard)
- [ ] T118 [US6] Calculate target marks per difficulty based on distribution
- [ ] T119 [US6] Select questions using weighted random to respect distribution within ±10% tolerance
- [ ] T120 [US6] Validate actual distribution matches target within ±10%, retry or raise InvalidExamDistributionError
- [ ] T121 [US6] Create Exam record in database with question_ids JSONB array, status=PENDING
- [ ] T122 [US6] Return Exam object with selected questions

### API Endpoints for User Story 6

- [ ] T123 [US6] Create POST /api/exams/generate endpoint in backend/src/routes/exams.py
- [ ] T124 [US6] Validate request: subject_id exists, difficulty_distribution sums to 1.0, total_marks > 0
- [ ] T125 [US6] Call ExamGenerationService.generate_exam()
- [ ] T126 [US6] Return 201 Created with exam object
- [ ] T127 [US6] Return 422 Unprocessable Entity if insufficient questions with specific error message
- [ ] T128 [US6] Create GET /api/exams/{id} endpoint returning exam details with questions
- [ ] T129 [US6] Register routes in backend/src/main.py

### Tests for User Story 6

- [ ] T130 [P] [US6] Unit test generate_exam() algorithm in backend/tests/unit/test_exam_generation.py
- [ ] T131 [P] [US6] Test difficulty distribution validation within ±10%
- [ ] T132 [P] [US6] Test insufficient questions raises error
- [ ] T133 [P] [US6] Test student exclusion (questions already attempted)
- [ ] T134 [P] [US6] Integration test POST /api/exams/generate in backend/tests/integration/test_exam_routes.py
- [ ] T135 [P] [US6] Test exam generation completes within 5 seconds (NFR-003)
- [ ] T136 [P] [US6] Test >90% of generation requests produce valid exams (SC-004)

**Checkpoint**: Exam generation produces valid exams in >90% of requests within 5 seconds (SC-004, NFR-003)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, documentation, final validation

- [ ] T137 [P] Create API documentation in docs/api/questions.md
- [ ] T138 [P] Create API documentation in docs/api/exams.md
- [ ] T139 [P] Create API documentation in docs/api/subjects.md
- [ ] T140 Create specs/002-question-bank/CLAUDE.md with Phase II-specific AI instructions (<300 lines)
- [ ] T141 Create Phase II gate script scripts/check-phase-2-complete.sh validating: migration applied, 100+ questions extracted, API endpoints working, >80% test coverage
- [ ] T142 Run test suite: uv run pytest backend/tests/ --cov=backend/src --cov-report=term-missing
- [ ] T143 Verify >80% test coverage (Constitutional Principle VII)
- [ ] T144 Manually test: Upload 10 Economics PDFs, verify >95% extraction accuracy
- [ ] T145 Manually test: Generate 5 exams with different criteria, verify distribution within ±10%
- [ ] T146 Run Phase II gate script: ./scripts/check-phase-2-complete.sh
- [ ] T147 Create ADR for PDF extraction library choice (pdfplumber) in history/adr/002-pdf-extraction-library.md
- [ ] T148 Create ADR for subject config storage strategy (JSONB + files) in history/adr/003-subject-config-storage.md
- [ ] T149 [P] Code cleanup: Run ruff linter and mypy type checker
- [ ] T150 [P] Security review: Verify no secrets in code, all in .env
- [ ] T151 Update docs/SESSION_HANDOFF.md with Phase II completion status

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 3 (Phase 3)**: Depends on Foundational - No dependencies on other stories
- **User Story 4 (Phase 4)**: Depends on Foundational + US3
- **User Story 5 (Phase 5)**: Depends on Foundational + US1 (needs questions in DB)
- **User Story 1 (Phase 6)**: Depends on Foundational + US3 + US4
- **User Story 2 (Phase 7)**: Depends on Foundational + US1
- **User Story 7 (Phase 8)**: Depends on Foundational + US1
- **User Story 6 (Phase 9)**: Depends on Foundational + US1 + US2 + US7
- **Polish (Phase 10)**: Depends on all user stories

### Critical Path (Sequential Implementation)

1. Setup (Phase 1)
2. Foundational (Phase 2) ← CRITICAL BLOCKER
3. US3: Filename Parsing (Phase 3)
4. US4: Question Extraction (Phase 4)
5. US1: Upload & Storage (Phase 6)
6. US2: Search (Phase 7) OR US7: Tagging (Phase 8) - can parallelize
7. US5: Mark Schemes (Phase 5) - can parallelize with US2/US7
8. US6: Exam Generation (Phase 9) - requires US1+US2+US7
9. Polish (Phase 10)

### Parallel Opportunities

**Within Phases**:
- Phase 1: T003, T004 can run in parallel
- Phase 2: T008-T009, T013-T014 can run in parallel
- Phase 3: All tests T022-T026 can run in parallel
- Phase 4: T027-T028, T034-T038 (all tests) can run in parallel
- Phase 5: T046-T049 (all tests) can run in parallel
- Phase 6: T050-T053 (models), T054-T056 (schemas), T070-T075 (tests) can run in parallel
- Phase 7: T076-T077, T090-T094 (tests) can run in parallel
- Phase 8: T095-T096, T107-T110 (tests) can run in parallel
- Phase 9: T111-T112, T130-T136 (tests) can run in parallel
- Phase 10: T137-T139, T149-T150 can run in parallel

**Between User Stories** (after Foundational complete):
- US3 (Phase 3) can start immediately
- US4 (Phase 4) starts after US3 complete
- US1 (Phase 6) starts after US3+US4 complete
- US2 (Phase 7), US5 (Phase 5), US7 (Phase 8) can ALL run in parallel after US1 complete
- US6 (Phase 9) waits for US1+US2+US7

---

## Parallel Example: After Foundational Complete

```bash
# Start US3 (Filename Parsing) immediately:
Task: T017-T026 (US3 complete)

# Once US3 done, start US4 (Question Extraction):
Task: T027-T038 (US4 complete)

# Once US3+US4 done, start US1 (Upload):
Task: T050-T075 (US1 complete)

# Once US1 done, START ALL THREE IN PARALLEL:
# Developer A:
Task: T076-T094 (US2 Search)

# Developer B:
Task: T039-T049 (US5 Mark Schemes)

# Developer C:
Task: T095-T110 (US7 Tagging)

# Once US1+US2+US7 all done:
Task: T111-T136 (US6 Exam Generation)
```

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Deliver working question bank with search**:
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US3 (Filename Parsing)
4. Complete Phase 4: US4 (Question Extraction)
5. Complete Phase 6: US1 (Upload & Storage)
6. Complete Phase 7: US2 (Search)
7. **STOP and VALIDATE**: Can upload Economics PDFs and search questions
8. Deploy/demo if ready

**MVP Scope**: US3 + US4 + US1 + US2 = Working question bank (upload, search)

### Incremental Delivery

1. **Foundation** → Database ready, configs seeded
2. **+ US3** → Filename parsing works
3. **+ US4** → Question extraction works
4. **+ US1** → Upload works (MVP CORE!)
5. **+ US2** → Search works (MVP COMPLETE - deliverable!)
6. **+ US5** → Mark schemes enhance questions
7. **+ US7** → Tagging enables smart search
8. **+ US6** → Exam generation (FULL FEATURE SET!)
9. **+ Polish** → Production ready

### Recommended Approach

**Solo Developer** (Sequential):
- Phases 1-2 (Setup + Foundational): 4-6 hours
- Phase 3 (US3): 2-3 hours
- Phase 4 (US4): 4-6 hours
- Phase 6 (US1): 6-8 hours ← **MVP Core Complete**
- Phase 7 (US2): 3-4 hours ← **MVP Deliverable**
- Phase 5 (US5): 4-5 hours
- Phase 8 (US7): 3-4 hours
- Phase 9 (US6): 5-6 hours ← **Full Feature Set**
- Phase 10 (Polish): 3-4 hours
- **Total**: ~35-45 hours (5-6 days)

**Team of 3** (Parallel after Foundation):
- Day 1: All work on Phase 1-2 (Setup + Foundational) together
- Day 2: All work on Phase 3-4-6 (US3 → US4 → US1 core path)
- Day 3: Split → Dev A: US2, Dev B: US5, Dev C: US7 (all parallel)
- Day 4: Merge, then Dev A+B+C: US6 (Exam Generation)
- Day 5: Polish, testing, gate validation
- **Total**: ~5 days with parallelization

---

## Success Criteria Mapping

Phase II complete when all success criteria met:

- ✅ **SC-001** (Phase 6: US1): Teachers upload Economics PDF, see extracted questions within 30s with >95% accuracy
- ✅ **SC-002** (Phase 6: US1 + Phase 4: US4): Extract from 10 Economics PDFs with <5% manual correction
- ✅ **SC-003** (Phase 5: US5): Mark scheme matching achieves 100% match rate
- ✅ **SC-004** (Phase 9: US6): Exam generation produces valid exams (±10% distribution) in >90% of requests
- ✅ **SC-005** (Phase 7: US2): Question search <500ms for 500+ questions
- ✅ **SC-006** (Phase 6: US1): Zero duplicates (unique constraint enforced, 409 errors)
- ✅ **SC-007** (Phase 6: US1): 100% of PDFs have complete source_paper metadata
- ✅ **SC-008** (Phase 10: Polish): Gate script passes, 100+ questions, >80% coverage

---

## Notes

- [P] tasks = different files, no shared state, can run in parallel
- [US#] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Tests written during implementation for coverage, not TDD
- Constitutional requirement: >80% test coverage (Principle VII)
- Commit after each task or logical group
- Phase 2 (Foundational) is CRITICAL BLOCKER - all user stories depend on it
- MVP = US1+US2 (upload + search), Full Feature Set = all 7 user stories
- Manual config creation (T012-T014) allocated 2-3 hours per research.md
- Economics 9708 chosen as MVP subject per plan.md
