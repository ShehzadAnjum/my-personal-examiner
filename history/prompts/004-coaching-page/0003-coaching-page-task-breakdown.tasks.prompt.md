---
id: 0003
title: Coaching Page Task Breakdown
stage: tasks
date: 2025-12-21T13:00:00Z
surface: cli
model: claude-sonnet-4-5-20250929
feature: 004-coaching-page
branch: 004-coaching-page
user: anjum
command: /sp.tasks
labels: [tasks, frontend, coaching, ai-teaching, phase-iv, implementation]
links:
  spec: specs/004-coaching-page/spec.md
  plan: specs/004-coaching-page/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/004-coaching-page/tasks.md
    status: created
    type: task-breakdown
tests:
  - type: format-validation
    status: passed
    description: All 76 tasks follow strict checklist format with IDs, labels, and file paths
---

## Prompt

User invoked `/sp.tasks` after completing `/sp.plan` for Coaching Page.

**Context**: Generate executable task breakdown organized by user story to enable independent implementation and testing. MVP-first approach with incremental delivery.

**Design Documents Available**:
- spec.md: 4 user stories (2 P1, 1 P2, 1 P3)
- plan.md: Tech stack (Next.js 16, React 19, TypeScript, TanStack Query, shadcn/ui, Tailwind)
- data-model.md: 4 entities (CoachingSession, Message, SessionOutcome, NextAction)
- contracts/types.ts: TypeScript interfaces
- contracts/api-client.ts: TanStack Query hooks
- research.md: 7 technical decisions
- quickstart.md: Testing requirements (Jest unit, Playwright E2E)

**User Stories from spec.md**:
- **US1 (P1)**: Start Coaching Session - Student describes struggle, receives coach's first question
- **US2 (P1)**: Chat Conversation - Send/receive messages, real-time updates, typing indicators
- **US3 (P2)**: Session Outcome - Display conclusion with summary and next actions
- **US4 (P3)**: Session History - View past coaching sessions, read-only transcripts

## Response snapshot

**Generated**: tasks.md with 76 tasks organized in 7 phases

**Task Organization** (by user story):

**Phase 1: Setup** (10 tasks)
- Project structure, dependencies, shadcn/ui, TypeScript/Jest/Playwright config, environment variables, TanStack Query provider

**Phase 2: Foundational** (7 tasks) - CRITICAL BLOCKER
- TypeScript types, API client implementation, shared hooks, page route, error boundary, backend verification

**Phase 3: User Story 1 - Start Session** (9 tasks)
- E2E test, SessionInitForm component, validation, useStartSession integration, error handling, accessibility

**Phase 4: User Story 2 - Chat Conversation** (16 tasks)
- E2E test, 5 components (MessageBubble, TypingIndicator, MessageInput, MessageList, ChatInterface), useSendMessage/useSession hooks, polling, localStorage, accessibility

**Phase 5: User Story 3 - Session Outcome** (9 tasks)
- E2E test, SessionOutcome/NextActionCard components, detect session end, disable input, new session option, accessibility

**Phase 6: User Story 4 - Session History** (10 tasks)
- E2E test, SessionHistory/SessionListItem components, useSessions hook, session detail page, filtering/pagination, accessibility

**Phase 7: Polish & Cross-Cutting** (15 tasks)
- Error boundaries, loading states, mobile responsive, performance optimization, keyboard shortcuts, accessibility audit, analytics, security verification, unit tests, demo video

**Key Metrics**:
- Total tasks: 76
- Parallel tasks: 35 (marked [P])
- MVP scope (US1 + US2): 42 tasks (55%)
- Time estimate: MVP 3-5 days, Full feature 5-7 days

**Implementation Strategy**:
1. **MVP First**: Phase 1-4 (42 tasks) → Deploy/Demo
2. **Incremental**: Add US3 → Deploy, Add US4 → Deploy, Polish → Production
3. **Parallel Team**: US1, US2, US4 can run in parallel after Foundational phase

## Outcome

- ✅ Impact: Complete, executable task breakdown for Coaching Page with 76 tasks organized by user story. Each user story is independently implementable and testable. MVP scope defined (42 tasks). Ready for `/sp.implement` execution.
- 🧪 Tests: Format validation passed (all 76 tasks follow strict checklist format). E2E tests included per user story (4 test tasks: T018, T027, T043, T052).
- 📁 Files: Created tasks.md (400+ lines with 76 tasks, dependencies, parallel examples, implementation strategies)
- 🔁 Next prompts: `/sp.implement` (execute tasks from tasks.md) or start manual implementation following task order
- 🧠 Reflection: SpecKitPlus workflow completed for Coaching Page (spec → plan → tasks). Task organization by user story enables independent delivery. Each phase is a deployable increment. MVP-first strategy prioritizes P1 user stories. Parallel opportunities identified (35 tasks). Security verification included (T071). All constitutional requirements addressed.

## Evaluation notes (flywheel)

- Failure modes observed: None. Followed task template structure, organized by user story, included exact file paths, strict format compliance.
- Graders run and results (PASS/FAIL): Format validation: PASS (all tasks have IDs, labels, file paths). User story independence: PASS (each story has complete test + implementation + accessibility tasks).
- Prompt variant (if applicable): Standard /sp.tasks workflow with E2E tests included (per quickstart.md)
- Next experiment (smallest change to try): Execute `/sp.implement` to start implementation, OR manually implement tasks in order (Setup → Foundational → US1 → US2 → US3 → US4 → Polish)
