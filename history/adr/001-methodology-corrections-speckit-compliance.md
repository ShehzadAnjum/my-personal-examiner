# ADR 001: Methodology Corrections - SpecKitPlus Strict Compliance

**Status**: Accepted
**Date**: 2025-12-18
**Decision Makers**: User (Project Owner), Claude Sonnet 4.5 (AI Assistant)
**Consulted**: Official SpecKitPlus documentation, Anthropic Skills catalog
**Informed**: Future development team, AI session continuations

---

## Context

During Phase I development (Dec 16-18, 2025), the user identified **3 critical methodology violations** that required immediate correction:

### Problem 1: Monolithic CLAUDE.md File
- **Issue**: Single 936-line CLAUDE.md at project root
- **Impact**: Difficult to navigate, maintenance burden, scalability issues
- **User Requirement**: Hierarchical CLAUDE.md structure (root + phase/feature subdirectories)

### Problem 2: SpecKitPlus Workflow Not Followed
- **Issue**: Phase I implemented without `/sp.specify` → `/sp.plan` → `/sp.tasks` workflow
- **Impact**: No spec documents, undocumented decisions, difficult handoff
- **Correct Sequence**: Must follow `/sp.constitution` → `/sp.specify` → `/sp.clarify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`

### Problem 3: Skills Created Without Checking Official Catalog
- **Issue**: Created 13 custom skills without first checking Anthropic's official skills
- **Impact**: Potential duplication, missed opportunities to reuse maintained skills
- **Official Catalog**: 16 skills available (docx, pdf, xlsx, web-artifacts-builder, etc.)

---

## Decision

We are implementing **3 structural changes** and adding **3 new constitutional principles** to enforce methodology compliance:

### Change 1: CLAUDE.md Reorganization

**Before**:
```
/CLAUDE.md (936 lines - monolithic)
```

**After**:
```
/CLAUDE.md (228 lines - project-wide only)
/specs/phase-1-core-infrastructure/CLAUDE.md (285 lines - Phase I-specific)
/specs/phase-2-question-bank/CLAUDE.md (to be created - Phase II-specific)
/specs/phase-N-*/CLAUDE.md (per phase)
/specs/features/<feature>/CLAUDE.md (if needed)
```

**Rule**: No CLAUDE.md file shall exceed 300 lines.

### Change 2: SpecKitPlus Workflow Documentation

**Mandatory Sequence** (enforced for all features):
```
1. /sp.specify <feature>    → Create specs/<feature>/spec.md
2. /sp.clarify              → Identify edge cases (if needed)
3. /sp.plan                 → Create specs/<feature>/plan.md
4. /sp.tasks                → Create specs/<feature>/tasks.md
5. /sp.implement            → Execute tasks from tasks.md
6. /sp.adr <title>          → Document architectural decisions
7. /sp.phr                  → Record prompt history
8. /sp.git.commit_pr        → Commit with constitutional compliance
```

**Enforcement**: Git hook checks for spec.md existence before code commits.

### Change 3: Official Skills Catalog Process

**Process** (mandatory for all skills):
```
1. Identify task requiring skill
2. Check official catalog: https://github.com/anthropics/skills
3. If official skill exists → USE IT
4. If no official skill → Document why, then create custom
5. Add rationale in custom skill frontmatter
```

**16 Official Skills Identified**:
- Document: docx, pdf, pptx, xlsx
- Development: web-artifacts-builder, webapp-testing, mcp-builder
- Creative: algorithmic-art, brand-guidelines, canvas-design
- Workflow: doc-coauthoring, skill-creator, internal-comms
- Others: frontend-design, slack-gif-creator, theme-factory

---

## Constitutional Amendments

Added **3 new principles** to constitution (v1.0.0 → v2.0.0):

### Principle IX: SpecKitPlus Workflow Compliance
- ALL features MUST follow /sp.* command sequence
- NEVER write code before spec exists
- ALWAYS create PHR and ADR for significant work
- Enforcement: Git hooks, CI/CD checks, AI refusal

### Principle X: Official Skills Priority
- CHECK Anthropic catalog BEFORE creating custom skills
- USE official skills when available
- DOCUMENT why official skill wasn't suitable
- Enforcement: Pre-skill-creation prompts, monthly audits

### Principle XI: CLAUDE.md Hierarchy
- NO single CLAUDE.md file exceeds 300 lines
- USE hierarchical structure (root + phase/feature)
- SPLIT early if approaching 250 lines
- Enforcement: Pre-commit line count checks, CI/CD failures

---

## Consequences

### Positive

