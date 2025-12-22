# Implementation Plan: Phase III - AI Teaching Roles

**Branch**: `003-ai-teaching-roles` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase-3-ai-teaching-roles/spec.md`
**Quality Bar**: Production v1.0 (not MVP demo - serious, robust implementation)

## Summary

Implement 6 core AI teaching roles (Teacher, Coach, Examiner, Marker, Reviewer, Planner) for Economics 9708, creating a fully automated PhD-level learning system. Students will learn topics, get tutoring help, take Cambridge-standard exams, receive strict marking with confidence scoring, see A* model answers with improvement plans, and follow personalized study schedules using SuperMemo 2 spaced repetition with contextual interleaving.

**Technical Approach**: FastAPI services leveraging Claude Sonnet 4.5 for teaching/coaching/marking/reviewing, SuperMemo 2 algorithm for planning, PostgreSQL JSONB for flexible data storage, production-ready error handling with double fallback (retry → cache → alternative LLM), and confidence-based manual review queuing for quality assurance.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**:
- FastAPI 0.115+, SQLModel 0.0.22+, PostgreSQL 16 (Neon)
- Claude Sonnet 4.5 (Anthropic API), GPT-4/Gemini (fallback LLMs)
- OpenAI embeddings (optional for caching/similarity)

**Storage**: PostgreSQL with JSONB fields for:
- coaching_sessions.session_transcript (array of {role, content, timestamp})
- study_plans.schedule (day-by-day with SM-2 intervals)
- study_plans.easiness_factors (SM-2 EF per syllabus point)
- improvement_plans.weaknesses (categorized by AO1/AO2/AO3)
- improvement_plans.action_items (specific remediation tasks)

**Testing**: pytest 8.3+ with ≥80% coverage target, accuracy validation vs. Cambridge mark schemes (≥85% agreement), integration tests for all 6 agents, end-to-end workflow test

**Target Platform**: Linux server (Neon PostgreSQL), Vercel deployment ready

**Project Type**: Web (backend services) - extends existing FastAPI backend

**Performance Goals**:
- <5s average response time for Teacher/Coach agents
- <10s timeout for teaching explanations (with fallback)
- ≥85% marking accuracy vs. Cambridge mark schemes
- 100% syllabus coverage in study plans

**Constraints**:
- Economics 9708 ONLY (extensibility for other subjects in Phase V)
- PhD-level strictness (Constitutional Principle II)
- Cambridge syllabus alignment (Constitutional Principle I)
- Multi-tenant data isolation (Constitutional Principle V)
- All feedback MUST explain WHY + HOW (Constitutional Principle VI)

**Scale/Scope**:
- 6 new services (Teaching, Coaching, Marking, Review, Planning, enhanced Exam Generation)
- 8 new API endpoints
- 3 new database tables
- 7 custom skills (.claude/skills/)
- 38 implementation tasks across 8 task groups

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Compliance Analysis

| Principle | Status | Notes |
|-----------|--------|-------|
| **I: Subject Accuracy** | ✅ PASS | Teacher explanations verified against Cambridge syllabus, Marker uses official mark schemes |
| **II: A* Standard** | ✅ PASS | PhD-level teaching (Teacher/Coach), strict marking (Marker), A* model answers (Reviewer), production v1.0 quality bar |
| **III: Syllabus Sync** | ✅ PASS | Integration with syllabus_points table, 100% coverage in study plans |
| **IV: Spec-Driven** | ✅ PASS | This spec created via /sp.specify, plan via /sp.plan, tasks via /sp.tasks to follow |
| **V: Multi-Tenant** | ✅ PASS | All services require student_id parameter, no cross-student data access |
| **VI: Constructive Feedback** | ✅ PASS | Reviewer always explains WHY wrong + HOW to improve, A* model answers with annotations |
| **VII: 80% Test Coverage** | ✅ PASS | All new services require ≥80% coverage, integration tests for endpoints |
| **VIII: Quality Over Quantity** | ✅ PASS | Phase III builds on Phase II question bank (100+ verified Economics questions) |
| **IX: SpecKitPlus Workflow** | ✅ PASS | Following /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement |
| **X: Official Skills Priority** | ✅ PASS | Using official Anthropic skills (pdf, docx, xlsx), creating domain-specific custom skills only |
| **XI: CLAUDE.md Hierarchy** | ✅ PASS | Will create specs/phase-3-ai-teaching-roles/CLAUDE.md (<300 lines) |

### Phase-Specific Rules (Phase III)

**Objective**: Implement Economics 9708 marking engine with PhD-level feedback (Constitutional Phase III definition)

**Features**:
1. ✅ Economics 9708 marking engine (theory validation, diagram checking, evaluation scoring) - **EXPANDED** to include Teacher, Coach, Planner, Reviewer
2. ✅ AI-powered feedback generator
3. ✅ Weakness analyzer
4. ✅ Answer rewriter (to A* standard)
5. ✅ Progress tracking
6. ✅ **NEW**: Teacher Agent (concept explanations)
7. ✅ **NEW**: Coach Agent (personalized tutoring)
8. ✅ **NEW**: Planner Agent (study schedule generation)
9. ✅ **NEW**: Examiner Agent enhancement (personalization)

**Explicit Non-Goals** (per constitution):
- ❌ Other subjects' marking engines (Phase V+)
- ❌ Web UI (Phase IV)
- ❌ MCP servers (Phase V)

**Deliverables Checklist** (constitutional compliance):
- [ ] `specs/phase-3-ai-teaching-roles/` (spec ✅, plan ✅, tasks ⏳)
- [ ] 6 agent services (Teacher, Coach, Examiner, Marker, Reviewer, Planner)
- [ ] 8 API endpoints
- [ ] 3 database migrations (coaching_sessions, study_plans, improvement_plans)
- [ ] 7 custom skills (.claude/skills/)
- [ ] Unit tests (>80% coverage)
- [ ] Accuracy tests (>85% vs Cambridge schemes)
- [ ] Integration tests (all endpoints)
- [ ] End-to-end workflow test

**Time Budget**: 7-10 days (focused implementation with production-grade testing)

**Phase III Complete Checklist** (constitutional gate):
- [ ] Can mark Economics 9708 answers with >85% accuracy
- [ ] Feedback explains WHY and HOW to improve
- [ ] Can rewrite answers to A* standard
- [ ] Weaknesses identified with remediation suggestions
- [ ] Can teach topics with PhD-level clarity
- [ ] Can provide personalized tutoring (Coach)
- [ ] Can generate n-day study plans with SM-2
- [ ] Tested on 50+ past paper questions
- [ ] All 6 roles working end-to-end
- [ ] `scripts/check-phase-3-complete.sh` passes

### Complexity Violations (None)

No constitutional violations. All complexity justified by production v1.0 requirement.

## Project Structure

### Documentation (this feature)

```text
specs/phase-3-ai-teaching-roles/
├── spec.md              # Feature specification (/sp.specify output) ✅
├── plan.md              # This file (/sp.plan output) ✅
├── research.md          # Phase 0 output (/sp.plan - LLM providers, SM-2, algorithms) ⏳
├── data-model.md        # Phase 1 output (/sp.plan - JSONB schemas, tables) ⏳
├── contracts/           # Phase 1 output (/sp.plan - API request/response schemas) ⏳
├── quickstart.md        # Phase 1 output (/sp.plan - testing each agent) ⏳
├── tasks.md             # Phase 2 output (/sp.tasks command) ⏳
└── CLAUDE.md            # Phase-specific AI instructions (<300 lines) ⏳
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── coaching_session.py       # NEW: CoachingSession model
│   │   ├── study_plan.py              # NEW: StudyPlan model
│   │   └── improvement_plan.py        # NEW: ImprovementPlan model
│   ├── services/
│   │   ├── teaching_service.py        # NEW: Teacher Agent
│   │   ├── coaching_service.py        # NEW: Coach Agent
│   │   ├── marking_service.py         # NEW: Marker Agent
│   │   ├── review_service.py          # NEW: Reviewer Agent
│   │   ├── planning_service.py        # NEW: Planner Agent (SM-2)
│   │   └── exam_generation_service.py # ENHANCE: Personalization
│   ├── routes/
│   │   ├── teaching.py                # NEW: /api/teaching/*
│   │   ├── coaching.py                # NEW: /api/coaching/*
│   │   ├── marking.py                 # NEW: /api/marking/*
│   │   ├── feedback.py                # NEW: /api/feedback/*
│   │   └── planning.py                # NEW: /api/planning/*
│   ├── ai_integration/
│   │   ├── anthropic_client.py        # NEW: Claude Sonnet 4.5 client
│   │   ├── openai_client.py           # NEW: GPT-4 fallback client
│   │   ├── gemini_client.py           # NEW: Gemini fallback client
│   │   ├── llm_fallback.py            # NEW: Double fallback orchestrator
│   │   └── prompt_templates/          # NEW: Agent-specific prompts
│   │       ├── teacher_prompts.py
│   │       ├── coach_prompts.py
│   │       ├── marker_prompts.py
│   │       ├── reviewer_prompts.py
│   │       └── planner_prompts.py
│   ├── algorithms/
│   │   ├── supermemo2.py              # NEW: SM-2 spaced repetition
│   │   └── contextual_interleaving.py # NEW: Topic mixing logic
│   └── schemas/
│       ├── teaching_schemas.py        # NEW: Request/response models
│       ├── coaching_schemas.py
│       ├── marking_schemas.py
│       ├── feedback_schemas.py
│       └── planning_schemas.py
├── alembic/versions/
│   ├── 003_coaching_sessions.py       # NEW: Migration
│   ├── 004_study_plans.py             # NEW: Migration
│   └── 005_improvement_plans.py       # NEW: Migration
└── tests/
    ├── unit/
    │   ├── test_teaching_service.py
    │   ├── test_coaching_service.py
    │   ├── test_marking_service.py
    │   ├── test_review_service.py
    │   ├── test_planning_service.py
    │   ├── test_supermemo2.py         # SM-2 algorithm tests
    │   └── test_llm_fallback.py       # Fallback strategy tests
    ├── integration/
    │   ├── test_teaching_routes.py
    │   ├── test_coaching_routes.py
    │   ├── test_marking_routes.py
    │   ├── test_feedback_routes.py
    │   ├── test_planning_routes.py
    │   └── test_end_to_end_workflow.py # Full learning cycle
    └── accuracy/
        └── test_marking_accuracy.py   # ≥85% vs Cambridge mark schemes

