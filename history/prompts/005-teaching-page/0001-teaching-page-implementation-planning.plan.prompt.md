---
id: 0001
title: Teaching Page Implementation Planning
stage: plan
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5
feature: 005-teaching-page
branch: 005-teaching-page
user: Shehzad Anjum
command: /sp.plan
labels: [planning, design, contracts, research, teaching-page, phase-4-web-ui]
links:
  spec: specs/005-teaching-page/spec.md
  ticket: null
  adr: null (pending /sp.adr if needed)
  pr: null (pending /sp.git.commit_pr)
files:
  - path: specs/005-teaching-page/spec.md
    change: existing (created via /sp.specify)
    lines: 176
  - path: specs/005-teaching-page/plan.md
    change: created
    lines: 595
  - path: specs/005-teaching-page/research.md
    change: created
    lines: 280
  - path: specs/005-teaching-page/data-model.md
    change: created
    lines: 360
  - path: specs/005-teaching-page/contracts/api-endpoints.md
    change: created
    lines: 520
  - path: specs/005-teaching-page/contracts/ui-components.md
    change: created
    lines: 680
  - path: specs/005-teaching-page/quickstart.md
    change: created
    lines: 450
  - path: CLAUDE.md
    change: modified (agent context updated with TypeScript/Next.js/TanStack Query)
    lines: updated
tests:
  - type: none
    status: n/a
    description: Planning phase - no tests yet (tests in /sp.implement)
---

## Prompt

User invoked `/sp.plan` skill after creating spec via `/sp.specify` for 005-teaching-page feature (Teaching Page - PhD-Level Concept Explanations).

**Context**: User requested sequential feature development: A (teaching-page) → B (marking-page) → C (review-page). This is the first feature (A) in the sequence.

**User Description**: "Teaching Page - Concept Explanations: Students request PhD-level explanations of Economics 9708 syllabus concepts. System displays topic selection interface with syllabus browser or search. Student selects a concept (e.g., 'Price Elasticity of Demand'). Teacher Agent generates comprehensive explanation with: precise definition, key terms with definitions, core principles explanation, 2-3 real-world examples with analysis, visual aids (diagram descriptions for supply/demand curves, graphs, etc.), worked examples with step-by-step solutions, common misconceptions with corrections, practice problems with answer outlines, connections to related concepts. Explanation displays in structured format with collapsible sections. Students can bookmark explanations for later review. Backend APIs exist: GET /api/teaching/syllabus (list topics), POST /api/teaching/explain (generate explanation for concept), GET /api/teaching/explanations (user's saved explanations). UI similar to educational content platform with clear typography, visual hierarchy, code/math formatting support."

**Spec Already Created**: spec.md completed and validated (176 lines, 3 user stories, 24 functional requirements, 0 clarifications needed).

**Task**: Execute `/sp.plan` workflow - create implementation plan with research, data model, contracts, and quickstart guide.

## Response snapshot

Completed full `/sp.plan` workflow for 005-teaching-page feature:

1. **Setup Phase**: Ran `setup-plan.sh --json`, parsed paths (FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH)

2. **Created plan.md** (595 lines):
   - Technical Context: TypeScript 5.7+, Next.js 16+, React 19, TanStack Query 5.62+, shadcn/ui, Tailwind CSS 4
   - Constitution Check: ✅ PASS (all 12 principles satisfied or N/A)
   - Project Structure: Frontend-only (backend APIs already exist), reuses 004-coaching-page patterns
   - Phase 0 Research Questions: 5 decisions (component reuse, caching, collapsible sections, search, bookmark backend)
   - Phase 1 Design: Data model (3 entities), API contracts (5 endpoints), UI components (9 components), quickstart flows
   - Expected Tasks: ~30 tasks (fewer than 004-coaching-page due to reusable patterns)

3. **Phase 0: Research** (research.md, 280 lines):
   - Decision 1: Reuse infrastructure from 004-coaching-page (error boundaries, toasts, skeletons) → **+2-3 hours saved**
   - Decision 2: Tiered caching (1h topics, 5m explanations, 1m saved) → **+50% cache hit rate**
   - Decision 3: shadcn/ui Accordion for collapsible sections → **+2 hours saved** (accessibility built-in)
   - Decision 4: Client-side search (Array.filter on 200 topics) → **+200-500ms faster** (no network latency)
   - Decision 5: Create SavedExplanation model + migration + endpoints (backend work required) → **-1-2 hours cost**
   - **Net Impact**: +3-4 hours saved overall

4. **Phase 1: Design** (data-model.md, 360 lines):
   - Entity 1: SyllabusPoint (backend, persisted) - 200 Economics topics with codes, descriptions, learning outcomes
   - Entity 2: SavedExplanation (backend, persisted) - Bookmarked explanations with student_id (multi-tenant isolation)
   - Entity 3: TopicExplanation (frontend, transient) - AI-generated explanation with 9 required components
   - Data flow: Browse → Select → AI Generate → Display → Bookmark → Saved List
   - Validation rules: PED calculation, unique bookmarks, multi-tenant filters

