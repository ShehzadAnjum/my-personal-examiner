# ADR 002: AI Teaching System - 6 Core Roles Architecture

**Status**: Accepted
**Date**: 2025-12-20
**Decision Makers**: Anjum (Project Owner), Claude Sonnet 4.5 (System Architect)
**Consulted**: Anthropic Skills Repository, Educational AI research
**Informed**: All development agents, future contributors

---

## Context

### Original Plan (Dec 16, 2025)
Initial architecture focused on **3 core capabilities**:
1. Question bank management (PDF extraction, storage)
2. Exam generation (custom paper creation)
3. AI marking (Economics 9708 marking engine)

**Gap Identified (Dec 20, 2025)**: User clarified the **true goal** is a **comprehensive, fully automated learning system** that replaces human teachers, tutors, examiners, markers, reviewers, and planners. The original plan was too narrow.

### Comprehensive Goal (User's Requirements)

Build a personalized, fully automated A-Level learning system with **6 distinct AI roles**:

1. **Teacher** - Explains concepts, teaches topics, delivers curriculum content
2. **Coaching Teacher** - Helps with difficult concepts, provides one-on-one tutoring
3. **Examiner** - Creates Cambridge-standard test papers for A* preparation
4. **Paper Checker** - Strict marking per Cambridge mark schemes
5. **Reviewer/Helper** - Identifies weak areas, produces A* model answers
6. **Planner** - Creates n-day study plans to cover entire syllabus

**Extensibility Requirements**:
- Reusable for ANY subject (initially: Economics 9708, Accounting 9706, Math 9709, English GP 8021)
- Later extensible to ANY grade level (GCSE, IB, AP, etc.)
- Pluggable architecture for rapid subject onboarding

---

## Decision

We are expanding the architecture from **3 capabilities** to **10 specialized agents** with **6 user-facing core roles**:

### Architecture: 10 Agents (6 Core + 4 Infrastructure)

#### **6 Core Role Agents** (User-Facing):

**1. Teacher Agent** (NEW)
- **Purpose**: Content delivery, concept explanations, topic teaching
- **Input**: Syllabus topic, student's current knowledge level
- **Output**: Clear explanations with examples, diagrams, analogies
- **Skills**: phd-pedagogy, subject-specific (e.g., subject-economics-9708)
- **LLM**: Claude Sonnet 4.5 (pedagogical reasoning)

**2. Coach Agent** (NEW)
- **Purpose**: Personalized tutoring, difficult concept scaffolding, adaptive learning
- **Input**: Student's struggle area, learning style preferences
- **Output**: Tailored explanations, practice problems, concept clarification
- **Skills**: phd-pedagogy, analogy generation, interactive quizzing
- **LLM**: Claude Sonnet 4.5 (empathy, adaptation)

**3. Examiner Agent** (ENHANCED from Assessment Engine)
- **Purpose**: Cambridge-standard exam paper creation
- **Input**: Subject, paper type, difficulty target, syllabus coverage requirements
- **Output**: Full exam papers (MCQ, data response, essays)
- **Skills**: cambridge-exam-patterns, subject-specific
- **LLM**: Claude Sonnet 4.5 (pattern matching, difficulty calibration)

**4. Marker Agent** (ENHANCED from Marking Engines)
- **Purpose**: Strict Cambridge-compliant marking
- **Input**: Student answer, mark scheme, question metadata
- **Output**: Marks breakdown (AO1/AO2/AO3), criterion-by-criterion scoring
- **Skills**: a-star-grading-rubrics, subject-specific marking engines
- **LLM**: Claude Sonnet 4.5 (strict evaluation, PhD-level precision)

**5. Reviewer Agent** (ELEVATED from Feedback Generator Subagent)
- **Purpose**: Weakness identification, improvement strategies, A* model answers
- **Input**: Marked attempt, student history, syllabus coverage
- **Output**: Weakness report, improvement plan, rewritten A* answer
- **Skills**: a-star-grading-rubrics, phd-pedagogy
- **LLM**: Claude Sonnet 4.5 (diagnostic reasoning, exemplar generation)

**6. Planner Agent** (NEW)
- **Purpose**: Personalized study schedule creation (n-day plans)
- **Input**: Syllabus, exam date, student's current progress, time availability
- **Output**: Day-by-day study schedule with topics, resources, checkpoints
- **Skills**: phd-pedagogy (spaced repetition, interleaving)
- **LLM**: GPT-4 Turbo (planning, optimization)

#### **4 Infrastructure Agents** (Supporting):

7. **System Architect** - Architecture, ADRs, constitutional compliance
8. **Backend Service** - FastAPI, database, API design
9. **Frontend Web** - Next.js UI/UX, React components
10. **Testing Quality** - Test strategy, coverage, E2E testing

