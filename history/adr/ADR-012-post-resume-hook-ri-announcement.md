# ADR-012: Post-Resume Hook for RI Announcement & Context Preservation

**Date**: 2025-12-27
**Status**: Accepted
**Deciders**: User requirement, Constitutional enforcement
**Feature**: Infrastructure / Constitutional compliance

---

## Context

After conversation compaction or session resume, Claude often:
1. Forgets to announce agent/subagent/skill usage
2. Loses awareness of available Reusable Intelligence (RI)
3. Doesn't load session context files
4. Uses patterns without referencing corresponding RI

This leads to:
- Lost transparency (user doesn't know which RI is being used)
- Inconsistent RI application
- Duplicate work (reinventing patterns that exist in skills)
- Poor knowledge transfer (team doesn't learn RI usage patterns)

**User Requirement**: "need to add a hook that shall be triggered after every conversation compaction & resume. the hook shall ensure that 'Announcement of agents / subagent / skills whenever they are used, also ensured that all agents/subagents/skill (definitions) are loaded and shall be triggered and utilized'"

---

## Decision

Implement a **Post-Resume Hook** (`.claude/hooks/post-resume.md`) that:

1. **Loads complete RI inventory** (16 agents, 5 subagents, 22 skills)
2. **Commits Claude to RI announcement** using 📢 format
3. **Reads session context files** (SESSION_HANDOFF.md, PROJECT_STATE.md, spec.md)
4. **Displays relevant RI** for current task
5. **Enforces constitutional requirement** (Principle XIII)

**Hook Trigger**: EVERY session start, resume, or after context compaction

**Hook Output**:
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

**Mandatory Announcement Format**:
```
📢 ANNOUNCING: Using Agent [ID] - [Name]
📢 ANNOUNCING: Using Subagent: [Name]
📢 ANNOUNCING: Using Skill: [Name]
```

---

## Alternatives Considered

### Alternative 1: Manual Announcement Reminders (Rejected)

**Approach**: Add reminders in CLAUDE.md to announce RI

**Pros**:
- Simple, no new files
- Low overhead

**Cons**:
- Easily forgotten after compaction
- No enforcement mechanism
- No automatic RI inventory loading
- No session context loading

**Rejection Reason**: Too passive, relies on memory after compaction

---

### Alternative 2: Inline RI References in Constitution (Rejected)

**Approach**: List all RI in constitution, expect Claude to reference it

**Pros**:
- Centralized in one document
- Already reading constitution

**Cons**:
- Constitution already 1800+ lines
- RI inventory changes frequently (new skills)
- Violates separation of concerns
- Makes constitution harder to navigate

**Rejection Reason**: Constitution should define principles, not list implementation details

---

### Alternative 3: Automated Pre-Work Checklist Script (Rejected)

**Approach**: Shell script that prints RI inventory before session

**Pros**:
- Automated
- Easy to run

**Cons**:
- User must remember to run script
- Not triggered automatically by Claude Code
- No enforcement of announcements
- Doesn't integrate with Claude's workflow

**Rejection Reason**: External script, not part of Claude's internal workflow

---

### Alternative 4: Post-Resume Hook (ACCEPTED)

**Approach**: Dedicated hook file that Claude reads after compaction

**Pros**:
- Automatic trigger (Claude Code reads hooks)
- Loads complete RI inventory
- Enforces announcement format
- Reads session context files
- Constitutional integration (Principle XIII)
- Reusable across all sessions

**Cons**:
- New file to maintain (`.claude/hooks/post-resume.md`)
- Relies on Claude Code hook system

**Acceptance Reason**: Best balance of automation, enforcement, and context preservation

---

## Consequences

### Positive

✅ **Transparency**: User always knows which RI is being used
✅ **Consistency**: RI announcements standardized across all sessions
✅ **Context Preservation**: Session context files loaded automatically
✅ **Knowledge Transfer**: Team learns which RI to use for tasks
✅ **Quality Assurance**: Confirms correct RI selection
✅ **Traceability**: Session logs show RI usage patterns
✅ **Constitutional Compliance**: Enforces Principle XIII

### Negative

⚠️ **Maintenance**: Hook file must be updated when new RI added
⚠️ **Hook Dependency**: Relies on Claude Code executing hooks properly
⚠️ **Initial Overhead**: 2-minute hook execution at session start

### Neutral

ℹ️ **RI Inventory File**: Created `.claude/RI_INVENTORY.md` for quick reference
ℹ️ **Constitution Update**: Added Principle XIII (RI Announcement Mandatory)
ℹ️ **CLAUDE.md Update**: Added Post-Resume Hook section to Quick Start

---

## Implementation

### Files Created

1. **`.claude/hooks/post-resume.md`** (primary hook file)
   - RI inventory (16 agents, 5 subagents, 22 skills)
   - Announcement format enforcement
   - Session context loading protocol
   - RI selection decision tree

2. **`.claude/RI_INVENTORY.md`** (quick reference)
   - Complete RI listing
   - Usage decision tree
   - Announcement examples
   - Quick lookup commands

### Files Modified

1. **`.specify/memory/constitution.md`**
   - Added Principle XIII: Reusable Intelligence Announcement Mandatory
   - Updated version: 3.0.0 → 3.1.0
   - Updated principle count: 12 → 13

2. **`CLAUDE.md`**
   - Added Post-Resume Hook section to Quick Start
   - Updated reading order (hook now #1 priority)
   - Updated last modified date

### Constitutional Changes

**Principle XIII**: Reusable Intelligence Announcement Mandatory

**Enforcement**:
- **Automated**: Post-resume hook loads RI inventory
- **Manual**: Code review checks announcements in logs
- **AI**: Claude refuses RI use without announcement

---

## Validation

### Success Criteria

- [ ] Hook executes at every session start
- [ ] RI inventory loads completely (16 agents, 5 subagents, 22 skills)
- [ ] Announcements appear in logs with 📢 format
- [ ] Session context files read automatically
- [ ] Zero forgotten RI after compaction

### Testing Plan

1. **Simulate context compaction**
   - Work on task until context fills
   - Verify hook executes after compaction
   - Check RI announcements continue

2. **New session start**
   - Start fresh Claude Code session
   - Verify hook executes automatically
   - Check RI inventory loaded

3. **RI usage validation**
   - Use Agent 02 (backend-service)
   - Verify announcement appears: "📢 ANNOUNCING: Using Agent 02 - Backend Service"
   - Use skill (sqlmodel-database-schema-design)
   - Verify announcement appears: "📢 ANNOUNCING: Using Skill: sqlmodel-database-schema-design"

---

## Future Improvements

1. **Automated RI Inventory Update**: Script to regenerate RI_INVENTORY.md when new RI added
2. **RI Usage Analytics**: Track which RI used most frequently
3. **RI Recommendation Engine**: Suggest RI based on task description
4. **Hook Version Control**: Track hook effectiveness, iterate on format

---

## References

- **Hook File**: `.claude/hooks/post-resume.md`
- **Inventory File**: `.claude/RI_INVENTORY.md`
- **Constitution**: `.specify/memory/constitution.md` (Principle XIII)
- **User Requirement**: "need to add a hook... announcement of agents/subagent/skills"

---

## Version History

- **1.0.0** (2025-12-27): Initial ADR creation
  - Post-resume hook implementation
  - RI announcement enforcement
  - Constitutional integration (Principle XIII)

---

**Decision**: ACCEPTED
**Next Review**: After first context compaction (validate effectiveness)
