# My Personal Examiner - Root Instructions

**Project**: PhD-Level A-Level Teaching & Examination System
**Current Phase**: Phase I Complete ✅ | Preparing Phase II
**Last Updated**: 2025-12-27

---

## 🎯 Quick Start (First-Time Reading)

**BEFORE ANY WORK, read these documents in order:**

1. **Post-Resume Hook** (`.claude/hooks/post-resume.md`) - Load RI inventory (16 agents, 5 subagents, 22 skills) [2 min] ⚡ **CRITICAL**
2. **Constitution** (`.specify/memory/constitution.md`) - 13 non-negotiable principles [30 min]
3. **Phase-Specific CLAUDE.md** (`specs/phase-N-*/CLAUDE.md`) - Current phase instructions [15 min]
4. **Session Handoff** (`docs/SESSION_HANDOFF.md`) - Current context and next steps [5 min]
5. **Methodology Corrections** (`docs/METHODOLOGY_CORRECTIONS.md`) - SpecKitPlus compliance [10 min]

**Total**: ~62 minutes to understand full context

**Why Critical?** Wrong content = exam failure = student's future damaged. Constitution prevents this.

---

## 🔄 Post-Resume Hook (MANDATORY - After Every Context Compaction)

**Trigger**: EVERY session start, resume, or after context compaction

**Action**: Read `.claude/hooks/post-resume.md` IMMEDIATELY

**Purpose**:
- Load complete RI inventory (16 agents, 5 subagents, 22 skills)
- Commit to announcing RI usage with 📢 format
- Read session context files
- Ensure continuity after compaction

**Constitutional Requirement**: Principle XIII - RI Announcement Mandatory

**Hook Output Expected**:
```
🔄 POST-RESUME HOOK EXECUTED
- Loaded 16 agents, 5 subagents, 22 skills
- Constitutional RI announcement requirement acknowledged
- Session context files read

📋 RELEVANT RI FOR CURRENT TASK:
- Agent 02: backend-service
- Skills: sqlmodel-database-schema-design, multi-tenant-query-pattern

✅ COMMITMENT: I will announce every agent/subagent/skill usage with 📢 ANNOUNCING format
```

**Announcement Format** (MANDATORY):
```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: fastapi-route-implementation
📢 ANNOUNCING: Using Subagent: alembic-migration-writer
```

---

## 📋 SpecKitPlus Workflow (MANDATORY)

**BEFORE implementing ANY feature, follow this exact sequence:**

```
1. /sp.specify <feature>    → Create specs/<feature>/spec.md
2. /sp.clarify              → Identify edge cases (if needed)
3. /sp.plan                 → Create specs/<feature>/plan.md
4. /sp.tasks                → Create specs/<feature>/tasks.md
5. /sp.implement            → Execute tasks from tasks.md
6. /sp.adr <title>          → Document architectural decisions
7. /sp.phr                  → Record prompt history
8. /sp.git.commit_pr        → Commit with constitutional compliance
```

**NEVER**:
- ❌ Write code before spec exists
- ❌ Skip clarify/plan/tasks steps
- ❌ Implement without following spec exactly

---

## 🛡️ Technology Stack (LOCKED by Constitution)

**Backend**:
- **ORM**: SQLModel (not SQLAlchemy, not Prisma)
- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 16 (Neon)
- **Package Manager**: UV 0.5+
- **Migrations**: Alembic 1.13+

**Frontend** (Phase IV):
- **Framework**: Next.js 16+ (App Router)
- **UI**: shadcn/ui + Tailwind CSS 4
- **State**: Zustand 5 or React Context

**AI/LLM**:
- **Primary**: OpenAI GPT-4.5 or Anthropic Claude Sonnet 4.5
- **Embeddings**: OpenAI text-embedding-3-small

**Testing**:
- **Backend**: pytest 8.3+ (>80% coverage required)
- **Frontend**: Jest 29+ + Playwright 1.49+

**Why Locked?** Changing tech stack mid-project wastes weeks. To change, must amend constitution.

---

## 📁 CLAUDE.md Hierarchy (NEW - User Requirement)

**Root** (`/CLAUDE.md`) - This file
- Project-wide instructions only
- Technology stack
- Constitutional reference
- SpecKitPlus workflow
- Where to find phase/feature instructions

**Phase-Specific** (`/specs/phase-N-*/CLAUDE.md`)
- Phase I: `specs/phase-1-core-infrastructure/CLAUDE.md` (auth, database, testing) ✅
- Phase II: `specs/phase-2-question-bank/CLAUDE.md` (PDF extraction, questions) ✅
- Phase III: `specs/phase-3-ai-teaching-roles/CLAUDE.md` (6 AI agents, marking) ✅
- Phase IV: `specs/phase-4-web-ui/CLAUDE.md` (Next.js, UI components) ✅
- Phase V: `specs/phase-5-advanced-features/CLAUDE.md` (CLI, MCP servers) ✅

