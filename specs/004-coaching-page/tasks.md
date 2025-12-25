---
description: "Task list for Coaching Page - Interactive AI Tutoring implementation"
---

# Tasks: Coaching Page - Interactive AI Tutoring

**Input**: Design documents from `/specs/004-coaching-page/`
**Prerequisites**: plan.md (tech stack), spec.md (user stories), data-model.md (entities), contracts/ (API client), research.md (decisions), quickstart.md (testing)

**Tests**: E2E tests with Playwright are included per user story (as specified in quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` (Next.js 16 App Router)
- **Backend**: `backend/` (existing, no changes)
- **Tests**: `frontend/tests/e2e/coaching/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for coaching page

- [x] T001 Create frontend directory structure per plan.md (app/(dashboard)/coaching/, components/coaching/, lib/api/, hooks/, types/)
- [x] T002 [P] Install Next.js dependencies in frontend/package.json (next@16, react@19, react-dom@19, typescript@5.7)
- [x] T003 [P] Install TanStack Query in frontend/package.json (@tanstack/react-query@5.62, @tanstack/react-query-devtools)
- [x] T004 [P] Install shadcn/ui CLI and initialize Tailwind CSS 4 in frontend/
- [x] T005 Install shadcn/ui components (button, input, textarea, card, avatar, badge, alert) in frontend/components/ui/
- [x] T006 [P] Configure TypeScript in frontend/tsconfig.json with strict mode and path aliases
- [x] T007 [P] Setup Jest configuration in frontend/jest.config.js for unit tests
- [x] T008 [P] Setup Playwright configuration in frontend/playwright.config.ts for E2E tests
- [x] T009 Create environment variables file frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
- [x] T010 [P] Setup TanStack Query provider in frontend/app/providers.tsx with coachingQueryConfig from contracts/api-client.ts

**Checkpoint**: Frontend project structure ready, all dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 [P] Copy TypeScript types from specs/004-coaching-page/contracts/types.ts to frontend/types/coaching.ts
- [x] T012 Implement API client from specs/004-coaching-page/contracts/api-client.ts to frontend/lib/api/coaching.ts (includes useStartSession, useSendMessage, useSession, useSessions hooks)
- [x] T013 [P] Create useOnlineStatus hook in frontend/hooks/useOnlineStatus.ts (from research.md: navigator.onLine detection)
- [x] T014 [P] Create useSessionOwnership hook in frontend/hooks/useSessionOwnership.ts (multi-tenant security verification)
- [x] T015 [P] Create coaching page route in frontend/app/(dashboard)/coaching/page.tsx (empty placeholder)
- [x] T016 [P] Setup global error boundary in frontend/app/error.tsx for coaching error handling
- [x] T017 Verify backend coaching APIs are functional (POST /api/coaching/tutor-session, POST /api/coaching/session/{id}/respond, GET /api/coaching/session/{id})

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Start Coaching Session (Priority: P1) 🎯 MVP

**Goal**: Student can initiate coaching session by describing struggle and receive coach's first diagnostic question

**Independent Test**:
1. Navigate to /coaching
2. Enter struggle description "I don't understand price elasticity" (min 10 chars)
3. Click "Start Session"
4. Coach's first question appears within 5 seconds
5. Session is active with unique session ID

### E2E Test for User Story 1

- [x] T018 [US1] Write E2E test in frontend/tests/e2e/coaching/start-session.spec.ts covering: empty struggle validation, loading state, coach question appearance, session ID generation

### Implementation for User Story 1

- [x] T019 [P] [US1] Create SessionInitForm component in frontend/components/coaching/SessionInitForm.tsx (textarea for struggle, validation, submit button)
- [x] T020 [P] [US1] Create form validation utilities in frontend/lib/validation/coaching.ts (topic min 10 chars, max 500 chars, pattern validation)
- [x] T021 [US1] Integrate useStartSession hook in SessionInitForm component (mutation, loading state, error handling)
- [x] T022 [US1] Update coaching page route frontend/app/(dashboard)/coaching/page.tsx to render SessionInitForm when no active session
- [x] T023 [US1] Add loading indicator component in frontend/components/coaching/LoadingIndicator.tsx ("Coach is preparing your session...")
- [x] T024 [US1] Handle session creation success: store session ID in state, display first coach message
- [x] T025 [US1] Add error handling for session creation failures (display user-friendly error, retry option)
- [x] T026 [US1] Add form accessibility (ARIA labels, keyboard navigation, screen reader support)

**Checkpoint**: At this point, User Story 1 should be fully functional - student can start session and see coach's first question

---

## Phase 4: User Story 2 - Chat Conversation (Priority: P1)

**Goal**: Student can send messages to coach, receive adaptive responses, and see full conversation history with real-time updates

**Independent Test**:
1. Start active session (from US1)
2. Send message "Demand goes down?"
3. Message appears immediately (optimistic update)
4. Coach response appears within 10 seconds
5. Conversation history shows all messages with timestamps
6. Student messages align right, coach messages align left
7. Typing indicator shows "Coach is thinking..."

### E2E Test for User Story 2

- [x] T027 [US2] Write E2E test in frontend/tests/e2e/coaching/chat-conversation.spec.ts covering: send message, optimistic update, coach response, message alignment, timestamps, typing indicator, long conversation (15+ messages), character limit validation

### Implementation for User Story 2

- [x] T028 [P] [US2] Create MessageBubble component in frontend/components/coaching/MessageBubble.tsx (role-based styling, timestamp formatting, avatar)
- [x] T029 [P] [US2] Create TypingIndicator component in frontend/components/coaching/TypingIndicator.tsx (animated dots, "Coach is thinking...")
- [x] T030 [P] [US2] Create MessageInput component in frontend/components/coaching/MessageInput.tsx (textarea, character counter, send button, Enter to send, Shift+Enter for newline)
- [x] T031 [P] [US2] Create MessageList component in frontend/components/coaching/MessageList.tsx (render messages, auto-scroll to bottom, manual scroll support)
- [x] T032 [US2] Create ChatInterface component in frontend/components/coaching/ChatInterface.tsx (container for MessageList + MessageInput, layout)
- [x] T033 [US2] Integrate useSendMessage hook in ChatInterface (optimistic updates, retry logic, error handling)
- [x] T034 [US2] Integrate useSession hook for polling in ChatInterface (refetchInterval: 2s for active sessions, from research.md)
- [x] T035 [US2] Implement localStorage persistence in useSession hook (cache session data, 5-min expiry, from research.md)
- [x] T036 [US2] Add message character validation (min 1, max 2000 chars) in MessageInput component
- [x] T037 [US2] Implement auto-scroll logic in MessageList (scroll to bottom on new message, preserve manual scroll position)
- [x] T038 [US2] Add timestamp formatting utility in frontend/lib/utils/date.ts (human-readable: "2 minutes ago", "10:45 AM")
- [x] T039 [US2] Update coaching page route to render ChatInterface when active session exists
- [x] T040 [US2] Add network status banner in ChatInterface (show "You are offline" when useOnlineStatus detects offline)
- [x] T041 [US2] Add retry indicator component in frontend/components/coaching/RetryIndicator.tsx (display retry attempt count during auto-retry)
- [x] T042 [US2] Add accessibility to chat interface (ARIA live regions for new messages, keyboard navigation, focus management)

**Checkpoint**: At this point, User Stories 1 AND 2 should work independently - full chat conversation is functional

---

## Phase 5: User Story 3 - Session Outcome & Conclusion (Priority: P2)

**Goal**: Display session outcome when coach determines session has concluded, with summary and next action options

**Independent Test**:
1. Complete coaching conversation until coach concludes session
2. Session outcome displays (resolved/needs_more_help/refer_to_teacher)
3. Summary shows what was learned
4. Next actions (1-5) are visible with links
5. Message input is disabled
6. "Session ended. Start new session to continue" message appears

### E2E Test for User Story 3

- [x] T043 [US3] Write E2E test in frontend/tests/e2e/coaching/session-outcome.spec.ts covering: outcome display (resolved/needs_more_help/refer_to_teacher), summary visible, next actions rendered, input disabled, new session option

### Implementation for User Story 3

- [x] T044 [P] [US3] Create SessionOutcome component in frontend/components/coaching/SessionOutcome.tsx (render outcome status, summary, next actions list)
- [x] T045 [P] [US3] Create NextActionCard component in frontend/components/coaching/NextActionCard.tsx (action type icon, label, description, link button, priority badge)
- [x] T046 [US3] Integrate SessionOutcome in ChatInterface (detect session.status !== 'active', render outcome below messages)
- [x] T047 [US3] Disable MessageInput when session has ended (add disabled prop, show "Session ended" message)
- [x] T048 [US3] Add "Start New Session" button in SessionOutcome component (navigate to coaching page, clear current session)
- [x] T049 [US3] Add visual distinction for ended sessions (gray out message input, add outcome banner at top)
- [x] T050 [US3] Handle outcome confidence score display (if present, show as percentage or visual indicator)
- [x] T051 [US3] Add accessibility to outcome component (announce outcome to screen readers, keyboard navigation for next actions)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should work independently - full coaching flow from start to outcome

---

## Phase 6: User Story 4 - View Past Session History (Priority: P3)

**Goal**: Student can review previous coaching sessions to revisit explanations and see how they overcame past misconceptions

**Independent Test**:
1. Navigate to /coaching/history (or history section on coaching page)
2. List of past sessions displays (topic, date, outcome)
3. Click on a session
4. Full conversation transcript displays in read-only mode
5. No input allowed (session is historical)

### E2E Test for User Story 4

- [x] T052 [US4] Write E2E test in frontend/tests/e2e/coaching/session-history.spec.ts covering: sessions list display, click to view transcript, read-only mode, empty state ("No sessions yet")

### Implementation for User Story 4

- [x] T053 [P] [US4] Create SessionHistory component in frontend/components/coaching/SessionHistory.tsx (list of past sessions, topic, date, outcome badge)
- [x] T054 [P] [US4] Create SessionListItem component in frontend/components/coaching/SessionListItem.tsx (session card with topic, date, outcome, click to view)
- [x] T055 [US4] Integrate useSessions hook in SessionHistory component (fetch past sessions, loading state, error handling)
- [x] T056 [US4] Create session detail view in frontend/app/(dashboard)/coaching/[sessionId]/page.tsx (read-only transcript)
- [x] T057 [US4] Reuse ChatInterface component in read-only mode (disable input, remove polling, show historical data)
- [x] T058 [US4] Add empty state component in frontend/components/coaching/EmptyHistory.tsx ("No coaching sessions yet. Start your first session to get help!")
- [x] T059 [US4] Add filtering/sorting to session history (sort by date, filter by outcome status)
- [x] T060 [US4] Add pagination or infinite scroll for session history (if >20 sessions)
- [x] T061 [US4] Add accessibility to history view (semantic HTML, keyboard navigation, screen reader announcements)

**Checkpoint**: All user stories (1-4) are now independently functional - full coaching feature complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

- [x] T062 [P] Add error boundaries for each major component (SessionInitForm, ChatInterface, SessionOutcome, SessionHistory) in respective files
- [x] T063 [P] Implement skeleton loading states for all async operations (session creation, message sending, history loading)
- [x] T064 [P] Add toast notifications for errors and success messages using shadcn/ui toast component
- [ ] T065 Add mobile responsive design verification (test at 375x667, 1024x768, 1920x1080 from quickstart.md) → **See MANUAL_VERIFICATION.md**
- [x] T066 [P] Optimize ChatInterface performance for 50+ message conversations (virtual scrolling with react-window or @tanstack/react-virtual)
- [x] T067 [P] Add keyboard shortcuts (Ctrl+Enter to send message, Esc to close modals, etc.)
- [ ] T068 Run accessibility audit with axe DevTools or Lighthouse (ensure WCAG 2.1 AA compliance) → **See MANUAL_VERIFICATION.md**
- [x] T069 [P] Add analytics tracking for coaching events (session start, message send, session end, outcome)
- [x] T070 [P] Create Phase IV CLAUDE.md in specs/phase-4-web-ui/CLAUDE.md with frontend patterns and conventions
- [ ] T071 Run security verification from quickstart.md (multi-tenant isolation test: Student B cannot access Student A's session) → **See MANUAL_VERIFICATION.md**
- [x] T072 [P] Add unit tests for utility functions (validation, date formatting, etc.) in frontend/lib/__tests__/
- [ ] T073 Run performance benchmarks from quickstart.md (session creation <3s, message send <2s, coach response <10s p95) → **See MANUAL_VERIFICATION.md**
- [ ] T074 Create demo video showing complete coaching workflow (<90 seconds per constitution) → **See MANUAL_VERIFICATION.md**
- [x] T075 Update PROJECT_STATUS_REPORT.md with coaching page completion status
- [ ] T076 Run quickstart.md manual testing checklist (all P1, P2, P3 scenarios) → **See MANUAL_VERIFICATION.md**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - MVP first
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can run in parallel with US1 if staffed
- **User Story 3 (Phase 5)**: Depends on User Story 2 (needs chat interface) - Should run after US2
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) - Can run in parallel with others
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can start after Foundational
- **User Story 2 (P1)**: Independent - can start after Foundational (but logically follows US1)
- **User Story 3 (P2)**: Depends on User Story 2 (uses ChatInterface component)
- **User Story 4 (P3)**: Independent - can start after Foundational

### Within Each User Story

1. E2E test FIRST (write test, ensure it fails)
2. Components in parallel (marked [P])
3. Integration tasks (compose components)
4. Accessibility and polish
5. Story complete - verify test passes

### Parallelization Opportunities

**Phase 1 (Setup)**: T002, T003, T004, T006, T007, T008, T010 can run in parallel
**Phase 2 (Foundational)**: T011, T013, T014, T015, T016 can run in parallel
**Phase 3 (US1)**: T019, T020 can run in parallel
**Phase 4 (US2)**: T028, T029, T030, T031 can run in parallel (different components)
**Phase 5 (US3)**: T044, T045 can run in parallel
**Phase 6 (US4)**: T053, T054 can run in parallel
**Phase 7 (Polish)**: T062, T063, T064, T066, T067, T068, T069, T070, T072 can run in parallel

---

## Parallel Example: User Story 2 (Chat Conversation)

```bash
# Launch all component creation in parallel (different files):
Task T028: "Create MessageBubble component in frontend/components/coaching/MessageBubble.tsx"
Task T029: "Create TypingIndicator component in frontend/components/coaching/TypingIndicator.tsx"
Task T030: "Create MessageInput component in frontend/components/coaching/MessageInput.tsx"
Task T031: "Create MessageList component in frontend/components/coaching/MessageList.tsx"

# After components complete, integrate sequentially:
Task T032: "Create ChatInterface component" (composes T028-T031)
Task T033: "Integrate useSendMessage hook" (depends on T032)
Task T034: "Integrate useSession hook for polling" (depends on T032)
# ... etc.
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

**Fastest path to working coaching feature:**

1. ✅ Complete Phase 1: Setup (T001-T010)
2. ✅ Complete Phase 2: Foundational (T011-T017) - CRITICAL
3. ✅ Complete Phase 3: User Story 1 (T018-T026) - Session start
4. ✅ Complete Phase 4: User Story 2 (T027-T042) - Chat conversation
5. **STOP and VALIDATE**: Test end-to-end coaching session
6. Deploy/demo if ready

**MVP Deliverable**: Students can start coaching sessions, have full conversations with AI coach, see real-time responses. This is the core value proposition.

### Incremental Delivery (Add Features Sequentially)

1. **Foundation** (Phase 1 + 2): Project ready, APIs connected
2. **MVP** (Phase 3 + 4): Start + Chat → Deploy/Demo ✅
3. **Enhanced** (Phase 5): Session outcomes → Deploy/Demo
4. **Complete** (Phase 6): Session history → Deploy/Demo
5. **Production** (Phase 7): Polish + security → Production release

Each phase adds value without breaking previous features.

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (Session start) → Phase 7 (Polish)
- **Developer B**: User Story 2 (Chat conversation) → Phase 7 (Polish)
- **Developer C**: User Story 4 (History - independent) → Phase 7 (Polish)
- **All together**: User Story 3 (Outcome - after US2 complete) → Phase 7 (Polish)

Stories complete independently, integrate seamlessly.

---

## Task Summary

**Total Tasks**: 76 tasks
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 7 tasks (CRITICAL - blocks all stories)
- Phase 3 (US1 - Start Session): 9 tasks (1 E2E test + 8 implementation)
- Phase 4 (US2 - Chat Conversation): 16 tasks (1 E2E test + 15 implementation)
- Phase 5 (US3 - Session Outcome): 9 tasks (1 E2E test + 8 implementation)
- Phase 6 (US4 - Session History): 10 tasks (1 E2E test + 9 implementation)
- Phase 7 (Polish): 15 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Recommended): Phase 1 + 2 + 3 + 4 = 42 tasks (55% of total)
**Time Estimate**:
- MVP: 3-5 days (with parallel execution)
- Full feature: 5-7 days (all 4 user stories + polish)

---

## Notes

- Each task includes exact file path for implementation
- [P] tasks operate on different files with no dependencies
- [Story] labels enable independent story testing and delivery
- E2E tests written FIRST per user story (TDD approach)
- Each checkpoint is a deployable increment
- Security verification (T071) is CRITICAL before production deployment
- Tests are included per quickstart.md requirements
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Status**: ✅ Task breakdown complete. Ready for `/sp.implement` execution.
