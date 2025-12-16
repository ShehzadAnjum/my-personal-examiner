# Claude Code Instructions: My Personal Examiner

**Project**: My Personal Examiner - PhD-Level A-Level Teaching & Examination System
**Your Role**: Constitutional Guardian + Code Generator
**Version**: 1.0.0
**Last Updated**: 2025-12-16
**Current Phase**: Phase I (Core Infrastructure & Database)
**MVP Subject**: Economics 9708 (Cambridge International AS & A Level)

---

## 🎯 Quick Start

**Before doing ANY work, read these in order:**

1. **This file** (CLAUDE.md) - Your root instructions (15 min)
2. **Constitution** (.specify/memory/constitution.md) - Project principles (30 min)
3. **Session Handoff** (docs/SESSION_HANDOFF.md) - Current context (5 min)
4. **Current Phase Spec** (specs/phase-1-core-infrastructure/spec.md) - What we're building now (10 min)

**Total time**: ~60 minutes to understand the full context

**Why?** This project affects students' A-Level exam preparation. Wrong content, lenient marking, or outdated syllabi waste student time and damage futures. Understanding the context prevents wasting development time going in wrong direction.

---

## 🚨 MANDATORY: Reusable Intelligence Announcement Protocol

**Constitution requires this. Always announce which agent/subagent/skill you're using.**

### Before ANY Significant Task, ANNOUNCE:

```
📋 USING: [agent-name], [subagent-name], [skill-name]

[Then proceed with the task...]
```

### Example Announcements:

```
📋 USING: System Architect agent, Assessment Engine agent

Designing multi-tenant database schema for Economics 9708 exam system...
```

```
📋 USING: Backend Service agent, Economics Theory Checker subagent

Implementing Economics 9708 marking engine with AO1/AO2/AO3 scoring...
```

```
📋 USING: Syllabus Research agent, Cambridge Syllabus Crawler subagent

Fetching latest Economics 9708 syllabus from Cambridge International website...
```

### When to Announce:
- Before implementing any feature
- Before debugging any issue
- Before creating/modifying infrastructure
- Before any multi-step task
- Before using any MCP server

### When Creating/Modifying RI Artifacts:

```
📋 CREATING: new subagent `economics-marker.md`
[or]
📋 MODIFYING: skill `cambridge-exam-patterns.md` - adding Economics 9708 patterns

[Ask for permission if modifying existing artifacts]
```

### Available Reusable Intelligence:

**Agents** (`.claude/agents/`):
- system-architect, backend-service, frontend-web, assessment-engine
- syllabus-research, ai-pedagogy, testing-quality, docs-demo
- deployment, mcp-integration

**Subagents** (`.claude/subagents/`):
- question-generator, marking-engine, feedback-generator, answer-rewriter
- weakness-analyzer, accounting-validator, economics-theory-checker
- math-symbolic-parser, english-essay-analyzer, cambridge-syllabus-crawler
- pdf-question-extractor, grade-calculator, student-progress-tracker
- (and more - see .claude/subagents/)

**Skills** (`.claude/skills/`):
- cambridge-exam-patterns, a-star-grading-rubrics, phd-pedagogy
- subject-economics-9708, web-artifacts-builder, xlsx, docx, pdf
- webapp-testing, mcp-builder
- (and more - see .claude/skills/)

**This is NON-NEGOTIABLE. Always announce. Always.**

---

## 📁 Project Structure

This project follows **SpecKitPlus methodology** with **Reusable Intelligence**.

