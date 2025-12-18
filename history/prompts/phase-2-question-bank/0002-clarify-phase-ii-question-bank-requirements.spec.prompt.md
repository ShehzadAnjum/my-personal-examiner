---
id: 0002
title: Clarify Phase II Question Bank Requirements
stage: spec
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5
feature: phase-2-question-bank
branch: 002-question-bank
user: anjum
command: /sp.clarify
labels: ["clarification", "spec", "phase-2", "generic-architecture", "economics-9708", "subject-bootstrap"]
links:
  spec: specs/002-question-bank/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-question-bank/spec.md
tests:
  - None (clarification stage)
---

## Prompt

User invoked `/sp.clarify` command after creating Phase II specification.

**Critical Strategic Context** (provided by user before clarification):
- System is NOT Economics-specific; it's a **generic/reusable framework** with Economics as test case
- Goal: **Auto-bootstrapping system** that can ingest any subject (inject resources → automatically builds question bank, tests, marking, progress tracking)
- Economics 9708 work should be **archived as reference template**, not discarded
- System should be **resource-agnostic** (PDFs, links, open search)

Clarification workflow executed to identify ambiguities and missing decision points in Phase II spec before planning.

## Response snapshot

**5 Critical Clarifications Identified and Resolved**:

**Q1: Subject Configuration Schema**
- **Answer**: Option C - JSONB config in subjects table + resource files
- **Impact**: Dual storage (queryable metadata in DB, complex templates as files)
- **Outcome**: `subjects.marking_config`, `subjects.extraction_patterns`, `subjects.paper_templates` (JSONB) + `backend/resources/subjects/{code}/` directory

**Q2: Resource Ingestion Pipeline**
- **Answer**: Option B - Hybrid (manual seed PDFs + AI-powered analysis)
- **Impact**: Admin uploads 10-20 past papers → AI generates config automatically
- **Outcome**: Practical MVP approach, proves automation works with Economics before full bootstrapping

**Q3: Economics-Specific Asset Archival**
- **Answer**: Option A - Dual storage (live DB + archived resources)
- **Impact**: Economics works operationally + serves as reference template
- **Outcome**: `backend/resources/subjects/9708/` with README.md, marking_config.json, extraction_patterns.yaml, paper_templates.json

**Q4: Multi-Subject Marking Engine Architecture**
- **Answer**: Combo B+C (plugin framework + AI, intelligently/efficiently/practically)
- **Impact**: Base MarkingEngine + subject-specific AI-powered plugins
- **Outcome**: Rule-based checks for objective criteria + AI for subjective evaluation, cache AI responses, fallback to rules

**Q5: Phase II Scope with Generic Architecture**
- **Answer**: Option B - Infrastructure + Economics MVP, defer full bootstrap to Phase V
- **Impact**: Prove generic architecture with Economics first, add automation later
- **Outcome**: Phase II delivers generic framework + working Economics, Phase V adds `/api/subjects/bootstrap` endpoint

**Spec Updated**:
- Added `## Clarifications` section with 5 Q&A entries
- Updated `Subject` entity with JSONB config fields
- Updated functional requirements (FR-016 to FR-021 revised)
- Added Economics 9708 Reference Archive deliverables
- Updated Out of Scope section (bootstrap deferred to Phase V)
- Added Phase III and Phase V preview sections

**Coverage Summary**:
- ✅ Functional Scope & Behavior: **Resolved** (generic architecture, Economics as test case)
- ✅ Domain & Data Model: **Resolved** (Subject config schema, plugin architecture)
- ✅ Integration & External Dependencies: **Resolved** (AI integration approach)
- ✅ Constraints & Tradeoffs: **Resolved** (Phase II scope decision)
- ✅ Terminology & Consistency: **Resolved** (generic vs Economics-specific clarified)
- ⏳ Edge Cases & Failure Handling: **Deferred** (will be addressed in /sp.plan with architecture)
- ⏳ Non-Functional Quality Attributes: **Partial** (performance targets exist, observability detailed in plan)
- ⏳ Completion Signals: **Clear** (acceptance criteria defined, Phase II gate script required)

## Outcome

- ✅ Impact: Successfully clarified **5 critical architectural decisions** that transform Phase II from Economics-specific to **generic/reusable framework**. Spec now defines clear separation: Phase II builds infrastructure + Economics MVP (manual config), Phase V adds AI-powered auto-bootstrap. Economics 9708 preserved as reference template for other subjects. Marking engine architecture (plugin + AI hybrid) defined for Phase III.

- 🧪 Tests: No tests written (clarification stage). Test requirements preserved in deliverables: unit tests for generic extraction framework, Economics config validation tests.

- 📁 Files: Updated `specs/002-question-bank/spec.md` with 5 clarifications integrated throughout (Clarifications section, Key Entities, Functional Requirements, Out of Scope, Deliverables). File grew from 523 to 568 lines with added Economics archive deliverables and Phase V preview.

- 🔁 Next prompts:
  1. Run `/sp.plan` to create architecture plan with generic extraction framework design
  2. Design Subject plugin architecture (base class + Economics9708Plugin)
  3. Design database migration for JSONB config columns
  4. Create Economics 9708 reference configuration files

- 🧠 Reflection: User's strategic clarification ("generic system, Economics as test case") **fundamentally reframed Phase II**. Without this, would have built Economics-specific solution requiring full rewrite for Math/English. Clarifications established clean architectural boundaries: generic framework (Phase II) + working Economics (Phase II) + auto-bootstrap (Phase V). Plugin + AI hybrid for marking engine is pragmatic: rules for speed/cost, AI for quality. Deferring bootstrap to Phase V is correct MVP scoping: prove architecture works before automating it.

## Evaluation notes (flywheel)

- Failure modes observed: None. User's strategic input was provided **before** clarification questions, preventing misdirection. All 5 clarifications directly addressed generic architecture needs.

- Graders run and results (PASS/FAIL): Not applicable (clarification stage, no code)

- Prompt variant (if applicable): Standard `/sp.clarify` workflow from `.claude/commands/sp.clarify.md`

- Next experiment (smallest change to try): Execute `/sp.plan` with generic architecture focus. Will test if plan captures: (1) Subject config schema implementation, (2) Generic extraction framework that reads JSONB config, (3) Plugin architecture for marking engines, (4) Economics 9708 config creation as manual task. Success metric: Plan should be **subject-agnostic** (no hard-coded Economics logic except in archive/reference files).
