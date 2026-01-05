---
id: 001
title: academic-level-hierarchy-spec
stage: spec
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: 008-academic-level-hierarchy
branch: 008-academic-level-hierarchy
user: anjum
command: /sp.specify
labels: ["architecture", "hierarchy", "database-design", "admin-setup"]
links:
  spec: specs/008-academic-level-hierarchy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-academic-level-hierarchy/spec.md
  - specs/008-academic-level-hierarchy/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

Restructure the system to support a proper hierarchy: Academic Level → Subject → Syllabus. The top level "academic_level" represents qualification types like A-Level, O-Level, IGCSE, IB. Subjects belong to an academic level. Syllabi (with codes like 9708) belong to subjects. This makes the system generic and not Cambridge-specific.

User clarified: "make the top level 'academic level' plan this architectural change properly with spec/plan/tasks"

## Response snapshot

Created comprehensive feature specification for Academic Level Hierarchy:

**Problem Statement**: Current system has flat structure with hardcoded "Economics 9708" mixing qualification level, subject, and syllabus code in one entity. Needs three-tier hierarchy for extensibility.

**Key Entities Defined**:
- Academic Level: Qualification types (A-Level, O-Level, IGCSE, IB) with name, code, exam_board
- Subject: Subject areas (Economics, Mathematics) belonging to one academic level
- Syllabus: Specific syllabus version (9708 for 2023-2025) with code, year_range, version

**User Stories** (5 total):
- P1: Admin creates academic levels
- P1: Admin creates subjects under academic level
- P1: Admin uploads syllabus for subject
- P2: Student navigates hierarchy
- P3: Admin manages hierarchy (edit/delete)

**Functional Requirements** (10 total): FR-001 through FR-010 covering CRUD, uniqueness constraints, UI updates, backward compatibility

**Success Criteria** (6 total): Measurable outcomes including setup time, reference cleanup, empty state handling, data preservation

## Outcome

- Impact: High - Architectural foundation for multi-qualification support
- Tests: N/A (specification phase)
- Files: 2 files created (spec.md, requirements.md checklist)
- Next prompts: /sp.plan to create implementation plan
- Reflection: Spec properly defers implementation details while capturing complete business requirements

## Evaluation notes (flywheel)

- Failure modes observed: None - spec generated cleanly from user requirements
- Graders run and results (PASS/FAIL): Checklist validation PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase
