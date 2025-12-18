---
id: 0001
title: Create Phase II Question Bank Specification
stage: spec
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5
feature: phase-2-question-bank
branch: 002-question-bank
user: anjum
command: /sp.specify phase-2-question-bank
labels: ["spec", "phase-2", "question-bank", "economics-9708", "pdf-extraction", "exam-generation"]
links:
  spec: specs/phase-2-question-bank/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-2-question-bank/spec.md
tests:
  - None (spec creation only)
---

## Prompt

User request: "resume"

Context: User mandated strict SpecKitPlus methodology compliance after identifying 3 critical violations in Phase I:
1. Monolithic CLAUDE.md file (936 lines) - corrected to hierarchical structure
2. SpecKitPlus workflow not followed - now mandatory for all features
3. Skills created without checking official catalog - now check first

After completing methodology corrections (constitution v2.0.0, ADR 001, reorganized CLAUDE.md), user instructed to continue with Phase II using correct workflow: /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement

This is the first step in Phase II development: creating comprehensive feature specification for Question Bank & Exam Generation.

## Response snapshot

Created comprehensive Phase II specification (`specs/phase-2-question-bank/spec.md`) following SpecKitPlus template with:

**7 Prioritized User Stories** (independently testable):
1. **P1**: Manual Question Upload & Storage - Upload Cambridge PDFs, extract questions, store in database
2. **P2**: Question Bank Search & Filtering - Search by subject, topic, difficulty, year
3. **P1**: Cambridge Filename Parsing - Parse standardized Cambridge PDF filenames (9708_s22_qp_31.pdf)
4. **P1**: PDF Question Extraction (Economics 9708) - Extract individual questions with marks
5. **P2**: Mark Scheme Extraction & Matching - Parse mark schemes and match to questions
6. **P3**: Intelligent Exam Generation - Generate custom exams with syllabus/difficulty criteria
7. **P3**: Syllabus Point Tagging - Tag questions with Cambridge syllabus codes

**Functional Requirements**: 29 FRs covering PDF processing, question bank management, exam generation, syllabus management, mark scheme matching, API endpoints, error handling

**Non-Functional Requirements**: 13 NFRs covering performance, scalability, accuracy, data quality, security, observability

**Key Entities**: Question, MarkingScheme (JSONB), Exam, SyllabusPoint, PDFExtractionLog

**Success Criteria**: 8 measurable outcomes including >95% extraction accuracy, <5% manual correction rate, 100% mark scheme match rate, >90% valid exam generation

**Technical Constraints**: Python 3.12+, FastAPI, SQLModel, PostgreSQL 16, pdfplumber, Economics 9708 MVP subject only

**Edge Cases**: Non-standard PDF formatting, diagram handling, duplicate questions, mark scheme ambiguities, bulk uploads, syllabus updates

**Clarifications Needed**: 4 user clarifications identified for diagram handling, difficulty calculation, syllabus seeding, exam generation constraints

**Deliverables Checklist**: Code (8 files), database (4 tables), testing (5 test suites), data (100+ questions), documentation (4 docs), quality gates

**Out of Scope**: AI marking (Phase III), automated syllabus crawling, multi-subject support, OCR, AI tagging, web UI, bulk uploads

## Outcome

- ✅ Impact: Comprehensive Phase II specification created following SpecKitPlus methodology strictly. Spec defines all requirements for building question bank system with Economics 9708 as MVP subject. 7 user stories prioritized and independently testable. Unblocks /sp.clarify and /sp.plan next steps.

- 🧪 Tests: No tests written yet (spec stage). Test requirements defined in deliverables checklist: unit tests for filename parsing, question extraction, integration tests for API endpoints, >80% coverage target.

- 📁 Files: Created `specs/phase-2-question-bank/spec.md` (comprehensive 500+ line specification)

- 🔁 Next prompts:
  1. Run `/sp.clarify` to identify underspecified areas and edge cases
  2. After clarification, run `/sp.plan` to create architecture and design decisions
  3. After plan, run `/sp.tasks` to generate atomic tasks with test cases
  4. Finally run `/sp.implement` to execute tasks

- 🧠 Reflection: This is the FIRST time in the project we're following strict SpecKitPlus workflow from the start (Phase I was corrected retroactively). Spec is comprehensive with clear priorities (P1/P2/P3), independently testable user stories, and measurable success criteria. Economics 9708 chosen as MVP subject (transferable patterns to other subjects). Identified 4 clarifications needed - will address in /sp.clarify step.

## Evaluation notes (flywheel)

- Failure modes observed: None. Spec creation successful on first attempt following template.

- Graders run and results (PASS/FAIL): Not applicable (spec stage, no code to grade)

- Prompt variant (if applicable): Standard /sp.specify workflow as defined in `.claude/commands/sp.specify.md`

- Next experiment (smallest change to try): Execute `/sp.clarify` to validate spec completeness and identify missing requirements before moving to architecture planning. This is the first time using /sp.clarify in the project - will test if it surfaces additional edge cases beyond the 7 already identified.