```
my_personal_examiner/
├── .specify/                        # SpecKitPlus configuration
│   ├── memory/
│   │   └── constitution.md          # 8 non-negotiable principles (v1.0.0)
│   ├── templates/                   # spec, plan, tasks, adr, phr templates
│   └── scripts/bash/                # phase checks, PHR creation
│
├── .claude/                         # Reusable Intelligence
│   ├── agents/                      # 10 long-lived domain owners
│   ├── subagents/                   # 18 narrow task specialists
│   ├── skills/                      # 13 reusable knowledge blocks
│   └── commands/                    # 11 SpecKit commands (sp.*)
│
├── specs/                           # Specifications (source of truth)
│   ├── phase-1-core-infrastructure/ # Phase I (current)
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── capstone.md
│   ├── phase-2-question-bank/       # Phase II (future)
│   ├── phase-3-ai-marking/          # Phase III (future)
│   ├── phase-4-web-ui/              # Phase IV (future)
│   ├── phase-5-advanced-features/   # Phase V (future)
│   └── subjects/                    # Subject-specific specs
│       └── economics-9708/
│
├── history/                         # Traceability
│   ├── adr/                         # Architecture Decision Records
│   └── prompts/                     # Prompt History Records (PHR)
│       ├── constitution/
│       ├── phase-1-core-infrastructure/
│       └── general/
│
├── backend/                         # FastAPI + SQLModel + PostgreSQL
│   ├── src/
│   │   ├── models/                  # Database models (SQLModel)
│   │   ├── schemas/                 # API schemas (Pydantic)
│   │   ├── routes/                  # API endpoints (FastAPI routers)
│   │   ├── services/                # Business logic
│   │   ├── marking_engines/         # Subject-specific markers
│   │   ├── question_extractors/     # PDF parsing (Cambridge)
│   │   ├── ai_integration/          # OpenAI/Anthropic clients
│   │   └── mcp_servers/             # Custom MCP servers
│   ├── alembic/                     # Database migrations
│   ├── tests/                       # Unit, integration, E2E tests
│   ├── pyproject.toml               # UV/Poetry config
│   └── README.md
│
├── frontend/                        # Next.js 16 App Router
│   ├── app/(dashboard)/             # Protected student routes
│   ├── components/                  # React components (shadcn/ui)
│   ├── lib/                         # API client, hooks, utils
│   └── README.md
│
├── cli/                             # CLI/MCP interface (Phase V)
│
├── docs/                            # Documentation
│   ├── SESSION_HANDOFF.md           # Context preservation (update after each session)
│   ├── DAILY_CHECKLIST.md           # Pre-work checklist
│   ├── architecture/
│   ├── subjects/
│   └── deployment/
│
├── scripts/                         # Automation
│   └── check-phase-{1-5}-complete.sh # Phase gate validators
│
├── .gitignore                       # Comprehensive ignore rules
├── .env.example                     # Environment template (no secrets)
├── README.md                        # Project overview
└── CLAUDE.md                        # This file
```

---

## 🎓 Educational Context: A-Level Teaching System

**What You're Building**: PhD-level AI teacher for Cambridge International A-Levels.

**Why This Matters**:
- **Students' Futures**: Wrong content = exam failure = university rejection
- **Cambridge Compliance**: Must match current syllabi exactly
- **A* Standards**: Mark at PhD-level strictness (>85% accuracy vs. Cambridge)
- **Security**: Multi-tenant isolation protects student data

**MVP Subject**: Economics 9708 (AS & A Level)
- Clear marking criteria (AO1 Knowledge, AO2 Application, AO3 Evaluation)
- Levels-based marking (Level 3, Level 2 descriptors)
- Essay, data response, and MCQ questions
- Official syllabus: 2023-2025, then 2026-2028

**Future Subjects** (Post-MVP):
- Accounting 9706
- English General Paper 8021 (AS Level)
- Mathematics 9709

---

## ⚖️ Constitutional Principles (8 Non-Negotiable)

**READ FULL CONSTITUTION**: `.specify/memory/constitution.md`

**Quick Reference**:

1. **Subject Accuracy is Non-Negotiable**
   - All content MUST match current Cambridge syllabi exactly
   - Every question MUST cite source (e.g., "9708_s22_qp_12 Q3(a)")
   - Monthly syllabus synchronization mandatory

2. **A* Standard Marking Always**
   - PhD-level strictness, no compromises
   - >85% accuracy vs. Cambridge mark schemes
   - Never award marks for effort—only demonstrated understanding

3. **Syllabus Synchronization First**
   - Check Cambridge website monthly
   - Before ANY feature work, ensure syllabus is current
   - Syllabus versions tracked in database

4. **Spec-Driven Development (No Code Before Spec)**
   - MUST use `/sp.specify` to create specs
   - MUST use `/sp.plan` to create plans
   - MUST use `/sp.tasks` to create tasks
   - Implementation follows spec exactly—no freelancing

5. **Multi-Tenant Isolation is Sacred**
   - Every database query MUST include `student_id` filter
   - No student can access another student's data
   - Security audits before each phase

6. **Feedback is Constructive and Detailed**
   - Always explain WHY and HOW to improve
   - Include model answer rewritten to A* standard
   - Never just "Wrong" or "Incorrect"

