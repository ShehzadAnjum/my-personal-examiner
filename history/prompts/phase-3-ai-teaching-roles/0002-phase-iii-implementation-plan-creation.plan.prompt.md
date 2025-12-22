---
id: 0002
title: Phase III Implementation Plan Creation
stage: plan
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5
feature: phase-3-ai-teaching-roles
branch: 002-question-bank
user: anjum
command: /sp.plan
labels: ["planning", "phase-3", "ai-teaching-roles", "research", "data-model", "api-contracts"]
links:
  spec: specs/phase-3-ai-teaching-roles/spec.md
  ticket: null
  adr: history/adr/002-ai-teaching-system-6-core-roles.md
  pr: null
files:
  - specs/phase-3-ai-teaching-roles/plan.md
  - specs/phase-3-ai-teaching-roles/research.md
  - specs/phase-3-ai-teaching-roles/data-model.md
  - specs/phase-3-ai-teaching-roles/contracts/teaching-api.yaml
  - specs/phase-3-ai-teaching-roles/contracts/coaching-api.yaml
  - specs/phase-3-ai-teaching-roles/contracts/marking-api.yaml
  - specs/phase-3-ai-teaching-roles/contracts/feedback-api.yaml
  - specs/phase-3-ai-teaching-roles/contracts/planning-api.yaml
  - specs/phase-3-ai-teaching-roles/quickstart.md
tests:
  - None (planning phase - no code written)
---

## Prompt

User executed `/sp.plan` command to create detailed implementation plan for Phase III AI Teaching Roles.

**Context**: Following completion of `/sp.clarify` with 5 critical decisions resolved (coaching transcript structure, LLM fallback, confidence threshold, SM-2 algorithm, interleaving strategy), user requested implementation plan creation before proceeding to `/sp.tasks`.

**User's Emphasis**: "Production v1.0, not MVP demo - this is serious implementation"

**Workflow Step**: `/sp.specify` ✅ → `/sp.clarify` ✅ → `/sp.plan` ⏳ (current) → `/sp.tasks` → `/sp.implement`

## Response snapshot

Executed complete `/sp.plan` workflow with Phase 0 (Research) and Phase 1 (Design & Contracts):

### Phase 0: Research (research.md)

Resolved 6 technical unknowns:
1. **LLM Provider Integration**: Claude Sonnet 4.5 primary, GPT-4/Gemini fallbacks, per-agent temperature configs
2. **SuperMemo 2 Algorithm**: Full SM-2 specification with formulas (I(n) = I(n-1) * EF, EF update formula), performance → quality mapping
3. **Contextual Interleaving**: Algorithm for topic relatedness (same syllabus section), max 3 topics/day, A→B→A→C pattern
4. **Confidence Scoring**: 6-signal heuristic (length mismatch, coverage, partial marks, ambiguous language, AO3 subjectivity, borderline marks), <70% threshold
5. **Double Fallback Strategy**: Retry (exponential backoff 1s, 2s, 4s) → Cache → Alternative LLM → User prompt, circuit breaker pattern
6. **Economics Marking Rubrics**: JSONB encoding of Cambridge mark schemes with AO1/AO2/AO3 breakdown, structured point extraction

### Phase 1: Design & Contracts (data-model.md, contracts/, quickstart.md)

**Data Model**:
- 3 new tables: coaching_sessions (JSONB transcript array), study_plans (JSONB schedule + EF), improvement_plans (JSONB weaknesses + actions)
- Enhanced attempted_questions: confidence_score (0-100), needs_review (bool), reviewed_by, reviewed_at
- 3 Alembic migrations (003, 004, 005)

**API Contracts** (5 OpenAPI YAML files):
- teaching-api.yaml: POST /api/teaching/explain-concept
- coaching-api.yaml: POST /api/coaching/tutor-session, POST /session/{id}/respond, GET /session/{id}
- marking-api.yaml: POST /api/marking/mark-answer, POST /api/marking/mark-attempt
- feedback-api.yaml: POST /api/feedback/analyze-weaknesses, POST /api/feedback/generate-model-answer
- planning-api.yaml: POST /api/planning/create-schedule, GET /api/planning/schedule/{id}, PATCH /api/planning/schedule/{id}/progress

**Quickstart Guide**: 30-minute test guide for all 6 agents with curl examples, expected responses, validation checklists, troubleshooting, performance benchmarks

**Constitutional Compliance**:
- ✅ All 11 principles passing
- ✅ Production v1.0 quality bar emphasized throughout
- ✅ Multi-tenant isolation enforced (student_id FKs)
- ✅ ≥85% marking accuracy target
- ✅ PhD-level teaching/marking/feedback standards

## Outcome

- ✅ Impact: Complete implementation plan with research, data models, API contracts, and test guide. Ready for `/sp.tasks` generation.
- 🧪 Tests: No code tests (planning phase), but defined validation criteria: ≥85% marking accuracy, <5s Teacher/Coach response time, 100% syllabus coverage
- 📁 Files: 9 planning artifacts created (plan.md, research.md, data-model.md, 5 API contracts, quickstart.md)
- 🔁 Next prompts: `/sp.tasks` to generate atomic implementation tasks from this plan, then `/sp.implement` to execute tasks
- 🧠 Reflection: Research phase resolved all technical unknowns with production-quality specifications. SM-2 algorithm fully specified with formulas enables testable implementation. Confidence scoring heuristic (6 signals) provides quantifiable threshold. Double fallback strategy ensures resilience. API contracts comprehensive (request/response schemas, error handling, examples). Quickstart provides end-to-end validation path.

## Evaluation notes (flywheel)

- Failure modes observed: None. User clarifications from /sp.clarify session prevented ambiguity.
- Graders run and results (PASS/FAIL): N/A (planning phase, no graders)
- Prompt variant (if applicable): Standard /sp.plan workflow from SpecKit
- Next experiment (smallest change to try): Execute `/sp.tasks` to validate if plan provides sufficient detail for atomic task breakdown. If tasks are still too large, plan may need more implementation detail in Phase 1.
