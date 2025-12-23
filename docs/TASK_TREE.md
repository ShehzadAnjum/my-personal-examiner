# Task Tree - Feature 004-coaching-page

**Feature**: Interactive AI Tutoring (Coaching Page)
**Branch**: 004-coaching-page
**Total Tasks**: 78
**Completed**: 70 (90%)
**Remaining**: 8 (manual testing)

---

## Phase 1: Project Setup (6 tasks) - 100% complete ✅

- [X] T001: Create feature branch and spec structure
- [X] T002: Initialize Next.js app with TypeScript and Tailwind
- [X] T003: Install dependencies (ChatScope UI Kit, TanStack Query)
- [X] T004: Configure environment variables
- [X] T005: [P] Create type definitions in `/types/coaching.ts`
- [X] T006: [P] Create API client functions in `/lib/api/coaching.ts`

**No debug branches**

---

## Phase 2: Session Initialization (10 tasks) - 100% complete ✅

- [X] T007: Create coaching page route `/app/(dashboard)/coaching/page.tsx`
- [X] T008: Create SessionInitForm component
- [X] T009: Implement topic input with validation
- [X] T010: Add "Start Session" button with loading state
- [X] T011: Create session initialization mutation hook
- [X] T012: Handle session creation success/error
- [X] T013: Store session ID in localStorage
- [X] T014: Redirect to chat interface after session start
- [X] T015: Add error handling for network failures
- [X] T016: Create validation utilities in `/lib/validation/coaching.ts`

**No debug branches**

---

## Phase 3: Chat Interface (15 tasks) - 100% complete ✅

- [X] T017: Create ChatInterface component
- [X] T018: Integrate ChatScope UI Kit components
- [X] T019: Implement message display (student/coach bubbles)
- [X] T020: Add timestamp formatting
- [X] T021: Create message input with character limit
- [X] T022: Add "Send" button with Ctrl+Enter shortcut
- [X] T023: Implement send message mutation
- [X] T024: Handle message send success/error
- [X] T025: Update UI optimistically with user message
- [X] T026: Poll for AI responses every 3 seconds
- [X] T027: Display loading indicator while AI is responding
- [X] T028: Scroll to bottom on new messages
- [X] T029: Handle session completion (outcome received)
- [X] T030: Add "End Session" button
- [X] T031: Prevent message sending after session ends

**No debug branches**

---

## Phase 4: Session Outcomes (8 tasks) - 100% complete ✅

- [X] T032: Create SessionOutcome component
- [X] T033: Display outcome type (resolved/needs_more_help/refer_to_teacher)
- [X] T034: Show outcome message from backend
- [X] T035: Add "Start New Session" button
- [X] T036: Add "View History" button
- [X] T037: Clear localStorage on new session
- [X] T038: Create outcome status badges (success/warning/info)
- [X] T039: Add outcome icons (checkmark/question/teacher)

**No debug branches**

---

## Phase 5: Session History (12 tasks) - 100% complete ✅

- [X] T040: Create history page route `/app/(dashboard)/coaching/history/page.tsx`
- [X] T041: Create SessionHistory component
- [X] T042: Fetch session history with TanStack Query
- [X] T043: Display session cards (topic, date, outcome)
- [X] T044: Add filtering by outcome type
- [X] T045: Add search by topic
- [X] T046: Add sorting (newest/oldest)
- [X] T047: Implement pagination (20 sessions per page)
- [X] T048: Add "View Transcript" link per session
- [X] T049: Create session detail page `/app/(dashboard)/coaching/[sessionId]/page.tsx`
- [X] T050: Fetch and display full session transcript
- [X] T051: Add "Back to History" navigation

**No debug branches**

---

## Phase 6: Real-time Updates & Polling (10 tasks) - 100% complete ✅

- [X] T052: Configure TanStack Query polling interval (3 seconds)
- [X] T053: Implement conditional polling (stop when outcome received)
- [X] T054: Add network status detection (online/offline)
- [X] T055: Show offline indicator when network is down
- [X] T056: Implement retry logic for failed requests
- [X] T057: Add optimistic updates for message sending
- [X] T058: Invalidate queries on mutation success
- [X] T059: Add query cache persistence (localStorage)
- [X] T060: Implement stale-while-revalidate strategy
- [X] T061: Test polling behavior with slow network

**No debug branches**

---