7. **Phase Boundaries Are Hard Gates**
   - 100% completion before next phase
   - Phase gate script MUST pass
   - No "we'll finish this later" exceptions

8. **Question Bank Quality Over Quantity**
   - Every question needs verified Cambridge mark scheme
   - Questions extracted from real past papers (not invented)
   - Source verification mandatory

---

## 🛡️ MANDATORY ENFORCEMENT RULES (NON-NEGOTIABLE)

### 1. Technology Stack (LOCKED)

**YOU MUST USE THESE EXACT TECHNOLOGIES - NO SUBSTITUTIONS:**

**Backend**:
- **ORM**: SQLModel (MANDATORY - not SQLAlchemy, not Prisma, not TypeORM)
- **Database**: PostgreSQL 16 via Neon (MANDATORY - not MySQL, not MongoDB)
- **Framework**: FastAPI 0.115+ (MANDATORY - not Django, not Flask)
- **Package Manager**: UV 0.5+ (MANDATORY - not pip, not Poetry)
- **Migration Tool**: Alembic 1.13+ (MANDATORY)

**Frontend**:
- **Framework**: Next.js 16+ (App Router) (MANDATORY - not React-only, not Vue)
- **UI Library**: shadcn/ui + Tailwind CSS 4 (MANDATORY)
- **State**: Zustand 5 or React Context (MANDATORY - not Redux)

**Deployment**:
- **Frontend**: Vercel (MANDATORY for Phase IV)
- **Backend**: Railway (Phase IV), then Azure Container Apps (production)
- **Database**: Neon PostgreSQL (MANDATORY)

**AI/LLM**:
- **Primary**: OpenAI GPT-4 Turbo or GPT-4.5
- **Secondary**: Anthropic Claude Sonnet 4.5
- **Embeddings**: OpenAI text-embedding-3-small

**Testing**:
- **Backend**: pytest 8.3+
- **Frontend**: Jest 29+ + Playwright 1.49+

**WHY LOCKED**: Changing tech stack mid-project wastes weeks. Constitution locks these choices. To change, you must amend constitution (requires user approval).

**ENFORCEMENT**: If you ever suggest "let's use Django instead" or "how about MongoDB", STOP and re-read this section.

---

### 2. Anthropic Skills Priority (CHECK FIRST)

**BEFORE creating ANY custom skill, CHECK Anthropic's official skills:**

**Available Anthropic Skills** (as of 2025-12-16):
1. `web-artifacts-builder` - UI development, React components
2. `xlsx` - Spreadsheet analysis, analytics, grading exports
3. `docx` - Word document handling, exam papers, feedback PDFs
4. `pdf` - PDF reading and analysis
5. `webapp-testing` - E2E testing with Playwright
6. `mcp-builder` - Building custom MCP servers

**Checking Process**:
```bash
# Step 1: List available skills
claude-code skills list

# Step 2: Check if skill exists for your task
# - Need UI work? Use web-artifacts-builder
# - Need PDF parsing? Use pdf skill
# - Need testing? Use webapp-testing skill

# Step 3: Only if NO Anthropic skill exists, create custom
```

**ENFORCEMENT**: If you create a custom skill without checking Anthropic's catalog first, that's a constitutional violation (wasted effort).

---

### 3. MCP Server Discovery (SEARCH BEFORE BUILD)

**BEFORE building ANY custom MCP server, SEARCH these registries:**

**Official MCP Registry**:
- Repository: https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-servers
- Check for: Database connectors, API wrappers, file system tools

**Community MCP Servers**:
- Repository: https://github.com/modelcontextprotocol/servers
- Check for: PostgreSQL, Git, Filesystem, Fetch servers

**Checking Process**:
```bash
# Step 1: Search GitHub
# "mcp server postgresql" or "mcp server [your-need]"

# Step 2: Evaluate available servers
# - Is it actively maintained?
# - Does it match our Python/TypeScript stack?
# - Is it production-ready?

# Step 3: Only build custom if no suitable server exists
```

**MANDATORY MCP Servers for this Project**:
- `@modelcontextprotocol/server-postgres` - Database queries
- `@modelcontextprotocol/server-git` - Git operations
- `@modelcontextprotocol/server-filesystem` - File operations
- `@modelcontextprotocol/server-fetch` - Web requests

