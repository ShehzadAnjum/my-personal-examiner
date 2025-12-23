---
id: 0002
title: Coaching Page Implementation Plan
stage: plan
date: 2025-12-21T12:30:00Z
surface: cli
model: claude-sonnet-4-5-20250929
feature: 004-coaching-page
branch: 004-coaching-page
user: anjum
command: /sp.plan
labels: [plan, frontend, coaching, ai-teaching, phase-iv]
links:
  spec: specs/004-coaching-page/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/004-coaching-page/plan.md
    status: created
    type: implementation-plan
  - path: specs/004-coaching-page/research.md
    status: created
    type: research-documentation
  - path: specs/004-coaching-page/data-model.md
    status: created
    type: data-model-specification
  - path: specs/004-coaching-page/contracts/types.ts
    status: created
    type: api-contract-types
  - path: specs/004-coaching-page/contracts/api-client.ts
    status: created
    type: api-client-hooks
  - path: specs/004-coaching-page/quickstart.md
    status: created
    type: quickstart-guide
tests:
  - type: constitution-check
    status: passed
    description: All 11 constitutional principles validated (conditional pass with 3 actions required)
---

## Prompt

User invoked `/sp.plan` after completing `/sp.specify` for Coaching Page.

**Context**: Sequential, chunked approach for frontend page development. First page after master frontend spec (003-ai-teaching-frontend). Coaching Page is ChatGPT-style chat interface for AI tutoring sessions.

**Feature Requirements** (from spec.md):
- P1: Start coaching session (student describes struggle, receives coach's first question)
- P1: Chat conversation (send/receive messages, real-time updates, typing indicators)
- P2: Session outcome (resolved/needs_more_help/refer_to_teacher with next actions)
- P3: Session history (view past sessions)

**Backend APIs** (assumed from Phase III):
- `POST /api/coaching/tutor-session` - Start new session
- `POST /api/coaching/session/{id}/respond` - Send message
- `GET /api/coaching/session/{id}` - Get transcript

**Technical Stack** (from CLAUDE.md):
- Frontend: Next.js 16+ (App Router), React 19, TypeScript 5.7+
- UI: shadcn/ui + Tailwind CSS 4
- State: TanStack Query 5.62+ (formerly React Query)
- Testing: Jest 29+ (unit), Playwright 1.49+ (E2E)

## Response snapshot

**Phase 0: Research** (research.md - 7 decisions)
1. **Real-time updates**: Polling (2s interval) + optimistic updates (no WebSocket needed)
2. **Session persistence**: Dual persistence (localStorage + API) for instant load + multi-device sync
3. **Auto-retry**: TanStack Query built-in retry (3 attempts, exponential backoff)
4. **Offline detection**: `navigator.onLine` + API failures
5. **Multi-tenant security**: JWT + session ownership check (backend enforces, frontend validates)
6. **UI components**: shadcn/ui + Tailwind CSS 4 (project standard)
7. **Streaming support**: Detect and gracefully degrade (future-proof)

**Phase 1: Design** (data-model.md, contracts/, quickstart.md)

**Data Model** (data-model.md):
- 4 core entities: CoachingSession, Message, SessionOutcome, NextAction
- 2 frontend state types: ChatUIState, MessageSendState
- 3 API response types: StartSessionResponse, SendMessageResponse, GetSessionResponse
- Validation rules: topic (10-500 chars), message (1-2000 chars), sessionId (UUID)
- Example data: Active session + Resolved session with outcome

**API Contracts** (contracts/):
- `types.ts`: TypeScript interfaces for all entities + API requests/responses
- `api-client.ts`: TanStack Query hooks (useStartSession, useSendMessage, useSession, useSessions)
- Optimistic updates for instant UI feedback
- Polling (2s) for coach responses
- localStorage persistence with 5-min cache expiry
- Network mode config: offlineFirst (queries), always (mutations)

**Quickstart Guide** (quickstart.md):
- Setup: Node.js 18+, shadcn/ui components, environment variables
- Running: Backend (port 8000) + Frontend (port 3000)
- Testing: Jest unit tests, Playwright E2E tests, manual testing checklist
- Security: Multi-tenant isolation tests (Student A cannot access Student B session)
- Performance benchmarks: Session creation <3s, message send <2s, coach response <10s
- Common issues: Backend connection, polling, optimistic updates, persistence

**Project Structure**:
```
frontend/app/(dashboard)/coaching/page.tsx  # Main route
frontend/components/coaching/*.tsx           # 8 components
frontend/lib/api/coaching.ts                # API client
frontend/hooks/useSession.ts                # Session state
tests/e2e/coaching/*.spec.ts                # E2E tests
```

**Constitution Check**: ✅ Conditional Pass
- Principle V (Multi-Tenant Isolation): ⚠️ Requires verification
- Required actions before implementation:
  1. Document JWT verification pattern
  2. Add session ownership integration tests
  3. Create Phase IV CLAUDE.md

## Outcome

- ✅ Impact: Complete implementation plan for Coaching Page with 6 design artifacts (plan, research, data-model, contracts, quickstart). All "NEEDS CLARIFICATION" items resolved. Ready for `/sp.tasks` to generate task breakdown.
- 🧪 Tests: Constitution check passed (11 principles validated). 3 actions required before implementation.
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/types.ts, contracts/api-client.ts, quickstart.md
- 🔁 Next prompts: `/sp.tasks` (generate task list) → `/sp.implement` (execute tasks)
- 🧠 Reflection: SpecKitPlus workflow followed correctly (spec → plan). Research phase resolved all technical decisions (polling, persistence, retry, security). Data model is comprehensive with examples. API contracts use TanStack Query best practices. Quickstart includes security checklist for multi-tenant verification.

## Evaluation notes (flywheel)

- Failure modes observed: None. Followed plan template structure, completed all Phase 0 (research) and Phase 1 (design) deliverables.
- Graders run and results (PASS/FAIL): Constitution Check: PASS (conditional - 3 actions required)
- Prompt variant (if applicable): Standard /sp.plan workflow for frontend feature
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to break down implementation into atomic tasks with time estimates