1. **Scalable Documentation**
   - Phase-specific CLAUDE.md files improve discoverability
   - New team members read only relevant phase instructions
   - Parallel development enabled (different phases, different docs)

2. **Traceability**
   - SpecKitPlus workflow creates spec/plan/tasks for all features
   - PHR records all significant user interactions
   - ADR documents all architectural decisions
   - Future AI sessions have full context

3. **Reusability**
   - Official skills catalog checked first prevents duplication
   - Custom skills focused on domain-specific needs
   - Anthropic-maintained skills get updates and bug fixes

4. **Quality Control**
   - Spec-driven development prevents scope creep
   - Phase gates enforce completion before advancement
   - Constitutional compliance automated where possible

### Negative

1. **Overhead**
   - Must run `/sp.*` commands for all features (adds 15-30 min per feature)
   - Must check official skills catalog (adds 5-10 min per skill)
   - Must maintain multiple CLAUDE.md files (ongoing maintenance)

2. **Learning Curve**
   - Team must learn SpecKitPlus workflow
   - Must understand constitutional principles
   - Requires discipline to follow process

3. **Initial Migration Cost**
   - Reorganizing CLAUDE.md took 2 hours
   - Creating methodology corrections doc took 1 hour
   - Updating constitution took 1 hour

### Mitigation Strategies

1. **Reduce Overhead**:
   - Create templates for spec/plan/tasks (once, reuse many times)
   - Bookmark official skills catalog for quick reference
   - Use AI to generate initial CLAUDE.md drafts

2. **Ease Learning Curve**:
   - Document workflow in docs/METHODOLOGY_CORRECTIONS.md
   - Create checklists for SpecKitPlus sequence
   - Add examples in Phase I CLAUDE.md

3. **Justify Migration Cost**:
   - One-time investment prevents future chaos
   - Scalability issues would compound over time
   - Early correction cheaper than late refactoring

---

## Alternatives Considered

### Alternative 1: Keep Monolithic CLAUDE.md
- **Pros**: Simpler structure, everything in one place
- **Cons**: Doesn't scale, 936 lines already too large
- **Rejected**: User requirement for hierarchy

### Alternative 2: Optional SpecKitPlus Workflow
- **Pros**: Faster development, less overhead
- **Cons**: Undocumented decisions, difficult handoff, scope creep
- **Rejected**: Quality over speed (constitutional principle)

### Alternative 3: Skip Official Skills Check
- **Pros**: Faster skill creation
- **Cons**: Duplication, missed reuse opportunities
- **Rejected**: Prevent reinventing the wheel

---

## References

### Official Documentation
- [SpecKitPlus Hands-On Guide](https://ai-native.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
- [CLAUDE.md Context Files](https://ai-native.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows/claude-md-context-files)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)

### Internal Documentation
- `docs/METHODOLOGY_CORRECTIONS.md` - Comprehensive corrections document
- `.specify/memory/constitution.md` v2.0.0 - Updated constitution
- `CLAUDE.md` - Root instructions (228 lines)
- `specs/phase-1-core-infrastructure/CLAUDE.md` - Phase I instructions (285 lines)

### Related ADRs
- None (this is ADR 001)

### Related PRs/Commits
- `ea208d2` - docs: methodology corrections - SpecKitPlus strict compliance
- `15f387c` - feat: complete Phase I - Core Infrastructure & Authentication
- `8b5a299` - docs: create 9 additional recurring-use skills (13 total)

---

## Implementation Status

### Completed ✅
1. Root CLAUDE.md reorganized (936 → 228 lines)
2. Phase I CLAUDE.md created (285 lines)
3. Methodology corrections documented (docs/METHODOLOGY_CORRECTIONS.md)
4. 3 new constitutional principles added (IX, X, XI)
5. Constitution version bumped (v1.0.0 → v2.0.0)
6. All 13 custom skills validated against official catalog

### In Progress ⏳
1. Phase II CLAUDE.md (to be created when starting Phase II)
2. Git hooks for CLAUDE.md line count checks
3. CI/CD automation for spec existence checks

### Not Started 📋
1. Pre-skill-creation prompts (requires hook implementation)
2. Monthly audits automation
3. Quarterly CLAUDE.md pruning process

---

## Review Schedule

- **Quarterly**: Review CLAUDE.md hierarchy (prune obsolete files)
- **Monthly**: Audit custom skills (check for official alternatives)
- **After each phase**: Update phase-specific CLAUDE.md with lessons learned
- **After Phase V**: Comprehensive methodology review

---

**ADR Author**: Claude Sonnet 4.5 (AI Assistant)
**ADR Approver**: User (Project Owner)
**Next Review**: After Phase II completion (2025-12-20 estimated)