**Custom MCP Servers (Build Only After MVP)**:
- `question-bank-api` - Query question database
- `student-assessment-api` - Marking and feedback
- `progress-tracking-api` - Student analytics
- `syllabus-management-api` - Cambridge syllabus sync

**ENFORCEMENT**: If you start building an MCP server without checking GitHub first, STOP and search.

---

### 4. Constitution Revalidation Checkpoints (MANDATORY)

**YOU MUST REVALIDATE AGAINST CONSTITUTION AT THESE CHECKPOINTS:**

**Checkpoint 1: End of Every Task**
```markdown
After completing EACH task from tasks.md:
1. Ask: "Does this violate any of the 8 principles?"
2. Check: Multi-tenant isolation (student_id filters)
3. Check: Subject accuracy (Cambridge compliance)
4. If violation detected: STOP, fix, re-test
```

**Checkpoint 2: End of Every Feature**
```markdown
After completing a feature (spec → plan → tasks → implementation):
1. Run: `/sp.analyze` (cross-artifact consistency check)
2. Verify: All functional requirements met
3. Verify: >80% test coverage
4. Verify: No hardcoded secrets, proper .env usage
```

**Checkpoint 3: End of Every Phase**
```markdown
Before declaring Phase N complete:
1. Run: `./scripts/check-phase-N-complete.sh`
2. Verify: All phase deliverables complete
3. Verify: All tests passing
4. Verify: Documentation updated (SESSION_HANDOFF.md)
5. Create: Phase capstone document
6. MANDATORY: Get user approval before Phase N+1
```

**Checkpoint 4: Before Every Git Commit**
```markdown
Pre-commit checklist (MUST PASS):
1. All tests pass: `pytest` (backend), `npm test` (frontend)
2. Linting pass: `ruff check .` (backend), `npm run lint` (frontend)
3. Type checking: `mypy src/` (backend)
4. No secrets in code: `git diff` review
5. Multi-tenant security: grep for unfiltered queries
```

**ENFORCEMENT**: Constitution mandates these checkpoints. Skipping them is a violation of Principle VII (Phase Boundaries Are Hard Gates).

---

### 5. Pre-Commit Testing (AUTOMATE OR BLOCK)

**NOTHING gets committed without passing tests:**

**Pre-Commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
set -e

echo "🧪 Running pre-commit tests..."

# Backend tests
if [ -d "backend" ]; then
  cd backend
  uv run pytest -v
  uv run ruff check .
  uv run mypy src/
  cd ..
fi

# Frontend tests (when Phase IV starts)
if [ -d "frontend/package.json" ]; then
  cd frontend
  npm test -- --passWithNoTests
  npm run lint
  cd ..
fi

