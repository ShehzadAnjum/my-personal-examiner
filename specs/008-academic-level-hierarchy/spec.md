# Feature Specification: Academic Level Hierarchy

**Feature Branch**: `008-academic-level-hierarchy`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "Restructure the system to support a proper hierarchy: Academic Level → Subject → Syllabus. The top level 'academic_level' represents qualification types like A-Level, O-Level, IGCSE, IB. Subjects belong to an academic level. Syllabi (with codes like 9708) belong to subjects. This makes the system generic and not Cambridge-specific."

---

## Problem Statement

The current system has a flat structure where subjects are hardcoded (e.g., "Economics 9708 A-Level"). This design is:
- **Cambridge-specific**: Assumes Cambridge International qualifications only
- **Inflexible**: Cannot support multiple qualification types (A-Level, O-Level, IGCSE, IB)
- **Poorly organized**: Mixes qualification level, subject, and syllabus code in one entity

The system needs a proper three-tier hierarchy to be generic and extensible:
```
Academic Level → Subject → Syllabus
```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Creates Academic Level (Priority: P1)

As an admin, I want to create academic levels (like "A-Level", "IGCSE") so that I can organize subjects under the correct qualification type.

**Why this priority**: This is the foundation - nothing else can be created without academic levels existing first.

**Independent Test**: Can be fully tested by creating an academic level and verifying it appears in the system. Delivers value by establishing the top-level organizational structure.

**Acceptance Scenarios**:

1. **Given** I am logged in as an admin, **When** I navigate to admin setup and create an academic level with name "A-Level" and code "A", **Then** the academic level is saved and appears in the list of available levels.

2. **Given** an academic level "A-Level" exists, **When** I try to create another academic level with the same code "A", **Then** the system prevents duplicate creation and shows an error.

3. **Given** I am on the admin dashboard, **When** I view academic levels, **Then** I see a list of all created levels with their names, codes, and subject counts.

---

### User Story 2 - Admin Creates Subject Under Academic Level (Priority: P1)

As an admin, I want to create subjects (like "Economics", "Mathematics") under a specific academic level so that subjects are properly categorized.

**Why this priority**: Subjects are the second tier of the hierarchy and are required before syllabi can be uploaded.

**Independent Test**: Can be fully tested by selecting an academic level and creating a subject under it. Delivers value by allowing proper subject organization.

**Acceptance Scenarios**:

1. **Given** an academic level "A-Level" exists, **When** I create a subject "Economics" under "A-Level", **Then** the subject is saved with a reference to "A-Level".

2. **Given** a subject "Economics" exists under "A-Level", **When** I try to create another "Economics" under "A-Level", **Then** the system prevents duplicate creation.

3. **Given** subjects exist under an academic level, **When** I view the academic level details, **Then** I see all subjects belonging to that level.

---

### User Story 3 - Admin Uploads Syllabus for Subject (Priority: P1)

As an admin, I want to upload a syllabus PDF for a specific subject so that the system can extract topics and organize learning content.

**Why this priority**: Syllabi contain the actual learning content structure. This is the core value delivery.

**Independent Test**: Can be fully tested by selecting a subject and uploading a syllabus PDF. Delivers value by populating the system with actual educational content.

**Acceptance Scenarios**:

1. **Given** a subject "Economics" exists under "A-Level", **When** I upload syllabus PDF with code "9708" and year range "2023-2025", **Then** the syllabus is saved with the correct subject reference.

2. **Given** a syllabus "9708" exists for "Economics", **When** I view the subject, **Then** I see the syllabus code, year range, and topic count.

3. **Given** I upload a syllabus, **When** the upload completes, **Then** the system extracts topics from the PDF and associates them with the syllabus.

---

### User Story 4 - Student Navigates Hierarchy (Priority: P2)

As a student, I want to see content organized by academic level and subject so that I can easily find my study materials.

**Why this priority**: User-facing navigation is important but depends on the admin setup being complete first.

**Independent Test**: Can be fully tested by viewing the teaching page as a student and navigating through levels/subjects/topics.

**Acceptance Scenarios**:

1. **Given** academic levels with subjects and syllabi exist, **When** I visit the teaching page, **Then** I see content organized by the active academic level and subject.