### Subagents Alignment (18+ Narrow Specialists)

**Teaching Domain** (6):
- Concept Explainer, Analogy Generator, Practice Problem Generator, Progress Tracker, Resource Curator, Interactive Quiz Builder

**Assessment Domain** (6):
- Question Selector, Difficulty Calibrator, Marking Engine, Feedback Generator, Answer Rewriter, Weakness Analyzer

**Planning Domain** (3):
- Schedule Optimizer, Syllabus Coverage Analyzer, Adaptive Pacer

**Infrastructure Domain** (5+):
- Cambridge Syllabus Crawler, PDF Question Extractor, Grade Calculator, Student Progress Tracker, DB Schema Migration

### Skills Architecture (13 Total)

**From Anthropic Repository** (6 - Reused):
1. pdf - PDF manipulation, text extraction
2. docx - Word document creation
3. xlsx - Excel spreadsheets, formulas
4. webapp-testing - Playwright E2E testing
5. artifacts-builder - React/Tailwind UI
6. mcp-server - MCP server creation

**Custom Education Skills** (7 - Following Anthropic Template):
7. cambridge-exam-patterns - Cambridge paper structure knowledge
8. a-star-grading-rubrics - A* marking criteria
9. phd-pedagogy - Evidence-based teaching strategies
10. subject-economics-9708 - Economics domain knowledge
11. subject-accounting-9706 - Accounting domain knowledge
12. subject-mathematics-9709 - Mathematics domain knowledge
13. subject-english-gp-8021 - English GP domain knowledge

**Rationale for Custom Skills**: No education/teaching-specific skills exist in Anthropic's repository (verified Dec 20, 2025). Custom skills created following official Agent Skills specification from https://github.com/anthropics/skills.

---

## Extensibility Strategy

### Subject Extensibility
- **Database**: Subject-agnostic schema with metadata tables
- **Marking Engines**: Pluggable Python modules per subject
- **Skills**: One subject-specific skill per subject (reusable teaching patterns)
- **Onboarding New Subject**: Create skill + marking engine + seed syllabus data

### Grade Extensibility (Future: GCSE, IB, AP)
- **Assessment Templates**: Grade-level configurable exam structures
- **Difficulty Calibration**: Grade-appropriate question selection algorithms
- **Mark Scheme Patterns**: Adaptable to different grading systems
- **UI/UX**: Age-appropriate interfaces (advanced vs. simplified)

### Language Extensibility (Future: Multilingual)
- **i18n Support**: React-intl for frontend, backend translation layer
- **Subject Content**: Localized syllabus sources
- **Feedback Language**: Student's preferred language
- **OCR Support**: Multi-language handwriting recognition (Phase VI+)

---

## Consequences

### Positive

✅ **Comprehensive Solution**: Addresses full learning lifecycle (teach → practice → test → mark → improve → plan)
✅ **Reusable Architecture**: Pluggable agents, skills, and marking engines
✅ **Scalable to Any Subject/Grade**: Metadata-driven, extensible design
✅ **Aligned with SpecKit**: Follows strict spec-driven development, constitutional principles
✅ **Leverages Anthropic Skills**: Reuses 6 official skills where applicable

### Negative

⚠️ **Increased Scope**: 6 core roles vs. original 3 capabilities
⚠️ **Longer Development Time**: More agents/skills to implement
⚠️ **LLM Cost**: Multiple agent interactions per student session

### Mitigation

1. **Phased Implementation**: Focus Phase III on Economics 9708 MVP with all 6 roles working end-to-end
2. **Reusable Patterns**: Once Economics works, replicate pattern for other subjects rapidly
3. **Cost Optimization**: Cache common explanations, batch LLM calls, use GPT-4 Mini for simpler tasks

---

## Implementation Plan

### Phase III (Current Focus)
- Implement Teacher, Coach, Planner agents for Economics 9708
- Enhance Examiner, Marker, Reviewer agents
- Create 7 custom education skills
- Build end-to-end workflow: teach → test → mark → review → plan

### Phase IV (Web UI)
- 6 role-specific interfaces (Teacher chat, Coach tutor, Exam taker, Results viewer, Improvement planner, Study scheduler)
- Unified student dashboard with progress tracking

### Phase V (Multi-Subject + CLI/MCP)
- Replicate pattern for Accounting 9706, Math 9709, English GP 8021
- CLI interface for all 6 roles
- MCP servers for external integrations

---

## Related Decisions

- **ADR-001**: SpecKitPlus Methodology Compliance
- **Constitution v2.0**: 6 Core Roles, 8 Constitutional Principles
- **PHR-001**: Comprehensive Goal Clarification Session

---

**Decision Date**: 2025-12-20
**Reviewed By**: Anjum (Project Owner)
**Next Review**: After Phase III MVP completion
