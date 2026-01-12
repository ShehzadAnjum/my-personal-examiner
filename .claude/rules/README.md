# Claude Rules Directory

This directory contains modular rules that guide Claude's behavior on this project.

## Rules Index

| Rule | Priority | Purpose |
|------|----------|---------|
| `multi-tenant-security.md` | CRITICAL | Every query must have student_id filter |
| `cambridge-accuracy.md` | CRITICAL | Content must match Cambridge syllabi exactly |
| `marking-standards.md` | CRITICAL | PhD-level marking, ≥85% accuracy |
| `spec-driven-development.md` | HIGH | No code before spec approval |
| `testing-requirements.md` | HIGH | ≥80% test coverage required |
| `ri-announcement.md` | MEDIUM | Announce agent/skill/subagent usage |

## Priority Levels

- **CRITICAL**: Violation risks student outcomes or security
- **HIGH**: Violation causes significant quality/process issues
- **MEDIUM**: Violation reduces transparency or efficiency

## Adding New Rules

1. Create `<rule-name>.md` in this directory
2. Use the template format (Priority, Enforcement, Rule Statement)
3. Include examples of correct and incorrect behavior
4. Reference relevant skills where applicable
5. Update this README with the new rule

## Relationship to Constitution

Rules are implementations of constitutional principles:
- `multi-tenant-security.md` → Principle V (Multi-Tenant Isolation Sacred)
- `cambridge-accuracy.md` → Principle I (Subject Accuracy Non-Negotiable)
- `marking-standards.md` → Principle II (A* Standard Marking Always)
- `spec-driven-development.md` → Principle IV (Spec-Driven Development)
- `testing-requirements.md` → Principle VII (Phase Boundaries Hard Gates)
- `ri-announcement.md` → Principle XIII (RI Announcement Mandatory)

---

**Last Updated**: 2026-01-05