2. **Given** multiple academic levels exist, **When** I am a student, **Then** I see only the subjects relevant to my academic level (or all if not specified).

---

### User Story 5 - Admin Manages Hierarchy (Priority: P3)

As an admin, I want to edit and delete academic levels and subjects so that I can maintain the organizational structure.

**Why this priority**: Management operations are less critical than creation flows for initial functionality.

**Independent Test**: Can be fully tested by editing an academic level name and verifying the change persists.

**Acceptance Scenarios**:

1. **Given** an academic level exists, **When** I edit its name from "A-Level" to "Cambridge A-Level", **Then** the change is saved and reflected everywhere.

2. **Given** an academic level has no subjects, **When** I delete it, **Then** it is removed from the system.

3. **Given** an academic level has subjects with syllabi, **When** I try to delete it, **Then** the system warns about cascading deletion or prevents it.

---

### Edge Cases

- What happens when an admin tries to delete an academic level that has subjects with active student progress?
- How does the system handle uploading a syllabus when the subject already has one? (Replace vs. version)
- What happens if a student has bookmarked content and the academic level is reorganized?
- How does the system behave when no academic levels exist? (Shows setup prompt)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow admins to create academic levels with a name, code, and optional description
- **FR-002**: System MUST allow admins to create subjects under a specific academic level
- **FR-003**: System MUST allow admins to upload syllabi (with code and year range) for a specific subject
- **FR-004**: System MUST enforce unique codes within academic levels (no duplicate level codes)
- **FR-005**: System MUST enforce unique subject names within an academic level (no duplicate subjects under same level)
- **FR-006**: System MUST display content organized by the hierarchy in the teaching page
- **FR-007**: System MUST show "No academic levels configured" state when none exist
- **FR-008**: System MUST guide admins through the setup flow: Academic Level → Subject → Syllabus
- **FR-009**: System MUST maintain backward compatibility with existing syllabus_points and generated_explanations data
- **FR-010**: System MUST update all UI components to show dynamic hierarchy names instead of hardcoded "Economics 9708"

### Key Entities

- **Academic Level**: Represents a qualification type (A-Level, O-Level, IGCSE, IB). Has name, code, description, exam_board.
- **Subject**: Represents a subject area (Economics, Mathematics, Accounting). Belongs to exactly one academic level. Has name, code.
- **Syllabus**: Represents a specific syllabus version (9708 for 2023-2025). Belongs to exactly one subject. Has code, year_range, version. Syllabus points (topics) belong to a syllabus.

**Entity Relationships**:
```
Academic Level (1) ──→ (many) Subject (1) ──→ (many) Syllabus (1) ──→ (many) Syllabus Point
```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin can create a complete hierarchy (academic level → subject → syllabus) in under 5 minutes
- **SC-002**: All hardcoded "Economics 9708" references are removed from the UI
- **SC-003**: System correctly displays "No academic levels configured" when database is empty
- **SC-004**: Existing student data (bookmarks, explanations) continues to work after migration
- **SC-005**: Admin setup wizard clearly guides users through the 3-step hierarchy creation
- **SC-006**: Navigation breadcrumbs reflect the full hierarchy (e.g., "A-Level > Economics > 9708")

---

## Assumptions

1. An academic level can have multiple subjects (1:many relationship)
2. A subject belongs to exactly one academic level (not shared across levels)
3. A subject can have multiple syllabi (different years/versions)
4. The existing `subjects` table will be refactored, not replaced, to maintain FK references
5. Initial supported academic levels: A-Level, AS-Level, O-Level, IGCSE (Cambridge-focused but extensible)
6. Admin is the only role that can manage the hierarchy
7. Students interact with the hierarchy through navigation, not management

---

## Out of Scope

- Student preference for academic level (future feature)
- Multi-exam-board support within the same academic level (e.g., Cambridge vs AQA A-Level)
- Automatic syllabus version detection and update alerts
- Bulk import of academic levels/subjects from external sources

---

## Dependencies

- Existing database schema (subjects, syllabus_points, generated_explanations)
- Admin authentication and authorization (already implemented)
- Syllabus PDF upload and parsing (already implemented in admin setup)
