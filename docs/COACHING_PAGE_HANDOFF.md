# Coaching Page Implementation Handoff

**Feature**: 004-coaching-page - Interactive AI Tutoring
**Date**: 2025-12-21
**Status**: Phase 1 Complete, Phase 2-4 In Progress
**Branch**: `004-coaching-page`

---

## 🎯 Implementation Strategy

**Using**: @chatscope/chat-ui-kit-react for chat UI (replaces custom components)
**Architecture**: TanStack Query + Polling (2s) + Optimistic Updates + localStorage persistence
**MVP Target**: 42 tasks (Phase 1-4) = User Story 1 (Start Session) + User Story 2 (Chat Conversation)

---

## ✅ Phase 1: Setup Complete (10/10 tasks)

### Directory Structure Created
```
frontend/
├── app/
│   ├── (dashboard)/coaching/    # Coaching page route
│   ├── layout.tsx                # Root layout with Providers
│   ├── providers.tsx             # TanStack Query provider
│   ├── page.tsx                  # Home page
│   └── globals.css               # Tailwind CSS + design tokens
├── components/coaching/          # Coaching components (to be created)
├── lib/
│   ├── api/                      # API client
│   ├── validation/               # Form validation
│   └── utils/                    # Utility functions
├── hooks/                        # Custom React hooks
├── types/
│   └── coaching.ts               # TypeScript types (copied from specs)
└── tests/e2e/coaching/          # Playwright E2E tests
```

### Dependencies Installed

**Production**:
- `@chatscope/chat-ui-kit-react` 2.1.1 - Chat UI components
- `@chatscope/chat-ui-kit-styles` 1.4.0 - Chat UI styles
- `@tanstack/react-query` 5.90.12 - State management + caching
- `@tanstack/react-query-devtools` 5.91.1 - Development tools
- `next` 15.5.9 - Next.js framework
- `react` 19.2.3 - React
- `tailwindcss` 3.4.19 - Styling
- `lucide-react` 0.460.0 - Icons
- Helper libraries: `clsx`, `tailwind-merge`, `class-variance-authority`

**Development**:
- `@playwright/test` 1.57.0 - E2E testing
- `@testing-library/jest-dom` 6.9.1 - Jest DOM matchers
- `@testing-library/react` 16.3.1 - React testing utilities
- `jest` 29.7.0 - Unit testing
- `typescript` 5.9.3 - TypeScript

### Configurations Created

**TypeScript** (`tsconfig.json`):
- Strict mode enabled
- Path aliases configured:
  - `@/components/*` → `./components/*`
  - `@/lib/*` → `./lib/*`
  - `@/hooks/*` → `./hooks/*`
  - `@/types/*` → `./types/*`
  - `@/app/*` → `./app/*`

**Jest** (`jest.config.js`):
- Environment: jsdom
- Coverage threshold: 80% (statements, branches, functions, lines)
- Setup file: `jest.setup.js` (imports @testing-library/jest-dom)

**Playwright** (`playwright.config.ts`):
- Test directory: `./tests/e2e`
- Base URL: `http://localhost:3000`
- Browser: Chromium (Desktop Chrome)
- Web server: Auto-starts dev server

**Tailwind CSS** (`tailwind.config.ts`):
- shadcn/ui design tokens
- Dark mode support
- Custom animations (accordion-down, accordion-up)
- Responsive breakpoints

**Next.js** (`next.config.mjs`):
- React strict mode enabled

