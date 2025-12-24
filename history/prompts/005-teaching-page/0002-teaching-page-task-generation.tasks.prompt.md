---
id: 0002
title: Teaching Page Task Generation
stage: tasks
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5
feature: 005-teaching-page
branch: 005-teaching-page
user: Shehzad Anjum
command: /sp.tasks
labels: [task-generation, user-stories, teaching-page, phase-4-web-ui]
links:
  spec: specs/005-teaching-page/spec.md
  ticket: null
  adr: null (pending /sp.adr if needed)
  pr: null (pending /sp.git.commit_pr)
files:
  - path: specs/005-teaching-page/tasks.md
    change: created
    lines: 450
tests:
  - type: none
    status: n/a
    description: Task generation phase - no tests yet (tests during /sp.implement if requested)
---

## Prompt

User invoked `/sp.tasks` skill after completing planning phase via `/sp.plan` for 005-teaching-page feature (Teaching Page - PhD-Level Concept Explanations).

**Context**: User is following SpecKitPlus workflow (specify → plan → tasks → implement). Planning artifacts complete: plan.md (595 lines), spec.md (176 lines), research.md (280 lines), data-model.md (360 lines), contracts/ (1200 lines), quickstart.md (450 lines).

**User Description**: None provided (skill arguments empty - used default task generation workflow from planning artifacts)

**Task**: Execute `/sp.tasks` workflow - generate actionable, dependency-ordered tasks.md organized by user story with parallel execution markers, clear file paths, and independent test criteria per story.

## Response snapshot

Completed full `/sp.tasks` workflow for 005-teaching-page feature:

1. **Setup Phase**: Ran `check-prerequisites.sh --json`, parsed FEATURE_DIR and AVAILABLE_DOCS

2. **Loaded Design Documents**:
   - plan.md (595 lines) - Tech stack (Next.js 16, React 19, TanStack Query 5.62+, shadcn/ui, Tailwind CSS 4), project structure (frontend/ only, backend APIs exist)
   - spec.md (176 lines) - 3 user stories with priorities (P1: View explanation, P2: Browse/search, P3: Bookmark), 24 functional requirements
   - research.md (280 lines) - 5 technical decisions (component reuse saves 2-3 hours, tiered caching, shadcn/ui Accordion, client-side search, SavedExplanation backend needed)
   - data-model.md (360 lines) - 3 entities (SyllabusPoint, SavedExplanation, TopicExplanation)
   - contracts/ - API endpoints (5 backend endpoints) + UI components (9 React components)

