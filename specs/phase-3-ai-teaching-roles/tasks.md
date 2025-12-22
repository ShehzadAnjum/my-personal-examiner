# Tasks: Phase III - AI Teaching Roles

**Input**: Design documents from `/specs/phase-3-ai-teaching-roles/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story (US1-US6) to enable independent implementation and testing of each AI teaching role.

**Quality Bar**: Production v1.0 (not MVP demo) - robust error handling, comprehensive testing, PhD-level quality

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions
- Path convention: `backend/src/` for all source code

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [X] T001 Install Anthropic Python SDK (anthropic>=0.40.0) in backend/pyproject.toml
- [X] T002 [P] Install OpenAI Python SDK (openai>=1.54.0) in backend/pyproject.toml
- [X] T003 [P] Install Google Generative AI SDK (google-generativeai>=0.8.0) in backend/pyproject.toml
- [X] T004 [P] Add environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY) to backend/.env.example
- [X] T005 Create backend/src/ai_integration/ directory structure
- [X] T006 Create backend/src/algorithms/ directory structure
- [X] T007 [P] Create backend/src/schemas/ directory for request/response models
- [X] T008 [P] Create backend/tests/unit/, backend/tests/integration/, backend/tests/accuracy/ directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations

- [X] T009 Create Alembic migration 003_coaching_sessions.py for coaching_sessions table in backend/alembic/versions/
- [X] T010 [P] Create Alembic migration 004_study_plans.py for study_plans table in backend/alembic/versions/
- [X] T011 [P] Create Alembic migration 005_improvement_plans.py for improvement_plans table in backend/alembic/versions/
- [X] T012 Create Alembic migration 006_attempted_questions_enhancements.py (add confidence_score, needs_review, reviewed_by, reviewed_at) in backend/alembic/versions/
- [X] T013 Run migrations and verify schema with `alembic upgrade head` ✅ COMPLETE - All 13 tables created at revision 4ac52e7be851

### Database Models

- [X] T014 [P] Create CoachingSession model in backend/src/models/coaching_session.py
- [X] T015 [P] Create StudyPlan model in backend/src/models/study_plan.py
- [X] T016 [P] Create ImprovementPlan model in backend/src/models/improvement_plan.py
- [X] T017 Enhance AttemptedQuestion model (add confidence_score, needs_review, reviewed_by, reviewed_at fields) in backend/src/models/attempted_question.py ✅ COMPLETE - Also created Attempt model

### LLM Integration Layer

- [X] T018 [P] Implement AnthropicClient (Claude Sonnet 4.5) in backend/src/ai_integration/anthropic_client.py
- [X] T019 [P] Implement OpenAIClient (GPT-4 fallback) in backend/src/ai_integration/openai_client.py
- [X] T020 [P] Implement GeminiClient (Gemini fallback) in backend/src/ai_integration/gemini_client.py
- [X] T021 Implement LLMFallbackOrchestrator (retry → cache → alt LLM → user prompt, circuit breaker) in backend/src/ai_integration/llm_fallback.py (depends on T018, T019, T020)
- [ ] T022 [P] Unit test AnthropicClient in backend/tests/unit/test_anthropic_client.py
- [ ] T023 [P] Unit test LLMFallbackOrchestrator in backend/tests/unit/test_llm_fallback.py

### Core Algorithms

- [X] T024 Implement SuperMemo 2 (SM-2) algorithm with interval/EF calculations in backend/src/algorithms/supermemo2.py
- [X] T025 [P] Implement contextual interleaving (topic relatedness, max 3 topics/day, A→B→A→C) in backend/src/algorithms/contextual_interleaving.py ✅ COMPLETE
- [X] T026 [P] Implement confidence scoring (6-signal heuristic, <70% threshold) in backend/src/algorithms/confidence_scoring.py
- [ ] T027 [P] Unit test SM-2 algorithm (I(1)=1, I(2)=6, I(n)=I(n-1)*EF, EF update formula) in backend/tests/unit/test_supermemo2.py
- [ ] T028 [P] Unit test contextual interleaving in backend/tests/unit/test_contextual_interleaving.py
- [ ] T029 [P] Unit test confidence scoring in backend/tests/unit/test_confidence_scoring.py

### Prompt Templates

- [X] T030 [P] Create teacher_prompts.py (concept explanation prompt with PhD-level quality, examples, diagrams) in backend/src/ai_integration/prompt_templates/ ✅ COMPLETE
- [X] T031 [P] Create coach_prompts.py (Socratic questioning, misconception diagnosis) in backend/src/ai_integration/prompt_templates/ ✅ COMPLETE
- [X] T032 [P] Create marker_prompts.py (AO1/AO2/AO3 strict marking, error categorization) in backend/src/ai_integration/prompt_templates/
- [X] T033 [P] Create reviewer_prompts.py (weakness analysis, A* model answer generation) in backend/src/ai_integration/prompt_templates/ ✅ COMPLETE
- [X] T034 [P] Create planner_prompts.py (study schedule optimization, topic prioritization) in backend/src/ai_integration/prompt_templates/ ✅ COMPLETE

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Teacher Agent (Priority: P1) 🎯 MVP

**Goal**: Students can request PhD-level explanations of Economics 9708 syllabus concepts with examples, diagrams, and practice problems

**Independent Test**: POST /api/teaching/explain-concept with syllabus_point_id → Returns structured explanation with key_concepts, examples[], diagrams[], practice_problems[]

### Pydantic Schemas

- [X] T035 [P] [US1] Create TeachingSchemas (ExplainConceptRequest, TopicExplanation response) in backend/src/schemas/teaching_schemas.py ✅ COMPLETE

### Service Layer

- [X] T036 [US1] Implement TeachingService.explain_concept() in backend/src/services/teaching_service.py (depends on T021, T030) ✅ COMPLETE
- [X] T037 [US1] Add diagram generation logic (Mermaid/ASCII) to TeachingService ✅ COMPLETE (integrated in T036 - LLM generates, service parses visual_aids)
- [X] T038 [US1] Add practice problem generation to TeachingService ✅ COMPLETE (integrated in T036 - LLM generates, service parses practice_problems)
- [ ] T039 [P] [US1] Unit test TeachingService in backend/tests/unit/test_teaching_service.py

### API Endpoints

- [X] T040 [US1] Create POST /api/teaching/explain-concept endpoint in backend/src/routes/teaching.py (depends on T036) ✅ COMPLETE
- [X] T041 [US1] Add error handling (404 syllabus point not found, 500 LLM failure) to teaching routes ✅ COMPLETE (integrated in T040)
- [ ] T042 [P] [US1] Integration test teaching endpoint in backend/tests/integration/test_teaching_routes.py

**Checkpoint**: User Story 1 fully functional - Students can learn any Economics 9708 topic with PhD-level teaching

---

## Phase 4: User Story 2 - Coach Agent (Priority: P1) 🎯 MVP

**Goal**: Students struggling with concepts can get personalized tutoring via Socratic questioning with adaptive follow-ups

**Independent Test**: POST /api/coaching/tutor-session → Start session → POST /api/coaching/session/{id}/respond → Get adaptive Socratic questions → GET /api/coaching/session/{id} → Retrieve full transcript

### Pydantic Schemas

- [X] T043 [P] [US2] Create CoachingSchemas (StartSessionRequest, SessionResponse, RespondRequest, TranscriptResponse) in backend/src/schemas/coaching_schemas.py ✅ COMPLETE

### Service Layer

- [X] T044 [US2] Implement CoachingService.start_tutoring_session() in backend/src/services/coaching_service.py (depends on T021, T031) ✅ COMPLETE
- [X] T045 [US2] Implement CoachingService.respond_to_coach() (append to session_transcript, generate next Socratic question) in backend/src/services/coaching_service.py ✅ COMPLETE
- [X] T046 [US2] Implement CoachingService.get_session_transcript() in backend/src/services/coaching_service.py ✅ COMPLETE
- [X] T047 [US2] Add analogy generation logic to CoachingService ✅ COMPLETE (integrated - LLM generates analogies via CoachPrompts)
- [X] T048 [US2] Add session outcome detection (resolved/needs_more_help/refer_to_teacher) in CoachingService ✅ COMPLETE (integrated - parsed from LLM response)
- [ ] T049 [P] [US2] Unit test CoachingService in backend/tests/unit/test_coaching_service.py

### API Endpoints

- [X] T050 [US2] Create POST /api/coaching/tutor-session endpoint in backend/src/routes/coaching.py (depends on T044) ✅ COMPLETE
- [X] T051 [US2] Create POST /api/coaching/session/{session_id}/respond endpoint in backend/src/routes/coaching.py (depends on T045) ✅ COMPLETE
- [X] T052 [US2] Create GET /api/coaching/session/{session_id} endpoint in backend/src/routes/coaching.py (depends on T046) ✅ COMPLETE
- [X] T053 [US2] Add error handling (500 LLM failure, 404 session not found) to coaching routes ✅ COMPLETE (integrated in T050-T052)
- [ ] T054 [P] [US2] Integration test coaching endpoints (full conversation flow) in backend/tests/integration/test_coaching_routes.py

**Checkpoint**: User Story 2 fully functional - Students can get personalized tutoring with misconception diagnosis

---

## Phase 5: User Story 3 - Examiner Enhancement (Priority: P2)

**Goal**: Exam generation avoids previously seen questions and targets identified student weaknesses for personalized practice

**Independent Test**: POST /api/exams with strategy=weakness_focused → Returns exam with questions targeting weaknesses, avoids previous questions

### Service Layer Enhancement

- [ ] T055 [US3] Add get_previous_question_ids(student_id) method to ExamGenerationService in backend/src/services/exam_generation_service.py
- [ ] T056 [US3] Add get_student_weaknesses(student_id) method (query improvement_plans) to ExamGenerationService
- [ ] T057 [US3] Enhance generate_exam() with personalization (avoid_previous=True, strategy="weakness_focused") in backend/src/services/exam_generation_service.py (depends on T055, T056)
- [ ] T058 [US3] Add difficulty_calibration logic (match student current level ±1) to ExamGenerationService
- [ ] T059 [P] [US3] Unit test enhanced ExamGenerationService in backend/tests/unit/test_exam_generation_service.py

### API Endpoints Enhancement

- [ ] T060 [US3] Enhance POST /api/exams endpoint with new parameters (strategy, avoid_previous) in backend/src/routes/exams.py (depends on T057)
- [ ] T061 [P] [US3] Integration test personalized exam generation in backend/tests/integration/test_exam_routes.py

**Checkpoint**: User Story 3 fully functional - Exams are intelligently personalized to student needs

---

## Phase 6: User Story 4 - Marker Agent (Priority: P1) 🎯 MVP

**Goal**: Economics 9708 answers receive PhD-level strict marking with AO1/AO2/AO3 breakdown, error categorization, and confidence scoring for manual review queue

**Independent Test**: POST /api/marking/mark-answer → Returns marks_awarded, ao1/ao2/ao3 scores, errors[], confidence_score, needs_review flag

### Pydantic Schemas

- [X] T062 [P] [US4] Create MarkingSchemas (MarkAnswerRequest, MarkingResult, MarkAttemptRequest, AttemptResult) in backend/src/schemas/marking_schemas.py ✅ COMPLETE

### Service Layer

- [X] T063 [US4] Implement MarkingService.mark_answer() (apply mark scheme, calculate AO scores) in backend/src/services/marking_service.py (depends on T021, T032, T026) ✅ COMPLETE
- [X] T064 [US4] Add error_detection() method (categorize AO1/AO2/AO3 errors) to MarkingService ✅ COMPLETE (integrated in T063 - LLM generates errors)
- [X] T065 [US4] Integrate confidence_scoring algorithm into mark_answer() (6 signals: length, coverage, partial marks, ambiguous language, AO3, borderline) in MarkingService ✅ COMPLETE
- [X] T066 [US4] Add needs_review flag logic (<70% confidence threshold) to MarkingService ✅ COMPLETE
- [X] T067 [US4] Implement MarkingService.mark_attempt() (mark all questions in exam attempt, aggregate scores) in backend/src/services/marking_service.py ✅ COMPLETE
- [ ] T068 [P] [US4] Unit test MarkingService in backend/tests/unit/test_marking_service.py

### API Endpoints

- [X] T069 [US4] Create POST /api/marking/mark-answer endpoint in backend/src/routes/marking.py (depends on T063) ✅ COMPLETE
- [X] T070 [US4] Create POST /api/marking/mark-attempt endpoint in backend/src/routes/marking.py (depends on T067) ✅ COMPLETE
- [X] T071 [US4] Add error handling (404 question not found, 500 marking failure) to marking routes ✅ COMPLETE (integrated in T069-T070)
- [ ] T072 [P] [US4] Integration test marking endpoints in backend/tests/integration/test_marking_routes.py

### Accuracy Validation

- [ ] T073 [US4] Create test_marking_accuracy.py with 10 sample Cambridge questions and official mark schemes in backend/tests/accuracy/
- [ ] T074 [US4] Validate marking accuracy ≥85% agreement with Cambridge mark schemes (run test_marking_accuracy.py)

**Checkpoint**: User Story 4 fully functional - Economics marking is PhD-level strict with manual review queue for low-confidence marks

---

## Phase 7: User Story 5 - Reviewer Agent (Priority: P1) 🎯 MVP

**Goal**: Students see categorized weaknesses (AO1/AO2/AO3), A* model answers with annotations, and actionable improvement plans

**Independent Test**: POST /api/feedback/analyze-weaknesses → Returns improvement_plan_id, weaknesses{AO1:[], AO2:[], AO3:[]}, action_items[] | POST /api/feedback/generate-model-answer → Returns model_answer with annotations[], comparison, key_improvements[]

### Pydantic Schemas

- [X] T075 [P] [US5] Create FeedbackSchemas (AnalyzeWeaknessesRequest, WeaknessReport, GenerateModelAnswerRequest, ModelAnswer) in backend/src/schemas/feedback_schemas.py ✅ COMPLETE

### Service Layer

- [X] T076 [US5] Implement ReviewService.analyze_weaknesses() (query attempt, categorize errors by AO) in backend/src/services/review_service.py (depends on T021, T033) ✅ COMPLETE
- [X] T077 [US5] Add create_improvement_plan() method (generate action_items from weaknesses) to ReviewService ✅ COMPLETE (integrated in T076)
- [X] T078 [US5] Implement ReviewService.generate_model_answer() (rewrite to A* standard with annotations) in backend/src/services/review_service.py ✅ COMPLETE
- [X] T079 [US5] Add comparison_generator() (side-by-side student vs. A* answer) to ReviewService ✅ COMPLETE (integrated in T078 - _generate_comparison)
- [X] T080 [US5] Add progress_comparison() method (current vs. previous attempts) to ReviewService ✅ COMPLETE (integrated in T076)
- [ ] T081 [P] [US5] Unit test ReviewService in backend/tests/unit/test_review_service.py

### API Endpoints

- [X] T082 [US5] Create POST /api/feedback/analyze-weaknesses endpoint in backend/src/routes/feedback.py (depends on T076) ✅ COMPLETE
- [X] T083 [US5] Create POST /api/feedback/generate-model-answer endpoint in backend/src/routes/feedback.py (depends on T078) ✅ COMPLETE
- [X] T084 [US5] Add error handling (404 attempt not found, 500 LLM failure) to feedback routes ✅ COMPLETE (integrated in T082-T083)
- [ ] T085 [P] [US5] Integration test feedback endpoints in backend/tests/integration/test_feedback_routes.py

**Checkpoint**: User Story 5 fully functional - Students see weaknesses, A* model answers, and improvement action items

---

## Phase 8: User Story 6 - Planner Agent (Priority: P1) 🎯 MVP

**Goal**: Students receive n-day study schedules using SuperMemo 2 spaced repetition with contextual interleaving (max 3 related topics/day), adaptive rescheduling based on performance

**Independent Test**: POST /api/planning/create-schedule → Returns plan with SM-2 intervals, 100% syllabus coverage | PATCH /api/planning/schedule/{id}/progress → Returns updated schedule with adapted EF values

### Pydantic Schemas

- [ ] T086 [P] [US6] Create PlanningSchemas (CreateScheduleRequest, StudyPlanResponse, UpdateProgressRequest, ProgressUpdate) in backend/src/schemas/planning_schemas.py

### Service Layer

- [ ] T087 [US6] Implement PlanningService.create_study_plan() (generate day-by-day schedule) in backend/src/services/planning_service.py (depends on T024, T025)
- [ ] T088 [US6] Integrate SM-2 algorithm for interval calculations (I(1)=1, I(2)=6, I(n)=I(n-1)*EF) in PlanningService
- [ ] T089 [US6] Integrate contextual_interleaving for topic grouping (max 3 related topics/day, same syllabus section) in PlanningService
- [ ] T090 [US6] Add syllabus_coverage_validation (ensure 100% coverage) to PlanningService
- [ ] T091 [US6] Implement PlanningService.get_study_plan() in backend/src/services/planning_service.py
- [ ] T092 [US6] Implement PlanningService.update_progress() (adapt EF based on performance, reschedule topics) in backend/src/services/planning_service.py
- [ ] T093 [US6] Add performance_to_quality mapping (marks % → SM-2 quality 0-5) in PlanningService
- [ ] T094 [P] [US6] Unit test PlanningService (validate SM-2 calculations, interleaving patterns, EF updates) in backend/tests/unit/test_planning_service.py

### API Endpoints

- [ ] T095 [US6] Create POST /api/planning/create-schedule endpoint in backend/src/routes/planning.py (depends on T087)
- [ ] T096 [US6] Create GET /api/planning/schedule/{plan_id} endpoint in backend/src/routes/planning.py (depends on T091)
- [ ] T097 [US6] Create PATCH /api/planning/schedule/{plan_id}/progress endpoint in backend/src/routes/planning.py (depends on T092)
- [ ] T098 [US6] Add error handling (404 plan not found, 400 invalid date) to planning routes
- [ ] T099 [P] [US6] Integration test planning endpoints (full schedule lifecycle) in backend/tests/integration/test_planning_routes.py

**Checkpoint**: User Story 6 fully functional - Students have evidence-based study plans with adaptive spaced repetition

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Integration, testing, and production readiness across all 6 AI teaching roles

### Custom Skills

- [ ] T100 [P] Create phd-pedagogy.md skill (evidence-based teaching strategies) in .claude/skills/
- [ ] T101 [P] Create a-star-grading-rubrics.md skill (Cambridge A* criteria) in .claude/skills/
- [ ] T102 [P] Create subject-economics-9708.md skill (Economics domain knowledge) in .claude/skills/
- [ ] T103 [P] Create supermemo2-scheduling.md skill (SM-2 algorithm skill) in .claude/skills/
- [ ] T104 [P] Create contextual-interleaving.md skill (interleaving strategy skill) in .claude/skills/
- [ ] T105 [P] Create anthropic-api-patterns.md skill (Claude integration patterns) in .claude/skills/
- [ ] T106 [P] Create confidence-scoring.md skill (marking confidence calculation) in .claude/skills/

### Agent Definitions

- [ ] T107 [P] Create Teacher Agent definition in .claude/agents/08-teacher.md
- [ ] T108 [P] Create Coach Agent definition in .claude/agents/09-coach.md
- [ ] T109 [P] Create Examiner Agent definition in .claude/agents/10-examiner.md
- [ ] T110 [P] Create Marker Agent definition in .claude/agents/11-marker.md
- [ ] T111 [P] Create Reviewer Agent definition in .claude/agents/12-reviewer.md
- [ ] T112 [P] Create Planner Agent definition in .claude/agents/13-planner.md

### End-to-End Testing

- [ ] T113 Create test_end_to_end_workflow.py (full learning cycle: Teacher→Coach→Examiner→Marker→Reviewer→Planner) in backend/tests/integration/
- [ ] T114 Run end-to-end test and validate all 6 roles work together without errors
- [ ] T115 Validate quickstart.md test guide (run all curl examples, verify expected responses) in specs/phase-3-ai-teaching-roles/quickstart.md

### Architecture Decision Records

- [ ] T116 [P] Create ADR 003-sm2-algorithm-choice.md (why SuperMemo 2) in history/adr/
- [ ] T117 [P] Create ADR 004-llm-fallback-strategy.md (double fallback approach) in history/adr/
- [ ] T118 [P] Create ADR 005-confidence-threshold.md (70% manual review threshold) in history/adr/

### Performance & Quality

- [ ] T119 Run pytest with coverage (target ≥80%) for all Phase III code
- [ ] T120 Validate LLM response times (<5s Teacher/Coach, <10s Marker timeout)
- [ ] T121 Validate 100% syllabus coverage in sample study plans
- [ ] T122 Code cleanup and refactoring (remove debug code, optimize imports)

### Documentation

- [ ] T123 [P] Create specs/phase-3-ai-teaching-roles/CLAUDE.md (<300 lines) with Phase III AI instructions
- [ ] T124 Update SESSION_HANDOFF.md with Phase III completion status in docs/
- [ ] T125 Run scripts/check-phase-3-complete.sh phase gate validation

**Final Checkpoint**: All 6 AI teaching roles production-ready - Phase III complete ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 → US2 → US4 → US5 → US6 → US3
  - Priority order rationale: Teacher/Coach/Marker/Reviewer are core learning cycle (P1), Planner enhances learning (P1), Examiner enhancement is improvement (P2)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Teacher)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US2 (Coach)**: Can start after Foundational (Phase 2) - Independent of US1
- **US3 (Examiner)**: Can start after Foundational (Phase 2) - Uses improvement_plans from US5, but fallback to default generation
- **US4 (Marker)**: Can start after Foundational (Phase 2) - Independent, but US1/US2 provide learning → testing flow
- **US5 (Reviewer)**: Can start after Foundational (Phase 2) - Requires marked attempts from US4 for full testing
- **US6 (Planner)**: Can start after Foundational (Phase 2) - Uses weaknesses from US5 for prioritization, but can use defaults

### Within Each User Story

- Schemas before services (Pydantic validation models)
- Services before endpoints (business logic before API)
- Core implementation before integration
- Tests can be written in parallel (marked with [P])
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**:
- T002 (OpenAI), T003 (Gemini), T004 (env vars), T007 (schemas dir), T008 (tests dir) can run in parallel

**Foundational Phase**:
- Migrations: T010, T011 can run in parallel after T009
- Models: T014, T015, T016 can run in parallel
- LLM Clients: T018, T019, T020 can run in parallel
- Algorithms: T025, T026 can run in parallel after T024
- Algorithm Tests: T027, T028, T029 can run in parallel
- Prompt Templates: T030, T031, T032, T033, T034 can all run in parallel

**User Story Phases** (after Foundational complete):
- US1, US2, US4, US5, US6 can all start in parallel (if team capacity allows)
- US3 should wait for US5 completion for full personalization testing

**Polish Phase**:
- Skills: T100-T106 can all run in parallel
- Agents: T107-T112 can all run in parallel
- ADRs: T116-T118 can all run in parallel

---

## Implementation Strategy

### Recommended Sequence (Single Developer)

1. **Week 1: Foundation + Core Learning (US1, US2, US4)**
   - Days 1-2: Phase 1 (Setup) + Phase 2 (Foundational) → Foundation ready
   - Day 3: Phase 3 (Teacher Agent - US1) → Test independently
   - Day 4: Phase 4 (Coach Agent - US2) → Test independently
   - Day 5: Phase 6 (Marker Agent - US4) → Test independently + Accuracy validation

2. **Week 2: Advanced Features + Integration (US5, US6, US3)**
   - Day 6: Phase 7 (Reviewer Agent - US5) → Test independently
   - Day 7: Phase 8 (Planner Agent - US6) → Test independently
   - Day 8: Phase 5 (Examiner Enhancement - US3) → Test independently
   - Day 9: Phase 9 (Polish, end-to-end tests, ADRs)
   - Day 10: Phase 9 (Final validation, quickstart testing, phase gate)

### Parallel Team Strategy

With 3 developers after Foundational completion:
- **Developer A**: US1 (Teacher) → US4 (Marker) → Polish
- **Developer B**: US2 (Coach) → US5 (Reviewer) → End-to-end testing
- **Developer C**: US6 (Planner) → US3 (Examiner) → Documentation

### MVP Milestones

**MVP v1** (Core Learning Cycle):
- Foundation + US1 (Teacher) + US2 (Coach) + US4 (Marker) = Students can learn, get help, take exams, get marked

**MVP v2** (Feedback Loop):
- MVP v1 + US5 (Reviewer) = Students see weaknesses and A* model answers

**MVP v3** (Complete System):
- MVP v2 + US6 (Planner) + US3 (Examiner) = Full personalized learning system with evidence-based scheduling

---

## Notes

- **[P] tasks** = different files, no dependencies, can execute in parallel
- **[Story] label** = maps task to specific user story for traceability
- **Production v1.0 quality bar**: Every task requires robust error handling, comprehensive testing, PhD-level output quality
- **Constitutional compliance**: All tasks align with 11 non-negotiable principles (Subject Accuracy, A* Standard, Multi-Tenant, Constructive Feedback, 80% Coverage)
- **Commit strategy**: Commit after completing each user story phase (checkpoints)
- **Testing first**: For critical algorithms (SM-2, confidence scoring), write unit tests before implementation
- **Stop at checkpoints**: Validate each user story works independently before proceeding

---

**Tasks Version**: 1.0.0
**Created**: 2025-12-20
**Total Tasks**: 125 atomic tasks across 9 phases
**Estimated Effort**: 7-10 days (focused implementation with production-grade testing)
