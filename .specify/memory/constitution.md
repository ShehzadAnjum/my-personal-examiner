<!--
================================================================================
SYNC IMPACT REPORT - Constitution v1.0.0 Initial Creation
================================================================================
Date: 2025-12-16
Version: N/A → 1.0.0 (INITIAL creation)
Action: Create comprehensive constitution for My Personal Examiner following SpecKitPlus methodology

VERSION CHANGES:
- Previous Version: N/A (template only)
- Current Version: 1.0.0
- Version Bump Type: MAJOR (initial constitution creation)

CHANGES MADE:
1. Created comprehensive constitution adapted from evolution_to_do structure
2. Defined 8 Non-Negotiable Principles specific to A-Level teaching system
3. Established 5-phase progressive development workflow
4. Defined enforcement mechanisms (3-level: automated, manual, AI)
5. Created phase-specific rules for Economics 9708 MVP focus
6. Established SpecKit workflow integration
7. Defined repository structure and hygiene rules

PRINCIPLES (8 Non-Negotiable - NEW):
1. Subject Accuracy is Non-Negotiable
2. A* Standard Marking Always
3. Syllabus Synchronization First
4. Spec-Driven Development (No Code Before Spec)
5. Multi-Tenant Isolation is Sacred
6. Feedback is Constructive and Detailed
7. Phase Boundaries Are Hard Gates
8. Question Bank Quality Over Quantity

SPECKIT WORKFLOW:
Constitution → Spec → Clarify (optional) → Plan → Tasks → Implementation → Capstone

TEMPLATE SYNCHRONIZATION STATUS:
⚠️ .specify/templates/spec-template.md - TO BE CREATED via /sp.specify
⚠️ .specify/templates/plan-template.md - TO BE CREATED via /sp.plan
⚠️ .specify/templates/tasks-template.md - TO BE CREATED via /sp.tasks
⚠️ .specify/templates/phr-template.prompt.md - TO BE CREATED
⚠️ .specify/templates/adr-template.md - TO BE CREATED

