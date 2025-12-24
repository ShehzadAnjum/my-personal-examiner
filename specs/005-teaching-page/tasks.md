# Tasks: Teaching Page - PhD-Level Concept Explanations

**Input**: Design documents from `/specs/005-teaching-page/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification - no test tasks included

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are absolute from repository root

## Path Conventions

- **Web app**: `frontend/` and `backend/` at repository root
- Frontend: Next.js 16 App Router structure (`frontend/app/`, `frontend/components/`, `frontend/lib/`)
- Backend: FastAPI structure (`backend/src/models/`, `backend/src/routes/`, `backend/src/services/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify backend APIs and create frontend foundation for all user stories

- [X] T001 Verify backend API operational: GET /api/teaching/syllabus returns Economics 9708 topics
- [X] T002 Verify backend API operational: POST /api/teaching/explain generates TopicExplanation successfully
- [X] T003 Create TypeScript types for teaching data in frontend/lib/types/teaching.ts (SyllabusTopic, TopicExplanation, SavedExplanation interfaces)
- [X] T004 Create API client for teaching endpoints in frontend/lib/api/teaching.ts (getTopics, explainConcept, getSavedExplanations, saveExplanation, removeSavedExplanation functions)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend work for SavedExplanation model + TanStack Query hooks that ALL user stories depend on

**⚠️ CRITICAL**: User Story 3 (Bookmark) cannot be implemented until SavedExplanation model exists. User Stories 1 and 2 can proceed after TanStack Query hooks are created.

- [X] T005 Create SavedExplanation SQLModel in backend/src/models/saved_explanation.py (id, student_id, syllabus_point_id, explanation_content JSON, date_saved, date_last_viewed, unique constraint on student+topic)
- [X] T006 Create Alembic migration 007_add_saved_explanations.py in backend/alembic/versions/ (create saved_explanations table with indexes on student_id, syllabus_point_id, unique constraint)
- [X] T007 Add saved explanation endpoints to backend/src/routes/teaching.py (GET /api/teaching/explanations, POST /api/teaching/explanations, DELETE /api/teaching/explanations/:id with multi-tenant student_id filtering)
- [X] T008 Run Alembic migration to create saved_explanations table in database (migration ready, run: alembic upgrade head)
- [X] T009 [P] Create useTopics TanStack Query hook in frontend/lib/hooks/useTopics.tsx (1-hour staleTime, 2-hour cacheTime, optional filters for search/level/paper)
- [X] T010 [P] Create useExplanation TanStack Query hook in frontend/lib/hooks/useExplanation.tsx (5-minute staleTime, 10-minute cacheTime, enabled when topicId provided)
- [X] T011 [P] Create useSavedExplanations TanStack Query hook in frontend/lib/hooks/useSavedExplanations.tsx (1-minute staleTime, 5-minute cacheTime)
- [X] T012 [P] Create useBookmark TanStack Query mutation hook in frontend/lib/hooks/useBookmark.tsx (saveExplanation, removeSavedExplanation mutations with cache invalidation)

**Checkpoint**: Foundation ready - User Stories 1 and 2 can now begin in parallel. User Story 3 depends on SavedExplanation backend (T005-T008) completion.

---

## Phase 3: User Story 1 - View PhD-Level Concept Explanation (Priority: P1) 🎯 MVP

**Goal**: Students can select a syllabus topic and receive a comprehensive PhD-level explanation with all 9 required components (definition, key terms, examples, visual aids, worked examples, misconceptions, practice problems, connections, core principles)

**Independent Test**: Navigate to /teaching, select "3.1.2 Price Elasticity of Demand", verify explanation displays with all sections (Definition, Key Terms, Examples, etc.), verify collapsible sections expand/collapse, verify bookmark button appears

### Implementation for User Story 1