.claude/
├── agents/
│   ├── 08-teacher.md                  # CREATED: Teacher Agent definition
│   ├── 09-coach.md                    # CREATED: Coach Agent definition
│   ├── 10-examiner.md                 # CREATED: Examiner Agent definition
│   ├── 11-marker.md                   # CREATED: Marker Agent definition
│   ├── 12-reviewer.md                 # CREATED: Reviewer Agent definition
│   └── 13-planner.md                  # CREATED: Planner Agent definition
└── skills/
    ├── phd-pedagogy.md                # NEW: Evidence-based teaching strategies
    ├── a-star-grading-rubrics.md      # NEW: Cambridge A* criteria
    ├── subject-economics-9708.md      # NEW: Economics domain knowledge
    ├── supermemo2-scheduling.md       # NEW: SM-2 algorithm skill
    ├── contextual-interleaving.md     # NEW: Interleaving strategy skill
    ├── anthropic-api-patterns.md      # NEW: Claude integration patterns
    └── confidence-scoring.md          # NEW: Marking confidence calculation

history/
├── adr/
│   ├── 003-sm2-algorithm-choice.md    # NEW: Why SuperMemo 2
│   ├── 004-llm-fallback-strategy.md   # NEW: Double fallback approach
│   └── 005-confidence-threshold.md    # NEW: 70% manual review threshold
└── prompts/
    └── phase-3-ai-teaching-roles/
        └── 0001-phase-iii-spec-clarification-session.spec.prompt.md # CREATED
