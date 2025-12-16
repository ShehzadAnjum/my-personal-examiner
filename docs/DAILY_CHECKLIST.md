# Daily Pre-Work Checklist

> **Purpose**: 5-minute constitutional compliance check before starting development work. Prevents violations, ensures context continuity, saves 30-60 minutes of backtracking.

**Date**: [YYYY-MM-DD]
**Session Start Time**: [HH:MM]
**Current Phase**: Phase I (Core Infrastructure & Database)

---

## 🚀 Quick Start (Do These First)

### 1. Read SESSION_HANDOFF.md
- [ ] Read `docs/SESSION_HANDOFF.md` (updated last session)
- [ ] Understand current state (Working/Broken/In Progress)
- [ ] Note Priority 1 task for today
- [ ] Check for blockers

**If SESSION_HANDOFF.md is stale** (>24 hours old):
- ⚠️ Proceed with caution - context may be incomplete
- Review git log for recent commits

### 2. Verify Environment
- [ ] Database accessible: `psql $DATABASE_URL -c "SELECT 1"`
- [ ] Backend dependencies current: `cd backend && uv sync`
- [ ] Frontend dependencies current: `cd frontend && npm ci` (if needed)

### 3. Git Status Check
```bash
git status
git log -3 --oneline
git diff
```
- [ ] No uncommitted WIP from last session (or intentionally saved)
- [ ] On correct branch: `[branch-name]`
- [ ] No merge conflicts

---

## 📋 Constitutional Compliance (8 Principles)

### Principle I: Subject Accuracy is Non-Negotiable
- [ ] Cambridge syllabus for Economics 9708 is current (2023-2025)
- [ ] No new content created without syllabus reference

**Last Verification**: [DATE]
**Next Verification Due**: [DATE + 30 days]

### Principle II: A* Standard Marking Always
- [ ] No marking logic implemented without >85% accuracy validation
- [ ] Cambridge mark scheme available for any question work

### Principle III: Syllabus Synchronization First
- [ ] Monthly Cambridge website check current
- [ ] No syllabus-dependent work without recent sync

**Last Cambridge Check**: [DATE]
**Next Check Due**: [DATE + 30 days]

### Principle IV: Spec-Driven Development
- [ ] Current task has spec in `specs/[feature]/spec.md`
- [ ] Plan exists: `specs/[feature]/plan.md`
- [ ] Tasks exist: `specs/[feature]/tasks.md`

**If NO spec exists**:
- ❌ STOP - Run `/sp.specify [feature-name]` first

### Principle V: Multi-Tenant Isolation is Sacred
- [ ] All new queries include `student_id` filter
- [ ] No global queries accessing student data

**Pattern to enforce**:
```python
# ✅ CORRECT
db.query(Model).filter(Model.student_id == current_user.id)

# ❌ PROHIBITED
db.query(Model).all()
```

### Principle VI: Feedback is Constructive and Detailed
- [ ] Any feedback code includes WHY + HOW structure
- [ ] No generic "good job" or "needs improvement" messages

### Principle VII: Phase Boundaries Are Hard Gates
- [ ] Current phase completion: [X%]
- [ ] No Phase II work started (Phase I incomplete)

**Phase I Gate Script**:
```bash
./scripts/check-phase-1-complete.sh
```
- [ ] Not run yet (Phase I in progress)

### Principle VIII: Question Bank Quality Over Quantity
- [ ] All questions have Cambridge source reference
- [ ] Mark schemes verified against official documents

---

## 🧪 Quality Gates (Pre-Work)

### Tests
- [ ] All tests passing from last session
- [ ] No skipped/ignored tests

**Run**:
```bash
# Backend
cd backend && uv run pytest

# Frontend (when implemented)
cd frontend && npm test
```

### Code Quality
- [ ] No linting errors: `cd backend && uv run ruff check .`
- [ ] Type checking passes: `cd backend && uv run mypy src/`
- [ ] No security warnings: `cd backend && uv run bandit -r src/`