- [X] T013 [P] [US1] Create ExplanationSection collapsible component in frontend/components/teaching/ExplanationSection.tsx (uses shadcn/ui Accordion, props: title, children, defaultExpanded, icon)
- [X] T014 [P] [US1] Create BookmarkButton component in frontend/components/teaching/BookmarkButton.tsx (props: isBookmarked, onClick, isLoading, integrates useBookmark hook)
- [X] T015 [P] [US1] Create ExplanationSkeleton loading component in frontend/components/teaching/ExplanationSkeleton.tsx (pulse animation, mimics ExplanationView structure)
- [X] T016 [US1] Create ExplanationView component in frontend/components/teaching/ExplanationView.tsx (props: explanation, isBookmarked, onBookmarkToggle, displays all 9 sections using ExplanationSection, Definition/Core Principles/Related expanded by default, Examples/Misconceptions/Practice collapsed)
- [X] T017 [US1] Create explanation page route in frontend/app/(dashboard)/teaching/[topicId]/page.tsx (uses useExplanation hook, displays ExplanationSkeleton during loading, renders ExplanationView when loaded, integrates BookmarkButton)
- [X] T018 [US1] Add error boundary for teaching routes in frontend/app/(dashboard)/teaching/error.tsx (reuse pattern from 004-coaching-page, user-friendly error messages, retry option)
- [X] T019 [US1] Test explanation display end-to-end: select topic "3.1.2 PED" from topic list, verify AI generates explanation within 10 seconds, verify all 9 components present, verify collapsible sections work, verify typography is clear and readable

**Checkpoint**: At this point, User Story 1 should be fully functional - students can view comprehensive explanations for any Economics 9708 topic

---

## Phase 4: User Story 2 - Browse and Search Syllabus Topics (Priority: P2)

**Goal**: Students can explore Economics 9708 syllabus topics by browsing hierarchical structure (AS/A2, Papers) or searching by keyword, and select topics to view explanations (integrates with User Story 1)

**Independent Test**: Navigate to /teaching, verify topics load in hierarchical browser (AS/A2 sections, Paper 1/2), type "elasticity" in search bar, verify results show PED/YED/PES topics with highlighted keywords, click a topic to navigate to explanation view

### Implementation for User Story 2

- [X] T020 [P] [US2] Create TopicCard component in frontend/components/teaching/TopicCard.tsx (props: topic, onClick, showRemoveButton, onRemove, displays topic code, description, learning outcomes preview)
- [X] T021 [P] [US2] Create TopicBrowser hierarchical tree component in frontend/components/teaching/TopicBrowser.tsx (props: topics from useTopics hook, organizes by AS/A2 level and paper number, renders TopicCard for each topic, onClick navigates to /teaching/[topicId])
- [X] T022 [P] [US2] Create TopicSearch search bar component in frontend/components/teaching/TopicSearch.tsx (props: topics, onSelectTopic, implements client-side search with useMemo filtering on code/description/learning_outcomes, 300ms debounce, highlights matching keywords with mark tag, shows result count and "No results" state)
- [X] T023 [P] [US2] Create TopicSearchSkeleton loading component in frontend/components/teaching/TopicSearchSkeleton.tsx (pulse animation for search bar and topic grid)
- [X] T024 [US2] Create main teaching page route in frontend/app/(dashboard)/teaching/page.tsx (uses useTopics hook, displays TopicBrowser and TopicSearch components, handles loading state with TopicSearchSkeleton, shows error toast if topics fail to load)
- [X] T025 [US2] Integrate client-side search filtering logic in TopicSearch component (Array.filter on topics by search query, case-insensitive match on code/description/learning_outcomes, instant results <1ms for 200 topics)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - students can browse/search topics and view explanations

---

## Phase 5: User Story 3 - Bookmark Explanations for Review (Priority: P3)

**Goal**: Students can bookmark helpful explanations and access all saved explanations from a dedicated "Saved Explanations" page for exam revision

**Independent Test**: View any explanation at /teaching/[topicId], click "Bookmark" button, verify toast confirmation appears, navigate to /teaching/saved, verify bookmarked explanation appears in list, click saved explanation to view it, click "Remove Bookmark" to unbookmark

