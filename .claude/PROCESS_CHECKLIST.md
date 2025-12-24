# Development Process Checklist

## Purpose
Ensure reusable intelligence (agents, skills) is actively used during development sessions.

---

## Before Starting Any Task

### ☐ 1. Check for Relevant Agent

```bash
# List all agents
ls .claude/agents/

# Search for relevant agent
ls .claude/agents/ | grep -i "backend\|frontend\|testing\|pedagogy\|deployment"
```

**If agent exists:**
```
📢 ANNOUNCING: Using Agent [NN] - [Agent Name]
```

**Agents by domain:**
- **00**: Project Management (PMP) - Task tracking, debug forks
- **01**: System Architect - Architecture decisions
- **02**: Backend Service - FastAPI, SQLModel, routes
- **03**: Frontend Web - React, Next.js, TanStack Query
- **04**: Assessment Engine - Exam generation, grading
- **05**: Syllabus Research - Cambridge content
- **06**: AI Pedagogy - Teaching UX, explanations
- **07**: Testing Quality - pytest, testing patterns
- **08**: Docs/Demo - Documentation, examples
- **09**: Coach/Deployment - AI coaching, infrastructure
- **10**: MCP Integration - Integration patterns
- **11**: Marker - Marking algorithms

### ☐ 2. Check for Relevant Skill

```bash
# List all skills
ls .claude/skills/

# Search for relevant skill
ls .claude/skills/ | grep -i "route\|component\|model\|query"
```

**If skill exists:**
```
📢 ANNOUNCING: Using Skill: [skill-name]
```

**Skills by category:**

**Development Tools:**
- port-management
- uv-package-management (Python)
- alembic-migration-creation

**Backend Patterns:**
- fastapi-route-implementation
- sqlmodel-database-schema-design
- multi-tenant-query-pattern
- pydantic-schema-validation
- bcrypt-password-hashing
- pytest-testing-patterns

**Frontend Patterns:**
- shadcn-ui-components
- phd-pedagogy (educational UX)
- tanstack-query-patterns (if created)
- client-side-caching-patterns (if created)

**AI Integration:**
- anthropic-api-patterns
- confidence-scoring
- supermemo2-scheduling
- contextual-interleaving

**Domain Knowledge:**
- cambridge-exam-patterns
- subject-economics-9708
- a-star-grading-rubrics

---

## During Implementation

### ☐ 3. When Task Gets Blocked or Error Occurs

**Invoke PMP Agent immediately:**

```
📢 ANNOUNCING: Using Agent 00 - Project Management (PMP)

Main Task: T[XXX] - [task description]
Blocker: [error or issue]
Creating Debug-00N: [fix description]
Return Point: T[XXX] (resume after debug complete)
```

**PMP Agent creates debug todos:**
- Debug-001: Fix missing dependency
- Debug-002: Fix test failures
- Debug-003: Fix import paths

**After debug complete, mark return point and resume main flow.**

### ☐ 4. Follow Patterns from Announced Skill/Agent

**Example:**
```
📢 ANNOUNCING: Using Skill: shadcn-ui-components

[Read skill for component import patterns]
[Follow skill's best practices for props and variants]
[Use skill's code examples as reference]
```

**Don't just announce - actually use the content!**

---

## After Implementation

### ☐ 5. Update Skill Evolution Log

**File:** `.claude/skills/skill-evolution-log.md`

**Add new learnings:**
```markdown
### [Date] [Feature] - [Pattern Name]

**What we learned:**
[New pattern or solution discovered]

**Where it was used:**
[File paths and context]

**Should update:**
[Which skill file(s) need updating]

**Code example:**
[Minimal example demonstrating pattern]
```

### ☐ 6. Create or Update Skills

**If new pattern is broadly reusable:**

1. Create new skill directory:
```bash
mkdir -p .claude/skills/[skill-name]
```

2. Create SKILL.md:
```markdown
---
description: [Brief description]
category: [backend|frontend|ai|domain|tools]
related-skills: []
constitutional-principles: []
---

# Skill: [Name]

## When to Use
[Context where this applies]

## Pattern
[Code example and explanation]

## Common Pitfalls
[What to avoid]
```

3. Update `.claude/skills/README.md` to include new skill

**If updating existing skill:**

1. Open skill file
2. Add new section or update existing section
3. Add code examples from current session
4. Document pitfalls discovered

---

## Session Completion Checklist

### ☐ 7. Review Session Quality

**Did you:**
- ✅ Announce agents used? (or explain why none were relevant)
- ✅ Announce skills used? (or explain why none were relevant)
- ✅ Invoke PMP when blocked? (or confirm no blockers occurred)
- ✅ Document new learnings in evolution log?
- ✅ Update/create skills based on learnings?

**If any ☐ are unchecked, review why and improve next session.**

---

## Quick Reference

### When to Use PMP Agent (Agent 00)

**Always invoke when:**
- Task fails or errors
- Missing dependencies discovered
- Test failures block progress
- Need to track main flow vs debug work

**Keywords:**
- "blocked", "error", "failed", "missing"
- "debug", "fix issue", "troubleshoot"
- "can't proceed", "stuck", "blocked by"

### When to Use Other Agents

**Backend work (Agent 02):**
- Creating routes, services, models
- Database schema design
- API endpoint implementation

**Frontend work (Agent 03):**
- Creating React components
- TanStack Query hooks
- Client-side state management

**Testing work (Agent 07):**
- Writing unit/integration tests
- Debugging test failures
- Test coverage improvement

**AI work (Agent 06):**
- Designing teaching interfaces
- Educational content structure
- PhD-level pedagogy patterns

---

## Enforcement

**Self-check every 3 tasks:**
```
[After completing T003, T006, T009, ...]

Did I check for agents/skills before starting last 3 tasks?
Did I announce any agents/skills I used?
Did I capture any learnings?
```

**End of session review:**
```
Total tasks: [N]
Agents announced: [list]
Skills announced: [list]
Learnings captured: [count]
Skills updated: [list]
```

**Goal:** Every session should have ≥1 agent/skill announced and ≥1 learning captured.

---

## Example Good Session

```markdown
## Session: 005-teaching-page (US1-US3)

### Agents Used:
- 📢 Agent 03 - Frontend Web (component creation)
- 📢 Agent 02 - Backend Service (API routes)
- 📢 Agent 00 - PMP (test failure debug fork)

### Skills Used:
- 📢 shadcn-ui-components (Card, Button, Accordion)
- 📢 tanstack-query-patterns (optimistic updates)
- 📢 sqlmodel-database-schema-design (SavedExplanation model)

### Learnings Captured:
1. TanStack Query optimistic updates with rollback
2. Hybrid localStorage + API caching pattern
3. SQLModel serialization fix for FastAPI

### Skills Updated:
1. Created: tanstack-query-patterns/SKILL.md
2. Updated: sqlmodel-database-schema-design/SKILL.md (serialization section)
3. Updated: shadcn-ui-components/SKILL.md (composition patterns)
```

---

## Why This Matters

**Without using agents/skills:**
- ❌ Reinventing solutions every time
- ❌ No knowledge accumulation
- ❌ Inconsistent patterns across features
- ❌ New team members can't learn from past work

**With active agent/skill usage:**
- ✅ Reuse proven solutions
- ✅ Build institutional knowledge
- ✅ Consistent patterns emerge
- ✅ Self-documenting codebase
- ✅ Faster development over time

**The goal:** Each session should make the next session easier by capturing reusable intelligence.
