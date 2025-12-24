---
name: sp-upgrade-ri
description: Upgrade reusable intelligence (agents/skills) to latest version standards. Internal skill for maintaining agent/skill quality.
---


# Skill: /sp.upgrade-ri - Auto-Upgrade Reusable Intelligence

**Type**: SpecKitPlus Command
**Domain**: Reusable Intelligence Management
**Purpose**: Auto-upgrade agents and skills by extracting learnings from completed tasks

---

## Overview

The `/sp.upgrade-ri` command scans completed tasks from tasks.md, extracts new patterns/learnings from implemented code, and appends them to the "Recent Learnings" sections of relevant agents. This keeps agents up-to-date with new knowledge gained during implementation.

**When to Use**:
- After completing a feature (all tasks in tasks.md done)
- After completing a phase (Phase 3, Phase 4, etc.)
- After fixing a major bug/blocker (debug branch resolved)
- Before starting a new feature (capture learnings from previous work)

---

## Execution Workflow

### Step 1: Load Feature Context

Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse:
- `FEATURE_DIR`: Absolute path to feature directory (e.g., `/path/to/specs/005-teaching-page`)
- `TASKS_FILE`: Absolute path to tasks.md

**Verify**:
- tasks.md exists
- At least 1 completed task exists (status marked [X])

**If no completed tasks**: Exit with message "No completed tasks found to extract learnings from."

---

### Step 2: Extract Completed Tasks

Parse tasks.md and extract all tasks marked `[X]` (completed):

```markdown
Example tasks.md:
- [X] T001: Create project structure per implementation plan
- [X] T013: Create ExplanationSection collapsible component in frontend/components/teaching/ExplanationSection.tsx
- [X] T014: Create BookmarkButton component in frontend/components/teaching/BookmarkButton.tsx
- [ ] T015: Create ExplanationSkeleton loading component
```

**Extract**:
- Task ID: T013, T014, etc.
- Task description: "Create ExplanationSection collapsible component"
- File paths: `frontend/components/teaching/ExplanationSection.tsx`

**Create Task List**:
```
Completed Tasks:
1. T013 - ExplanationSection component (frontend/components/teaching/ExplanationSection.tsx)
2. T014 - BookmarkButton component (frontend/components/teaching/BookmarkButton.tsx)
```

---

### Step 3: Read Implemented Files

For each completed task, read the file(s) mentioned:

**Example** (T013):
- Read `frontend/components/teaching/ExplanationSection.tsx`
- Identify patterns used:
  - shadcn/ui Accordion component
  - Collapsible section pattern
  - TypeScript prop interface
  - Accessibility attributes (aria-expanded, role)

**Example** (T014):
- Read `frontend/components/teaching/BookmarkButton.tsx`
- Identify patterns used:
  - 3 button variants (BookmarkButton, BookmarkIconButton, BookmarkButtonWithCount)
  - State management (isBookmarked, isLoading)
  - Icon animation (Loader2 spinner)
  - WCAG 2.1 AA compliance (aria-label, aria-pressed)

---

### Step 4: Detect Relevant Agents

For each completed task, determine which agent(s) should learn from it:

**Detection Rules**:

| File Pattern | Agent |
|--------------|-------|
| `frontend/components/**/*.tsx` | Agent 03 (Frontend Web) |
| `frontend/app/**/*.tsx` | Agent 03 (Frontend Web) |
| `backend/src/models/**/*.py` | Agent 02 (Backend Service) |
| `backend/src/routes/**/*.py` | Agent 02 (Backend Service) |
| `backend/src/services/**/*.py` | Agent 02 (Backend Service) |
| `backend/alembic/versions/**/*.py` | Agent 02 (Backend Service) |
| `tests/e2e/**/*.spec.ts` | Agent 07 (Testing Quality) |
| `tests/unit/**/*.py` | Agent 07 (Testing Quality) |
| Explanation structure design | Agent 06 (AI Pedagogy) |
| Debug branch (Debug-001, Debug-002) | Agent 00 (PMP) |

**Example**:
- T013 (ExplanationSection.tsx) → Agent 03
- T014 (BookmarkButton.tsx) → Agent 03
- T005 (SavedExplanation model) → Agent 02

---

### Step 5: Extract Learning Patterns

For each task, extract 1-3 key learnings to append to agent's "Recent Learnings" section:

**Learning Format**:
```markdown
### YYYY-MM-DD: [Pattern Name] ([Task ID] Context)
- **Pattern**: [What was implemented]
  - Rationale: [Why this approach was chosen]
  - Alternative: [What else was considered] - Rejected ([why])
- **File**: [Absolute or relative path]
- **Constitutional Compliance**: Principle [N] ([how it aligns])
- **Learning**: [Key insight or best practice discovered]
```

**Example Learning** (from T013):
```markdown
### 2025-12-24: shadcn/ui Accordion for Collapsible Sections (T013 ExplanationSection)
- **Pattern**: Use shadcn/ui Accordion component with controlled `defaultValue`
  - Rationale: Provides built-in accessibility (keyboard navigation, ARIA attributes)
  - Alternative: Custom collapsible with useState - Rejected (reinventing the wheel, missing a11y)
- **File**: frontend/components/teaching/ExplanationSection.tsx
- **Constitutional Compliance**: Principle II (A* standard - accessibility built-in)
- **Learning**: Always check shadcn/ui catalog before building custom interactive components
```

**Example Learning** (from T014):
```markdown
### 2025-12-24: Multi-Variant Button Pattern (T014 BookmarkButton)
- **Pattern**: Export 3 variants from single file (BookmarkButton, BookmarkIconButton, BookmarkButtonWithCount)
  - Rationale: DRY principle - shared logic (state, icons, loading), different presentations
  - Alternative: Separate files per variant - Rejected (code duplication, harder to maintain)
- **File**: frontend/components/teaching/BookmarkButton.tsx
- **Constitutional Compliance**: Principle II (A* standard - WCAG 2.1 AA with aria-label, aria-pressed)
- **Learning**: When components have shared logic but different UX needs, use variant exports instead of separate files
```

---

### Step 6: Append to Agent "Recent Learnings"

For each agent with new learnings:

1. **Read agent file** (e.g., `.claude/agents/03-frontend-web.md`)
2. **Locate "Recent Learnings" section**
3. **Append new learning** at the top (most recent first)
4. **Increment version** (patch bump: 2.0.0 → 2.0.1, 2.0.1 → 2.0.2)
5. **Update last-updated date** in YAML frontmatter
6. **Write updated agent file**

**Before**:
```markdown
---
version: 2.0.0
last-updated: 2025-12-23
---

## Recent Learnings (Auto-Updated)

### 2025-12-23: TanStack Query Tiered Caching (T009-T012)
...
```

**After**:
```markdown
---
version: 2.0.1
last-updated: 2025-12-24
---

## Recent Learnings (Auto-Updated)

### 2025-12-24: shadcn/ui Accordion for Collapsible Sections (T013)
- **Pattern**: Use shadcn/ui Accordion component with controlled `defaultValue`
  - Rationale: Provides built-in accessibility (keyboard navigation, ARIA attributes)
  - Alternative: Custom collapsible with useState - Rejected (reinventing the wheel, missing a11y)
- **File**: frontend/components/teaching/ExplanationSection.tsx
- **Constitutional Compliance**: Principle II (A* standard - accessibility built-in)
- **Learning**: Always check shadcn/ui catalog before building custom interactive components

### 2025-12-24: Multi-Variant Button Pattern (T014)
- **Pattern**: Export 3 variants from single file
  - Rationale: DRY principle - shared logic, different presentations
  - Alternative: Separate files - Rejected (code duplication)
- **File**: frontend/components/teaching/BookmarkButton.tsx
- **Constitutional Compliance**: Principle II (WCAG 2.1 AA compliance)
- **Learning**: Use variant exports for shared logic + different UX needs

### 2025-12-23: TanStack Query Tiered Caching (T009-T012)
...
```

---

### Step 7: Report Completion

Output summary:

```
✅ Auto-Upgrade Complete

Updated Agents: 2
  - Agent 03 (Frontend Web): v2.0.0 → v2.0.1 (2 learnings added)
  - Agent 02 (Backend Service): v2.0.0 → v2.0.1 (1 learning added)

Learnings Extracted:
  - T013: shadcn/ui Accordion for Collapsible Sections → Agent 03
  - T014: Multi-Variant Button Pattern → Agent 03
  - T005: JSONB for SavedExplanation → Agent 02

Next Steps:
  ✅ Agents are now up-to-date with latest patterns
  ✅ New work will benefit from these learnings
  → Continue with next feature or phase
```

