# Rule: Spec-Driven Development

**Priority**: HIGH
**Enforcement**: Before writing any feature code

---

## Rule Statement

No feature code shall be written before its specification exists and is approved.

## Required Workflow

```
1. /sp.specify <feature>    → Create spec.md
2. /sp.clarify              → Resolve ambiguities (if needed)
3. /sp.plan                 → Create plan.md with architecture
4. /sp.tasks                → Create tasks.md with testable tasks
5. /sp.implement            → Execute tasks from tasks.md
```

## Why This Matters

- Prevents scope creep and rework
- Ensures all stakeholders agree on requirements
- Creates documentation for future reference
- Enables accurate effort estimation

## Artifacts Required

| Phase | File | Purpose |
|-------|------|---------|
| Specify | `spec.md` | Requirements and user stories |
| Plan | `plan.md` | Architecture decisions |
| Tasks | `tasks.md` | Atomic, testable work items |

## Exceptions

- Hotfixes for production bugs (document after)
- Minor typo corrections
- Dependency updates