echo "✅ All pre-commit checks passed"
```

**Manual Override** (USE SPARINGLY):
```bash
# Only use if tests are legitimately broken and you need to WIP commit
git commit --no-verify -m "WIP: [reason for skipping tests]"
```

**ENFORCEMENT**: If you commit without running tests, you're violating development hygiene. Use `git commit` (with hooks) not `git commit --no-verify`.

---

### 6. Session Handoff Protocol (MANDATORY UPDATES)

**SESSION_HANDOFF.md MUST BE UPDATED:**

**When**: At end of EVERY development session (no exceptions)

**What to Update**:
1. **What I Did This Session** - Bullet list of completed work
2. **Current State** - What's working, what's broken, what's in progress
3. **Next Session Priorities** - P1, P2, P3 tasks
4. **Context for AI** - Recent decisions, weird issues, dependencies

**Why Enforced**: Next AI session (or you tomorrow) will waste 30-60 minutes reconstructing context without this. 5 min investment → 60 min saved.

**ENFORCEMENT**: Before running `/sp.git.commit_pr` or ending session, check if SESSION_HANDOFF.md is current.

---

### 7. Reusable Intelligence Update Protocol

**AGENTS/SUBAGENTS/SKILLS MUST BE KEPT CURRENT:**

**When to Update RI Artifacts:**

**Trigger 1: New Domain Emerges (Create Agent)**
```markdown
Example: "We need to integrate with Cambridge Assessment API"
→ Create: `.claude/agents/cambridge-integration.md`
→ Document: Domain, responsibilities, scope, skills
→ Announce: 📋 CREATING: new agent `cambridge-integration.md`
```

**Trigger 2: Specialized Task Pattern Repeats (Create Subagent)**
```markdown
Example: "We keep validating Economics graphs manually"
→ Create: `.claude/subagents/economics-graph-validator.md`
→ Document: Narrow task, inputs/outputs, validation rules
→ Announce: 📋 CREATING: new subagent `economics-graph-validator.md`
```

**Trigger 3: Knowledge Block Reused (Create Skill)**
```markdown
Example: "Every marking engine needs AO1/AO2/AO3 scoring rules"
→ Create: `.claude/skills/ao-assessment-framework.md`
→ Document: Reusable knowledge, not task-specific
→ Announce: 📋 CREATING: new skill `ao-assessment-framework.md`
```

**Update Checkpoints:**
- End of Phase: Review all agents/subagents/skills for completeness
- After Major Feature: Document new patterns as RI artifacts
- Monthly: Prune obsolete RI artifacts

**ENFORCEMENT**: If you find yourself repeating the same task 3+ times, that's a signal to create a subagent.

---

### 8. Test-Before-Progress Protocol (MILESTONE GATES)

**AFTER EVERY MILESTONE, YOU MUST TEST:**

**Milestone 1: Database Model Created**
```bash
# Test: Can model be imported and instantiated?
pytest backend/tests/unit/test_models.py -v
```

**Milestone 2: API Endpoint Implemented**
```bash
# Test: Does endpoint return expected response?
pytest backend/tests/integration/test_routes.py -v
```

**Milestone 3: Feature Complete**
```bash
# Test: Do all user stories pass acceptance tests?
pytest backend/tests/e2e/test_feature.py -v
```

**Milestone 4: Phase Complete**
```bash
# Test: Does phase gate script pass?
./scripts/check-phase-N-complete.sh
```

**ENFORCEMENT**: If you move to next milestone without tests passing, you're building on shaky foundation. STOP and fix tests first.

---

### 9. Specialized Agent Definitions (COMPLETE IMMEDIATELY)

**YOU CURRENTLY HAVE ONLY 2 AGENTS. YOU NEED 10 MINIMUM.**

**MISSING AGENTS (Create These NOW)**:

1. **Testing Quality Agent** (`.claude/agents/testing-quality.md`)
   - Responsibilities: Test strategy, coverage, quality gates, E2E testing
   - When to use: Writing tests, debugging test failures, test architecture

2. **Git Workflow Agent** (`.claude/agents/git-workflow.md`)
   - Responsibilities: Branching, commits, PRs, merge strategies
   - When to use: Git operations, conflict resolution, commit messages

3. **Frontend Web Agent** (`.claude/agents/frontend-web.md`)
   - Responsibilities: Next.js UI/UX, React components, shadcn/ui integration
   - When to use: Building student dashboard, exam interface, progress charts
   - **NOTE**: Use Anthropic's `web-artifacts-builder` skill

4. **Database Integrity Agent** (`.claude/agents/database-integrity.md`)
   - Responsibilities: Schema design, constraints, indexes, migrations, ACID compliance
   - When to use: Database modeling, migration writing, performance tuning

5. **Constitution Enforcement Agent** (`.claude/agents/constitution-enforcement.md`)
   - Responsibilities: Validate all work against 8 principles, block violations
   - When to use: Before commits, before phase transitions, during PR reviews

6. **API Design Agent** (`.claude/agents/api-design.md`)
   - Responsibilities: RESTful patterns, status codes, validation, documentation
   - When to use: Creating endpoints, API versioning, error handling

7. **Deployment Agent** (`.claude/agents/deployment.md`)
   - Responsibilities: Vercel (frontend), Railway (backend), Azure (prod), CI/CD
   - When to use: Phase IV deployment, environment configuration, monitoring

8. **Syllabus Research Agent** (`.claude/agents/syllabus-research.md`)
   - Responsibilities: Cambridge website scraping, syllabus updates, content verification
   - When to use: Monthly syllabus checks, question validation

9. **AI Pedagogy Agent** (`.claude/agents/ai-pedagogy.md`)
   - Responsibilities: LLM integration, prompt engineering, personalization
   - When to use: Marking engine design, feedback generation, answer rewriting

10. **Assessment Engine Agent** (`.claude/agents/assessment-engine.md`)
    - Responsibilities: Question generation, exam creation, marking algorithms
    - When to use: Building marking engines, question extraction, grade calculation

**ACTION REQUIRED**: Create all 10 agent definitions BEFORE proceeding to `/sp.plan`.

**ENFORCEMENT**: If you proceed without defining these agents, you're violating Reusable Intelligence principles.

---

### 10. FastAPI/SQLModel Specialization

**YOU NEED SPECIALIZED SUBAGENTS FOR FASTAPI + SQLMODEL:**

**Create These Subagents:**

1. **SQLModel Schema Designer** (`.claude/subagents/sqlmodel-schema-designer.md`)
   - Task: Design multi-tenant database schemas with constraints
   - Pattern: student_id filters, foreign keys, indexes

2. **FastAPI Route Builder** (`.claude/subagents/fastapi-route-builder.md`)
   - Task: Create CRUD endpoints with validation and error handling
   - Pattern: Dependency injection, Pydantic schemas, status codes

3. **Alembic Migration Writer** (`.claude/subagents/alembic-migration-writer.md`)
   - Task: Generate database migrations from model changes
   - Pattern: Forward migration, rollback, data preservation

4. **SQLModel Query Optimizer** (`.claude/subagents/sqlmodel-query-optimizer.md`)
   - Task: Write efficient queries with proper indexing
   - Pattern: N+1 prevention, eager loading, query analysis

**ENFORCEMENT**: If you write SQLModel code without using these subagents, you're missing domain expertise.

---

## 🔄 SpecKit Workflow (Mandatory)

**All features MUST follow this workflow:**

1. **Specify**: `/sp.specify` → Creates `specs/{feature}/spec.md`
2. **Plan**: `/sp.plan` → Creates `specs/{feature}/plan.md`
3. **Tasks**: `/sp.tasks` → Creates `specs/{feature}/tasks.md`
4. **Implement**: Claude Code implements from spec
5. **Test**: Verify against Cambridge mark schemes
6. **Capstone**: Validate against Spec, Plan, Constitution

**Available Commands**:
- `/sp.constitution` - Create/update constitution
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
- ❌ Manually writing specs with `vim specs/...`
- ❌ Implementing code before spec exists
- ❌ Skipping plan or tasks steps

---

## 📊 Current Phase: Phase I (Core Infrastructure)

**Objective**: Establish SpecKitPlus structure, database, authentication, basic API.

**Timeline**: Days 1-4 (Dec 16-19)

**Deliverables**:
- [ ] Constitution ratified (✅ DONE)
- [ ] SpecKitPlus directory structure (✅ DONE)
- [ ] Database schema (multi-tenant PostgreSQL)
- [ ] Student authentication (Better Auth + JWT)
- [ ] Core API endpoints (students, subjects)
- [ ] Unit tests (>80% coverage)

**Technology Stack**:
- Backend: Python 3.12+, FastAPI 0.115+, SQLModel 0.0.22+
- Database: PostgreSQL 16 (Neon Serverless)
- Auth: Better Auth (JWT)
- Package Manager: UV 0.5+

**Explicit Non-Goals** (Phase II+ features):
- ❌ Question bank
- ❌ Marking engine
- ❌ Web UI
- ❌ MCP servers

**Phase Gate**: `scripts/check-phase-1-complete.sh`

---

## 🛡️ Enforcement Mechanisms (3-Level)

### Level 1: Automated Checks
- Pre-commit hooks (block secrets, build artifacts)
- Phase gate scripts (validate completion)
- Database constraints (student_id NOT NULL)
- CI/CD pipelines (test coverage >80%)

### Level 2: Manual Checklists
- **DAILY_CHECKLIST.md** (5 min before work)
- **SESSION_HANDOFF.md** (5 min after work)
- Phase completion checklists
- Weekly cleanup script

### Level 3: AI Reminders (Your Responsibility)
- **You enforce principles during implementation**
- Refuse non-compliant work (e.g., code before spec)
- Ask validation questions ("Is Phase N complete?")
- Remind of constitutional requirements

---

## 🔐 Multi-Tenant Security Pattern (ENFORCED)

**ALWAYS include student_id filter in queries:**

```python
# ✅ CORRECT - Filtered by student_id
def get_student_exams(student_id: UUID, db: Session):
    return db.query(Exam).filter(
        Exam.student_id == student_id  # REQUIRED
    ).all()