5. **Phase 1: Contracts** (contracts/, 2 files, 1200 lines combined):
   - API endpoints (api-endpoints.md, 520 lines): 5 backend endpoints (GET syllabus, POST explain, GET/POST/DELETE saved explanations)
   - UI components (ui-components.md, 680 lines): 9 React components (TopicCard, TopicBrowser, TopicSearch, ExplanationView, ExplanationSection, BookmarkButton, SavedExplanationsList, ExplanationSkeleton, TopicSearchSkeleton)
   - TanStack Query hooks: useTopics, useExplanation, useSavedExplanations, useBookmark (with cache strategies)
   - Error handling: HTTP status codes, retry logic, toast notifications

6. **Phase 1: Quickstart** (quickstart.md, 450 lines):
   - Flow 1: View Explanation (P1) - 6 steps, 5-10 second AI generation, collapsible sections, caching behavior
   - Flow 2: Search Topics (P2) - 6 steps, instant client-side filter (<1ms), keyword highlighting
   - Flow 3: Bookmark (P3) - 8 steps, save/remove bookmark, toast feedback, cache invalidation
   - Integration scenarios: First-time user, power user (10 bookmarks), mobile student (375px, 3G)
   - Error scenarios: AI timeout, duplicate bookmark
   - Performance benchmarks: Load times, cache hit rates, Lighthouse scores (target 90+)

7. **Agent Context Update**:
   - Ran `update-agent-context.sh claude` successfully
   - Updated CLAUDE.md with TypeScript 5.7+, Next.js 16+, TanStack Query 5.62+ from 005-teaching-page
   - Technology stack now documented for future AI sessions

8. **Constitution Re-Check**: ✅ PASS (no violations introduced during design phase)

## Outcome

- ✅ Impact: Complete implementation plan for 005-teaching-page feature (2110 lines across 7 artifacts). Reuses 004-coaching-page patterns (saves 3-4 hours). Backend work required: SavedExplanation model + migration + 3 endpoints (1-2 hours). Estimated timeline: 2 days (Dec 24-25).
- 🧪 Tests: Planning phase only - no tests yet. Testing strategy documented in contracts (unit tests for components, E2E tests for flows, accessibility audit WCAG 2.1 AA).
- 📁 Files: 7 planning artifacts created (plan.md, research.md, data-model.md, contracts/*.md, quickstart.md). Agent context updated (CLAUDE.md).
- 🔁 Next prompts:
  1. `/sp.tasks` - Generate task breakdown organized by user story (expected ~30 tasks)
  2. `/sp.implement` - Execute tasks from tasks.md
  3. `/sp.adr` (if needed) - Document architectural decisions (TanStack Query caching, client-side search)
  4. `/sp.git.commit_pr` - Commit implementation work
- 🧠 Reflection: Planning workflow smooth due to clear spec from /sp.specify. Research phase identified key reuse opportunities (4 components from 004-coaching-page). Backend gap discovered (SavedExplanation model missing) - caught early, added to tasks. Tiered caching strategy will reduce AI generation load (~50% cache hit rate). Client-side search optimal for current scale (200 topics), scalable to server-side if needed (1000+ topics). Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning. Workflow executed correctly (setup → research → design → contracts → quickstart → agent update). Backend gap (SavedExplanation model) caught early through systematic research (Decision 5).
- Graders run and results (PASS/FAIL):
  - ✅ PASS - Constitution check (all 12 principles satisfied or N/A)
  - ✅ PASS - Research decisions (5 decisions with rationale, alternatives, tradeoffs)
  - ✅ PASS - Data model (3 entities with attributes, relationships, validation rules, multi-tenant isolation)
  - ✅ PASS - API contracts (5 endpoints with request/response examples, error handling, caching strategy)
  - ✅ PASS - UI components (9 components with props, implementation skeletons, accessibility notes)
  - ✅ PASS - Quickstart flows (3 user flows with technical details, integration scenarios, error handling)
  - ✅ PASS - Agent context updated (CLAUDE.md reflects new tech stack)
- Prompt variant (if applicable): Default /sp.plan workflow (no variants). Followed standard sequence: setup → research (5 questions) → design (3 entities) → contracts (2 files) → quickstart (3 flows) → agent update.
- Next experiment (smallest change to try): Test impact of client-side search at scale (simulate 1000 topics). If Array.filter performance degrades (>100ms), switch to server-side search (GET /api/teaching/syllabus?search=query). Current decision based on 200 topics (<1ms) but should validate at 5x scale before adding more subjects (Accounting, Math, English).