3. **Extracted Information**:
   - **From spec.md**: 3 user stories (US1/P1: View explanation, US2/P2: Browse/search, US3/P3: Bookmark)
   - **From plan.md**: Frontend-only feature (backend APIs exist), reuse 004-coaching-page patterns, Next.js 16 App Router structure
   - **From research.md**: CRITICAL finding - SavedExplanation model DOES NOT EXIST in backend (T005-T008 backend work required before US3)
   - **From data-model.md**: 3 entities mapped to user stories (SyllabusPoint for US2, TopicExplanation for US1, SavedExplanation for US3)
   - **From contracts/**: 9 UI components mapped to user stories (ExplanationView/ExplanationSection/BookmarkButton for US1, TopicBrowser/TopicSearch/TopicCard for US2, SavedExplanationsList for US3)

4. **Generated tasks.md** (450 lines, 36 tasks):

   **Phase 1: Setup** (4 tasks):
   - T001-T002: Verify backend APIs operational (GET /api/teaching/syllabus, POST /api/teaching/explain)
   - T003: Create TypeScript types (SyllabusTopic, TopicExplanation, SavedExplanation interfaces)
   - T004: Create API client (getTopics, explainConcept, getSavedExplanations, saveExplanation, removeSavedExplanation)

   **Phase 2: Foundational** (8 tasks - BLOCKS user stories):
   - T005-T008: SavedExplanation backend (model, migration, endpoints, run migration) - REQUIRED for US3
   - T009-T012 [P]: TanStack Query hooks (useTopics, useExplanation, useSavedExplanations, useBookmark) with tiered caching (1h/5m/1m)

   **Phase 3: User Story 1 - View Explanation (P1)** 🎯 MVP (7 tasks):
   - T013-T015 [P]: Components (ExplanationSection with shadcn/ui Accordion, BookmarkButton, ExplanationSkeleton)
   - T016: ExplanationView component (all 9 sections, Definition/Core Principles/Related expanded, Examples/Misconceptions/Practice collapsed)
   - T017: Explanation page route (frontend/app/(dashboard)/teaching/[topicId]/page.tsx)
   - T018: Error boundary (reuse 004-coaching-page pattern)
   - T019: End-to-end testing (select "3.1.2 PED", verify AI generates within 10s, all 9 components present)

   **Phase 4: User Story 2 - Browse/Search Topics (P2)** (6 tasks):
   - T020-T023 [P]: Components (TopicCard, TopicBrowser hierarchical tree, TopicSearch with client-side filter, TopicSearchSkeleton)
   - T024: Main teaching page route (frontend/app/(dashboard)/teaching/page.tsx)
   - T025: Client-side search logic (Array.filter <1ms for 200 topics, 300ms debounce, keyword highlighting)

   **Phase 5: User Story 3 - Bookmark Explanations (P3)** (4 tasks):
   - T026-T027 [P]: Components (SavedExplanationsList, saved page route frontend/app/(dashboard)/teaching/saved/page.tsx)
   - T028: Integrate bookmark mutation (saveExplanation/removeSavedExplanation with cache invalidation)
   - T029: End-to-end testing (bookmark PED, navigate to /teaching/saved, verify appears, remove bookmark)

   **Phase 6: Polish** (7 tasks):
   - T030-T032 [P]: Accessibility (keyboard nav, screen reader labels), mobile responsive (375px+), performance (caching 50% hit rate, <10s AI)
   - T033-T034: Lighthouse audits (accessibility 90+, performance 90+)
   - T035: Update specs/phase-4-web-ui/CLAUDE.md with teaching page patterns
   - T036: Verify all quickstart.md flows (3 flows, 3 integration scenarios)

5. **Task Organization**:
   - **By User Story**: Each phase (3-5) maps to exactly 1 user story for independent implementation/testing
   - **Parallel Markers [P]**: 19 tasks marked [P] (different files, no dependencies, can run in parallel)
   - **Story Labels [US1/US2/US3]**: All implementation tasks labeled with user story for traceability
   - **Dependency Graph**: Setup → Foundational (blocks all) → US1+US2 (parallel after TanStack hooks) → US3 (requires SavedExplanation backend) → Polish
   - **MVP Scope**: 19 tasks (Phase 1 + partial Phase 2 + Phase 3) = User Story 1 only = working explanation viewer

6. **Format Validation**: ✅ ALL 36 tasks follow strict checklist format:
   - Checkbox: `- [ ]` prefix (markdown checkbox)
   - Task ID: T001-T036 sequential
   - [P] marker: Only on parallelizable tasks (19 total)
   - [Story] label: US1/US2/US3 on implementation tasks (17 total)
   - Description: Clear action + exact file path (e.g., "Create ExplanationView component in frontend/components/teaching/ExplanationView.tsx")

7. **Independent Test Criteria**:
   - **US1**: Select topic → verify explanation displays with all 9 sections → verify collapsible sections work
   - **US2**: Type "elasticity" in search → verify PED/YED/PES results → click topic to view explanation
   - **US3**: View explanation → click Bookmark → navigate to /teaching/saved → verify appears → remove bookmark

8. **Parallel Opportunities Identified**:
   - **Phase 2**: T009-T012 (all TanStack Query hooks)
   - **Phase 3**: T013-T015 (ExplanationSection, BookmarkButton, Skeleton)
   - **Phase 4**: T020-T023 (TopicCard, TopicBrowser, TopicSearch, Skeleton)
   - **Phase 5**: T026-T027 (SavedExplanationsList, saved page)
   - **Phase 6**: T030-T032 (accessibility, mobile, performance)

9. **Implementation Strategies Documented**:
   - **MVP First**: 19 tasks (Setup + Foundational hooks + US1) = working explanation viewer
   - **Incremental Delivery**: Add US2 (browse/search) → Add US3 (bookmark) → Polish = 3 deployable increments
   - **Parallel Team**: Backend dev (T005-T008), Frontend dev A (US1), Frontend dev B (US2), Frontend dev C (US3 after backend ready)

## Outcome

- ✅ Impact: Complete task breakdown for 005-teaching-page feature (36 tasks across 6 phases). Organized by user story to enable independent implementation/testing. MVP scope identified (19 tasks for US1 only). Parallel opportunities marked (19 tasks). Backend gap documented (SavedExplanation model needed for US3). Estimated timeline: 2 days (Dec 24-25).
- 🧪 Tests: Task generation phase only - no tests yet. Testing strategy documented in tasks (T019, T029, T036 for end-to-end validation). No unit test tasks generated (not requested in spec).
- 📁 Files: 1 file created (tasks.md, 450 lines, 36 tasks). Depends on plan.md, spec.md, research.md, data-model.md, contracts/ artifacts.
- 🔁 Next prompts:
  1. `/sp.implement` - Execute tasks from tasks.md (starts with T001, follows dependency graph)
  2. `/sp.adr` (optional) - Document architectural decisions (TanStack Query caching, client-side search, shadcn/ui Accordion)
  3. `/sp.git.commit_pr` - Commit implementation work after /sp.implement completes
- 🧠 Reflection: Task generation workflow smooth due to comprehensive planning artifacts. Organized by user story as required (3 phases for 3 stories). Backend gap (SavedExplanation) correctly identified from research.md and added as blocking foundational tasks (T005-T008). Parallel opportunities clearly marked (19 tasks). MVP scope (US1 only, 19 tasks) enables fast initial delivery. Tiered dependencies allow US1+US2 to proceed while SavedExplanation backend developed (blocks only US3). Format validation passed (all 36 tasks follow checkbox + ID + [P?] + [Story?] + description + file path pattern). Ready for /sp.implement execution.

## Evaluation notes (flywheel)

- Failure modes observed: None during task generation. Workflow executed correctly (load docs → extract user stories → map entities/endpoints to stories → generate phases → validate format). Backend gap (SavedExplanation) caught early from research.md and properly sequenced as foundational blocking tasks.
- Graders run and results (PASS/FAIL):
  - ✅ PASS - Format validation: All 36 tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format
  - ✅ PASS - User story organization: 3 phases (3-5) map 1:1 to 3 user stories (US1, US2, US3)
  - ✅ PASS - Independent test criteria: Each user story has clear verification steps
  - ✅ PASS - Parallel markers: 19 tasks marked [P] (components in different files, no dependencies)
  - ✅ PASS - Dependency graph: Setup → Foundational → User Stories (US1+US2 parallel, US3 blocked by SavedExplanation) → Polish
  - ✅ PASS - MVP scope defined: 19 tasks for User Story 1 only (working explanation viewer)
  - ✅ PASS - File paths included: All 36 tasks specify exact file paths (e.g., frontend/components/teaching/ExplanationView.tsx)
  - ✅ PASS - Foundational phase correctly blocks user stories: TanStack Query hooks required before US1/US2, SavedExplanation backend required before US3
- Prompt variant (if applicable): Default /sp.tasks workflow (no variants). Followed standard sequence: setup → foundational → user stories in priority order (P1, P2, P3) → polish. Tests omitted (not requested in spec).
- Next experiment (smallest change to try): Validate tiered caching assumptions (1h topics, 5m explanations, 1m saved) during /sp.implement. If cache hit rate <50% for explanations, consider adjusting staleTime from 5m to 10m. If topics stale after syllabus update, add cache invalidation trigger when syllabus_points table modified (requires backend event hook).