---

## Pattern Extraction Rules

### **What to Extract** ✅

1. **New Patterns** (not already in agent)
   - Component patterns (hooks, variants, composition)
   - Architecture patterns (tiered caching, multi-tenant queries)
   - Tool configurations (shadcn/ui setup, TanStack Query config)
   - Debug fixes (missing dependencies, error recovery)

2. **Alternatives Considered**
   - Why approach A was chosen over approach B
   - Tradeoffs documented (performance vs. simplicity, etc.)
   - Constitutional compliance implications

3. **Key Insights**
   - "Always check X before doing Y"
   - "Avoid pattern Z because..."
   - "When condition C, use pattern P"

### **What to Skip** ❌

1. **Already Documented Patterns**
   - If agent already has similar learning, skip duplicate
   - If pattern matches existing "Core Expertise" section, skip

2. **Trivial Changes**
   - Simple typo fixes
   - Formatting changes
   - Single-line edits

3. **Incomplete Work**
   - Tasks marked `[ ]` (not completed)
   - Tasks marked as blocked or in-progress

---

## Version Increment Rules

**Patch Bump** (x.y.Z): New learnings added
- 2.0.0 → 2.0.1 (1st learning batch)
- 2.0.1 → 2.0.2 (2nd learning batch)

**Minor Bump** (x.Y.0): New capabilities added
- 2.0.2 → 2.1.0 (added new capability to capabilities list)

**Major Bump** (X.0.0): Breaking changes (rare)
- 2.1.0 → 3.0.0 (complete rewrite, incompatible with previous version)

**For /sp.upgrade-ri**: Always patch bump (learnings = non-breaking enhancements)

---

## Constitutional Compliance

**Principle IX: SpecKitPlus Workflow Compliance**
- `/sp.upgrade-ri` is part of SpecKitPlus workflow
- Ensures agents evolve with project (not static)
- Maintains institutional knowledge in RI system

---

## Example Usage

### Scenario 1: After Completing Feature 005-teaching-page

```bash
User: "/sp.upgrade-ri"

Agent: [Executes workflow]

Output:
✅ Auto-Upgrade Complete

Scanned: specs/005-teaching-page/tasks.md
Completed Tasks: 14 of 36 tasks

Updated Agents: 2
  - Agent 03 (Frontend Web): v2.0.0 → v2.0.1
    - T013: shadcn/ui Accordion pattern
    - T014: Multi-variant button pattern
  - Agent 02 (Backend Service): v2.0.0 → v2.0.1
    - T005: JSONB for SavedExplanation

Learnings Extracted: 3
Next: Continue with T015-T036
```

### Scenario 2: After Completing Phase (All Tasks Done)

```bash
User: "/sp.upgrade-ri"

Agent: [Executes workflow]

Output:
✅ Auto-Upgrade Complete

Scanned: specs/005-teaching-page/tasks.md
Completed Tasks: 36 of 36 tasks (Phase Complete)

Updated Agents: 4
  - Agent 03 (Frontend Web): v2.0.1 → v2.0.2 (5 learnings)
  - Agent 02 (Backend Service): v2.0.1 → v2.0.2 (3 learnings)
  - Agent 06 (AI Pedagogy): v2.0.0 → v2.0.1 (2 learnings)
  - Agent 07 (Testing Quality): v2.0.0 → v2.0.1 (4 learnings)

Learnings Extracted: 14
Next: Start new feature or phase with upgraded agents
```

---

## Integration with Workflow

**Recommended Integration Points**:

1. **After feature complete**: `/sp.upgrade-ri` before starting next feature
2. **Before phase gate**: `/sp.upgrade-ri` to capture all phase learnings
3. **After major debug**: `/sp.upgrade-ri` to document error recovery patterns
4. **Monthly cadence**: `/sp.upgrade-ri` to keep agents fresh

**Workflow Example**:
```
1. /sp.specify "New feature"
2. /sp.plan
3. /sp.tasks
4. /sp.implement
5. /sp.upgrade-ri  ← NEW STEP (capture learnings)
6. /sp.git.commit_pr
```

---

## Version History

- **1.0.0** (2025-12-24): Initial skill creation with auto-upgrade workflow, pattern extraction rules, version increment logic

**Status**: Active | **Next Review**: After first real usage (will refine extraction rules based on quality of learnings)