```

**Structure Decision**: Web application (Option 2) - extending existing backend/ directory with new services, routes, and AI integration layer. No frontend changes (Phase IV).

## Complexity Tracking

No violations requiring justification. All complexity aligns with production v1.0 quality bar and constitutional principles.

## Phase 0: Outline & Research

### Research Tasks

**R1: LLM Provider Integration Patterns**
- **Unknown**: Best practices for Claude Sonnet 4.5 integration (Anthropic API)
- **Research**: Official Anthropic docs, error handling, rate limiting, streaming
- **Deliverable**: `research.md` section on Anthropic API patterns
- **Output**: anthropic_client.py implementation pattern

**R2: SuperMemo 2 (SM-2) Algorithm**
- **Unknown**: SM-2 formula, easiness factor calculation, interval computation
- **Research**: Original SM-2 paper, Anki implementation, production edge cases
- **Deliverable**: `research.md` section on SM-2 with formula breakdown
- **Output**: supermemo2.py implementation with unit tests

**R3: Contextual Interleaving Strategy**
- **Unknown**: How to determine "related topics" algorithmically
- **Research**: Cognitive science papers, syllabus structure analysis
- **Deliverable**: `research.md` section on interleaving patterns
- **Output**: contextual_interleaving.py with topic grouping rules

**R4: Marking Confidence Scoring**
- **Unknown**: How to calculate 0-100 confidence score from LLM output
- **Research**: LLM confidence calibration, logprobs analysis, ensemble methods
- **Deliverable**: `research.md` section on confidence calculation
- **Output**: confidence_scoring.py algorithm

**R5: Double Fallback Strategy**
- **Unknown**: Retry timing, cache invalidation, alternative LLM selection
- **Research**: Resilience patterns, exponential backoff, circuit breakers
- **Deliverable**: `research.md` section on fallback orchestration
- **Output**: llm_fallback.py with retry logic

**R6: Economics 9708 Marking Rubrics**
- **Unknown**: Detailed AO1/AO2/AO3 mark allocation per question type
- **Research**: Cambridge examiner reports, specimen papers, mark schemes
- **Deliverable**: `research.md` section on marking criteria
- **Output**: economics_marker.py rubric encoding

### Research Consolidation (research.md)

Output format:
```markdown
# Phase III Research: AI Teaching Roles