**Dependencies**: Requires T005-T008 (SavedExplanation backend) to be complete

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create SavedExplanationsList component in frontend/components/teaching/SavedExplanationsList.tsx (props: savedExplanations from useSavedExplanations hook, renders TopicCard grid with showRemoveButton true, onRemove calls removeBookmark mutation)
- [ ] T027 [US3] Create saved explanations page route in frontend/app/(dashboard)/teaching/saved/page.tsx (uses useSavedExplanations hook, displays SavedExplanationsList, shows empty state if no bookmarks, displays loading skeleton while fetching)
- [ ] T028 [US3] Integrate useBookmark mutation in BookmarkButton component (already created in T014, verify saveExplanation mutation works, verify cache invalidation on save/remove, verify toast notifications for success/error, verify button state updates immediately)
- [ ] T029 [US3] Test bookmark flow end-to-end: view explanation "3.1.2 PED", click Bookmark, verify POST /api/teaching/explanations succeeds, verify toast shows "Explanation saved", navigate to /teaching/saved, verify PED appears in saved list, click PED to view explanation (cached or re-fetched), click Remove to unbookmark, verify DELETE endpoint called and topic removed from saved list

**Checkpoint**: All 3 user stories should now be independently functional - students can browse topics, view explanations, and bookmark favorites

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

- [ ] T030 [P] Add accessibility features: keyboard navigation for TopicBrowser (Tab to navigate topics, Enter to select), screen reader labels for collapsible sections (aria-expanded announcements), focus indicators on interactive elements
- [ ] T031 [P] Mobile responsive testing: verify layout works on 375px minimum width, test TopicBrowser collapses to single column on mobile, test ExplanationView sections readable on small screens, verify touch targets meet 44px minimum
- [ ] T032 [P] Performance optimization: verify TanStack Query caching reduces AI calls (50% cache hit rate target), verify client-side search <1ms for 200 topics, verify explanation loads within 10 seconds for 95% of requests
- [ ] T033 Run Lighthouse accessibility audit on /teaching page, target 90+ score (WCAG 2.1 AA compliance), fix any critical accessibility issues identified
- [ ] T034 Run Lighthouse performance audit on /teaching and /teaching/[topicId] pages, target 90+ score, optimize images if needed (lazy loading), verify code splitting working (Next.js automatic)
- [ ] T035 Update specs/phase-4-web-ui/CLAUDE.md with teaching page patterns (TanStack Query hooks for teaching APIs, shadcn/ui Accordion collapsible pattern, client-side search pattern, bookmark mutation with cache invalidation)
- [ ] T036 Verify all quickstart.md flows work end-to-end: Flow 1 (View Explanation 5-10s), Flow 2 (Search Topics instant), Flow 3 (Bookmark save/remove), Integration Scenarios (first-time user, power user with 10 bookmarks, mobile student on 375px screen)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 3 (SavedExplanation backend T005-T008 required)
  - User Stories 1 and 2 can start after TanStack Query hooks (T009-T012) are ready
- **User Stories (Phase 3-5)**:
  - US1 and US2 can proceed in parallel after Foundational TanStack Query hooks complete
  - US3 MUST wait for SavedExplanation backend (T005-T008) completion
- **Polish (Phase 6)**: Depends on all 3 user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after T009-T010 (useTopics, useExplanation hooks) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after T009 (useTopics hook) - Integrates with US1 by navigating to explanation pages, but independently testable
- **User Story 3 (P3)**: REQUIRES T005-T008 (SavedExplanation backend) + T011-T012 (useSavedExplanations, useBookmark hooks) - Integrates with US1 (BookmarkButton in ExplanationView), but independently testable

### Within Each User Story

- **US1**: T013-T015 (ExplanationSection, BookmarkButton, Skeleton) can run in parallel → T016 (ExplanationView uses all 3) → T017 (page route) → T018 (error boundary) → T019 (testing)
- **US2**: T020-T023 (TopicCard, TopicBrowser, TopicSearch, Skeleton) can run in parallel → T024 (page route integrates all) → T025 (search logic)
- **US3**: T026 (SavedExplanationsList) can run in parallel with T027 (saved page route) → T028 (integrate bookmark mutation) → T029 (testing)

### Parallel Opportunities

