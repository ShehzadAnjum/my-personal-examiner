# Skills Directory - Reusable Knowledge Blocks

## Overview
Skills are reusable knowledge blocks that capture common patterns, best practices, and procedural knowledge. Each skill is a self-contained markdown document that can be referenced by AI agents or developers working on the project.

## Skill Categories

### Development Tools
- **port-management.md** - Kill stuck ports (3000-3002, 8000), handle IPv4/IPv6
- **uv-package-management.md** - Python dependency management with UV
- **alembic-migration-creation.md** - Database migration patterns

### Backend Patterns
- **fastapi-route-implementation/** - REST API endpoint patterns
- **sqlmodel-database-schema-design/** - Database modeling with SQLModel
- **multi-tenant-query-pattern.md** - Student-scoped query patterns
- **pydantic-schema-validation.md** - Request/response validation
- **bcrypt-password-hashing.md** - Password security patterns
- **pytest-testing-patterns.md** - Unit/integration testing

### Frontend Patterns
- **shadcn-ui-components/** - UI component library usage
- **phd-pedagogy/** - Educational interface design

### AI Integration
- **anthropic-api-patterns.md** - Claude API best practices
- **confidence-scoring.md** - Student confidence tracking
- **supermemo2-scheduling.md** - Spaced repetition algorithms
- **contextual-interleaving.md** - Learning optimization

### Domain Knowledge
- **cambridge-exam-patterns.md** - Cambridge A-Level exam structure
- **subject-economics-9708.md** - Economics 9708 syllabus
- **a-star-grading-rubrics.md** - A* grading criteria

### Deployment
- **vercel-fastapi-deployment.md** - Production deployment patterns

## How to Use Skills

### For AI Agents
When you encounter a task that matches a skill domain, reference the skill:

```
📢 ANNOUNCING: Using Skill: port-management
```

Then follow the patterns and commands documented in the skill.

### For Developers
Skills serve as quick reference documentation:

```bash
# Find a skill
ls .claude/skills/

# Read a skill
cat .claude/skills/port-management.md

# Use a skill's commands
./scripts/kill-ports.sh  # From port-management skill
```

### For New Team Members
Read skills in order of your work area:

**Backend Developer Path:**
1. uv-package-management.md
2. alembic-migration-creation.md
3. sqlmodel-database-schema-design/
4. fastapi-route-implementation/
5. multi-tenant-query-pattern.md
6. pytest-testing-patterns.md

**Frontend Developer Path:**
1. shadcn-ui-components/
2. phd-pedagogy/
3. anthropic-api-patterns.md

**DevOps/Infrastructure:**
1. port-management.md
2. vercel-fastapi-deployment.md

## Creating New Skills

### Skill Template
```markdown
# Skill: [Name]

**Type**: [Development Tools | Backend | Frontend | AI | Domain | Deployment]
**Created**: YYYY-MM-DD
**Domain**: [Brief domain description]
**Parent Agent**: [Agent name or "General"]

## Overview
[1-2 sentence description of what this skill covers]

## When to Use
[Scenarios where this skill applies]

## Quick Commands
[Most common commands/patterns]

## Technical Details
[In-depth explanation]

## Troubleshooting
[Common issues and solutions]

## Lessons Learned
[Project-specific insights]

## Related Skills
[Links to other skills]

**Version**: X.Y.Z | **Last Updated**: YYYY-MM-DD
```

### Naming Conventions
- Use kebab-case: `skill-name.md`
- Be specific: `port-management.md` not `utils.md`
- Group related skills in subdirectories for complex topics

### When to Create a Skill
- **DO**: Reusable patterns used >3 times
- **DO**: Complex procedures that need documentation
- **DO**: Domain knowledge that's project-specific
- **DON'T**: One-off solutions
- **DON'T**: Standard library documentation (link instead)

## Skill Lifecycle

### Version Updates
- **Patch (X.Y.Z)**: Typo fixes, clarifications
- **Minor (X.Y.0)**: New sections, additional commands
- **Major (X.0.0)**: Breaking changes, complete rewrites

### Deprecation
Mark outdated skills with:
```markdown
**Status**: DEPRECATED - Use [new-skill.md] instead
```

### Archival
Move deprecated skills to `.claude/skills/archived/`

## Discovery Mechanisms

### 1. Grep Search
```bash
# Find skills by keyword
grep -r "Next.js" .claude/skills/

# Find skills by type
grep "^**Type**: Development Tools" .claude/skills/*.md
```

### 2. Skills Index (This File)
Browse this README for categorized skill list

### 3. Agent Announcements
Agents announce skill usage in conversation:
```
📢 ANNOUNCING: Using Skill: port-management
```

### 4. Related Skills Links
Each skill links to related skills at bottom

## Maintenance

### Review Schedule
- **Monthly**: Update version numbers and timestamps
- **Quarterly**: Archive deprecated skills
- **After major feature**: Add new skills or update existing

### Quality Standards
- ✅ All commands must be tested
- ✅ Examples must be real project examples
- ✅ Lessons Learned section must have ≥2 insights
- ✅ Related Skills must link to ≥1 other skill
- ✅ Version and Last Updated must be current

## Contributing

### Adding a Skill
1. Create skill file following template
2. Add to this README's category index
3. Link from related skills
4. Test all commands
5. Commit with message: `docs(skills): add [skill-name]`

### Updating a Skill
1. Edit skill file
2. Update version number
3. Update Last Updated timestamp
4. Document changes in commit message
5. Commit with message: `docs(skills): update [skill-name] - [change summary]`

---

**Total Skills**: 21 (15 files + 6 directories)
**Last Updated**: 2025-12-24
**Maintainer**: AI Agents + Development Team