# ❌ PROHIBITED - Unfiltered query
def get_all_exams(db: Session):
    return db.query(Exam).all()  # SECURITY VIOLATION
```

**API Endpoint Pattern:**

```python
@router.get("/api/students/{student_id}/exams")
async def get_exams(
    student_id: UUID,
    current_user = Depends(get_current_user)
):
    # Verify JWT student_id matches request student_id
    if student_id != current_user.id:
        raise HTTPException(403, "Access denied")

    # Query with student_id filter
    return db.query(Exam).filter(
        Exam.student_id == student_id
    ).all()
```

---

## 📚 Key Resources

**Cambridge International**:
- Economics 9708 Syllabus: https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-economics-9708/
- Syllabus PDF (2023-2025): https://www.cambridgeinternational.org/Images/595463-2023-2025-syllabus.pdf
- Past Papers: https://pastpapers.papacambridge.com/papers/caie/as-and-a-level-economics-9708

**Documentation (MUST READ Before Using)**:
- Better Auth (30 min): https://www.better-auth.com/docs
- Neon PostgreSQL (15 min): https://neon.tech/docs
- FastAPI (30 min): https://fastapi.tiangolo.com/
- SQLModel (20 min): https://sqlmodel.tiangolo.com/
- Next.js App Router (45 min): https://nextjs.org/docs/app
- OpenAI API (30 min): https://platform.openai.com/docs/api-reference
- Anthropic API (30 min): https://docs.anthropic.com/claude/reference/getting-started

---

## 🧪 Testing Requirements

**Coverage Target**: >80% (enforced by phase gate)

**Test Types**:
- **Unit Tests**: pytest (backend), Jest (frontend)
- **Integration Tests**: API endpoint flows, database operations
- **E2E Tests**: Playwright (critical user journeys)
- **Accuracy Tests**: >85% vs. Cambridge mark schemes (Phase III+)

**Subject-Specific Tests** (Phase III+):
- Economics: Theory-diagram matching, AO1/AO2/AO3 scoring
- Accounting: Financial calculation accuracy, double-entry validation
- Mathematics: Symbolic parsing, proof verification
- English: Essay structure analysis, argument scoring

---

## 🚀 Daily Workflow

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

---

## ⚠️ Common Mistakes to Avoid

1. **❌ Implementing code before spec exists**
   - ✅ Always run `/sp.specify` first

2. **❌ Skipping student_id filter in queries**
   - ✅ Every query MUST filter by student_id

3. **❌ Inventing questions instead of using Cambridge past papers**
   - ✅ Extract questions from official PDFs with source citation

4. **❌ Lenient marking to make students feel good**
   - ✅ PhD-level strictness, >85% accuracy vs. Cambridge

5. **❌ Starting Phase N+1 before Phase N is 100% complete**
   - ✅ Run phase gate script, wait for pass

6. **❌ Not reading documentation before using new tools**
   - ✅ 30-minute reading rule saves hours of debugging

7. **❌ Forgetting to update SESSION_HANDOFF.md**
   - ✅ 5 minutes at end of session saves 30-60 minutes next time

---

## 📞 When You Need Help

**If unclear about task**:
1. Read the spec: `@specs/phase-N/{feature}/spec.md`
2. Check constitution: `.specify/memory/constitution.md`
3. Review SESSION_HANDOFF.md for context
4. Ask specific question: "Should Economics 9708 marking use levels-based or points-based scoring?"

**If stuck on implementation**:
1. Check if spec is clear (if not, use `/sp.clarify`)
2. Read official docs (30-minute rule)
3. Check if similar code exists in A-Level-Learning project
4. Ask for architectural guidance

**If constitutional violation detected**:
1. STOP immediately
2. Document the violation
3. Ask for constitutional amendment if needed (via `/sp.constitution`)

---

## 🎯 Success Criteria

**Phase I Complete When**:
- [ ] Constitution ratified (v1.0.0)
- [ ] Database schema created and migrated
- [ ] Student can register/login via API
- [ ] JWT tokens working
- [ ] Unit tests passing (>80% coverage)
- [ ] `scripts/check-phase-1-complete.sh` passes

**Overall Project Success When**:
- [ ] Economics 9708 fully supported
- [ ] >85% marking accuracy
- [ ] PhD-level feedback quality
- [ ] Multi-tenant security verified
- [ ] Syllabus synchronized
- [ ] All tests passing
- [ ] Deployed and accessible
- [ ] Ready for additional subjects

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-16 | **Next Review**: After Phase I completion

🎓 **Remember**: Every decision affects students' A-Level exam success. Quality over speed. Always.