**Feature-Specific** (`/specs/00X-*/`) - Individual feature specs with spec.md, plan.md, tasks.md

**Modular Rules** (`.claude/rules/`) - Focused behavioral constraints
- `multi-tenant-security.md` - Student data isolation
- `cambridge-accuracy.md` - Content accuracy requirements
- `marking-standards.md` - PhD-level marking criteria
- `spec-driven-development.md` - No code before spec
- `testing-requirements.md` - 80% coverage gates
- `ri-announcement.md` - Agent/skill usage announcement

**Rule**: No CLAUDE.md file should exceed 300 lines. Split into subdirectories if larger.

---

## 🎓 Project Context

**What**: AI teacher for Cambridge International A-Levels
**MVP Subject**: Economics 9708 (AS & A Level)
**Standard**: PhD-level strictness (>85% accuracy vs Cambridge mark schemes)
**Architecture**: Multi-tenant (student-scoped data isolation)

**Future Subjects**: Accounting 9706, English GP 8021, Mathematics 9709

---

## ⚖️ Constitutional Principles (11 Total)

**READ FULL CONSTITUTION**: `.specify/memory/constitution.md`

**Critical Principles**:
1. **Subject Accuracy Non-Negotiable** - Match Cambridge syllabi exactly
2. **A* Standard Marking Always** - PhD-level strictness
3. **Syllabus Synchronization First** - Monthly Cambridge updates
4. **Spec-Driven Development** - No code before spec
5. **Multi-Tenant Isolation Sacred** - Every query includes student_id filter
6. **Feedback Constructive & Detailed** - Always explain WHY and HOW
7. **Phase Boundaries Hard Gates** - 100% completion before next phase
8. **Question Bank Quality Over Quantity** - Every question has verified mark scheme
9. **SpecKitPlus Workflow Compliance** (NEW) - Follow /sp.* command sequence
10. **Official Skills Priority** (NEW) - Check Anthropic skills catalog first
11. **CLAUDE.md Hierarchy** (NEW) - Root + phase/feature subdirectories

**Enforcement**: Automated (phase gates), Manual (checklists), AI (Claude enforces)

---

## 📚 Official Skills Catalog (Check BEFORE Creating Custom)

**Source**: https://github.com/anthropics/skills

**Available Official Skills** (Use these if applicable):
- `web-artifacts-builder` - UI development, React components
- `xlsx` - Spreadsheet analysis, analytics, grading exports
- `docx` - Word documents, exam papers, feedback
- `pdf` - PDF reading and analysis
- `webapp-testing` - E2E testing with Playwright
- `mcp-builder` - Building custom MCP servers

**Process**:
1. Check if official skill exists for your task
2. Use official skill if available
3. Only create custom skill if no official alternative
4. Document why official skill wasn't suitable

---

## 🔄 Reusable Intelligence

**Available Artifacts**:
- **Agents** (`.claude/agents/`) - 10 long-lived domain owners
- **Subagents** (`.claude/subagents/`) - 18+ narrow task specialists
- **Skills** (`.claude/skills/`) - 21+ reusable knowledge blocks
- **Commands** (`.claude/commands/`) - 11 SpecKit commands

**Quick Access to Common Skills**:
- **port-management.md** - Kill stuck ports (3000-3002, 8000), handle IPv4/IPv6
- **uv-package-management.md** - Python dependency management
- **multi-tenant-query-pattern.md** - Student-scoped database queries
- **See all**: `.claude/skills/README.md`

**Always Announce Usage**:
```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: fastapi-route-implementation
📢 ANNOUNCING: Using Skill: port-management
```

---

## 📊 Project Structure