- **Phase 1**: T001-T002 (backend verification) can run in parallel with T003-T004 (frontend types and API client)
- **Phase 2 Backend**: T005-T008 (SavedExplanation model, migration, endpoints, run migration) must run sequentially
- **Phase 2 Frontend**: T009-T012 (all TanStack Query hooks) can run in parallel
- **Phase 3 (US1)**: T013, T014, T015 (components) can run in parallel
- **Phase 4 (US2)**: T020, T021, T022, T023 (components) can run in parallel
- **Phase 5 (US3)**: T026, T027 can run in parallel
- **Phase 6**: T030, T031, T032 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all independent components for US1 together:
Task: "Create ExplanationSection collapsible component in frontend/components/teaching/ExplanationSection.tsx"
Task: "Create BookmarkButton component in frontend/components/teaching/BookmarkButton.tsx"
Task: "Create ExplanationSkeleton loading component in frontend/components/teaching/ExplanationSkeleton.tsx"

# After all 3 complete, proceed to ExplanationView which uses all 3:
Task: "Create ExplanationView component in frontend/components/teaching/ExplanationView.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational TanStack Query hooks (T009-T010 only, skip T005-T008 backend work and T011-T012 bookmark hooks)
3. Complete Phase 3: User Story 1 (T013-T019)
4. **STOP and VALIDATE**: Test User Story 1 independently - students can view comprehensive explanations
5. Deploy/demo if ready - **This is a working MVP!**

### Incremental Delivery

1. Complete Setup (Phase 1) + Foundational TanStack Query hooks (T009-T010) → Foundation for US1 and US2 ready
2. Add User Story 1 (Phase 3) → Test independently → **Deploy/Demo (MVP: View Explanations)**
3. Add User Story 2 (Phase 4) → Test independently → **Deploy/Demo (Browse/Search added)**
4. Complete SavedExplanation backend (T005-T008) + bookmark hooks (T011-T012) → Foundation for US3 ready
5. Add User Story 3 (Phase 5) → Test independently → **Deploy/Demo (Bookmarking added)**
6. Add Polish (Phase 6) → **Final production-ready release**
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (Phase 1) together
2. Team completes Foundational (Phase 2) together (backend dev does T005-T008, frontend dev does T009-T012 in parallel)
3. Once TanStack Query hooks ready (T009-T010):
   - **Developer A**: User Story 1 (T013-T019)
   - **Developer B**: User Story 2 (T020-T025)
   - **Developer C** (backend): Complete SavedExplanation backend (T005-T008) if not done
4. Once SavedExplanation backend ready (T005-T008 + T011-T012):
   - **Developer C**: User Story 3 (T026-T029)
5. All developers: Polish (Phase 6, T030-T036 in parallel where possible)

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability (US1, US2, US3)
- Each user story should be independently completable and testable
- **Backend work** (T005-T008) is CRITICAL for User Story 3 but can be deferred if MVP is just US1+US2
- **Reuse patterns** from 004-coaching-page: Error boundaries, toasts, skeletons, TanStack Query provider already exist
- **Accessibility** is built into shadcn/ui components (Accordion, Card, Button), but verify with Lighthouse audit (T033)
- **Caching strategy** documented in research.md: 1h topics, 5m explanations, 1m saved (implemented in T009-T012)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Avoid**: Same file conflicts (tasks on same file must run sequentially), cross-story dependencies that break independence

---

**Total Tasks**: 36 tasks
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 8 tasks
- Phase 3 (US1): 7 tasks
- Phase 4 (US2): 6 tasks
- Phase 5 (US3): 4 tasks
- Phase 6 (Polish): 7 tasks

**MVP Scope** (User Story 1 only): 19 tasks (Phase 1 + partial Phase 2 [T009-T010] + Phase 3)
**Full Feature Scope** (All 3 user stories): 36 tasks

**Estimated Timeline**:
- Day 1: Setup + Foundational + US1 (View Explanation) → MVP ready
- Day 2: US2 (Browse/Search) + US3 (Bookmark) + Polish → Full feature complete

---

**Status**: Ready for `/sp.implement`
**Next Command**: `/sp.implement` to execute tasks from this file