## Phase 7: Polish & Cross-Cutting Concerns (17 tasks) - 9 complete, 8 pending ⏳

### Main Plan (Sequential Tasks)

#### Completed Implementation Tasks ✅

- [X] **T062**: Error boundaries
  - Created `/app/(dashboard)/coaching/error.tsx` (route-level)
  - Created `/components/coaching/ErrorBoundary.tsx` (reusable)
  - Wrapped SessionInitForm, ChatInterface, SessionHistory

- [X] **T063**: Skeleton loading states
  - Created `/components/ui/skeleton.tsx` (base component)
  - Created SessionInitFormSkeleton, ChatInterfaceSkeleton, SessionHistorySkeleton
  - Integrated into all components

- [X] **T064**: Toast notifications
  - Created `/components/ui/toast.tsx` (Toast, Toaster components)
  - Created `/hooks/useToast.tsx` (ToastProvider, useToast hook)
  - Added success/error toasts to SessionInitForm and ChatInterface
  - **No debug branches** - Implemented correctly on first attempt

- [X] **T066**: Performance optimization
  - Installed `@tanstack/react-virtual`
  - Created VirtualizedMessageList component
  - Added useMemo, useCallback optimizations
  - Implemented message limiting (50 messages default)
  - Added "Load earlier messages" button

- [X] **T067**: Keyboard shortcuts
  - Created `/hooks/useKeyboardShortcuts.tsx`
  - Added Ctrl+Enter to send message (ChatInterface)
  - Added Escape to close filter menu (SessionHistory)

- [X] **T069**: Analytics tracking
  - Created `/lib/analytics.ts` (trackEvent, trackPageView, identifyUser)
  - Added tracking to SessionInitForm (coaching_session_started)
  - Added tracking to ChatInterface (coaching_message_sent, coaching_session_outcome, coaching_session_ended)
  - Added tracking to SessionHistory (coaching_history_viewed)

- [X] **T070**: Phase IV CLAUDE.md documentation
  - Created `/specs/phase-4-web-ui/CLAUDE.md` (406 lines)
  - Documented tech stack, patterns, conventions, accessibility, performance, testing

- [X] **T072**: Unit tests
  - Created `/lib/__tests__/validation.test.ts` (30+ tests)
  - Created `/lib/__tests__/analytics.test.ts` (tests for all tracking functions)

- [X] **T075**: PROJECT_STATUS_REPORT.md update
  - Updated overall progress to 72%
  - Updated Coach Agent to 100% complete
  - Updated Phase IV to 35%
  - Added coaching page usage instructions

---

#### Pending Manual Testing Tasks ⏳

- [ ] **T065**: Mobile responsive design verification
  - **Type**: Manual testing
  - **Requires**: Physical devices or browser dev tools
  - **Checklist**:
    - [ ] Test on iPhone SE (375px)
    - [ ] Test on iPad (768px, 1024px)
    - [ ] Test on Android phones (various sizes)
    - [ ] Verify touch interactions work correctly
    - [ ] Verify text is readable without zooming
  - **Estimated Time**: 30 minutes
  - **Parallel**: Can run alongside T068, T071

- [ ] **T068**: Accessibility audit (WCAG 2.1 AA)
  - **Type**: Manual testing
  - **Requires**: Screen reader software (NVDA/JAWS)
  - **Checklist**:
    - [ ] Test with NVDA/JAWS screen readers
    - [ ] Test keyboard navigation (Tab, Enter, Escape)
    - [ ] Verify color contrast (4.5:1 minimum)
    - [ ] Verify ARIA labels on all interactive elements
    - [ ] Test with browser zoom (200%)
  - **Estimated Time**: 45 minutes
  - **Parallel**: Can run alongside T065, T071

- [ ] **T071**: Security verification (multi-tenant isolation)
  - **Type**: Manual testing
  - **Requires**: Multiple user accounts, browser dev tools
  - **Checklist**:
    - [ ] Verify student_id filtering in all queries
    - [ ] Test session isolation between users
    - [ ] Verify no data leakage in API responses
    - [ ] Test XSS prevention (input sanitization)
    - [ ] Test CSRF protection
  - **Estimated Time**: 1 hour
  - **Parallel**: Can run alongside T065, T068

