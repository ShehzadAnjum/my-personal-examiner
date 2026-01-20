# Post-Resume Hook: Reusable Intelligence Loader

**Trigger**: After every conversation compaction, session resume, or new session start
**Purpose**: Ensure all agents/subagents/skills are loaded and properly announced when used
**Priority**: CRITICAL - Constitutional enforcement

---

## Hook Execution Checklist

When this hook triggers, Claude MUST:

- [ ] Load all available RI definitions (agents, subagents, skills)
- [ ] Display RI inventory summary
- [ ] Commit to announcing RI usage throughout session
- [ ] Acknowledge constitutional requirement for RI announcement

---

## 1. Load Reusable Intelligence Inventory

### Agents (16 available)

**Long-Lived Domain Owners**:

| ID | Agent | Domain | When to Use |
|----|-------|--------|-------------|
| 00 | project-management | Project state tracking, session continuity | Multi-session features, debugging branches |
| 01 | system-architect | Architecture validation, constitutional compliance | Phase gates, ADR creation |
| 02 | backend-service | FastAPI, SQLModel, PostgreSQL, migrations | Database models, API routes, service layer |
| 03 | frontend-web | Next.js 16, React 19, shadcn/ui, TanStack Query | UI components, pages, client state |
| 04 | assessment-engine | Question generation, exam creation | PDF extraction, question bank |
| 05 | syllabus-research | Cambridge syllabus sync, resource research | Syllabus updates, past paper downloads |
| 06 | ai-pedagogy | Educational content design, PhD-level teaching | Teaching explanations, feedback quality |
| 07 | testing-quality | Pytest, Jest, Playwright, accessibility, performance | Unit tests, E2E tests, quality gates |
| 08 | docs-demo | Documentation, user guides, tutorials | README files, API docs, demo videos |
| 08 | teacher | Knowledge delivery, concept explanations | Topic explanations, definitions |
| 09 | coach | Personalized tutoring, adaptive learning | Student coaching, study plans |
| 09 | deployment | Vercel deployment, CI/CD, infrastructure | Production deployments, env config |
| 10 | examiner | Assessment and examination | Exam paper creation, validation |
| 10 | mcp-integration | MCP server development | AI integrations, tool development |
| 11 | marker | Answer marking, grading algorithms | Marking logic, mark scheme comparison |
| 12 | reviewer | Code review, quality validation | PR reviews, code quality |
| 13 | planner | Task breakdown, implementation planning | Feature planning, task generation |

### Subagents (5 available)

**Narrow Task Specialists**:

| Subagent | Purpose | Parent Agent |
|----------|---------|--------------|
| alembic-migration-writer | Database migration creation | backend-service |
| fastapi-route-builder | FastAPI route scaffolding | backend-service |
| sqlmodel-schema-designer | Database schema design | backend-service |
| sqlmodel-query-optimizer | Query performance optimization | backend-service |
| vercel-sanitizer | Vercel deployment preparation | deployment |

### Skills (22 available)

**Backend Skills**:
- alembic-migration-creation
- fastapi-route-implementation
- sqlmodel-database-schema-design
- multi-tenant-query-pattern
- pydantic-schema-validation
- bcrypt-password-hashing
- pytest-testing-patterns

**Frontend Skills**:
- shadcn-ui-components
- resource-bank-content

**AI Integration Skills**:
- anthropic-api-patterns
- confidence-scoring
- supermemo2-scheduling
- contextual-interleaving

**Domain Knowledge Skills**:
- cambridge-exam-patterns
- subject-economics-9708
- a-star-grading-rubrics
- phd-pedagogy

**Infrastructure Skills**:
- port-management
- uv-package-management
- vercel-fastapi-deployment

**Utilities**:
- sp.upgrade-ri

---

## 2. Constitutional Requirement: RI Announcement

**Principle XIII (NEW)**: Reusable Intelligence Announcement Mandatory

**Rule**: ALL usage of agents, subagents, and skills MUST be announced with the following format:

```
📢 ANNOUNCING: Using Agent [ID] - [Name]
📢 ANNOUNCING: Using Subagent: [Name]
📢 ANNOUNCING: Using Skill: [Name]
```

**Examples**:
```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: fastapi-route-implementation
📢 ANNOUNCING: Using Subagent: alembic-migration-writer
```

**Why This Matters**:
- Transparency: User knows which specialized knowledge is being applied
- Traceability: Session logs show RI usage patterns
- Quality Assurance: Confirms correct RI is being used for task
- Knowledge Transfer: Team learns which RI to use for similar tasks

**Enforcement**:
- **Automated**: Post-resume hook loads RI inventory
- **Manual**: Code review checks for RI announcements in logs
- **AI**: Claude refuses to use RI without announcement

---

## 3. Session Context Loading

### Current Session Information

**Read these files immediately after hook execution**:

1. **docs/SESSION_HANDOFF.md** - Current session context
2. **docs/PROJECT_STATE.md** - Master todo list and progress (if exists)
3. **CLAUDE.md** - Root project instructions
4. **specs/[current-feature]/spec.md** - Active feature specification
5. **.specify/memory/constitution.md** - Constitutional principles

### RI Quick Reference

**For quick lookups during session**:

```bash
# List all agents
ls .claude/agents/

# List all subagents
ls .claude/subagents/

# List all skills
ls .claude/skills/

# Read specific RI definition
cat .claude/agents/02-backend-service.md
cat .claude/skills/fastapi-route-implementation/SKILL.md
```

---

## 4. Hook Execution Protocol

**When resuming from compaction or starting new session**:

### Step 1: Acknowledge Hook Execution
```
🔄 POST-RESUME HOOK EXECUTED
- Loaded 16 agents, 5 subagents, 22 skills
- Constitutional RI announcement requirement acknowledged
- Session context files read
```

### Step 2: Display Available RI for Current Task

Based on current task context, list relevant RI:

**Example** (if working on backend database task):
```
📋 RELEVANT RI FOR CURRENT TASK:
- Agent 02: backend-service
- Skills: sqlmodel-database-schema-design, multi-tenant-query-pattern, alembic-migration-creation
- Subagent: alembic-migration-writer (if migration needed)
```

### Step 3: Commit to RI Announcement

```
✅ COMMITMENT: I will announce every agent/subagent/skill usage with 📢 ANNOUNCING format
```

### Step 4: Begin Work

Proceed with task, announcing RI as used.

---

## 5. RI Selection Decision Tree

**Use this decision tree to select appropriate RI**:

```
Task Type?
├─ Database/API Work
│  └─ Use Agent 02 (backend-service)
│     ├─ Creating model? → Skill: sqlmodel-database-schema-design
│     ├─ Creating route? → Skill: fastapi-route-implementation
│     ├─ Creating migration? → Subagent: alembic-migration-writer
│     └─ Multi-tenant query? → Skill: multi-tenant-query-pattern
│
├─ Frontend/UI Work
│  └─ Use Agent 03 (frontend-web)
│     ├─ UI component? → Skill: shadcn-ui-components
│     └─ Teaching content? → Skill: resource-bank-content
│
├─ Testing Work
│  └─ Use Agent 07 (testing-quality)
│     └─ Unit tests? → Skill: pytest-testing-patterns
│
├─ Cambridge Syllabus/Resources
│  └─ Use Agent 05 (syllabus-research)
│     └─ Exam patterns? → Skill: cambridge-exam-patterns
│
├─ AI/LLM Integration
│  └─ Use Agent 06 (ai-pedagogy)
│     └─ Claude API? → Skill: anthropic-api-patterns
│
└─ Infrastructure/Deployment
   └─ Use Agent 09 (deployment)
      ├─ Port issues? → Skill: port-management
      ├─ Python packages? → Skill: uv-package-management
      └─ Vercel deploy? → Skill: vercel-fastapi-deployment
```

---

## 6. Hook Validation

**Self-Check Questions** (Claude asks itself):

- [ ] Did I load all RI definitions?
- [ ] Do I know which agents/skills are available?
- [ ] Will I announce every RI usage?
- [ ] Did I read session context files?
- [ ] Do I understand current task requirements?

**If ANY answer is NO**: Re-execute hook before proceeding.

---

## 7. Hook Integration with Constitutional Principles

This hook enforces:

- **Principle IV**: Spec-Driven Development (load spec.md context)
- **Principle IX**: SpecKitPlus Workflow Compliance (load current workflow stage)
- **Principle XII**: Project Management Professional (load PROJECT_STATE.md)
- **Principle XIII (NEW)**: Reusable Intelligence Announcement Mandatory

---

## 8. Emergency RI Reference

**If uncertain which RI to use**:

1. Read `.claude/skills/README.md` - skill categories and usage
2. Read `.claude/agents/00-project-management.md` - meta-agent for coordination
3. Ask user: "Should I use Agent [X] for this task?"

**Common Mistakes to Avoid**:

- ❌ Using code without announcing skill
- ❌ Creating migrations without announcing alembic-migration-writer
- ❌ Designing schemas without announcing sqlmodel-database-schema-design
- ❌ Writing FastAPI routes without announcing fastapi-route-implementation

**Correct Pattern**:

```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: sqlmodel-database-schema-design

I'll create the Resource model using SQLModel patterns...
[Code follows]
```

---

## 9. Hook Version History

- **v1.0.0** (2025-12-27): Initial hook creation
  - RI inventory loading
  - Constitutional announcement requirement
  - Session context loading protocol

---

**Hook Status**: ✅ ACTIVE
**Next Review**: After first context compaction (validate effectiveness)