```
my_personal_examiner/
├── CLAUDE.md                          # This file (project-wide)
├── .specify/memory/constitution.md    # 13 principles
├── .claude/
│   ├── agents/                        # 16 long-lived domain owners
│   ├── subagents/                     # 5 narrow task specialists
│   ├── skills/                        # 22+ reusable knowledge blocks
│   ├── rules/                         # Modular behavioral constraints
│   ├── hooks/                         # Event-triggered scripts
│   └── RI_INVENTORY.md                # Complete RI catalog
├── specs/
│   ├── phase-1-core-infrastructure/   # Phase I meta (CLAUDE.md)
│   ├── phase-2-question-bank/         # Phase II meta (CLAUDE.md)
│   ├── phase-3-ai-teaching-roles/     # Phase III meta (CLAUDE.md + spec)
│   ├── phase-4-web-ui/                # Phase IV meta (CLAUDE.md)
│   ├── phase-5-advanced-features/     # Phase V meta (CLAUDE.md)
│   ├── 001-phase-1-infra/             # Feature: Core infrastructure
│   ├── 004-coaching-page/             # Feature: Coaching UI
│   ├── 005-teaching-page/             # Feature: Teaching UI
│   ├── 006-resource-bank/             # Feature: Resource Bank
│   └── 007-resource-bank-files/       # Feature: File management
├── resources/                          # Learning materials (hierarchical)
│   └── cambridge-a-level/
│       └── economics-9708/            # Syllabus, textbooks, past papers
├── history/
│   ├── adr/                           # Architecture Decision Records
│   └── prompts/                       # Prompt History Records
├── backend/                           # FastAPI + SQLModel + PostgreSQL
├── frontend/                          # Next.js 16 (Phase IV)
├── docs/
│   ├── SESSION_HANDOFF.md             # Current context
│   └── METHODOLOGY_CORRECTIONS.md     # SpecKitPlus compliance
└── scripts/
    └── check-phase-N-complete.sh      # Phase gate validators
```

---

## 🚀 Current Status

**Phase I**: ✅ COMPLETE
- Authentication (register, login)
- Database (Student model, multi-tenant)
- Testing (40 tests, 82% coverage)
- Phase gate passed

**Feature Development**: 🔄 IN PROGRESS
- 004-coaching-page: ✅ Complete
- 005-teaching-page: ✅ Complete
- 006-resource-bank: ✅ Complete
- 007-resource-bank-files: 🔄 In Progress

**Phase II**: 📋 PLANNED
- See `specs/phase-2-question-bank/CLAUDE.md` for details

---

## 📞 Where to Get Help

**For Phase-Specific Questions**: Read `specs/phase-N-*/CLAUDE.md`
**For Constitutional Clarification**: Read `.specify/memory/constitution.md`
**For Current Context**: Read `docs/SESSION_HANDOFF.md`
**For SpecKitPlus Workflow**: Read `docs/METHODOLOGY_CORRECTIONS.md`

---

## 🎯 Success Criteria

**This Project Succeeds When**:
- Economics 9708 fully supported
- >85% marking accuracy vs Cambridge
- PhD-level feedback quality
- Multi-tenant security verified
- All 11 constitutional principles enforced
- SpecKitPlus workflow followed religiously

---

**Version**: 2.1.0 | **Last Updated**: 2026-01-05 | **Next Review**: After Phase II
**Methodology**: SpecKitPlus (Strict compliance enforced)

🎓 **Remember**: Every decision affects students' A-Level exam success. Quality over speed. Always.

---

## 📂 Directory Structure (Updated 2026-01-05)

Recent restructuring completed:
- ✅ Phase CLAUDE.md files created (phases 2, 3, 5)
- ✅ `.claude/rules/` directory with 6 modular rules
- ✅ `resources/` hierarchical learning materials
- ✅ Feature spec structure standardized

## Active Technologies
- TypeScript 5.7+ + Next.js 16+ (App Router), React 19, shadcn/ui, Tailwind CSS 4, TanStack Query 5.62+ (004-coaching-page)
- Backend PostgreSQL (via API calls), browser localStorage for session persistence (004-coaching-page)
- TypeScript 5.7+ (Next.js 16+, React 19) + Next.js 16 App Router, React 19, shadcn/ui, Tailwind CSS 4, TanStack Query 5.62+, Lucide React (icons) (005-teaching-page)
- PostgreSQL via REST API calls (backend already implemented) (005-teaching-page)
- Python 3.11+ (Backend), TypeScript 5.7+ (Frontend) + FastAPI 0.115+, SQLModel, Next.js 16+, React 19, TanStack Query 5.62+ (006-resource-bank)
- PostgreSQL 16 (Neon) - primary, Local file cache (backend/cache/) - secondary (006-resource-bank)
- Python 3.11+ (backend) (007-resource-bank-files)
- Python 3.11+, TypeScript 5.7+ + FastAPI 0.115+, SQLModel, Next.js 16+, React 19, TanStack Query 5.62+ (008-academic-level-hierarchy)
- PostgreSQL 16 (Neon Serverless) (008-academic-level-hierarchy)

## Recent Changes
- 004-coaching-page: Added TypeScript 5.7+ + Next.js 16+ (App Router), React 19, shadcn/ui, Tailwind CSS 4, TanStack Query 5.62+
