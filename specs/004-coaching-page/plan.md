# Implementation Plan: Coaching Page - Interactive AI Tutoring

**Branch**: `004-coaching-page` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-coaching-page/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a ChatGPT-style interactive coaching interface where students initiate sessions by describing their struggle, engage in Socratic dialogue with an AI coach, and receive session outcomes. The frontend will integrate with existing backend APIs (POST /api/coaching/tutor-session, POST /api/coaching/session/{id}/respond, GET /api/coaching/session/{id}) to deliver real-time chat-based tutoring for Economics concepts. The interface must handle loading states, errors, multi-tenant isolation, and conversation persistence across page refreshes.

## Technical Context

**Language/Version**: TypeScript 5.7+
**Primary Dependencies**: Next.js 16+ (App Router), React 19, shadcn/ui, Tailwind CSS 4, TanStack Query 5.62+
**Storage**: Backend PostgreSQL (via API calls), browser localStorage for session persistence
**Testing**: Jest 29+ (unit), Playwright 1.49+ (E2E)
**Target Platform**: Web (responsive: desktop 1920x1080, tablet 1024x768, mobile 375x667)
**Project Type**: Web (frontend component of existing FastAPI backend)
**Performance Goals**: Session creation <3s, message send <2s, coach response <10s (95th percentile), 60 FPS scrolling
**Constraints**: <200ms p95 for UI interactions, handles 50+ messages without lag, auto-retry message sends 3 times
**Scale/Scope**: Multi-tenant (student-scoped sessions), real-time chat, conversation history, error recovery

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Subject Accuracy is Non-Negotiable
- **Status**: ✅ PASS
- **Reasoning**: Frontend displays coach responses from backend AI (accuracy enforced there). No content generation in frontend.
- **Action**: None required

### Principle II: A* Standard Marking Always
- **Status**: ✅ PASS (Not Applicable)
- **Reasoning**: Coaching page is tutoring interface, not marking. A* standards enforced in backend marking service (separate feature).
- **Action**: None required

### Principle III: Syllabus Synchronization First
- **Status**: ✅ PASS (Not Applicable)
- **Reasoning**: Frontend displays syllabus-aligned coach responses from backend. No syllabus management in this feature.
- **Action**: None required

### Principle IV: Spec-Driven Development
- **Status**: ✅ PASS
- **Reasoning**: Following SpecKitPlus workflow: /sp.specify → /sp.plan (current) → /sp.tasks → /sp.implement
- **Evidence**: spec.md exists, plan.md being created, tasks.md next, implementation follows
- **Action**: Continue following workflow

### Principle V: Multi-Tenant Isolation is Sacred
- **Status**: ⚠️ REQUIRES VERIFICATION
- **Reasoning**: Frontend must verify student_id in JWT matches session owner before displaying data
- **Action Required**:
  - Verify JWT token extraction in API client
  - Verify session ownership check before rendering conversation
  - Integration tests: Student A cannot view Student B's sessions
  - Document security pattern in quickstart.md

### Principle VI: Feedback is Constructive and Detailed
- **Status**: ✅ PASS
- **Reasoning**: Coach responses (backend-generated) follow feedback template. Frontend displays verbatim.
- **Action**: Ensure proper rendering of multiline feedback with formatting

### Principle VII: Phase Boundaries Are Hard Gates
- **Status**: ✅ PASS
- **Reasoning**: Phase I complete (100%), Phase III AI Teaching backend complete (75% - APIs functional). This is Phase IV frontend.
- **Evidence**: Backend coaching APIs exist and functional
- **Action**: None required

### Principle VIII: Question Bank Quality Over Quantity
- **Status**: ✅ PASS (Not Applicable)
- **Reasoning**: Coaching page doesn't interact with question bank directly
- **Action**: None required

### Principle IX: SpecKitPlus Workflow Compliance
- **Status**: ✅ PASS
- **Reasoning**: Currently executing /sp.plan after /sp.specify. Will run /sp.tasks next, then /sp.implement.
- **Evidence**: Branch 004-coaching-page, spec.md, checklists/requirements.md, PHR created
- **Action**: Continue workflow compliance

### Principle X: Official Skills Priority
- **Status**: ✅ PASS
- **Reasoning**: Using official skill `web-artifacts-builder` for UI development (React components)
- **Action**: Verify official skill usage in tasks.md generation

### Principle XI: CLAUDE.md Hierarchy
- **Status**: ✅ PASS
- **Reasoning**: Root CLAUDE.md (228 lines), phase-specific CLAUDE.md planned for Phase IV
- **Action**: Create specs/phase-4-web-ui/CLAUDE.md if not exists (before implementation)

### **GATE DECISION**: ⚠️ CONDITIONAL PASS
- **Violations**: None
- **Required Actions Before Implementation**:
  1. Document JWT verification pattern
  2. Add session ownership integration tests
  3. Create Phase IV CLAUDE.md
- **Proceed to Phase 0**: YES

## Project Structure

### Documentation (this feature)

```text
specs/004-coaching-page/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-client.ts    # TanStack Query hooks for coaching APIs
│   └── types.ts         # TypeScript interfaces for session, message, outcome
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/                           # Next.js 16 App Router
├── app/
│   └── (dashboard)/
│       └── coaching/
│           ├── page.tsx            # Main coaching page route
│           └── [sessionId]/
│               └── page.tsx        # Individual session view (optional, for history)
├── components/
│   └── coaching/
│       ├── SessionInitForm.tsx     # Start new coaching session form
│       ├── ChatInterface.tsx       # Main chat container
│       ├── MessageList.tsx         # Conversation history display
│       ├── MessageBubble.tsx       # Individual message component
│       ├── MessageInput.tsx        # Message composition input
│       ├── TypingIndicator.tsx     # "Coach is thinking..." indicator
│       ├── SessionOutcome.tsx      # Display session conclusion
│       └── SessionHistory.tsx      # Past sessions list (P3)
├── lib/
│   └── api/
│       └── coaching.ts             # TanStack Query hooks + API client
├── hooks/
│   ├── useSession.ts               # Session state management
│   └── useMessages.ts              # Message array management
└── types/
    └── coaching.ts                 # TypeScript interfaces

backend/                            # Existing FastAPI backend (no changes)
└── src/
    └── routes/
        └── coaching.py             # APIs already exist (assumption from spec)

tests/
└── e2e/
    └── coaching/
        ├── start-session.spec.ts   # P1 tests
        ├── chat-conversation.spec.ts # P1 tests
        └── session-outcome.spec.ts # P2 tests
```

**Structure Decision**: Web application structure (frontend + backend). Frontend is Next.js App Router with component-based architecture. Backend APIs pre-exist (Phase III). This feature focuses on frontend implementation only.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Complexity Notes**:
- Chat interface requires real-time state updates (message streaming)
- Session persistence requires localStorage + API state sync
- Error recovery requires retry logic + optimistic updates
- Multi-tenant security requires JWT validation

All complexity is justified by functional requirements (FR-001 to FR-024). No unnecessary abstraction.

---

**Status**: ✅ Plan skeleton complete. Proceeding to Phase 0 (Research) and Phase 1 (Design).