**Environment** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEVTOOLS=true
```

### TanStack Query Setup

**Provider** (`app/providers.tsx`):
- Query client with coaching config:
  - Queries: `networkMode: 'offlineFirst'`, `gcTime: 5min`, `retry: 2`
  - Mutations: `networkMode: 'always'`, `retry: 3`
- React Query DevTools enabled in development

**Global CSS** (`app/globals.css`):
- Tailwind base styles
- Design tokens (light/dark mode)
- CSS variables for theming

**Utility** (`lib/utils.ts`):
- `cn()` function for className merging (clsx + tailwind-merge)

---

## 🔄 Phase 2: Foundational (2/7 tasks complete)

### ✅ Completed

**T011**: TypeScript types copied
- Source: `specs/004-coaching-page/contracts/types.ts`
- Destination: `frontend/types/coaching.ts`
- Includes:
  - `CoachingSession`, `Message`, `SessionOutcome`, `NextAction`
  - Request/Response types for all 3 APIs
  - Validation rules constants
  - Frontend state types (`ChatUIState`, `MessageSendState`)

**T012**: API client implementation (80% complete)
- Source: `specs/004-coaching-page/contracts/api-client.ts`
- Destination: `frontend/lib/api/coaching.ts`
- Includes:
  - `useStartSession()` - Start coaching session
  - `useSendMessage()` - Send message with optimistic updates
  - `useSession()` - Fetch session with polling (2s)
  - `useSessions()` - List all sessions (P3)
  - `useOnlineStatus()` - Detect offline
  - `useSessionOwnership()` - Multi-tenant security
- **Note**: Needs "use client" directive cleanup

### ⏳ Remaining Tasks (T013-T017)

**T013**: Create `useOnlineStatus` hook
- File: `frontend/hooks/useOnlineStatus.ts`
- Detects: `navigator.onLine` + network events

**T014**: Create `useSessionOwnership` hook
- File: `frontend/hooks/useSessionOwnership.ts`
- Validates: Student can only access their own sessions

**T015**: Create coaching page route
- File: `frontend/app/(dashboard)/coaching/page.tsx`
- Empty placeholder (will be populated in Phase 3-4)

**T016**: Setup global error boundary
- File: `frontend/app/error.tsx`
- Catches unhandled errors

**T017**: Verify backend APIs
- Method: `curl` commands to test:
  - `POST /api/coaching/tutor-session`
  - `POST /api/coaching/session/{id}/respond`
  - `GET /api/coaching/session/{id}`

---

## 📋 Phase 3: User Story 1 - Start Session (0/9 tasks)

**Goal**: Student can start coaching session and see coach's first question

### Tasks

**T018**: E2E test - `tests/e2e/coaching/start-session.spec.ts`
- Test: Empty validation, loading state, coach question appears, session ID generated

**T019**: SessionInitForm component - `components/coaching/SessionInitForm.tsx`
- Textarea for struggle description
- Validation (min 10 chars, max 500 chars)
- Submit button

**T020**: Validation utilities - `lib/validation/coaching.ts`
- Topic validation (10-500 chars, pattern)

**T021**: Integrate useStartSession hook in SessionInitForm
- Mutation, loading state, error handling

**T022**: Update coaching page route
- Render SessionInitForm when no active session

**T023**: LoadingIndicator component - `components/coaching/LoadingIndicator.tsx`
- "Coach is preparing your session..."

**T024**: Handle session creation success
- Store session ID in state
- Display first coach message

**T025**: Error handling for session creation
- User-friendly error messages
- Retry option

**T026**: Accessibility for SessionInitForm
- ARIA labels, keyboard navigation, screen reader support

---

## 📋 Phase 4: User Story 2 - Chat Conversation (0/16 tasks)

**Goal**: Real-time chat with coach using ChatScope components

### ChatScope Integration Strategy

**Original Plan** (5 custom components):
- MessageBubble, TypingIndicator, MessageInput, MessageList, ChatInterface

**With ChatScope** (simplified):
- Use ChatScope's `MainContainer`, `ChatContainer`, `MessageList`, `Message`, `MessageInput`, `TypingIndicator`
- Customize with Tailwind to match shadcn/ui design
- Integrate with TanStack Query hooks (useSession, useSendMessage)

### Tasks (Modified for ChatScope)

**T027**: E2E test - `tests/e2e/coaching/chat-conversation.spec.ts`

**T028**: Import ChatScope and configure styles
```tsx
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  Avatar
} from '@chatscope/chat-ui-kit-react'
```

**T029**: Create ChatInterface component with ChatScope
- File: `components/coaching/ChatInterface.tsx`
- Use ChatScope's MainContainer + ChatContainer
- Integrate useSession hook (polling: 2s)
- Integrate useSendMessage hook (optimistic updates)

**T030**: Customize ChatScope theme
- Match shadcn/ui Tailwind design
- Custom CSS for student/coach message alignment

**T031-T042**: Integration tasks
- localStorage persistence
- Auto-scroll
- Timestamp formatting
- Network status banner
- Retry indicator
- Accessibility

---

## 🔧 How to Continue Implementation

### Start Development Server

```bash
cd frontend
pnpm dev
```

Server runs at: `http://localhost:3000`

### Run Tests

```bash
# Unit tests
pnpm test

# E2E tests (requires dev server running)
pnpm test:e2e

# E2E with UI
pnpm test:e2e:ui
```