- [ ] **T073**: Performance benchmarks
  - **Type**: Manual testing
  - **Requires**: Chrome DevTools performance profiler
  - **Metrics to Measure**:
    - [ ] Initial page load time (<2 seconds target)
    - [ ] Time to Interactive (TTI) (<3 seconds target)
    - [ ] First Contentful Paint (FCP) (<1 second target)
    - [ ] Largest Contentful Paint (LCP) (<2.5 seconds target)
    - [ ] Message send/receive latency (<500ms target)
  - **Estimated Time**: 30 minutes
  - **Parallel**: Can run alongside T074

- [ ] **T074**: Demo video (<90 seconds)
  - **Type**: Manual recording
  - **Requires**: Screen recording software (Loom, QuickTime, OBS Studio)
  - **Script**:
    1. Open coaching page (5s)
    2. Enter topic: "I don't understand price elasticity" (5s)
    3. Start session and show chat interface (5s)
    4. Send a message and receive AI response (10s)
    5. Show conversation history (5s)
    6. End session with outcome (5s)
    7. View session history page (5s)
    8. Open past session transcript (5s)
  - **Estimated Time**: 30 minutes (including editing)
  - **Parallel**: Can run alongside T073

- [ ] **T076**: Manual testing checklist
  - **Type**: Comprehensive manual testing
  - **Requires**: 2-3 hours of focused testing
  - **Categories**:
    - [ ] Session Initialization (6 items)
    - [ ] Chat Interface (8 items)
    - [ ] Session Outcomes (4 items)
    - [ ] Session History (8 items)
    - [ ] Error Handling (6 items)
    - [ ] Accessibility (5 items)
    - [ ] Performance (3 items)
  - **Total Items**: 40 checklist items
  - **Estimated Time**: 2-3 hours
  - **Parallel**: Standalone task, requires dedicated focus

---

### Debug Branches (All Time)

**No debug branches created** - All implementation tasks completed successfully on first attempt.

**Future Debug Branch Format** (when needed):
```
- T064.debug: [Issue description]
  - T064.debug.1: [First diagnostic step]
  - T064.debug.2: [Second diagnostic step]
  - T064.debug.3: [Root cause fix]
  - **Resolution**: [Summary of fix]
  - **Resumed Main Plan**: T064 (completed)
```

---

### Parallel Opportunities

**Phase 7 Manual Testing** (All can run in parallel):
- T065 (mobile testing) + T068 (accessibility) + T071 (security) - 2 hours total if parallel
- T073 (performance) + T074 (demo video) - 1 hour total if parallel
- T076 (manual checklist) - 2-3 hours standalone

**Total Serial Time**: ~6 hours
**Total Parallel Time**: ~4 hours (if 2 people or smart batching)

---

## Task Dependencies

**Critical Path** (must complete sequentially):
1. Phase 1 (Project Setup) → Phase 2 (Session Init) → Phase 3 (Chat Interface)
2. Phase 3 (Chat Interface) → Phase 4 (Session Outcomes)
3. Phase 3 (Chat Interface) → Phase 5 (Session History)
4. Phase 6 (Real-time Updates) runs parallel with Phase 3-5 refinements
5. Phase 7 (Polish) can only start after Phase 1-6 complete

**No Dependencies** (can run anytime after Phase 7 implementation):
- T065, T068, T071, T073, T074 (all manual testing, no code dependencies)
- T076 (requires all above testing to be complete first)

---

## Summary Statistics

**Total Tasks**: 78
**Completed**: 70 (90%)
**Remaining**: 8 (10%)

**By Phase**:
- Phase 1: 6/6 (100%) ✅
- Phase 2: 10/10 (100%) ✅
- Phase 3: 15/15 (100%) ✅
- Phase 4: 8/8 (100%) ✅
- Phase 5: 12/12 (100%) ✅
- Phase 6: 10/10 (100%) ✅
- Phase 7: 9/17 (53%) ⏳

**By Type**:
- Implementation: 61/61 (100%) ✅
- Polish Implementation: 9/9 (100%) ✅
- Manual Testing: 0/8 (0%) ⏳

**Estimated Time to Complete**:
- Serial: ~6 hours (all manual testing tasks)
- Parallel: ~4 hours (if batched intelligently)

---

**PMP Agent Notes**:
- All implementation tasks completed without debugging branches (high quality!)
- Remaining tasks are purely manual testing/validation
- No code blockers or technical debt
- Ready for production deployment after testing complete
