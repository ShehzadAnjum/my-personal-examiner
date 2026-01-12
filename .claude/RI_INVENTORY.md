# Reusable Intelligence (RI) Inventory

**Last Updated**: 2025-12-27
**Total RI**: 43 (16 agents + 5 subagents + 22 skills)

**Constitutional Requirement**: Principle XIII - ALL RI usage MUST be announced with 📢 format

---

## Quick Reference

### Agents (16) - Long-Lived Domain Owners

| ID | Name | Domain | Primary Tools | Key Skills |
|----|------|--------|---------------|------------|
| 00 | project-management | Session continuity, debugging branches | Read, Write, Edit, Bash | Project state tracking, task trees |
| 01 | system-architect | Architecture validation, ADRs | Read, Grep, Glob, Bash | Constitutional compliance, phase gates |
| 02 | backend-service | FastAPI, SQLModel, PostgreSQL | Read, Write, Edit, Grep, Glob, Bash | fastapi-route-implementation, sqlmodel-database-schema-design, alembic-migration-creation, multi-tenant-query-pattern |
| 03 | frontend-web | Next.js, React, shadcn/ui | Read, Write, Edit, Grep, Glob, Bash | shadcn-ui-components, resource-bank-content |
| 04 | assessment-engine | Question generation, exam creation | Read, Write, Edit, Grep, Glob, Bash | cambridge-exam-patterns |
| 05 | syllabus-research | Cambridge sync, resource research | Read, Grep, Glob, WebFetch, WebSearch | cambridge-exam-patterns, subject-economics-9708 |
| 06 | ai-pedagogy | Educational content, PhD teaching | Read, Write, Edit, Grep, Glob | phd-pedagogy, anthropic-api-patterns |
| 07 | testing-quality | pytest, Playwright, accessibility | Read, Write, Edit, Bash, Grep, Glob | pytest-testing-patterns |
| 08 | docs-demo | Documentation, tutorials | Read, Write, Edit, Grep, Glob | N/A |
| 08 | teacher | Knowledge delivery, explanations | Read, Write, Edit | phd-pedagogy, subject-economics-9708 |
| 09 | coach | Personalized tutoring | Read, Write, Edit | confidence-scoring, contextual-interleaving |
| 09 | deployment | Vercel, CI/CD, infrastructure | Read, Bash, Grep, Glob | vercel-fastapi-deployment |
| 10 | examiner | Assessment, exam creation | Read, Write, Edit, Grep | cambridge-exam-patterns, a-star-grading-rubrics |
| 10 | mcp-integration | MCP server development | Read, Write, Edit, Bash, Grep, Glob | anthropic-api-patterns |
| 11 | marker | Answer marking, grading | Read, Write, Edit | a-star-grading-rubrics |
| 12 | reviewer | Code review, quality | Read, Grep, Glob, LSP | Constitutional compliance validation |
| 13 | planner | Task breakdown, planning | Read, Write, Edit, Grep, Glob | Task generation, dependency management |

---

### Subagents (5) - Narrow Task Specialists

| Subagent | Purpose | Parent Agent | When to Use |
|----------|---------|--------------|-------------|
| alembic-migration-writer | Database migration creation | backend-service (02) | Creating Alembic migrations for schema changes |
| fastapi-route-builder | FastAPI route scaffolding | backend-service (02) | Building new API endpoints |
| sqlmodel-schema-designer | Database schema design | backend-service (02) | Designing SQLModel models and relationships |
| sqlmodel-query-optimizer | Query performance optimization | backend-service (02) | Optimizing complex database queries |
| vercel-sanitizer | Vercel deployment preparation | deployment (09) | Preparing code for Vercel deployment |

---

### Skills (22) - Reusable Knowledge Blocks

#### Backend Skills (7)
- **alembic-migration-creation** - Alembic migration patterns with SQLModel
- **fastapi-route-implementation** - REST API endpoint patterns, error handling
- **sqlmodel-database-schema-design** - Database modeling, relationships, JSONB
- **multi-tenant-query-pattern** - Student-scoped queries, visibility filtering
- **pydantic-schema-validation** - Request/response schemas, validation
- **bcrypt-password-hashing** - Password security, hashing patterns
- **pytest-testing-patterns** - Unit/integration tests, fixtures, mocking

#### Frontend Skills (2)
- **shadcn-ui-components** - Accordion, Card, Button, Toast, Skeleton usage
- **resource-bank-content** - Topic explanation 9-component schema

#### AI Integration Skills (4)
- **anthropic-api-patterns** - Claude API, marking, coaching integration
- **confidence-scoring** - Student confidence tracking algorithms
- **supermemo2-scheduling** - Spaced repetition scheduling
- **contextual-interleaving** - Learning optimization, practice sequencing

#### Domain Knowledge Skills (4)
- **cambridge-exam-patterns** - A-Level exam structure, question types
- **subject-economics-9708** - Economics 9708 syllabus content
- **a-star-grading-rubrics** - A* grading criteria, marking standards
- **phd-pedagogy** - Educational content design, explanations

#### Infrastructure Skills (4)
- **port-management** - Kill stuck ports (3000-3002, 8000)
- **uv-package-management** - Python dependency management with UV
- **vercel-fastapi-deployment** - Production deployment patterns
- **better-auth-setup** - Better Auth v1 configuration

#### Utility Skills (1)
- **sp.upgrade-ri** - Upgrade RI to latest standards

---

## Usage Decision Tree

