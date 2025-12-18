# Methodology Corrections - SpecKitPlus Compliance

**Date**: 2025-12-18
**Status**: CRITICAL - Immediate corrections required
**Triggered By**: User feedback on constitutional non-compliance

---

## Summary of Issues

### 1. ❌ CLAUDE.md File Organization
**Current**: Single monolithic 936-line CLAUDE.md at root
**Required**: Hierarchical CLAUDE.md files (root + phase/feature subdirectories)

### 2. ❌ SpecKitPlus Sequence Not Followed
**Current**: Jumped straight to implementation without following spec workflow
**Required**: Strict adherence to `/sp.constitution` → `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` sequence

### 3. ❌ Skills Created Without Checking Official Catalog
**Current**: Created 13 custom skills without first checking Anthropic's official skills
**Required**: Check official skills FIRST, only create custom if no alternative exists

---

## Official Documentation Findings

### SpecKitPlus Command Sequence (MANDATORY)

**Source**: https://ai-native.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on

**Complete Workflow**:
1. **`/sp.constitution`** — Establish project-wide quality standards
2. **`/sp.specify`** — Convert vague ideas into clear, testable requirements
3. **`/sp.clarify`** — Identify missing constraints and edge cases iteratively
4. **`/sp.plan`** — Generate architecture and design decisions
5. **`/sp.tasks`** — Decompose work into atomic, checkpoint-driven units
6. **`/sp.implement`** — Execute tasks with AI collaboration

**Supporting Commands**:
- `/sp.adr` — Document architectural decisions
- `/sp.phr` — Record prompt history
- `/sp.analyze` — Check cross-artifact consistency
- `/sp.checklist` — Generate custom checklists
- `/sp.git.commit_pr` — Autonomous git workflows

### Official Anthropic Skills Catalog

**Source**: https://github.com/anthropics/skills

**Available Official Skills** (16 total):
1. **algorithmic-art** - Algorithmic art creation
2. **brand-guidelines** - Brand identity and guidelines
3. **canvas-design** - Canvas-based design work
4. **doc-coauthoring** - Collaborative document writing
5. **docx** - Word document creation & editing (source-available)
6. **frontend-design** - Frontend UI/UX design
7. **internal-comms** - Internal communications
8. **mcp-builder** - MCP server development
9. **pdf** - PDF creation & editing (source-available)
10. **pptx** - PowerPoint creation & editing (source-available)
11. **skill-creator** - Skill creation guidance
12. **slack-gif-creator** - Slack GIF creation
13. **theme-factory** - Theme generation
14. **web-artifacts-builder** - Web artifacts & frontend components
15. **webapp-testing** - Playwright-based web app testing
16. **xlsx** - Excel spreadsheet creation & editing (source-available)

**Skills We Should Have Used**:
- ✅ `web-artifacts-builder` (for frontend work - Phase IV)
- ✅ `xlsx` (for analytics, grading exports)
- ✅ `docx` (for exam papers, feedback docs)
- ✅ `pdf` (for PDF reading/analysis)
- ✅ `webapp-testing` (for E2E testing)
- ✅ `mcp-builder` (for custom MCP servers)

**Skills We Created That May Be Redundant**:
- ❓ Check if our custom skills overlap with official skills
- ❓ Consolidate or remove redundant skills

### CLAUDE.md File Organization

**Source**: https://ai-native.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows/claude-md-context-files

**Official Recommendation**: One CLAUDE.md at root
**User Requirement**: Multiple CLAUDE.md files (root + subdirectories)

**Interpretation**: User's approach is more scalable:
- Root CLAUDE.md: Project-wide instructions only
- Phase-specific CLAUDE.md: Phase I, Phase II, etc.
- Feature-specific CLAUDE.md: Per-feature instructions

This prevents monolithic files and improves maintainability.

---

## Corrective Actions Required

### Action 1: Reorganize CLAUDE.md Structure

**New Structure**:
```
/CLAUDE.md                                     # Project-wide only (technology stack, constitution reference, structure)
/specs/phase-1-core-infrastructure/CLAUDE.md  # Phase I specific (auth, database, testing)
/specs/phase-2-question-bank/CLAUDE.md        # Phase II specific (PDF extraction, question bank)
/specs/phase-3-ai-marking/CLAUDE.md           # Phase III specific (marking engines, feedback)
/specs/phase-4-web-ui/CLAUDE.md               # Phase IV specific (Next.js, UI components)
/specs/phase-5-advanced-features/CLAUDE.md    # Phase V specific (CLI, MCP servers)
/specs/features/student-auth/CLAUDE.md        # Feature-specific if needed
```

**Root CLAUDE.md Should Contain**:
- Project overview (1-2 paragraphs)
- Technology stack (locked choices)
- Constitutional reference (link to .specify/memory/constitution.md)
- Directory structure
- SpecKitPlus workflow reminder
- Session handoff protocol
- Where to find phase/feature-specific instructions

**Phase-Specific CLAUDE.md Should Contain**:
- Phase objectives and deliverables
- Phase-specific patterns and conventions
- Phase-specific testing requirements
- Phase-specific agent/subagent/skill usage
- Phase-specific security considerations
- Phase gate requirements

### Action 2: Update Constitution

**Add to Constitution**:

**Principle IX: SpecKitPlus Workflow Compliance** (NEW)
- MUST follow command sequence: /sp.constitution → /sp.specify → /sp.plan → /sp.tasks → /sp.implement
- NEVER write code before spec exists
- NEVER skip clarify/plan/tasks steps
- ALWAYS use /sp.adr for architectural decisions
- ALWAYS use /sp.phr for prompt history recording

