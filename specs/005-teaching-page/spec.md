# Feature Specification: Teaching Page - PhD-Level Concept Explanations

**Feature Branch**: `005-teaching-page`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Teaching Page - Concept Explanations: Students request PhD-level explanations of Economics 9708 syllabus concepts. System displays topic selection interface with syllabus browser or search. Student selects a concept (e.g., 'Price Elasticity of Demand'). Teacher Agent generates comprehensive explanation with: precise definition, key terms with definitions, core principles explanation, 2-3 real-world examples with analysis, visual aids (diagram descriptions for supply/demand curves, graphs, etc.), worked examples with step-by-step solutions, common misconceptions with corrections, practice problems with answer outlines, connections to related concepts. Explanation displays in structured format with collapsible sections. Students can bookmark explanations for later review. Backend APIs exist: GET /api/teaching/syllabus (list topics), POST /api/teaching/explain (generate explanation for concept), GET /api/teaching/explanations (user's saved explanations). UI similar to educational content platform with clear typography, visual hierarchy, code/math formatting support."

## User Scenarios & Testing

### User Story 1 - View PhD-Level Concept Explanation (Priority: P1)

A student studying for A-Level Economics 9708 needs to understand a specific syllabus concept (e.g., "Price Elasticity of Demand"). They select the concept from the topic list and receive a comprehensive, PhD-level explanation with definitions, examples, diagrams, worked problems, and common misconceptions. The explanation helps them deeply understand the concept beyond memorization.

**Why this priority**: This is the core value proposition of the teaching page - delivering expert-quality explanations that help students truly understand Economics concepts. Without this, the teaching page has no purpose.

**Independent Test**: Can be fully tested by selecting any syllabus concept (e.g., "Supply and Demand"), submitting the request, and verifying that the system returns a complete explanation with all required components (definition, examples, diagrams, etc.). Delivers immediate educational value as a standalone feature.

**Acceptance Scenarios**:

1. **Given** student is logged in and on teaching page, **When** student selects "Price Elasticity of Demand" from topic list, **Then** system displays comprehensive explanation with: precise definition, 3+ key terms with definitions, 2-3 real-world examples, visual aid descriptions, worked example, common misconceptions, and practice problems
2. **Given** student views an explanation, **When** student clicks on collapsible sections (Examples, Misconceptions, Practice), **Then** sections expand/collapse smoothly without losing content
3. **Given** student receives an explanation, **When** student scrolls through content, **Then** typography is clear, mathematical notation renders correctly, and visual hierarchy guides reading flow
4. **Given** explanation is loading, **When** AI generates content, **Then** student sees loading indicator and receives explanation within 10 seconds
5. **Given** AI service fails, **When** explanation cannot be generated, **Then** student sees user-friendly error message with retry option

---

### User Story 2 - Browse and Search Syllabus Topics (Priority: P2)

A student wants to explore available Economics 9708 syllabus topics to decide what to study. They can browse topics by syllabus code hierarchy (AS vs A2, Paper 1 vs Paper 2) or search by keyword (e.g., "elasticity", "market failure"). The interface displays topic codes, descriptions, and quick preview of content coverage.

**Why this priority**: Students need to find concepts before they can learn about them. This is essential for discoverability but secondary to the actual explanation quality (P1). Can be implemented after P1 using a simple list as MVP.

**Independent Test**: Can be fully tested by loading the teaching page, using the search bar to find "elasticity", and verifying that relevant topics appear (e.g., "3.1.2 Price Elasticity of Demand", "3.1.3 Income Elasticity"). Delivers value as a navigation feature independently of P1.

**Acceptance Scenarios**:

1. **Given** student is on teaching page, **When** student views topic browser, **Then** topics are organized by syllabus structure (AS/A2, Paper 1/2, sections) with codes and descriptions
2. **Given** student types "elasticity" in search bar, **When** search executes, **Then** results show all topics containing "elasticity" (PED, YED, PES) with highlighted keywords
3. **Given** student browses topics, **When** student hovers over a topic, **Then** quick preview shows: topic code, learning outcomes, number of practice problems available
4. **Given** student selects a topic, **When** topic loads, **Then** system transitions smoothly to explanation view (User Story 1)

---

### User Story 3 - Bookmark Explanations for Review (Priority: P3)

A student finds an explanation particularly helpful and wants to save it for exam revision. They click "Bookmark" on the explanation page, and it's added to their personal "Saved Explanations" collection. Later, they can access all bookmarked explanations from a dedicated section, organized by topic or date saved.

**Why this priority**: Bookmarking enhances the learning experience but isn't critical for the core teaching functionality. Students can still benefit from explanations without bookmarking (they can navigate back manually). This is a quality-of-life feature for power users.

**Independent Test**: Can be fully tested by viewing any explanation, clicking "Bookmark", navigating to "Saved Explanations" page, and verifying the explanation appears there. Delivers value as a study organization tool independently of other features.

**Acceptance Scenarios**:

1. **Given** student views an explanation, **When** student clicks "Bookmark" button, **Then** explanation is saved to their account and button shows "Bookmarked" state
2. **Given** student has bookmarked explanations, **When** student navigates to "Saved Explanations" section, **Then** all bookmarked explanations are listed with topic name, syllabus code, and date saved
3. **Given** student views saved explanations, **When** student clicks on a saved explanation, **Then** full explanation loads (cached if possible, or re-fetched)
4. **Given** student views a bookmarked explanation, **When** student clicks "Remove Bookmark", **Then** explanation is removed from saved list and bookmark button resets

---

### Edge Cases

- What happens when **a syllabus topic has no available content** (not yet added to database)? System shows "Topic not yet available" message with option to request it.
- What happens when **AI generates an incomplete explanation** (e.g., missing examples)? System detects missing components and triggers automatic retry OR shows warning "Explanation may be incomplete - contact support".
- What happens when **student searches for a topic not in Economics 9708 syllabus** (e.g., "Bitcoin")? Search returns "No results found in Economics 9708 syllabus" with suggestion to refine query.
- What happens when **student has very slow internet** and explanation takes >10 seconds? System shows progress indicator ("Generating explanation... 45% complete") and doesn't time out prematurely.
- What happens when **student bookmarks the same explanation twice**? System prevents duplicates and shows "Already bookmarked" feedback.
- What happens when **student's bookmark quota is full** (e.g., 100 bookmarks limit)? System shows "Bookmark limit reached - remove old bookmarks to add new ones" with link to manage bookmarks.

## Requirements

### Functional Requirements

**Topic Selection & Navigation**:
- **FR-001**: System MUST display all Economics 9708 syllabus topics organized by AS/A2 level, paper number, and section hierarchy
- **FR-002**: System MUST provide search functionality that matches keywords against topic codes, descriptions, and learning outcomes
- **FR-003**: System MUST display topic metadata (code, description, learning outcomes) in browsable interface before selection
- **FR-004**: Users MUST be able to select a topic and navigate to its explanation view

**Explanation Generation & Display**:
- **FR-005**: System MUST call Teacher Agent AI to generate PhD-level explanations for selected concepts
- **FR-006**: System MUST display explanations with these mandatory components: precise definition, key terms (3+ with definitions), core principles explanation, real-world examples (2-3 with analysis), visual aid descriptions (diagrams, graphs, curves), worked examples (step-by-step solutions with marks breakdown), common misconceptions (with corrections), practice problems (with answer outlines), connections to related syllabus concepts
- **FR-007**: System MUST render explanations in structured format with collapsible sections for Examples, Misconceptions, Practice Problems
- **FR-008**: System MUST format mathematical notation, economic terminology, and code snippets with appropriate styling
- **FR-009**: System MUST show loading indicators during AI generation (expected 5-10 seconds)
- **FR-010**: System MUST handle AI failures gracefully with user-friendly error messages and retry options

**Bookmarking & Saved Explanations**:
- **FR-011**: Users MUST be able to bookmark explanations with a single click
- **FR-012**: System MUST persist bookmarked explanations to user's account (associated with student_id)
- **FR-013**: Users MUST be able to view all their bookmarked explanations in a dedicated "Saved Explanations" section
- **FR-014**: Users MUST be able to remove bookmarks from saved list
- **FR-015**: System MUST prevent duplicate bookmarks for the same topic
- **FR-016**: System MUST display bookmark metadata (topic name, syllabus code, date saved) in saved list

**Performance & Reliability**:
- **FR-017**: System MUST generate explanations within 10 seconds for 95% of requests
- **FR-018**: System MUST cache generated explanations to improve load times for repeat views
- **FR-019**: System MUST validate that AI-generated explanations contain all required components before displaying
- **FR-020**: System MUST log incomplete/failed explanations for monitoring and improvement

**UI/UX Requirements**:
- **FR-021**: Interface MUST follow educational content platform patterns (clear typography, visual hierarchy, readable line lengths)
- **FR-022**: Interface MUST support responsive design for desktop, tablet, and mobile devices
- **FR-023**: Interface MUST provide accessible navigation (keyboard shortcuts, screen reader support)
- **FR-024**: Interface MUST clearly indicate which sections are collapsible with visual affordances (chevron icons, hover states)

### Key Entities

- **SyllabusPoint**: Represents a single topic in the Economics 9708 syllabus (e.g., "3.1.2 Price Elasticity of Demand"). Attributes: code, description, learning_outcomes, AS/A2 level, paper number, section. Relationships: belongs to Subject, has many SavedExplanations.

- **SavedExplanation**: Represents a student's bookmarked explanation for future review. Attributes: student_id, syllabus_point_id, explanation_content (JSON), date_saved, date_last_viewed. Relationships: belongs to Student, references SyllabusPoint.

- **TopicExplanation** (transient, not persisted): AI-generated explanation structure. Attributes: concept_name, definition, key_terms[], examples[], visual_aids[], worked_examples[], misconceptions[], practice_problems[], related_concepts[].

## Success Criteria

### Measurable Outcomes

- **SC-001**: Students can select a syllabus topic and receive a complete PhD-level explanation in under 10 seconds for 95% of requests
- **SC-002**: Explanations contain all 9 required components (definition, key terms, examples, visual aids, worked examples, misconceptions, practice problems, connections, core principles) in 100% of successful generations
- **SC-003**: Students successfully find target topics using search in under 30 seconds (measured by time from search input to topic selection)
- **SC-004**: Students can bookmark and retrieve explanations with zero data loss (100% persistence reliability)
- **SC-005**: Interface achieves 90+ Google Lighthouse accessibility score (WCAG 2.1 AA compliance)
- **SC-006**: 80% of students who view an explanation spend more than 2 minutes reading it (indicates engagement and quality)
- **SC-007**: System handles AI service failures gracefully with user-friendly errors in 100% of failure cases (no crashes or blank screens)
- **SC-008**: Students report improved conceptual understanding in post-feature surveys (target: 85% positive feedback on "helpfulness" metric)

## Assumptions

- **A-001**: Backend APIs already exist and are functional (GET /api/teaching/syllabus, POST /api/teaching/explain, GET /api/teaching/explanations)
- **A-002**: Teacher Agent AI (backend service) reliably generates PhD-level explanations for all Economics 9708 topics
- **A-003**: SyllabusPoint database table is already populated with all Economics 9708 AS & A2 topics with accurate codes and descriptions
- **A-004**: Students are authenticated before accessing the teaching page (authentication is handled by existing system)
- **A-005**: Explanation content is primarily text-based with diagram descriptions (no actual diagram rendering required in MVP - descriptions suffice)
- **A-006**: Students have stable internet connection (minimum 3G speed) for AI-generated content delivery

## Dependencies

- **Backend APIs**: GET /api/teaching/syllabus (list topics), POST /api/teaching/explain (generate explanation), GET /api/teaching/explanations (retrieve saved explanations)
- **Teacher Agent Service**: AI service (backend/src/services/teaching_service.py) must be operational and generate explanations per TopicExplanation schema
- **Database**: SyllabusPoint table populated with Economics 9708 topics, SavedExplanation table created for bookmarking
- **Authentication System**: Student login/session management must be complete (user must be authenticated to access teaching page)
- **Frontend Framework**: Next.js 16+ App Router, React 19, shadcn/ui, Tailwind CSS 4 (established in 004-coaching-page)
- **State Management**: TanStack Query 5.62+ for server state (used in 004-coaching-page, reusable pattern)

## Risks

- **R-001**: AI-generated explanations may occasionally be incomplete or low-quality (Mitigation: Implement validation logic to check for required components; flag incomplete explanations for manual review)
- **R-002**: Search functionality may return too many or too few results for broad/narrow queries (Mitigation: Implement fuzzy matching and relevance scoring; show "No results" gracefully with suggestions)
- **R-003**: Students may expect actual diagrams instead of text descriptions (Mitigation: Set clear expectations in UI; consider adding diagram rendering in future iteration)
- **R-004**: Collapsible sections may hide important content students don't realize exists (Mitigation: Keep critical sections expanded by default; use visual cues like badges showing "3 examples inside")
- **R-005**: Bookmark limit may frustrate power users (Mitigation: Set generous limit (100+); provide clear feedback when approaching limit; allow bulk delete)
- **R-006**: Explanation caching may serve stale content if syllabus is updated (Mitigation: Implement cache invalidation when syllabus points are modified; show "Last updated" timestamp)

## Out of Scope

- **Actual diagram rendering** (SVG/Canvas graphics for supply/demand curves): MVP uses text descriptions only. Rendering diagrams is a Phase V advanced feature.
- **Interactive diagrams** (students can drag curves, change variables): Not planned for this phase.
- **Video explanations**: Text-based explanations only. Video content requires separate infrastructure.
- **Collaborative features** (students can share/comment on explanations): Social features are out of scope for teaching page MVP.
- **Offline mode** (cached explanations available without internet): Requires PWA setup and service worker implementation (future enhancement).
- **Multi-subject support**: Teaching page focuses exclusively on Economics 9708. Other subjects (Accounting 9706, Math 9709) will be added in future phases.
- **Personalized explanation difficulty** (adjust PhD-level to student's current understanding): AI personalization is advanced feature for later iteration.
- **Spaced repetition reminders** (remind students to review bookmarked explanations): Requires notification system not yet built.

## Notes

- **Design inspiration**: Khan Academy, Coursera, and Notion for collapsible sections and clean content layouts
- **Typography**: Use system fonts for readability (Inter, SF Pro, Segoe UI). Economic terms in **bold**, definitions in quote blocks.
- **Mathematical notation**: Use KaTeX or similar library if needed for rendering formulas (most Economics content is text-based)
- **Accessibility**: All collapsible sections must be keyboard-navigable (Enter to expand/collapse), screen reader announcements for state changes
- **Error messaging**: Follow established patterns from 004-coaching-page (toast notifications for transient errors, inline messages for validation errors)
- **Caching strategy**: Use TanStack Query's built-in caching (staleTime: 5 minutes for explanations, 1 hour for syllabus topics list)
