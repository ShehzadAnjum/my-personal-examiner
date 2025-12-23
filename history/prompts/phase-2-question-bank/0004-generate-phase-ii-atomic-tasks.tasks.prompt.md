---
id: 0004
title: Generate Phase II Atomic Tasks
stage: tasks
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5
feature: phase-2-question-bank
branch: 002-question-bank
user: anjum
command: /sp.tasks
labels: ["tasks", "phase-2", "question-bank", "generic-architecture", "user-stories"]
links:
  spec: specs/002-question-bank/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-question-bank/tasks.md
tests:
  - None (task generation stage)
---

## Prompt

User invoked `/sp.tasks` command after completing Phase II implementation plan.

**Context**: Following SpecKitPlus workflow after successful `/sp.plan` execution. Design documents available: plan.md (645 lines, 5 architecture decisions), spec.md (575 lines, 7 user stories with P1-P3 priorities), research.md (529 lines, 8 technology decisions).

**Requirements**: Generate atomic, testable tasks organized by user story to enable independent implementation and testing of each story. Tasks must follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`.

**User Stories from spec.md** (with priorities):
- US1 (P1): Manual Question Upload & Storage
- US2 (P2): Question Bank Search & Filtering
- US3 (P1): Cambridge Filename Parsing & Metadata Extraction
- US4 (P1): PDF Question Extraction (Economics 9708)
- US5 (P2): Mark Scheme Extraction & Matching
- US6 (P3): Intelligent Exam Generation
- US7 (P3): Syllabus Point Tagging & Mapping

**Architecture from plan.md**:
- Generic extraction framework (config-driven, not subject-specific)
- JSONB + resource files for subject configuration
- Economics 9708 as reference template
- Weighted random exam generation algorithm
- Python 3.12+, FastAPI, SQLModel, pdfplumber, PostgreSQL 16

**Task Organization Requirement**: Group by user story (not by layer like models/services/routes) to enable independent story implementation and MVP delivery.

## Response snapshot

**Tasks.md Generated**: 151 atomic tasks organized into 10 phases

**Phase Structure**:
1. **Phase 1: Setup** (4 tasks) - Project structure, dependencies, Economics sample PDFs
2. **Phase 2: Foundational** (12 tasks) - Database migration, JSONB config creation, Economics config seeding (CRITICAL BLOCKER)
3. **Phase 3: US3 - Filename Parsing** (10 tasks) - P1, no dependencies, independently testable
4. **Phase 4: US4 - Question Extraction** (12 tasks) - P1, depends on US3
5. **Phase 5: US5 - Mark Scheme Matching** (11 tasks) - P2, depends on US1
6. **Phase 6: US1 - Upload & Storage** (26 tasks) - P1, depends on US3+US4, MVP core
7. **Phase 7: US2 - Search & Filtering** (19 tasks) - P2, depends on US1, MVP complete with this
8. **Phase 8: US7 - Syllabus Tagging** (16 tasks) - P3, depends on US1
9. **Phase 9: US6 - Exam Generation** (24 tasks) - P3, depends on US1+US2+US7, full feature set
10. **Phase 10: Polish** (17 tasks) - Documentation, ADRs, gate script, test coverage validation

**Key Task Organization Features**:
- Strict checklist format: `- [ ] T001 [P] [US1] Description in file/path.py`
- [P] marker for parallelizable tasks (different files, no dependencies)
- [Story] label (US1-US7) for traceability
- Tests included for >80% coverage (Constitutional Principle VII), not TDD approach
- Each user story independently completable and testable

**Dependencies Mapped**:
- Foundational (Phase 2) BLOCKS all user stories
- Critical path: US3 → US4 → US1 (core upload functionality)
- Parallel opportunities: After US1 complete, US2 + US5 + US7 can all run in parallel
- US6 (Exam Generation) requires US1 + US2 + US7

**Implementation Strategies Provided**:
- **MVP First**: US3 + US4 + US1 + US2 = Working question bank (upload + search) in ~20-25 hours
- **Incremental Delivery**: Each story adds value independently
- **Solo Developer**: Sequential, 5-6 days (35-45 hours)
- **Team of 3**: Parallel after Foundation, 5 days with parallelization

**Success Criteria Mapped**: All 8 success criteria from spec.md mapped to specific phases (SC-001 to SC-008)

## Outcome

- ✅ Impact: Successfully generated 151 atomic tasks organized by **user story** (not technical layer) enabling independent implementation and incremental MVP delivery. Critical architectural insight: Phase 2 (Foundational) with database migration and Economics config creation is CRITICAL BLOCKER for all user stories. MVP path clearly defined: Setup → Foundational → US3 → US4 → US1 → US2 delivers working question bank in ~25 hours. Full feature set (all 7 stories) completes Phase II in 35-45 hours solo or 5 days with team of 3.

- 🧪 Tests: 61 test tasks included across all user stories for >80% coverage compliance (Constitutional Principle VII). Tests written during implementation, not TDD approach. Unit tests for parsing/extraction/services, integration tests for API endpoints, performance tests for NFR validation (e.g., search <500ms, extraction <30s).

- 📁 Files: Created `specs/002-question-bank/tasks.md` (588 lines). Tasks create 30+ new files across: models (question.py, exam.py, pdf_extraction_log.py), services (question_service.py, exam_generation_service.py, pdf_processing_service.py, subject_config_service.py), routes (questions.py, exams.py), extractors (cambridge_parser.py, generic_extractor.py, mark_scheme_extractor.py), tests (15+ test files), docs (3 API docs), ADRs (2), gate script (1).

- 🔁 Next prompts:
  1. Review tasks.md and approve task breakdown
  2. Run `/sp.implement` or begin manual implementation starting with Phase 1 (Setup)
  3. Create Phase II CLAUDE.md with AI instructions (<300 lines)
  4. Execute critical path: Setup → Foundational → US3 → US4 → US1 → US2 for MVP
  5. After implementation complete, run gate script: `./scripts/check-phase-2-complete.sh`

- 🧠 Reflection: User story organization (vs technical layer grouping) is critical for incremental delivery and MVP definition. Foundational phase (database migration + Economics config seeding) correctly identified as CRITICAL BLOCKER - all 7 user stories depend on it. Economics config creation (T012-T014) allocated 2-3 hours per research.md - this manual work proves generic architecture before AI automation in Phase V. Parallel opportunities well-defined: After Foundation complete, US2 + US5 + US7 can run concurrently if team has capacity. MVP scope (US1+US2) vs Full Feature Set (all 7 stories) distinction enables stop-and-validate checkpoints.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation workflow executed smoothly. User story extraction from spec.md, dependency analysis from plan.md, and task organization all functioned correctly. Template structure followed precisely.

- Graders run and results (PASS/FAIL): Not applicable (task generation stage, no code to grade)

- Prompt variant (if applicable): Standard `/sp.tasks` workflow from `.claude/commands/sp.tasks.md`

- Next experiment (smallest change to try): Execute `/sp.implement` to begin implementation, or manually start with Phase 1 (Setup). Validate that Foundational phase (Phase 2) blocking all stories is architecturally correct - may want to parallelize some Foundational tasks (e.g., Economics config creation can start before database migration completes). Success metric: MVP (US1+US2) deliverable in ~25 hours, Full Feature Set in 35-45 hours.