## Decision 1: LLM Provider (Claude Sonnet 4.5)
**Chosen**: Anthropic Claude Sonnet 4.5 as primary, GPT-4/Gemini as fallbacks
**Rationale**: [reasons]
**Alternatives**: [OpenAI GPT-4 only, Google Gemini only]

## Decision 2: Spaced Repetition (SuperMemo 2)
**Chosen**: SM-2 algorithm with production-grade implementation
**Rationale**: [proven effectiveness, clear formulas, Anki uses it]
**Alternatives**: [SM-15+, FSRS, Leitner system]
...
```

## Phase 1: Design & Contracts

### Data Model (data-model.md)

**Entities** (extracted from spec.md + clarifications):

**1. CoachingSession**
- **Fields**: id (UUID), student_id (UUID FK), topic (VARCHAR 500), struggle_description (TEXT), session_transcript (JSONB array), outcome (VARCHAR 50), created_at (TIMESTAMP)
- **Validation**: session_transcript MUST be array of {role, content, timestamp} objects
- **Relationships**: BelongsTo Student
- **State**: outcome ∈ {"resolved", "needs_more_help", "refer_to_teacher"}

**2. StudyPlan**
- **Fields**: id (UUID), student_id (UUID FK), subject_id (UUID FK), exam_date (DATE), total_days (INT), hours_per_day (FLOAT), schedule (JSONB array), easiness_factors (JSONB object), status (VARCHAR 20), created_at, updated_at
- **Validation**:
  - schedule: array of {day, topics[], interval, activities[]}
  - easiness_factors: object {"9708.1.1": 2.5, "9708.2.1": 2.8}
- **Relationships**: BelongsTo Student, BelongsTo Subject
- **State**: status ∈ {"active", "completed", "abandoned"}

**3. ImprovementPlan**
- **Fields**: id (UUID), student_id (UUID FK), attempt_id (UUID FK), weaknesses (JSONB), action_items (JSONB), progress (JSONB), created_at
- **Validation**:
  - weaknesses: {"AO1": [...], "AO2": [...], "AO3": [...]}
  - action_items: array of {action, completed, due_date}
- **Relationships**: BelongsTo Student, BelongsTo Attempt

**4. MarkingResult** (enhancement to attempted_questions)
- **New Fields**: confidence_score (INT 0-100), needs_review (BOOLEAN)
- **Validation**: needs_review = true if confidence_score < 70

### API Contracts (contracts/ directory)

**Teacher Agent**:
- `POST /api/teaching/explain-concept`
  - Request: {syllabus_point_id: UUID, student_id: UUID}
  - Response: {explanation: string, examples: [], diagrams: [], practice_problems: []}
  - Error: 404 (syllabus point not found), 500 (LLM failure with fallback attempted)

**Coach Agent**:
- `POST /api/coaching/tutor-session`
  - Request: {topic: string, struggle_description: string, student_id: UUID}
  - Response: {session_id: UUID, first_question: string, session_status: string}
  - Error: 500 (LLM failure)

**Marker Agent**:
- `POST /api/marking/mark-answer`
  - Request: {question_id: UUID, student_answer: string, student_id: UUID}
  - Response: {marks_awarded: int, max_marks: int, ao1_score: int, ao2_score: int, ao3_score: int, errors: [], confidence_score: int, needs_review: bool}
  - Error: 404 (question not found), 500 (marking failure)

**Reviewer Agent**:
- `POST /api/feedback/analyze-weaknesses`
  - Request: {attempt_id: UUID, student_id: UUID}
  - Response: {weaknesses: {AO1: [], AO2: [], AO3: []}, improvement_plan_id: UUID}

- `POST /api/feedback/generate-model-answer`
  - Request: {question_id: UUID, student_answer: string}
  - Response: {model_answer: string, annotations: [], comparison: string}

**Planner Agent**:
- `POST /api/planning/create-schedule`
  - Request: {subject_id: UUID, exam_date: date, hours_per_day: float, student_id: UUID}
  - Response: {plan_id: UUID, schedule: [], total_days: int}

- `GET /api/planning/schedule/{id}`
  - Response: {plan_id: UUID, schedule: [], progress: int}

- `PATCH /api/planning/schedule/{id}/progress`
  - Request: {completed_day: int, performance_data: {}}
  - Response: {updated_schedule: [], next_day: int}

### Quickstart Guide (quickstart.md)

```markdown
# Phase III Quickstart: Testing AI Teaching Roles

