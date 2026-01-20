# Rule: Reusable Intelligence Announcement

**Priority**: MEDIUM
**Enforcement**: Every agent/skill/subagent usage

---

## Rule Statement

Every usage of an agent, subagent, or skill must be announced with the 📢 format.

## Announcement Format

```
📢 ANNOUNCING: Using Agent 02 - Backend Service
📢 ANNOUNCING: Using Skill: fastapi-route-implementation
📢 ANNOUNCING: Using Subagent: alembic-migration-writer
```

## Why This Matters

- Transparency for users about AI assistance
- Enables learning from which RI is most useful
- Creates audit trail for quality control
- Helps identify gaps in RI catalog

## RI Inventory

Full inventory at `.claude/RI_INVENTORY.md`:
- 16 agents
- 5 subagents
- 22+ skills

## Post-Resume Hook

After context compaction, execute `.claude/hooks/post-resume.md` to:
1. Load complete RI inventory
2. Acknowledge announcement requirement
3. Identify relevant RI for current task