### Verify Backend APIs

```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Test coaching API (requires JWT token)
curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"topic": "I dont understand price elasticity"}'
```

---

## 📂 Key Files Reference

### Specifications
- **Spec**: `specs/004-coaching-page/spec.md`
- **Plan**: `specs/004-coaching-page/plan.md`
- **Tasks**: `specs/004-coaching-page/tasks.md`
- **Data Model**: `specs/004-coaching-page/data-model.md`
- **Research**: `specs/004-coaching-page/research.md`
- **Quickstart**: `specs/004-coaching-page/quickstart.md`

### Contracts (Reference)
- **Types**: `specs/004-coaching-page/contracts/types.ts`
- **API Client**: `specs/004-coaching-page/contracts/api-client.ts`

### Frontend Implementation
- **Types**: `frontend/types/coaching.ts`
- **API Client**: `frontend/lib/api/coaching.ts`
- **Providers**: `frontend/app/providers.tsx`

---

## 🎯 Next Steps (MVP Completion)

### Immediate (Phase 2 completion)
1. ✅ Extract useOnlineStatus to separate hook file
2. ✅ Extract useSessionOwnership to separate hook file
3. ✅ Create coaching page route placeholder
4. ✅ Create error boundary
5. ✅ Verify backend APIs (manual curl test)

### Phase 3 (User Story 1)
6. Write E2E test for session start
7. Build SessionInitForm component
8. Create validation utilities
9. Integrate useStartSession hook
10. Update coaching page route
11. Add loading indicator
12. Handle success/error states
13. Add accessibility

### Phase 4 (User Story 2)
14. Write E2E test for chat
15. Import and configure ChatScope
16. Build ChatInterface with ChatScope components
17. Customize ChatScope theme (Tailwind)
18. Integrate useSession (polling)
19. Integrate useSendMessage (optimistic updates)
20. Add localStorage persistence
21. Add auto-scroll, timestamps, network banner
22. Add accessibility

### MVP Complete (Checkpoint)
23. Test end-to-end: Start session → Chat → See coach responses
24. Verify performance: Session <3s, Message <2s, Response <10s
25. Verify security: Multi-tenant isolation
26. Deploy/Demo

---

## 🚨 Critical Notes

### ChatScope vs Custom Components
- **Decision**: Use @chatscope/chat-ui-kit-react
- **Rationale**: Saves 80% UI implementation time, professional ChatGPT-style UI, works with our TanStack Query architecture
- **Impact**: Reduces Phase 4 from 16 tasks to ~9 tasks

### Backend APIs
- **Assumption**: Backend coaching APIs are functional from Phase III
- **Required Endpoints**:
  - `POST /api/coaching/tutor-session` (start session)
  - `POST /api/coaching/session/{id}/respond` (send message)
  - `GET /api/coaching/session/{id}` (get transcript)
- **Auth**: JWT token required (from Phase I)

### Multi-Tenant Security
- **Critical**: Session ownership must be verified
- **Test**: Student A cannot access Student B's session (403 error)
- **Task T071**: Security verification E2E test (in Phase 7 - Polish)

### Performance Targets
- Session creation: <3 seconds
- Message send: <2 seconds
- Coach response: <10 seconds (95th percentile)
- Chat scroll: 60 FPS

---

## 📊 Task Completion Status

**Total Tasks**: 76
**Completed**: 12 (16%)
**Remaining**: 64

**MVP Tasks** (Phase 1-4): 42 total
**MVP Completed**: 12 (29%)
**MVP Remaining**: 30

**Estimated Time to MVP**: 3-4 hours (with ChatScope)

---

## 🔗 Links

**Documentation**:
- ChatScope Docs: https://chatscope.io/storybook/react/
- TanStack Query Docs: https://tanstack.com/query/latest/docs/react/overview
- shadcn/ui Docs: https://ui.shadcn.com/docs

**PHRs** (Prompt History Records):
- Spec: `history/prompts/004-coaching-page/0001-coaching-page-specification.spec.prompt.md`
- Plan: `history/prompts/004-coaching-page/0002-coaching-page-implementation-plan.plan.prompt.md`
- Tasks: `history/prompts/004-coaching-page/0003-coaching-page-task-breakdown.tasks.prompt.md`

---

**Last Updated**: 2025-12-21
**Next Session**: Continue from Phase 2 Task T013 (useOnlineStatus hook)
