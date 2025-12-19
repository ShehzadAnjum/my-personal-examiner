# My Personal Examiner - Project Constitution

**Last Updated**: 2025-12-20
**Version**: 2.0
**Status**: Active

---

## MISSION STATEMENT

Build a **fully automated, PhD-level A-Level learning system** that delivers personalized, comprehensive education through 6 core AI roles: Teacher, Coach, Examiner, Marker, Reviewer, and Planner. The system must produce consistent **A* standard outcomes** through strict adherence to Cambridge International examination standards.

**Ultimate Goal**: Create a reusable, extensible architecture that can be rapidly adapted to any subject (initially A-Levels: Economics 9708, Accounting 9706, Mathematics 9709, English GP 8021) and later extended to any grade level worldwide.

---

## THE 6 CORE ROLES (Non-Negotiable)

### 1. **TEACHER** - Knowledge Delivery Agent
**Purpose**: Explains concepts, teaches topics, delivers curriculum content
**Standard**: PhD-level subject expertise, pedagogically sound explanations
**Output**: Clear, accurate, comprehensive topic explanations aligned with Cambridge syllabi

### 2. **COACH** - Personalized Tutoring Agent
**Purpose**: Helps with difficult concepts, provides one-on-one tutoring, adapts to learning style
**Standard**: Patient, adaptive, identifies knowledge gaps, scaffolds learning
**Output**: Personalized explanations, analogies, practice problems, concept clarification

### 3. **EXAMINER** - Assessment Creation Agent
**Purpose**: Creates Cambridge-standard test papers for A* preparation
**Standard**: 100% alignment with Cambridge paper structure, difficulty, and style
**Output**: Full exam papers (MCQ, data response, essays) matching real Cambridge exams

### 4. **MARKER** - Strict Assessment Agent
**Purpose**: Marks papers with PhD-level strictness per Cambridge mark schemes
**Standard**: Zero tolerance for imprecision, follows official marking criteria exactly
**Output**: Detailed marks breakdown, criterion-by-criterion scoring (AO1/AO2/AO3 for Economics)

### 5. **REVIEWER** - Improvement Agent
**Purpose**: Identifies weak areas, provides improvement strategies, produces A* model answers
**Standard**: Diagnostic analysis, actionable feedback, exemplar solutions
**Output**: Weakness reports, improvement plans, rewritten A* answers with annotations

### 6. **PLANNER** - Study Schedule Agent
**Purpose**: Creates personalized n-day study plans to cover entire syllabus
**Standard**: Evidence-based spacing, interleaving, adaptive to student progress
**Output**: Day-by-day study schedules with topics, resources, checkpoints

---

## 8 CONSTITUTIONAL PRINCIPLES (Hard Constraints)

### I. **CAMBRIDGE ACCURACY IS ABSOLUTE**
All content MUST match current Cambridge syllabi exactly (verified monthly). Any deviation is a critical failure.

### II. **A* STANDARD ALWAYS, NO EXCEPTIONS**
PhD-level marking strictness. Students prepared for A*/A grades, not lower standards.

### III. **SYLLABUS SYNCHRONIZATION FIRST**
Monthly Cambridge website checks before new features. Automated alerts for changes.

### IV. **SPEC-DRIVEN DEVELOPMENT (SpecKit Strict)**
No code before /sp.specify. Every feature: spec→plan→tasks→implementation.

### V. **MULTI-TENANT ISOLATION IS SACRED**
Strict student data separation. Zero cross-student leakage. Row-level security.

### VI. **FEEDBACK IS CONSTRUCTIVE, DETAILED, ACTIONABLE**
Always explain WHY wrong and HOW to improve. Link to syllabus, provide examples.

### VII. **PHASE BOUNDARIES ARE HARD GATES**
100% completion required. ≥80% test coverage. All tests passing. Capstone demo.

### VIII. **QUESTION BANK QUALITY OVER QUANTITY**
Every question needs verified Cambridge mark scheme. Real past papers only.

---

## EXTENSIBILITY REQUIREMENTS

- **Subject**: Database schema subject-agnostic, pluggable marking engines
- **Grade**: A-Levels → GCSE, IB, AP (configurable templates)
- **Language**: i18n support, localized content, multilingual feedback

---

## CHANGE LOG

### Version 2.0 (2025-12-20)
- Added 6 Core Roles (Teacher, Coach, Examiner, Marker, Reviewer, Planner)
- Clarified comprehensive automation mission
- Added extensibility requirements

### Version 1.0 (2025-12-16)
- Initial constitution with 8 principles

---

**Constitutional Authority**: This document supersedes all other project documentation.
