---
id: 002
title: academic-level-hierarchy-plan
stage: plan
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: 008-academic-level-hierarchy
branch: 008-academic-level-hierarchy
user: anjum
command: /sp.plan
labels: ["architecture", "database-design", "migration", "hierarchy"]
links:
  spec: specs/008-academic-level-hierarchy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-academic-level-hierarchy/plan.md
  - specs/008-academic-level-hierarchy/research.md
  - specs/008-academic-level-hierarchy/data-model.md
  - specs/008-academic-level-hierarchy/quickstart.md
  - specs/008-academic-level-hierarchy/contracts/openapi.yaml
tests:
  - N/A (planning phase)
---

## Prompt

Execute the implementation planning workflow for the Academic Level Hierarchy feature using the plan template to generate design artifacts.

## Response snapshot

Created comprehensive implementation plan for Academic Level Hierarchy:

**Phase 0 - Research (research.md)**:
- Decision: Adjacency list pattern for hierarchical data (simple FKs between levels)
- Decision: RESTRICT on delete (prevent cascade, require explicit cleanup)
- Decision: Two-phase migration with preserved rollback capability
- Decision: URL params + React Context for wizard state management

**Phase 1 - Data Model (data-model.md)**:
- NEW: AcademicLevel entity (name, code, exam_board, description)
- MODIFIED: Subject entity (removed level/exam_board/code, added academic_level_id FK)
- NEW: Syllabus entity (code, year_range, version, subject_id FK)
- MODIFIED: SyllabusPoint (changed subject_id FK to syllabus_id FK)

**API Contracts (contracts/openapi.yaml)**:
- 9 new endpoints for CRUD operations on academic levels, subjects, syllabi
- Hierarchy tree endpoint for full structure
- Standard REST patterns with proper error handling

**Quick Start Guide (quickstart.md)**:
- Migration commands
- API testing examples
- Admin setup flow
- Common issues and solutions

**Constitution Check**: All 7 relevant principles PASSED

## Outcome

- Impact: High - Architectural foundation enabling multi-qualification support
- Tests: N/A (planning phase)
- Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, openapi.yaml)
- Next prompts: /sp.tasks to generate implementation task list
- Reflection: Plan provides clear migration strategy for existing data while enabling extensibility

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generated cleanly following template
- Graders run and results (PASS/FAIL): Constitution Check PASS (7/7 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to tasks generation