FILES TO BE CREATED:
⚠️ .claude/agents/* - 10 agent definitions pending
⚠️ .claude/subagents/* - 18 subagent definitions pending
⚠️ .claude/commands/* - 11 SpecKit commands pending
⚠️ docs/SESSION_HANDOFF.md - Context preservation template
⚠️ docs/DAILY_CHECKLIST.md - Pre-work checklist
⚠️ CLAUDE.md - Root AI instructions

COMMIT MESSAGE SUGGESTION:
docs: create constitution v1.0.0 (8 principles + 5-phase workflow)

- Establish PhD-level A-Level teaching system governance
- Define 8 non-negotiable principles (subject accuracy, A* standards, etc.)
- Create 5-phase progressive development plan
- Establish SpecKitPlus methodology integration
- Set enforcement mechanisms (automated, manual, AI)
- Initial version: 1.0.0

================================================================================
-->

# My Personal Examiner: Project Constitution

**Created**: December 16, 2025
**Version**: 1.0.0
**Last Amended**: 2025-12-16
**Project**: My Personal Examiner - PhD-Level A-Level Teaching & Examination System
**Objective**: Create automated, personalized PhD-level teacher for Cambridge International A-Levels achieving A* grades

---

## Table of Contents

1. [Meta-Constitution: Why This Document Exists](#meta-constitution-why-this-document-exists)
2. [Core Philosophy](#core-philosophy)
3. [Non-Negotiable Principles](#non-negotiable-principles)
4. [Phase-Specific Rules](#phase-specific-rules)
5. [Enforcement Mechanisms](#enforcement-mechanisms)
6. [Repository Structure & Hygiene](#repository-structure--hygiene)
7. [Daily & Weekly Workflows](#daily--weekly-workflows)
8. [Success Metrics](#success-metrics)
9. [Governance](#governance)

---

## Meta-Constitution: Why This Document Exists

### The Purpose

This project builds a PhD-level AI teacher for Cambridge International A-Levels. The stakes are high: students trust this system to prepare them for university-admission examinations. **Wrong content, lenient marking, or outdated syllabi waste student time and damage futures.**

This constitution ensures:
1. **Subject Accuracy**: All content matches current Cambridge syllabi exactly
2. **A* Standards**: PhD-level rigor in all marking and feedback
3. **Quality Over Speed**: Each phase is production-ready before advancing
4. **Systematic Development**: SpecKitPlus methodology prevents scope creep

### The Stakes

- **Timeline**: 2-3 weeks for MVP (Economics 9708)
- **Students Impacted**: Multi-tenant system serving many students
- **Educational Consequences**: Incorrect preparation leads to exam failure
- **Technical Complexity**: 4 subjects × marking engines × AI integration
- **Risk**: Premature features, outdated content, security vulnerabilities

### The Commitment

**I commit to following this constitution exactly as written.** This constitution is the contract between the AI teacher's promise (PhD-level standards) and its implementation (disciplined, spec-driven development).

If deviations occur:
1. Document the deviation explicitly (WHY.md)
2. Update constitution if change is permanent via `/sp.constitution`
3. Accept the consequences (potential quality compromise)

**This constitution protects students by protecting development discipline.**

---

## Core Philosophy

### 1. Spec-Driven Development (SpecKitPlus Methodology)

**Rule**: AI (Claude Code) writes code. Human writes specs **using SpecKit commands**.

**Process** (Using SpecKit Commands):
1. Human: Create spec using `/sp.specify` command
2. Human: Create plan using `/sp.plan` command
3. Human: Generate tasks using `/sp.tasks` command
4. Human: Reference spec: `@specs/phase-N/spec.md`
5. Claude: Read spec and implement
6. Human: Test result against Cambridge mark schemes
7. If wrong: Update spec using `/sp.specify` or `/sp.clarify`, then re-implement
8. Repeat until correct
9. Capstone: Validate against Spec, Plan, Constitution

**MANDATORY SpecKit Commands**:
- `/sp.constitution` - Create/update this constitution
- `/sp.specify` - Create feature specifications
- `/sp.plan` - Create implementation plans
- `/sp.tasks` - Generate task lists
- `/sp.clarify` - Clarify ambiguities in specs
- `/sp.analyze` - Check cross-artifact consistency
- `/sp.adr` - Record architectural decisions
- `/sp.phr` - Record prompt history
- `/sp.checklist` - Generate custom checklists
- `/sp.git.commit_pr` - Autonomous git workflows
- `/sp.implement` - Execute tasks from tasks.md

**Prohibited**:
- ❌ Manually writing implementation code (AI writes code)
- ❌ Editing generated code extensively (update spec instead)
- ❌ Creating specs manually with `vim specs/...` (MUST use `/sp.specify`)
- ❌ Creating plans manually (MUST use `/sp.plan`)
- ❌ Creating tasks manually (MUST use `/sp.tasks`)

**Allowed**:
- ✅ Using SpecKit `/sp.*` commands for all specs/plans/tasks
- ✅ Writing configs (CLAUDE.md, .gitignore, .env.example)
- ✅ Writing documentation
- ✅ Bug fixes when AI is blocked

### 2. Phase Discipline

**Rule**: Each phase is a HARD GATE. Cannot start Phase N+1 until Phase N is 100% complete.

**Why**: Prevents half-finished marking engines, incomplete syllabi, untested code reaching students.

**Enforcement**: Automated phase gate script (`scripts/check-phase-N-complete.sh`)

### 3. Subject Accuracy as Non-Negotiable

**Rule**: All content (questions, marking schemes, syllabi) MUST match current Cambridge International specifications exactly.

**Why**: Wrong syllabus content = wasted student preparation = exam failure.

**Enforcement**:
- Automated: Monthly syllabus version checks
- Manual: Source verification for all questions
- AI: Reject any question without Cambridge source citation

### 4. Multi-Tenant Security

**Rule**: Student data MUST be strictly isolated. Every database query MUST include student_id filter.

**Why**: Privacy, security, compliance, and student trust are non-negotiable.

**Enforcement**:
- Automated: Database query validator (student_id presence check)
- Manual: Security audit before each phase
- AI: Code review flags missing student_id filters

### 5. Quality Over Speed

**Rule**: Each phase must be production-ready at its level. Never sacrifice A* standards for timeline.

**Not Acceptable**:
- ❌ "Quick and dirty marking algorithm"
- ❌ "We'll fix marking accuracy later"
- ❌ "Skip syllabus verification to move faster"

**Acceptable**:
- ✅ Phase I has only database, no marking (by design)
- ✅ Phase II has only Economics 9708 (other subjects Phase 5+)
- ✅ Intentional MVP scoping per phase

---

## Non-Negotiable Principles

### Principle I: Subject Accuracy is Non-Negotiable

**Rule**: All content, questions, marking schemes, and syllabi MUST match current Cambridge International specifications exactly.

**What This Means**:
- Every question MUST cite source (e.g., "9708_s22_qp_12 Q3(a)")
- Marking schemes MUST match official Cambridge mark schemes
- Syllabus points MUST reference official syllabus codes
- Learning outcomes MUST be verbatim from Cambridge documents

**Why This Matters**:
- Wrong syllabus content = wasted student time
- Outdated exam patterns = wrong preparation strategy
- Incorrect marking schemes = false confidence
- **Result**: Exam failure, wasted year, university rejection

**Enforcement**:
- **Automated**:
  - Database constraint: questions table requires `source_paper` field
  - Monthly cron job: Check Cambridge website for syllabus updates
  - Build fails if syllabus version mismatch detected
- **Manual**:
  - Pre-phase checklist: "Verified syllabus is current?"
  - Question bank review: Sample 10 questions, verify sources
- **AI**:
  - Claude rejects question submissions without valid Cambridge source
  - Prompt template enforces source citation

**Testing**:
- Spot-check 10% of questions against official past papers
- Verify marking scheme alignment with Cambridge schemes
- Compare syllabus points to official 2025-2027 specifications

---

### Principle II: A* Standard Marking Always

**Rule**: All marking MUST be at PhD-level strictness. Never compromise grading standards to make students feel good.

**What This Means**:
- Mark exactly as Cambridge examiners would
- Deduct marks for incomplete reasoning (even if answer is correct)
- Demand A* quality: thorough, perceptive, sophisticated, balanced
- Never award marks for effort—only for demonstrated understanding

**Why This Matters**:
- Lenient marking = false confidence = exam shock
- Students need realistic assessment to improve
- A* requires 80-85% of total marks—no shortcuts
- **Result**: Underprepared students fail real exams

**Enforcement**:
- **Automated**:
  - Marking algorithm tests: Validate against Cambridge mark schemes
  - Accuracy target: >85% agreement with official marking
  - Regression tests on past papers with known outcomes
- **Manual**:
  - Weekly spot-check: Compare 10 AI markings vs. official schemes
  - Calibration: Test marking engine on released examiner reports
- **AI**:
  - Prompt templates enforce PhD-level rigor
  - Chain-of-thought prompts demand explicit reasoning
  - GPT-4/Claude Sonnet with strict system prompts

**Testing**:
- Mark 50 past paper questions, compare to official schemes
- Achieve >85% accuracy (within ±2 marks for long questions)
- Test on deliberately wrong answers (must catch all errors)

---

### Principle III: Syllabus Synchronization First

**Rule**: Before ANY feature work, ensure syllabi are current. Check Cambridge website monthly.

**What This Means**:
- Syllabus versions tracked in database (`subjects.syllabus_year`)
- Monthly check: Cambridge International website for updates
- If syllabus changes mid-cycle: Emergency update protocol
- Never start a phase without verified current syllabus

**Why This Matters**:
- Cambridge updates syllabi every 2-3 years (major cycles)
- Minor amendments can occur annually
- Outdated syllabus = students learn wrong content
- **Result**: Exam questions from new syllabus, student unprepared

**Enforcement**:
- **Automated**:
  - Cron job (1st of each month): Check Cambridge syllabus versions
  - Alert if mismatch detected between DB and Cambridge website
  - Build warning if last sync >30 days ago
- **Manual**:
  - Phase gate checklist: "Syllabus synchronized this month?"
  - Pre-implementation: Verify syllabus version in spec
- **AI**:
  - Monthly reminder: "Check Cambridge website for syllabus updates"
  - Block feature work if syllabus verification overdue

**Cambridge Sources**:
- Economics 9708: https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-economics-9708/
- Syllabus for examination: 2023-2025, then 2026-2028 (check currently active)

**Testing**:
- Visit Cambridge website, compare syllabus version to database
- Verify syllabus points match official learning outcomes
- Check grade boundaries updated to latest session

---

### Principle IV: Spec-Driven Development (No Code Before Spec)

**Rule**: All features MUST have specs created via `/sp.specify` before ANY implementation.

**What This Means**:
- Run `/sp.specify` to create `specs/{feature}/spec.md`
- Run `/sp.plan` to create `specs/{feature}/plan.md`
- Run `/sp.tasks` to create `specs/{feature}/tasks.md`
- Implementation follows spec exactly—no freelancing
- If spec is wrong: Update spec via `/sp.specify`, then re-implement

**Why This Matters**:
- Prevents scope creep and feature bloat
- Ensures alignment with educational goals
- Enables validation against Cambridge standards
- **Result**: Code matches requirements, not developer assumptions

**Enforcement**:
- **Automated**:
  - Git pre-commit hook: Block commits without spec reference
  - CI check: Fail build if implemented features lack specs
- **Manual**:
  - Code review checklist: "Does this reference a spec?"
  - Daily checklist: "Created spec before coding today?"
- **AI**:
  - Claude refuses to implement without spec path provided
  - Prompt template: "Reference @specs/path/to/spec.md"

**Spec Structure** (via `/sp.specify` template):
- Problem Statement
- Functional Requirements
- Non-Functional Requirements
- Cambridge Alignment (syllabus references)
- Marking Criteria (if applicable)
- Test Acceptance Criteria

---

### Principle V: Multi-Tenant Isolation is Sacred

**Rule**: Student data MUST be strictly isolated. No student can access another student's data. Every query filtered by student_id.

**What This Means**:
- All database queries include `WHERE student_id = ?`
- API endpoints verify JWT token student_id matches request student_id
- No global queries returning all students' data
- Audit logs track all data access

**Why This Matters**:
- Privacy violation = trust destroyed
- Regulatory compliance (GDPR, student data protection)
- Security vulnerability if students see others' answers
- **Result**: Legal liability, reputation damage, system shutdown

**Enforcement**:
- **Automated**:
  - ORM query validator: Lint checks for missing student_id filters
  - Integration tests: User A cannot access User B's data
  - Penetration testing: Attempt cross-student data access
- **Manual**:
  - Security audit before each phase: Review all queries
  - Code review: Flag any query without student_id filter
- **AI**:
  - Code generation template: Always include student_id in WHERE
  - Claude Code reviews generated code for security

**Testing**:
- Create 2 students (A, B)
- Student A attempts to access Student B's exams (should fail with 403)
- Verify JWT token validation rejects mismatched student_id
- Audit log shows blocked access attempt

---

### Principle VI: Feedback is Constructive and Detailed

**Rule**: All feedback MUST explain WHY something is wrong and HOW to improve to A* standard.

**What This Means**:
- Never just "Wrong" or "Incorrect"
- Always explain: "This is wrong because... The correct approach is..."
- Include model answer rewritten to A* standard
- Identify specific weaknesses (e.g., "Evaluation lacks depth")

**Why This Matters**:
- Students need actionable guidance to improve
- Generic feedback ("Try harder") is useless
- PhD-level teaching = Socratic method, deep explanation
- **Result**: Students learn why, not just what

**Enforcement**:
- **Automated**:
  - Feedback template validation: Must have "WHY" and "HOW" sections
  - Min length check: Feedback >100 characters (forces detail)
- **Manual**:
  - Sample 10 feedback instances per subject monthly
  - Verify constructive tone and actionable guidance
- **AI**:
  - Prompt template enforces structure: "Explain why... Suggest how..."
  - Chain-of-thought prompts demand explicit reasoning

**Feedback Template** (enforced in code):
```
## Marking Feedback for Question {id}

### Score: {marks_awarded} / {max_marks}

### Why This Score:
{Explain what was good, what was missing, why marks were deducted}

### How to Improve to A*:
{Specific, actionable steps to reach top band}

### Model Answer (A* Standard):
{Rewritten answer demonstrating A* quality}

### Weaknesses Identified:
- {Specific weakness 1 with remediation}
- {Specific weakness 2 with remediation}
```

---

### Principle VII: Phase Boundaries Are Hard Gates

**Rule**: Complete Phase N 100% before starting ANY Phase N+1 work.

**What This Means**:
- Phase I complete = ALL deliverables done, not 95%
- Phase gate script MUST pass before next phase
- No "we'll finish this later" exceptions
- Each phase includes demo video and capstone validation

**Why This Matters**:
- Prevents accumulation of incomplete features
- Ensures quality at each level before building on it
- Protects against timeline pressure causing shortcuts
- **Result**: Production-ready system at each phase

**Phase Completion Criteria** (ALL must be YES):
- [ ] All specs in `specs/phase-N/` complete
- [ ] All tasks in `specs/phase-N/tasks.md` marked done
- [ ] All tests passing (>80% coverage)
- [ ] Deployed (if applicable for phase)
- [ ] Demo video recorded (<90 seconds)
- [ ] Capstone validation complete
- [ ] `scripts/check-phase-N-complete.sh` passes

**Enforcement**:
- **Automated**:
  - Phase gate script checks all completion criteria
  - Build fails if phase N+1 work detected before phase N complete
  - Git branch protection: Cannot merge phase-N+1 until phase-N merged
- **Manual**:
  - Daily checklist: "Is current phase 100% complete?"
  - Weekly review: Phase completion status vs. timeline
- **AI**:
  - Claude asks "Is Phase N complete?" before Phase N+1 work
  - Refuses to implement Phase N+1 features until gate passes

**Phase Gate Script** (example for Phase I):
```bash
#!/bin/bash
# scripts/check-phase-1-complete.sh

echo "Phase I Completion Gate"
echo "======================="

# Check specs exist
[ -f "specs/phase-1-core-infrastructure/spec.md" ] || exit 1
[ -f "specs/phase-1-core-infrastructure/plan.md" ] || exit 1
[ -f "specs/phase-1-core-infrastructure/tasks.md" ] || exit 1

# Check database working
python -c "from backend.src.database import engine; engine.connect()" || exit 1

# Check auth working
curl -X POST http://localhost:8000/api/auth/register || exit 1

# Check tests passing
cd backend && pytest --cov=src --cov-report=term --cov-fail-under=80 || exit 1

echo "✅ Phase I Complete - Ready for Phase II"
```

---

### Principle VIII: Question Bank Quality Over Quantity

**Rule**: Every question MUST have verified Cambridge mark scheme. No question without official source.

**What This Means**:
- Questions extracted from Cambridge past papers (not invented)
- Each question links to source paper (e.g., "9708_s22_qp_12.pdf")
- Marking scheme extracted from official Cambridge mark schemes
- Metadata includes: subject, paper, variant, year, season, question number

**Why This Matters**:
- Invented questions may not match Cambridge style
- Wrong marking schemes give false feedback
- Students need authentic exam practice
- **Result**: Realistic preparation, accurate marking

**Enforcement**:
- **Automated**:
  - Database constraint: `questions.source_paper NOT NULL`
  - Database constraint: `questions.marking_scheme NOT NULL`
  - Validation: Source paper filename matches regex pattern
- **Manual**:
  - Question review: Verify 10% of questions link to real past papers
  - Marking scheme audit: Compare to official Cambridge PDFs
- **AI**:
  - Reject question submissions without source
  - PDF extractor validates Cambridge filename format

**Question Metadata** (required fields):
```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY,
  subject_id UUID NOT NULL REFERENCES subjects(id),
  source_paper VARCHAR(50) NOT NULL,  -- e.g., "9708_s22_qp_12"
  question_number VARCHAR(20) NOT NULL,  -- e.g., "3(a)"
  question_text TEXT NOT NULL,
  max_marks INTEGER NOT NULL,
  marking_scheme JSONB NOT NULL,  -- Official Cambridge scheme
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Source Verification**:
- Cambridge past papers: https://pastpapers.papacambridge.com/papers/caie/as-and-a-level-economics-9708
- Official syllabus: https://www.cambridgeinternational.org/Images/595463-2023-2025-syllabus.pdf
- Grade thresholds: Published after each examination session

---

## Phase-Specific Rules

### Phase I: Core Infrastructure & Database (Days 1-4)

**Objective**: Establish SpecKitPlus structure, database, authentication, basic API.

**Technology Stack**:
- Backend: Python 3.12+, FastAPI 0.115+, SQLModel 0.0.22+
- Database: PostgreSQL 16 (Neon Serverless)
- Auth: Better Auth (JWT)
- Package Manager: UV 0.5+

**Features**:
1. Complete SpecKitPlus directory structure
2. Constitution (this document)
3. Database schema (multi-tenant)
4. Student authentication (register, login, JWT)
5. Core API endpoints (students, subjects)

**Explicit Non-Goals**:
- ❌ Question bank (Phase II)
- ❌ Marking engine (Phase III)
- ❌ Web UI (Phase IV)
- ❌ MCP servers (Phase V)

**Deliverables**:
- [ ] `.specify/memory/constitution.md` (this document)
- [ ] `specs/phase-1-core-infrastructure/` (spec, plan, tasks)
- [ ] `.claude/agents/` (10 agent definitions)
- [ ] `.claude/subagents/` (18 subagent definitions)
- [ ] `.claude/commands/` (11 SpecKit commands)
- [ ] `backend/src/models/` (SQLModel database models)
- [ ] `backend/alembic/versions/001_initial_schema.py`
- [ ] `backend/src/routes/auth.py`, `students.py`
- [ ] `docs/SESSION_HANDOFF.md`, `DAILY_CHECKLIST.md`
- [ ] `CLAUDE.md` (root AI instructions)
- [ ] Unit tests (>80% coverage)

**Time Budget**: 4 days (Dec 16-19)

**New Concepts** (MUST READ DOCS FIRST):
- Better Auth (30 min): https://www.better-auth.com/docs
- Neon PostgreSQL (15 min): https://neon.tech/docs
- FastAPI (30 min): https://fastapi.tiangolo.com/
- SQLModel (20 min): https://sqlmodel.tiangolo.com/

**Phase I Complete Checklist**:
- [ ] Constitution ratified (this document)
- [ ] All agents/subagents/commands defined
- [ ] Database schema created and migrated
- [ ] Student can register/login via API
- [ ] JWT tokens working
- [ ] Unit tests passing (>80% coverage)
- [ ] `scripts/check-phase-1-complete.sh` passes

**Phase Gate**: `scripts/check-phase-1-complete.sh`

---

### Phase II: Question Bank & Exam Generation (Days 5-9)

**Objective**: Extract Cambridge past papers, build question bank, generate exams (Economics 9708 only).

**Features**:
1. PDF question extractor (reuse from A-Level-Learning)
2. Cambridge syllabus crawler (Economics 9708)
3. Question bank (100+ Economics questions)
4. Exam generation service
5. Syllabus management API

**Explicit Non-Goals**:
- ❌ AI marking (Phase III)
- ❌ Other subjects (Phase 5+)
- ❌ Web UI (Phase IV)
- ❌ MCP servers (Phase V)

**Deliverables**:
- [ ] `specs/phase-2-question-bank/` (spec, plan, tasks)
- [ ] `backend/src/question_extractors/cambridge_pdf_extractor.py`
- [ ] `backend/src/question_extractors/metadata_extractor.py`
- [ ] `backend/src/services/syllabus_service.py`
- [ ] `backend/src/services/assessment_service.py`
- [ ] Economics 9708 question bank (100+ questions)
- [ ] API endpoints: `GET /api/questions`, `POST /api/exams`
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (exam generation)

**Time Budget**: 5 days (Dec 20-24)

**Reusable Components** (from A-Level-Learning):
- PDF metadata extractor: `/home/anjum/dev/A-Level-Learning/src/dynamic_resource_manager/metadata_extractor.py`
- PDF question extractor: `/home/anjum/dev/A-Level-Learning/src/content_generation_engine/pdf_qa_extractor.py`

**Phase II Complete Checklist**:
- [ ] Can extract questions from Cambridge PDFs
- [ ] Question bank has 100+ Economics 9708 questions
- [ ] Can generate custom exams (topic-based, difficulty-based)
- [ ] All questions have verified Cambridge sources
- [ ] Syllabus data synchronized with Cambridge website
- [ ] `scripts/check-phase-2-complete.sh` passes

**Phase Gate**: `scripts/check-phase-2-complete.sh`

---

### Phase III: AI Marking & Feedback Engine (Days 10-14)

**Objective**: Implement Economics 9708 marking engine with PhD-level feedback.

**Features**:
1. Economics 9708 marking engine (theory validation, diagram checking, evaluation scoring)
2. AI-powered feedback generator
3. Weakness analyzer
4. Answer rewriter (to A* standard)
5. Progress tracking

**Explicit Non-Goals**:
- ❌ Other subjects' marking engines (Phase 5+)
- ❌ Web UI (Phase IV)
- ❌ MCP servers (Phase V)

**Deliverables**:
- [ ] `specs/phase-3-ai-marking/` (spec, plan, tasks)
- [ ] `backend/src/marking_engines/economics_marker.py`
- [ ] `backend/src/services/marking_service.py`
- [ ] `backend/src/services/feedback_service.py`
- [ ] `backend/src/ai_integration/anthropic_client.py`
- [ ] `backend/src/ai_integration/openai_client.py`
- [ ] `backend/src/ai_integration/prompt_templates.py`
- [ ] API endpoints: `POST /api/marking/mark-answer`
- [ ] Unit tests (>80% coverage)
- [ ] Accuracy tests (>85% vs Cambridge schemes)

**Time Budget**: 5 days (Dec 25-29)

**New Concepts** (MUST READ DOCS FIRST):
- OpenAI API (30 min): https://platform.openai.com/docs/api-reference
- Anthropic API (30 min): https://docs.anthropic.com/claude/reference/getting-started
- Prompt Engineering (45 min): https://www.anthropic.com/index/prompting

**Economics 9708 Marking Capabilities**:
- Theory validation (correct economic concepts applied)
- Diagram accuracy (supply/demand curves, shifts, equilibrium)
- AO1 (Knowledge) scoring
- AO2 (Application) scoring
- AO3 (Evaluation) scoring
- Levels-based marking (Level 3, Level 2 descriptors)

**Phase III Complete Checklist**:
- [ ] Can mark Economics 9708 answers with >85% accuracy
- [ ] Feedback explains WHY and HOW to improve
- [ ] Can rewrite answers to A* standard
- [ ] Weaknesses identified with remediation suggestions
- [ ] Tested on 50+ past paper questions
- [ ] `scripts/check-phase-3-complete.sh` passes

**Phase Gate**: `scripts/check-phase-3-complete.sh`

---

### Phase IV: Web UI & Student Interface (Days 15-18)

**Objective**: Build Next.js frontend for students to take exams, view feedback, track progress.

**Technology Stack**:
- Frontend: Next.js 16+, TypeScript 5.7+, React 19
- Styling: Tailwind CSS 4, shadcn/ui
- State: Zustand 5 / React Context
- API Client: TanStack Query 5.62+
- Deployment: Vercel

**Features**:
1. Student dashboard
2. Subject selection (Economics 9708)
3. Exam-taking interface
4. Review and feedback UI
5. Progress tracking charts
6. Mobile-responsive design

**Explicit Non-Goals**:
- ❌ CLI/MCP interface (Phase V)
- ❌ Other subjects (Phase 5+)

**Deliverables**:
- [ ] `specs/phase-4-web-ui/` (spec, plan, tasks)
- [ ] `frontend/app/(dashboard)/` (Next.js app)
- [ ] `frontend/components/exam/` (exam components)
- [ ] `frontend/components/marking/` (feedback components)
- [ ] `frontend/components/progress/` (analytics components)
- [ ] `frontend/lib/api/` (API client)
- [ ] Deployed on Vercel
- [ ] E2E tests (Playwright)

**Time Budget**: 4 days (Dec 30 - Jan 2)

**New Concepts** (MUST READ DOCS FIRST):
- Next.js App Router (45 min): https://nextjs.org/docs/app
- shadcn/ui (20 min): https://ui.shadcn.com/docs
- TanStack Query (30 min): https://tanstack.com/query/latest/docs/react/overview

**Phase IV Complete Checklist**:
- [ ] Student can login via web UI
- [ ] Can select Economics 9708
- [ ] Can generate and take exam
- [ ] Can view detailed marking feedback
- [ ] Can see progress over time
- [ ] Works on mobile and desktop
- [ ] Deployed on Vercel
- [ ] `scripts/check-phase-4-complete.sh` passes

**Phase Gate**: `scripts/check-phase-4-complete.sh`

---

### Phase V: CLI/MCP & Advanced Features (Days 19-21)

**Objective**: Build custom MCP servers, CLI interface, conversational AI teacher.

**Technology Stack**:
- MCP: Python MCP SDK (official)
- CLI: Typer 0.15+
- AI: OpenAI Agents SDK

**Features**:
1. Question Bank MCP Server
2. Student Assessment MCP Server
3. Progress Tracking MCP Server
4. Syllabus Management MCP Server
5. CLI interface (Typer)
6. Conversational AI teacher
7. Grade prediction

**Explicit Non-Goals**:
- ❌ Other subjects (future releases)

**Deliverables**:
- [ ] `specs/phase-5-advanced-features/` (spec, plan, tasks)
- [ ] `backend/src/mcp_servers/question_bank_mcp.py`
- [ ] `backend/src/mcp_servers/marking_mcp.py`
- [ ] `backend/src/mcp_servers/syllabus_mcp.py`
- [ ] `backend/src/mcp_servers/student_progress_mcp.py`
- [ ] `cli/` (CLI application)
- [ ] MCP integration tests
- [ ] CLI tests

**Time Budget**: 3 days (Jan 3-5)

**New Concepts** (MUST READ DOCS FIRST):
- MCP Python SDK (60 min): https://github.com/modelcontextprotocol/python-sdk
- OpenAI Agents SDK (45 min): https://platform.openai.com/docs/guides/agents
- Typer (20 min): https://typer.tiangolo.com/

**Phase V Complete Checklist**:
- [ ] 4 custom MCP servers functional
- [ ] CLI can perform all operations
- [ ] Conversational AI teacher provides personalized guidance
- [ ] Grade prediction working
- [ ] System production-ready
- [ ] `scripts/check-phase-5-complete.sh` passes

**Phase Gate**: `scripts/check-phase-5-complete.sh`

---

## Enforcement Mechanisms

### Three-Level Enforcement

**Level 1: Automated Checks**
- Pre-commit hooks (block commits with violations)
- Phase gate scripts (prevent premature phase advancement)
- Database constraints (enforce data integrity)
- CI/CD pipelines (enforce quality gates)

**Level 2: Manual Checklists**
- `docs/DAILY_CHECKLIST.md` - Pre-work verification (5 min)
- `docs/SESSION_HANDOFF.md` - End-of-session updates (5 min)
- Phase completion checklists (before gate scripts)
- Weekly cleanup script (repository hygiene)

**Level 3: AI Reminders**
- Claude Code enforces principles during implementation
- Refuses non-compliant work (e.g., code before spec)
- Asks validation questions ("Is Phase N complete?")
- Reminds of constitutional requirements

### Pre-Commit Hooks

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "Constitutional Compliance Check"
echo "================================"

# Check 1: No build artifacts
if git diff --cached --name-only | grep -E '\.pyc$|__pycache__|node_modules|\.next'; then
  echo "❌ BLOCKED: Build artifacts detected"
  echo "Add to .gitignore instead"
  exit 1
fi

# Check 2: No secrets
if git diff --cached | grep -E 'API_KEY|SECRET|PASSWORD'; then
  echo "❌ BLOCKED: Potential secrets detected"
  echo "Use .env files instead"
  exit 1
fi

# Check 3: SESSION_HANDOFF.md updated recently
if [ -f docs/SESSION_HANDOFF.md ]; then
  LAST_MODIFIED=$(stat -c %Y docs/SESSION_HANDOFF.md)
  NOW=$(date +%s)
  DIFF=$((NOW - LAST_MODIFIED))
  if [ $DIFF -gt 7200 ]; then  # 2 hours
    echo "⚠️  WARNING: SESSION_HANDOFF.md not updated in 2+ hours"
    echo "Update before committing? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
      exit 1
    fi
  fi
fi

echo "✅ Pre-commit checks passed"
```

### Daily Checklist

**File**: `docs/DAILY_CHECKLIST.md`

```markdown
# Daily Pre-Work Checklist (5 minutes)

Run this BEFORE starting any work session.

## Context & Planning
- [ ] Read SESSION_HANDOFF.md from last session
- [ ] Know which phase I'm in (Phase I/II/III/IV/V)
- [ ] Know which task I'm working on today
- [ ] Today's task is in specs/{phase}/tasks.md

## Constitutional Compliance
- [ ] Syllabus checked this month (if >30 days, check Cambridge website)
- [ ] Current phase <100% complete? (cannot start next phase)
- [ ] Have spec before coding? (if new feature, run /sp.specify first)

## Tools & Environment
- [ ] Backend server running (if needed)
- [ ] Database connected (if needed)
- [ ] Tests passing from last session

## Output
I will work on: [Task name from tasks.md]
Expected completion: [Today / This week]
Blockers: [None / List blockers]
```

### Session Handoff Template

**File**: `docs/SESSION_HANDOFF.md`

```markdown
# Session Handoff

**Last Updated**: [DATE TIME]
**Current Phase**: [Phase I/II/III/IV/V]
**Phase Completion**: [XX%]

## What I Did This Session

[Bullet list of completed work]

## Current State

**Working**: [What's functional]
**Broken**: [What's not working]
**In Progress**: [What's half-done]

## Next Session

**Priority 1**: [Most important task]
**Priority 2**: [Second task]
**Blockers**: [Anything blocking progress]

## Context for AI

**Current Focus**: [What I'm building]
**Recent Decisions**: [Any architectural choices]
**Weird Issues**: [Any strange behaviors to remember]

## Constitutional Compliance

- [ ] Syllabus is current (checked [DATE])
- [ ] All code has specs
- [ ] Phase N complete before starting Phase N+1
- [ ] Student data isolation verified
```

### Weekly Cleanup Script

**File**: `scripts/weekly-cleanup.sh`

```bash
#!/bin/bash

echo "Weekly Repository Cleanup"
echo "========================="

# Delete merged branches
git branch --merged main | grep -v "main" | xargs -r git branch -d

# Clean build artifacts
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Check for large files
find . -type f -size +10M

echo "✅ Cleanup complete"
```

---

## Repository Structure & Hygiene

### Directory Structure (Mandatory)

```
my_personal_examiner/
├── .specify/           # SpecKitPlus configuration
├── .claude/            # Agent definitions, commands, skills
├── specs/              # All specifications (created via /sp.specify)
├── history/            # ADRs and PHRs for traceability
├── backend/            # FastAPI + SQLModel + PostgreSQL
├── frontend/           # Next.js + React + Tailwind
├── cli/                # CLI interface
├── docs/               # Documentation
├── scripts/            # Automation scripts
├── .gitignore          # Comprehensive ignore rules
├── .env.example        # Environment template (no secrets)
├── README.md           # Project documentation
└── CLAUDE.md           # Root AI instructions
```

### .gitignore (Required Entries)

```gitignore
# Build artifacts
__pycache__/
*.pyc
*.pyo
.pytest_cache/
node_modules/
.next/
dist/
build/

# Environment
.env
.env.local
*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

### Repository Cleanliness Rules

1. **Never commit**:
   - Build artifacts (`__pycache__`, `node_modules`, `.next`)
   - Secrets (`.env` files, API keys)
   - Large files (>10MB)
   - IDE config (`.vscode`, `.idea`)

2. **Always commit**:
   - Source code
   - Specs, plans, tasks (via SpecKit commands)
   - Documentation
   - Example configs (`.env.example`)

3. **Organization**:
   - Docs in `docs/`, not root
   - Specs in `specs/`, not scattered
   - No duplicate files
   - Descriptive filenames

4. **Weekly cleanup**:
   - Run `scripts/weekly-cleanup.sh`
   - Delete merged branches
   - Remove stale files

---

## Daily & Weekly Workflows

### Daily Workflow

**Morning (5 minutes)**:
1. Read `docs/SESSION_HANDOFF.md`
2. Run `docs/DAILY_CHECKLIST.md`
3. Verify environment (DB, tests)

**During Work**:
4. Use SpecKit commands for all specs/plans/tasks
5. Follow constitutional principles
6. Test frequently
7. Commit often with descriptive messages

**Evening (5 minutes)**:
8. Update `docs/SESSION_HANDOFF.md`
9. Commit work
10. Note blockers for next session

**Time Invested**: 10 minutes/day
**Time Saved**: 30-60 minutes context reload prevention

### Weekly Workflow

**End of Week (15 minutes)**:
1. Review phase progress vs. timeline
2. Run phase gate script (if phase complete)
3. Run `scripts/weekly-cleanup.sh`
4. Check syllabus sync status
5. Spot-check question bank quality (10 questions)
6. Review marking accuracy (10 markings vs. Cambridge)

**Monthly**:
7. Check Cambridge website for syllabus updates
8. Update syllabus database if changes detected
9. Recalibrate marking engines if needed

---

## Success Metrics

### Phase I Success (Days 1-4)

- [ ] ✅ Constitution ratified
- [ ] ✅ SpecKitPlus structure complete
- [ ] ✅ Database schema created
- [ ] ✅ Student auth working
- [ ] ✅ Tests >80% coverage
- [ ] ✅ Phase gate passed

### Phase II Success (Days 5-9)

- [ ] ✅ 100+ Economics questions in bank
- [ ] ✅ All questions have Cambridge sources
- [ ] ✅ Exam generation working
- [ ] ✅ Syllabus synchronized
- [ ] ✅ Tests >80% coverage
- [ ] ✅ Phase gate passed

### Phase III Success (Days 10-14)

- [ ] ✅ Marking accuracy >85% vs Cambridge
- [ ] ✅ Feedback explains WHY and HOW
- [ ] ✅ Answer rewriter produces A* answers
- [ ] ✅ Weakness analyzer identifies patterns
- [ ] ✅ Tests >80% coverage
- [ ] ✅ Phase gate passed

### Phase IV Success (Days 15-18)

- [ ] ✅ Web UI deployed on Vercel
- [ ] ✅ Student can take exams
- [ ] ✅ Feedback UI working
- [ ] ✅ Progress tracking visible
- [ ] ✅ Mobile responsive
- [ ] ✅ E2E tests passing
- [ ] ✅ Phase gate passed

### Phase V Success (Days 19-21)

- [ ] ✅ 4 MCP servers functional
- [ ] ✅ CLI interface working
- [ ] ✅ Conversational AI teacher
- [ ] ✅ Grade prediction accurate
- [ ] ✅ System production-ready
- [ ] ✅ Phase gate passed

### Overall Project Success

- [ ] ✅ Economics 9708 fully supported
- [ ] ✅ >85% marking accuracy
- [ ] ✅ PhD-level feedback quality
- [ ] ✅ Multi-tenant security verified
- [ ] ✅ Syllabus synchronized
- [ ] ✅ All tests passing
- [ ] ✅ Deployed and accessible
- [ ] ✅ Documentation complete
- [ ] ✅ Ready for additional subjects

---

## Governance

### Constitution Amendments

**When to Amend**:
- New principle discovered (e.g., new compliance requirement)
- Principle clarification needed (ambiguous rule)
- Technology stack change (major shift)
- Workflow improvement (proven efficiency gain)

**How to Amend**:
1. Run `/sp.constitution` command
2. Update principles and version number
3. Create ADR documenting reasoning (`/sp.adr`)
4. Create PHR recording amendment (`/sp.phr`)
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

**Version Numbering** (Semantic Versioning):
- **MAJOR** (X.0.0): Backward-incompatible principle changes
- **MINOR** (X.Y.0): New principles added
- **PATCH** (X.Y.Z): Clarifications, wording fixes

### Prohibited Changes

**Never**:
- ❌ Remove Principle I-VIII (these are non-negotiable)
- ❌ Weaken quality standards (e.g., lower marking accuracy)
- ❌ Bypass phase gates (defeats purpose)
- ❌ Skip SpecKit commands (mandatory workflow)

**Allowed**:
- ✅ Add new principles (MINOR bump)
- ✅ Clarify existing principles (PATCH bump)
- ✅ Update enforcement mechanisms (PATCH bump)
- ✅ Adjust timelines (PATCH bump)

### Sync Requirements

When constitution changes, update:
- [ ] `.specify/templates/` (if workflow changes)
- [ ] `.claude/agents/` (if agent responsibilities change)
- [ ] `CLAUDE.md` (if AI instructions change)
- [ ] `docs/` (if process documentation changes)

### Review Cadence

- **Daily**: Compliance during development
- **Weekly**: Phase progress vs. constitution
- **Monthly**: Syllabus sync, metric review
- **Post-Phase**: Retrospective, principle validation

---

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