---

## 📂 Current Phase Validation

### Phase I: Core Infrastructure & Database (Days 1-4)

**Deliverables Status**:
- [ ] Directory structure (SpecKitPlus compliant)
- [ ] Constitution v1.0.0 created
- [ ] Database schema designed (SQLModel)
- [ ] PostgreSQL (Neon) connected
- [ ] Student authentication (Better Auth + JWT)
- [ ] Basic API endpoints (students, auth, subjects)
- [ ] Unit tests (>80% coverage)

**Current Focus**: [What you're working on today]

**Phase I Gate Criteria** (not ready to run yet):
- [ ] All database models implemented
- [ ] Alembic migrations created and applied
- [ ] Authentication working (register, login, JWT)
- [ ] CRUD endpoints functional
- [ ] >80% test coverage
- [ ] All constitutional principles followed

---

## 🛠️ Tool & Dependency Check

### Python Backend
- [ ] Python version: `python --version` (expect 3.12+)
- [ ] UV installed: `uv --version` (expect 0.5+)
- [ ] Virtual environment active (if used)

### Node Frontend (Phase IV)
- [ ] Node version: `node --version` (expect 20+)
- [ ] npm installed: `npm --version`

### Database
- [ ] Neon PostgreSQL connection string in `.env`
- [ ] Database accessible: `psql $DATABASE_URL -c "\dt"`

### AI Services (Phase III)
- [ ] OpenAI API key in `.env` (required for marking)
- [ ] Anthropic API key in `.env` (optional)

---

## 📝 Reusable Intelligence Check

### Agents Available
- [ ] System Architect (`.claude/agents/system-architect.md`)
- [ ] Backend Service (`.claude/agents/backend-service.md`)

**Missing agents** (complete in Phase I):
- Assessment Engine, Frontend Web, Syllabus Research, AI Pedagogy, Testing Quality, Docs Demo, Deployment, MCP Integration

### SpecKit Commands Available
- [ ] All 11 commands in `.claude/commands/sp.*.md`
- [ ] `/sp.specify`, `/sp.plan`, `/sp.tasks` tested and working

---

## ⚠️ Common Mistakes to Avoid (Reminders)

1. ❌ **Never write code before spec** - Run `/sp.specify` first
2. ❌ **Never skip student_id filter** - Multi-tenant isolation is sacred
3. ❌ **Never hardcode Cambridge content** - Always reference current syllabus
4. ❌ **Never mark <85% accuracy** - PhD-level standards required
5. ❌ **Never skip phase gates** - 100% completion before advancing
6. ❌ **Never commit secrets** - Use `.env` for all credentials
7. ❌ **Never create questions without source** - Cambridge reference mandatory
8. ❌ **Never give feedback without WHY+HOW** - Constructive detail required

---

## 🚦 Ready to Start?

### All Green (✅ all checks passed)
→ Proceed with Priority 1 task from SESSION_HANDOFF.md

### Some Yellow (⚠️ minor issues)
→ Fix minor issues first, then proceed

### Any Red (❌ critical failures)
→ **STOP** - Fix critical issues before starting work:
- Tests failing → Debug and fix
- No spec → Run `/sp.specify`
- Phase gate issues → Complete current phase first
- Environment broken → Fix setup

---

## 📊 End-of-Day Update

**Before ending session** (5 minutes):
1. Update `docs/SESSION_HANDOFF.md` with today's work
2. Run phase gate script if phase complete: `./scripts/check-phase-1-complete.sh`
3. Commit all work with meaningful message
4. Push to remote if phase deliverable complete

**Tomorrow's checklist will start fresh with this updated handoff.**

---

**Checklist Version**: 1.0.0
**Last Updated**: 2025-12-16
**Constitution Version**: 1.0.0
**Estimated Time**: 5 minutes (investment saves 30-60 min context reload)