```
What are you working on?

┌─ DATABASE/API
│  ├─ 📢 Agent 02: backend-service
│  ├─ Creating model? → 📢 Skill: sqlmodel-database-schema-design
│  ├─ Creating route? → 📢 Skill: fastapi-route-implementation
│  ├─ Creating migration? → 📢 Subagent: alembic-migration-writer
│  └─ Multi-tenant query? → 📢 Skill: multi-tenant-query-pattern
│
┌─ FRONTEND/UI
│  ├─ 📢 Agent 03: frontend-web
│  ├─ UI component? → 📢 Skill: shadcn-ui-components
│  └─ Teaching content? → 📢 Skill: resource-bank-content
│
┌─ TESTING
│  ├─ 📢 Agent 07: testing-quality
│  ├─ Backend tests? → 📢 Skill: pytest-testing-patterns
│  └─ E2E tests? → Built-in Playwright knowledge
│
┌─ CAMBRIDGE RESOURCES
│  ├─ 📢 Agent 05: syllabus-research
│  ├─ Exam patterns? → 📢 Skill: cambridge-exam-patterns
│  └─ Economics 9708? → 📢 Skill: subject-economics-9708
│
┌─ AI/LLM INTEGRATION
│  ├─ 📢 Agent 06: ai-pedagogy
│  ├─ Claude API? → 📢 Skill: anthropic-api-patterns
│  ├─ Teaching content? → 📢 Skill: phd-pedagogy
│  └─ Grading? → 📢 Skill: a-star-grading-rubrics
│
┌─ INFRASTRUCTURE
│  ├─ 📢 Agent 09: deployment
│  ├─ Port issues? → 📢 Skill: port-management
│  ├─ Python packages? → 📢 Skill: uv-package-management
│  └─ Vercel deploy? → 📢 Skill: vercel-fastapi-deployment
│
└─ PROJECT MANAGEMENT
   └─ 📢 Agent 00: project-management
```

---

## Announcement Examples

### Correct Usage ✅

```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: sqlmodel-database-schema-design

I'll create the Resource model with JSONB metadata field...
[Code follows]
```

```
📢 ANNOUNCING: Using Agent 03 - Frontend Web
📢 ANNOUNCING: Using Skill: shadcn-ui-components

I'll implement the file upload component using shadcn Button and Toast...
[Code follows]
```

### Incorrect Usage ❌

```
I'll create the Resource model...
[Code without announcement]
```

```
Using backend patterns to create the API route...
[No specific agent/skill announcement]
```

---

## Common Task → RI Mapping

| Task | Agent | Skills/Subagents |
|------|-------|------------------|
| Create database model | 02: backend-service | sqlmodel-database-schema-design, multi-tenant-query-pattern |
| Create API endpoint | 02: backend-service | fastapi-route-implementation, pydantic-schema-validation |
| Create database migration | 02: backend-service | alembic-migration-writer (subagent) |
| Build UI component | 03: frontend-web | shadcn-ui-components |
| Generate topic explanation | 08: teacher | resource-bank-content, phd-pedagogy |
| Write unit tests | 07: testing-quality | pytest-testing-patterns |
| Sync Cambridge resources | 05: syllabus-research | cambridge-exam-patterns |
| Deploy to Vercel | 09: deployment | vercel-fastapi-deployment |
| Create marking algorithm | 11: marker | a-star-grading-rubrics |
| Fix port conflicts | N/A (direct skill) | port-management |
| Manage Python packages | N/A (direct skill) | uv-package-management |

---

## Quick Lookup Commands

```bash
# List all agents
ls .claude/agents/

# List all subagents
ls .claude/subagents/

# List all skills
ls .claude/skills/

# Read specific agent
cat .claude/agents/02-backend-service.md

# Read specific skill
cat .claude/skills/fastapi-route-implementation/SKILL.md

# View this inventory
cat .claude/RI_INVENTORY.md

# Execute post-resume hook
cat .claude/hooks/post-resume.md
```

---

## RI Creation Guidelines

**When to Create New RI**:

**Agent** (Long-lived domain owner):
- Manages a major architectural domain
- Used across multiple features
- Has dedicated tools and workflows
- Examples: backend-service, frontend-web, testing-quality

**Subagent** (Narrow specialist):
- Handles specific sub-task within agent domain
- One-time or occasional use
- Offloads complexity from parent agent
- Examples: alembic-migration-writer, fastapi-route-builder

**Skill** (Reusable pattern):
- Codifies repeatable pattern or best practice
- Referenced across multiple agents
- Provides templates and examples
- Examples: multi-tenant-query-pattern, pytest-testing-patterns

**Don't Create RI If**:
- One-time use only
- Too simple to document
- Already covered by existing RI

---

## Constitutional Enforcement

**Principle XIII**: Reusable Intelligence Announcement Mandatory

**Rule**: ALL RI usage MUST be announced with 📢 format

**Enforcement**:
- **Automated**: Post-resume hook loads RI inventory
- **Manual**: Code review checks announcements
- **AI**: Claude refuses RI use without announcement

**Violation Examples**:
- ❌ Using fastapi-route-implementation without announcing
- ❌ Using Agent 02 without 📢 announcement
- ❌ Writing SQLModel code without announcing sqlmodel-database-schema-design

**Compliance Examples**:
- ✅ Announcing before every agent use
- ✅ Announcing before every skill use
- ✅ Announcing before every subagent call

---

**Version**: 1.0.0
**Last Review**: 2025-12-27
**Next Review**: After first context compaction (validate hook effectiveness)