## Prerequisites
- Phase II complete (question bank, exam generation working)
- Anthropic API key set in .env (ANTHROPIC_API_KEY=...)
- PostgreSQL database running

## Test Teacher Agent
```bash
curl -X POST http://localhost:8000/api/teaching/explain-concept \
  -H "Content-Type: application/json" \
  -d '{"syllabus_point_id": "<UUID>", "student_id": "<UUID>"}'
```

## Test Coach Agent
```bash
curl -X POST http://localhost:8000/api/coaching/tutor-session \
  -H "Content-Type: application/json" \
  -d '{"topic": "price elasticity of demand", "struggle_description": "I dont understand why PED is negative", "student_id": "<UUID>"}'
```

## Test Marker Agent
```bash
curl -X POST http://localhost:8000/api/marking/mark-answer \
  -H "Content-Type: application/json" \
  -d '{"question_id": "<UUID>", "student_answer": "Demand is...", "student_id": "<UUID>"}'
```

## Expected Results
- Teacher: Structured explanation with examples and diagrams
- Coach: Socratic question to diagnose misconception
- Marker: Marks breakdown + confidence score + needs_review flag
```

### Agent Context Update

After creating contracts, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This adds Phase III technology context (Claude Sonnet 4.5, SM-2, JSONB schemas) to `.claude/context.md`.

## Post-Phase 1: Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| **I: Subject Accuracy** | ✅ PASS | All APIs reference syllabus_points table |
| **II: A* Standard** | ✅ PASS | Model answers, strict marking, PhD-level teaching |
| **V: Multi-Tenant** | ✅ PASS | All APIs require student_id parameter |
| **VI: Constructive Feedback** | ✅ PASS | Reviewer APIs return WHY + HOW + model answers |

No violations introduced during design phase.

## Next Steps

1. ✅ Complete Phase 0 (research.md)
2. ✅ Complete Phase 1 (data-model.md, contracts/, quickstart.md)
3. ⏳ Run `/sp.tasks` to generate atomic tasks from this plan
4. ⏳ Implement via `/sp.implement` (execute tasks.md)
5. ⏳ Create ADRs for key decisions (SM-2, fallback, confidence)
6. ⏳ Create PHR for planning session
7. ⏳ Run end-to-end tests
8. ⏳ Execute phase gate: `scripts/check-phase-3-complete.sh`

---

**Plan Version**: 1.0.0
**Created**: 2025-12-20
**Status**: Phase 0 (Research) → In Progress