**Principle X: Official Skills Priority** (NEW)
- BEFORE creating any custom skill, check Anthropic's official skills catalog
- ONLY create custom skills if no official alternative exists
- Document why official skill wasn't suitable in skill frontmatter

**Principle XI: CLAUDE.md Hierarchy** (NEW)
- Root CLAUDE.md: Project-wide instructions only
- Phase CLAUDE.md: Phase-specific instructions
- Feature CLAUDE.md: Feature-specific instructions (if needed)
- NEVER let CLAUDE.md exceed 300 lines (split into subdirectories)

### Action 3: Review Existing Skills

**Check Against Official Catalog**:
1. `vercel-fastapi-deployment` - No official equivalent ✅ KEEP
2. `sqlmodel-database-schema-design` - No official equivalent ✅ KEEP
3. `fastapi-route-implementation` - No official equivalent ✅ KEEP
4. `multi-tenant-query-pattern` - No official equivalent ✅ KEEP
5. `pydantic-schema-validation` - No official equivalent ✅ KEEP
6. `bcrypt-password-hashing` - No official equivalent ✅ KEEP
7. `subject-economics-9708` - No official equivalent ✅ KEEP
8. `cambridge-exam-patterns` - No official equivalent ✅ KEEP
9. `a-star-grading-rubrics` - No official equivalent ✅ KEEP
10. `phd-pedagogy` - No official equivalent ✅ KEEP
11. `uv-package-management` - No official equivalent ✅ KEEP
12. `alembic-migration-creation` - No official equivalent ✅ KEEP
13. `pytest-testing-patterns` - Compare with `webapp-testing` ❓ REVIEW

**Action**: All skills appear domain-specific and not covered by official catalog. All kept.

### Action 4: Create Phase II Workflow (CORRECT)

**For Phase II (Question Bank), MUST Follow**:
1. `/sp.specify phase-2-question-bank` — Create spec.md with requirements
2. `/sp.clarify` — Identify edge cases (PDF formats, question numbering, mark scheme matching)
3. `/sp.plan` — Architecture for PDF extraction, question storage, exam generation
4. `/sp.tasks` — Atomic tasks with test cases
5. `/sp.implement` — Execute tasks from tasks.md
6. `/sp.adr` — Document decisions (PDF library choice, question schema design)
7. `/sp.git.commit_pr` — Commit with constitutional compliance

**Phase II-Specific CLAUDE.md** (to be created):
- PDF extraction patterns (using official `pdf` skill)
- Cambridge filename parsing
- Question schema design
- Mark scheme matching
- Exam generation algorithms

### Action 5: Document Corrections in ADR

**Create**: `history/adr/004-methodology-corrections-speckit-compliance.md`

**Content**:
- Context: User feedback on non-compliance
- Decision: Reorganize CLAUDE.md, enforce SpecKitPlus workflow, prioritize official skills
- Consequences: More structured approach, better maintainability, reduced duplication
- Status: Accepted
- Date: 2025-12-18

---

## Implementation Plan

**Priority 1: Immediate** (Today)
1. ✅ Fetch official documentation (DONE)
2. ✅ Check official skills catalog (DONE)
3. ⚠️ Create this document (IN PROGRESS)
4. ⏳ Reorganize CLAUDE.md structure
5. ⏳ Update constitution with 3 new principles
6. ⏳ Create ADR for methodology corrections
7. ⏳ Commit corrections

**Priority 2: Before Phase II** (Tomorrow)
1. Create Phase I CLAUDE.md (extract from root)
2. Create Phase II CLAUDE.md (new)
3. Test SpecKitPlus workflow with /sp.specify for Phase II
4. Verify all slash commands work correctly

**Priority 3: Ongoing** (Throughout Project)
1. Always check official skills before creating custom
2. Always follow SpecKitPlus command sequence
3. Keep CLAUDE.md files under 300 lines each
4. Update phase CLAUDE.md as we learn

---

## Lessons Learned

### What We Did Wrong
1. Created monolithic CLAUDE.md (936 lines)
2. Skipped /sp.specify → /sp.plan → /sp.tasks workflow
3. Created skills without checking official catalog first
4. Implemented Phase I without proper spec documents

### What We Did Right
1. Created constitution early (good foundation)
2. Established reusable intelligence structure
3. Achieved 82% test coverage
4. Created phase gate validation script
5. Multi-tenant security enforced

### How to Prevent Recurrence
1. **Checkpoint**: Before any feature, run `/sp.specify` (no exceptions)
2. **Checkpoint**: Before creating any skill, search official catalog
3. **Checkpoint**: Monthly CLAUDE.md size check (split if >300 lines)
4. **Checkpoint**: Constitution review before each phase

---

## Next Steps

**Immediate**:
1. Complete reorganization of CLAUDE.md structure
2. Update constitution with new principles
3. Create ADR documenting corrections
4. Commit all changes

**Phase II Preparation**:
1. Run `/sp.specify phase-2-question-bank`
2. Use `/sp.clarify` to identify edge cases
3. Run `/sp.plan` to create architecture
4. Run `/sp.tasks` to generate atomic tasks
5. Use `/sp.implement` to execute (not manual implementation)

**References**:
- [SpecKitPlus Hands-On Guide](https://ai-native.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
- [CLAUDE.md Context Files](https://ai-native.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows/claude-md-context-files)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

---

**Status**: Documentation complete, ready for reorganization implementation
**Next**: Execute Action 4 (Reorganize CLAUDE.md structure)
