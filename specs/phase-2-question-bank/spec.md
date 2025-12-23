# Feature Specification: Phase II - Question Bank & Exam Generation

**Feature Branch**: `002-question-bank`
**Created**: 2025-12-18
**Status**: Draft
**Input**: User description: "phase-2-question-bank"
**Subject MVP**: Economics 9708 (Cambridge International A-Level)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manual Question Upload & Storage (Priority: P1)

A teacher wants to manually upload a Cambridge past paper PDF and have the system extract, parse, and store individual questions with their mark schemes in the database for later exam generation.

**Why this priority**: This is the foundational capability. Without questions in the database, no other Phase II features can work. This MVP slice delivers immediate value by allowing manual question curation and proves the PDF extraction pipeline works.

**Independent Test**: Can be fully tested by uploading a single Economics 9708 past paper PDF (e.g., 9708_s22_qp_31.pdf), verifying questions are extracted correctly with marks and mark schemes, and querying the database to confirm storage. Delivers value even without automated crawling or exam generation.

**Acceptance Scenarios**:

1. **Given** a valid Cambridge Economics 9708 PDF file (e.g., 9708_w21_qp_32.pdf) containing 3 essay questions
   **When** teacher uploads the PDF via API endpoint `/api/questions/upload`
   **Then** system extracts all 3 questions with question text, max marks, paper metadata (subject, year, session, paper number), and stores them in `questions` table with `source_paper` populated

2. **Given** a Cambridge PDF with mark scheme (e.g., 9708_w21_ms_32.pdf)
   **When** teacher uploads the mark scheme PDF
   **Then** system extracts marking criteria, level descriptors, and model answers, associates them with corresponding questions via paper matching, and stores in `marking_scheme` JSONB field

3. **Given** an uploaded question with ID `q123`
   **When** teacher queries `/api/questions/q123`
   **Then** system returns complete question object with: question_text, max_marks, difficulty (auto-calculated from past performance), source_paper, syllabus_point_ids (empty initially), and marking_scheme JSONB

4. **Given** a malformed PDF or non-Cambridge format
   **When** teacher uploads the file
   **Then** system returns 400 Bad Request with specific error message ("Unable to parse Cambridge question format" or "Missing required metadata in filename")

5. **Given** a duplicate question (same source_paper + question_number)
   **When** teacher uploads a PDF already processed
   **Then** system detects duplicate via unique constraint on (subject_id, source_paper, question_number), skips insertion, and returns 409 Conflict with message "Question already exists: 9708_w21_qp_32_q1"

---

### User Story 2 - Question Bank Search & Filtering (Priority: P2)

A teacher wants to search the question bank by subject, topic, difficulty, and year range to find specific questions for manual exam creation or review.

**Why this priority**: Once questions are stored (P1), teachers need to discover and retrieve them efficiently. This enables manual exam curation before automated generation is built. Independent of exam generation logic.

**Independent Test**: After uploading 20+ Economics 9708 questions covering various topics and years, test search queries like "all microeconomics questions from 2018-2022 with difficulty 'medium'" and verify correct filtering. Delivers value for manual question review and selection.

**Acceptance Scenarios**:

1. **Given** 50 Economics 9708 questions stored with syllabus_point_ids tagged (e.g., `["9708.1.1", "9708.1.2"]` for microeconomics)
   **When** teacher queries `/api/questions?subject_id=<economics_9708_id>&syllabus_points=9708.1.1,9708.1.2&year_min=2018&year_max=2022&difficulty=medium`
   **Then** system returns paginated list of questions matching all filters, sorted by year descending (newest first), with 20 results per page

2. **Given** questions tagged with multiple syllabus points (e.g., question covers both microeconomics and macroeconomics)
   **When** teacher searches for any question related to "9708.1.1" (microeconomics)
   **Then** system returns all questions where `syllabus_point_ids` array contains "9708.1.1" (using PostgreSQL `@>` operator for JSONB array containment)

3. **Given** a question bank with 200 questions
   **When** teacher queries without filters (`/api/questions?subject_id=<economics_9708_id>`)
   **Then** system returns first 20 questions with pagination metadata (total_count, page, per_page, total_pages) and `next` link for cursor-based pagination

4. **Given** a search query that matches no questions
   **When** teacher queries `/api/questions?subject_id=<economics_9708_id>&year_min=2030`
   **Then** system returns 200 OK with empty results array `[]` and total_count=0 (not a 404 error)

---

### User Story 3 - Cambridge Filename Parsing & Metadata Extraction (Priority: P1)

The system must automatically parse Cambridge International PDF filenames (e.g., `9708_s22_qp_31.pdf`, `9708_w21_ms_32.pdf`) to extract subject code, year, session, paper type, and paper number for metadata tagging.

**Why this priority**: This is a dependency for P1 (manual upload). Without filename parsing, we can't automatically populate `source_paper` metadata. This is a small, independently testable utility that unblocks all other question bank features.

**Independent Test**: Test with 10+ different Cambridge filename formats (question papers, mark schemes, various years/sessions) and verify correct parsing into structured metadata. Can be unit tested without database or API.

**Acceptance Scenarios**:

1. **Given** filename `9708_s22_qp_31.pdf`
   **When** system parses filename
   **Then** extracts: `{subject_code: "9708", year: 2022, session: "MAY_JUNE", paper_type: "QUESTION_PAPER", paper_number: 31, variant: null}`

2. **Given** filename `9708_w21_ms_32.pdf`
   **When** system parses filename
   **Then** extracts: `{subject_code: "9708", year: 2021, session: "OCT_NOV", paper_type: "MARK_SCHEME", paper_number: 32, variant: null}`

3. **Given** filename `9706_m23_qp_42.pdf` (March 2023 Accounting)
   **When** system parses filename
   **Then** extracts: `{subject_code: "9706", year: 2023, session: "FEB_MARCH", paper_type: "QUESTION_PAPER", paper_number: 42, variant: null}`

4. **Given** filename `random_economics_questions.pdf` (non-Cambridge format)
   **When** system attempts to parse
   **Then** raises `InvalidFilenameFormatError` with message "Filename does not match Cambridge International format (expected: NNNN_sYY_qp_NN.pdf)"

5. **Given** filename `9708_s22_qp_31_v2.pdf` (variant 2)
   **When** system parses filename
   **Then** extracts: `{subject_code: "9708", year: 2022, session: "MAY_JUNE", paper_type: "QUESTION_PAPER", paper_number: 31, variant: 2}`

---

### User Story 4 - PDF Question Extraction (Economics 9708) (Priority: P1)

The system must extract individual questions from Economics 9708 Cambridge PDFs, identifying question numbers, question text (including any diagrams/tables descriptions), and maximum marks.

**Why this priority**: Core functionality for P1 manual upload. This is where the AI/ML complexity lives. Economics 9708 is chosen as MVP subject because it has clear question delimiters ("Question 1", "Question 2") and predictable structure.

**Independent Test**: Test with 5 different Economics 9708 past papers (Papers 1, 2, 3) and verify all questions are extracted with correct text and marks. Compare against manual count to ensure no questions are missed. Can be tested independently via Python unit tests.

**Acceptance Scenarios**:

1. **Given** Economics 9708 Paper 3 PDF (essay paper) with 3 questions, each worth 25 marks
   **When** system processes PDF
   **Then** extracts 3 question objects: `[{question_number: 1, question_text: "Discuss the extent to which...", max_marks: 25}, ...]`

2. **Given** a question spanning multiple pages (e.g., question text on page 5, diagram on page 6)
   **When** system extracts question
   **Then** concatenates text from all pages belonging to that question, preserving order, and includes diagram description or placeholder `[DIAGRAM: Supply and demand curves]`

3. **Given** a question with sub-parts (e.g., Question 1(a), 1(b), 1(c))
   **When** system extracts question
   **Then** stores as single question with max_marks as sum of sub-parts (e.g., `max_marks: 20` for 1(a)=8, 1(b)=6, 1(c)=6), and question_text includes all sub-parts with clear delimiters

4. **Given** a PDF with footer text ("Cambridge International AS and A Level Economics 9708")
   **When** system extracts questions
   **Then** filters out headers/footers/page numbers, returning only question content

5. **Given** a mark scheme PDF (not question paper)
   **When** system attempts question extraction
   **Then** returns empty list `[]` or raises `InvalidPaperTypeError` with message "This is a mark scheme, not a question paper" (detected via filename parsing P1-3)

---

### User Story 5 - Mark Scheme Extraction & Matching (Priority: P2)

The system must extract marking criteria from Cambridge mark scheme PDFs and automatically match them to corresponding questions based on paper metadata and question numbers.

**Why this priority**: Required for AI marking (Phase III), but not blocking for Phase II exam generation. Can be tested independently after P1 (upload) and P1-4 (question extraction) are complete. Delivers value by enriching question bank with marking guidance.

**Independent Test**: Upload a question paper PDF (9708_s22_qp_31.pdf) and corresponding mark scheme PDF (9708_s22_ms_31.pdf), verify all questions are matched to their marking criteria, and check that `marking_scheme` JSONB field is populated correctly.

**Acceptance Scenarios**:

1. **Given** mark scheme PDF `9708_s22_ms_31.pdf` with level descriptors for Question 1 (e.g., "Level 4: 18-25 marks - Sophisticated analysis with evaluation...")
   **When** system processes mark scheme
   **Then** extracts marking criteria as structured JSONB: `{levels: [{level: 4, marks: "18-25", descriptor: "Sophisticated analysis..."}], keywords: ["analysis", "evaluation", "diagrams"], model_answer_points: [...]}`

2. **Given** a question paper `9708_s22_qp_31.pdf` with 3 questions and corresponding mark scheme `9708_s22_ms_31.pdf`
   **When** both PDFs are uploaded
   **Then** system matches questions to mark schemes via `(subject_code, year, session, paper_number, question_number)` tuple and updates `questions.marking_scheme` JSONB field for all 3 questions

3. **Given** a mark scheme with alternative acceptable answers (e.g., "Accept 'supply shock' or 'cost-push inflation'")
   **When** system extracts mark scheme
   **Then** stores alternatives in JSONB: `{acceptable_answers: [["supply shock", "cost-push inflation"]], ...}`

4. **Given** a mark scheme uploaded before the corresponding question paper
   **When** question paper is uploaded later
   **Then** system retroactively matches mark scheme to questions using database query on `source_paper` metadata

5. **Given** a mark scheme for a different subject (e.g., 9706 Accounting) when processing Economics 9708 questions
   **When** system attempts matching
   **Then** no matches occur (due to subject_code mismatch), and mark scheme is stored separately for future 9706 question uploads

---

### User Story 6 - Intelligent Exam Generation (Priority: P3)

A teacher wants to generate a custom Economics 9708 exam by specifying syllabus topics, difficulty distribution, and total marks, with the system intelligently selecting questions to match criteria and avoid duplicates.

**Why this priority**: This is the core value proposition of Phase II but depends on P1 (question bank populated), P2 (search working), and ideally P2-5 (mark schemes available). This is the "capstone" feature that ties everything together.

**Independent Test**: With 100+ Economics 9708 questions tagged with syllabus points and difficulty, request exam generation with specific criteria (e.g., "60% microeconomics, 40% macroeconomics, difficulty distribution: 30% easy, 50% medium, 20% hard, total 75 marks") and verify generated exam matches criteria within tolerance (±5%). Deliverable: A valid exam JSON object that can be used for student attempts.

**Acceptance Scenarios**:

1. **Given** 150 Economics 9708 questions tagged with syllabus points and difficulty levels
   **When** teacher requests `/api/exams/generate` with criteria: `{subject_id: <9708_id>, syllabus_points: ["9708.1.*", "9708.2.*"], difficulty_distribution: {easy: 0.3, medium: 0.5, hard: 0.2}, total_marks: 75, paper_type: "MIXED"}`
   **Then** system generates exam with 3-4 questions (since Economics essay questions are typically 20-25 marks each), matching syllabus coverage (60% micro, 40% macro within ±10%), difficulty distribution within ±10%, and total marks exactly 75 (or within ±5 marks if exact match impossible)

2. **Given** a student who has previously attempted questions Q1, Q5, Q10
   **When** teacher generates exam for that student
   **Then** system excludes Q1, Q5, Q10 from selection pool to avoid repetition (queries `attempted_questions` table for student_id)

3. **Given** insufficient questions matching criteria (e.g., only 2 "hard" Economics 9708 questions exist but criteria requires 3)
   **When** system attempts exam generation
   **Then** returns 422 Unprocessable Entity with message "Insufficient questions to match criteria: need 3 'hard' questions but only 2 available. Adjust difficulty distribution or add more questions."

4. **Given** a generated exam
   **When** system saves exam to database
   **Then** creates `exams` record with `{student_id, subject_id, exam_type: "PRACTICE", paper_number: null, total_marks: 75, duration: 90, status: "PENDING"}` and links selected questions via junction table or `question_ids` JSONB array

5. **Given** a teacher wants to replicate a specific Cambridge paper structure (e.g., Paper 3: 3 questions, 25 marks each)
   **When** teacher specifies `paper_template: "9708_paper_3"` in generation request
   **Then** system selects exactly 3 questions worth 25 marks each, matching Paper 3 syllabus coverage (typically broad economics topics requiring evaluation)

---

### User Story 7 - Syllabus Point Tagging & Mapping (Priority: P3)

Questions must be tagged with Cambridge International Economics 9708 syllabus points (e.g., "9708.1.1 - Basic economic ideas") to enable intelligent exam generation and progress tracking.

**Why this priority**: Required for P3-6 (exam generation) and Phase IV (progress tracking), but can be done manually initially. Automated tagging via AI can come later. This unblocks other features with manual tagging MVP.

**Independent Test**: Manually tag 20 Economics 9708 questions with syllabus points, verify tags are stored in `questions.syllabus_point_ids` JSONB array, and test search query filtering by syllabus point. Deliverable: Database schema supports syllabus tagging and API endpoint allows CRUD operations on tags.

**Acceptance Scenarios**:

1. **Given** a question about "market equilibrium and price determination"
   **When** teacher tags question with syllabus points via `/api/questions/{id}/tags` PATCH endpoint
   **Then** system updates `questions.syllabus_point_ids` to `["9708.1.1", "9708.1.3"]` (JSONB array for many-to-many relationship)

2. **Given** all Economics 9708 syllabus points stored in `syllabus_points` table (from Phase I seed data)
   **When** teacher retrieves `/api/subjects/9708/syllabus`
   **Then** system returns hierarchical syllabus structure: `[{code: "9708.1", name: "Basic economic ideas and resource allocation", children: [{code: "9708.1.1", name: "Scarcity, choice, opportunity cost"}, ...]}, ...]`

3. **Given** a question with multiple syllabus tags (e.g., covers both microeconomics and macroeconomics concepts)
   **When** system calculates question difficulty
   **Then** considers cross-topic questions as higher difficulty (since they require integrated knowledge)

4. **Given** 100 questions with syllabus tags and teacher requests exam generation for specific topic "9708.2.1" (macroeconomic aims)
   **When** system selects questions
   **Then** filters to questions where `syllabus_point_ids @> '["9708.2.1"]'::jsonb` (PostgreSQL JSONB containment operator)

5. **Given** future AI-powered syllabus tagging (Phase V)
   **When** system auto-tags questions during upload
   **Then** stores tags with confidence score in JSONB: `{syllabus_point_ids: ["9708.1.1"], confidence: 0.87, auto_tagged: true}`, allowing manual review/override

---

### Edge Cases

- **What happens when a Cambridge PDF has non-standard formatting?** (e.g., 2019 exam format changed)
  → System logs parsing errors to `pdf_extraction_logs` table with PDF hash, error message, and manual review flag. Admin can manually correct and update parsing rules. System should not crash or partially extract (fail-safe: skip entire PDF and notify admin).

- **How does system handle questions with diagrams that are essential to understanding?**
  → Phase II: Extract diagram placeholder text `[DIAGRAM: Description from caption]`. Phase III: Use OCR or image analysis to extract diagram data. For MVP, require manual review flag for diagram-heavy questions.

- **What if two questions from different papers are identical (Cambridge reuses questions)?**
  → Store both with separate `source_paper` metadata but link via `duplicate_of_question_id` foreign key. Exam generation avoids selecting duplicates in same exam.

- **How to handle mark scheme ambiguities** (e.g., "award 1-2 marks for partial explanation")?
  → Store ambiguous ranges in JSONB: `{marks: {min: 1, max: 2}, condition: "partial explanation"}`. Phase III AI marking uses this for partial credit logic.

- **What if teacher uploads 1000 PDFs at once?**
  → Implement async job queue (Celery or similar) with status tracking. API returns 202 Accepted with job ID. Teacher polls `/api/jobs/{job_id}` for progress. Limit concurrent uploads to 10 per teacher.

- **How to handle syllabus updates** (e.g., Cambridge updates Economics 9708 syllabus in 2026)?
  → Store syllabus version in `subjects.syllabus_year` field. Questions tagged with old syllabus points are marked as "legacy" but not deleted. Admin can bulk-retag questions to new syllabus via mapping tool.

---

## Requirements *(mandatory)*

### Functional Requirements

**PDF Processing**:
- **FR-001**: System MUST parse Cambridge International PDF filenames to extract subject code, year, session, paper type, and paper number
- **FR-002**: System MUST extract individual questions from Economics 9708 question paper PDFs, identifying question numbers, question text, and maximum marks
- **FR-003**: System MUST extract marking criteria from Economics 9708 mark scheme PDFs, including level descriptors, keywords, and model answer points
- **FR-004**: System MUST handle multi-page questions by concatenating text across pages while preserving order
- **FR-005**: System MUST filter out headers, footers, and page numbers from extracted question text

**Question Bank Management**:
- **FR-006**: System MUST store questions in PostgreSQL `questions` table with fields: id, subject_id, syllabus_point_ids (JSONB array), question_text, max_marks, difficulty, source_paper, marking_scheme (JSONB)
- **FR-007**: System MUST enforce unique constraint on (subject_id, source_paper, question_number) to prevent duplicate questions
- **FR-008**: System MUST support question search by subject, syllabus points, difficulty, year range, and marks range with pagination (20 results per page)
- **FR-009**: System MUST allow manual tagging of questions with syllabus points via PATCH endpoint `/api/questions/{id}/tags`
- **FR-010**: System MUST automatically calculate question difficulty based on historical student performance (average score / max marks) once Phase III marking is implemented

**Exam Generation**:
- **FR-011**: System MUST generate custom exams based on criteria: subject, syllabus points, difficulty distribution, total marks, and paper type
- **FR-012**: System MUST select questions intelligently to match syllabus coverage within ±10% tolerance
- **FR-013**: System MUST exclude questions previously attempted by target student (query `attempted_questions` table)
- **FR-014**: System MUST validate that sufficient questions exist to meet generation criteria before creating exam
- **FR-015**: System MUST store generated exams in `exams` table linked to selected questions via `question_ids` JSONB array

**Syllabus Management**:
- **FR-016**: System MUST store Economics 9708 syllabus hierarchy in `syllabus_points` table (seeded from Cambridge website)
- **FR-017**: System MUST support syllabus querying via `/api/subjects/{id}/syllabus` returning hierarchical JSON structure
- **FR-018**: System MUST track syllabus version per subject via `subjects.syllabus_year` field

**Mark Scheme Matching**:
- **FR-019**: System MUST automatically match mark scheme PDFs to question paper PDFs via (subject_code, year, session, paper_number) tuple
- **FR-020**: System MUST support retroactive mark scheme matching (mark scheme uploaded before questions)

**API Endpoints** (RESTful):
- **FR-021**: `POST /api/questions/upload` - Upload single PDF (question paper or mark scheme), returns 201 with extracted questions count
- **FR-022**: `GET /api/questions` - Search questions with filters (subject_id, syllabus_points, difficulty, year_min, year_max, marks_min, marks_max), returns paginated results
- **FR-023**: `GET /api/questions/{id}` - Retrieve single question with full metadata and marking scheme
- **FR-024**: `PATCH /api/questions/{id}/tags` - Update syllabus_point_ids for question
- **FR-025**: `POST /api/exams/generate` - Generate exam with criteria, returns 201 with exam object including selected question IDs
- **FR-026**: `GET /api/subjects/{id}/syllabus` - Retrieve hierarchical syllabus structure

**Error Handling**:
- **FR-027**: System MUST return 400 Bad Request for invalid PDF formats or non-Cambridge filenames with specific error messages
- **FR-028**: System MUST return 409 Conflict when uploading duplicate questions (same source_paper + question_number)
- **FR-029**: System MUST return 422 Unprocessable Entity when exam generation criteria cannot be met due to insufficient questions

### Non-Functional Requirements

**Performance**:
- **NFR-001**: PDF extraction MUST complete within 30 seconds for typical 10-page Cambridge paper
- **NFR-002**: Question search queries MUST return results within 500ms for database with 1000+ questions
- **NFR-003**: Exam generation MUST complete within 5 seconds for typical criteria (3-4 questions)

**Scalability**:
- **NFR-004**: System MUST support concurrent PDF uploads from 10 teachers without performance degradation
- **NFR-005**: Database schema MUST efficiently handle 10,000+ questions per subject via proper indexing (subject_id, difficulty, syllabus_point_ids GIN index)

**Accuracy**:
- **NFR-006**: PDF question extraction MUST achieve >95% accuracy (all questions extracted with correct marks) for Economics 9708 standard format papers
- **NFR-007**: Filename parsing MUST achieve 100% accuracy for Cambridge International standard naming convention

**Data Quality**:
- **NFR-008**: All extracted questions MUST be stored with complete source_paper metadata for provenance tracking
- **NFR-009**: Mark scheme JSONB structure MUST be validated against schema before storage (e.g., required fields: levels, descriptor)

**Security**:
- **NFR-010**: PDF upload endpoint MUST validate file type (PDF only) and file size (<10MB) to prevent abuse
- **NFR-011**: All question bank queries MUST be filtered by student_id (multi-tenant isolation) once student access is implemented

**Observability**:
- **NFR-012**: System MUST log all PDF extraction attempts with success/failure status and error messages
- **NFR-013**: System MUST track exam generation requests with criteria and selected question IDs for audit trail

### Key Entities

**Question**: Represents a single exam question extracted from Cambridge paper
- Attributes: id (UUID), subject_id (FK), syllabus_point_ids (JSONB array), question_text (TEXT), max_marks (INTEGER), difficulty (ENUM: easy/medium/hard), source_paper (TEXT), question_number (INTEGER), marking_scheme (JSONB), created_at, updated_at
- Relationships: Belongs to Subject, appears in many Exams via junction, has many AttemptedQuestions
- Unique constraint: (subject_id, source_paper, question_number)

**MarkingScheme** (embedded in Question.marking_scheme JSONB):
- Structure: `{levels: [{level: INT, marks: STRING, descriptor: TEXT}], keywords: [STRING], model_answer_points: [TEXT], acceptable_answers: [[STRING]], partial_credit_rules: [{condition: STRING, marks: {min: INT, max: INT}}]}`
- No separate table; stored as JSONB within Question for flexibility

**Exam**: Represents a generated practice exam or timed exam for a student
- Attributes: id (UUID), student_id (FK), subject_id (FK), exam_type (ENUM: PRACTICE/TIMED/FULL_PAPER), paper_number (INTEGER, nullable), question_ids (JSONB array), total_marks (INTEGER), duration (INTEGER minutes), status (ENUM: PENDING/IN_PROGRESS/COMPLETED), created_at
- Relationships: Belongs to Student, belongs to Subject, contains Questions (via question_ids array)

**SyllabusPoint**: Represents a single topic in Cambridge syllabus hierarchy
- Attributes: id (UUID), subject_id (FK), code (STRING, e.g., "9708.1.1"), name (TEXT), parent_code (STRING, nullable for hierarchy), learning_outcomes (JSONB array), created_at
- Relationships: Belongs to Subject, has many Questions (via questions.syllabus_point_ids containment)
- Index: GIN index on code for fast prefix matching (e.g., "9708.1.*" searches)

**PDFExtractionLog**: Audit trail for PDF processing
- Attributes: id (UUID), filename (TEXT), file_hash (SHA256), subject_id (FK), extraction_status (ENUM: SUCCESS/FAILED/PARTIAL), questions_extracted (INTEGER), errors (JSONB array), processed_at
- Relationships: Belongs to Subject
- Purpose: Debugging, manual review queue, preventing duplicate processing

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Teachers can upload a Cambridge Economics 9708 PDF and see extracted questions in database within 30 seconds with >95% accuracy (all questions extracted with correct marks)

- **SC-002**: System successfully extracts questions from 10 different Economics 9708 past papers (Papers 1, 2, 3) spanning 2018-2023 with <5% manual correction rate

- **SC-003**: Mark scheme extraction and matching achieves 100% match rate for standard Cambridge format (same subject, year, session, paper number)

- **SC-004**: Exam generation produces valid exams (total marks within ±5 of target, syllabus coverage within ±10%, difficulty distribution within ±10%) in >90% of generation requests

- **SC-005**: Question bank search returns results within 500ms for database with 500+ Economics 9708 questions

- **SC-006**: Zero duplicate questions stored in database (unique constraint enforced, 409 errors returned for duplicates)

- **SC-007**: 100% of uploaded PDFs have complete source_paper metadata (subject, year, session, paper number) for provenance tracking

- **SC-008**: Phase II gate script passes: ✅ Question extraction working, ✅ Mark scheme matching working, ✅ Exam generation working, ✅ Database has 100+ Economics 9708 questions, ✅ API endpoints tested, ✅ >80% test coverage

---

## Out of Scope (Phase II)

**Explicitly NOT in Phase II** (deferred to later phases):

- ❌ AI-powered marking of student answers (Phase III)
- ❌ Automated syllabus crawling from Cambridge website (manual seed data OK)
- ❌ Support for subjects other than Economics 9708 (MVP subject only)
- ❌ OCR or image analysis for diagrams (placeholder text only)
- ❌ Automated syllabus tagging via AI (manual tagging only)
- ❌ Web UI for question bank management (API only)
- ❌ Bulk PDF upload (single file upload only; batch via multiple API calls)
- ❌ Question versioning or edit history (immutable questions in MVP)
- ❌ Collaborative question curation (single teacher/admin workflow)
- ❌ Integration with external question banks or APIs

---

## Dependencies

**Internal** (from Phase I):
- ✅ PostgreSQL database with Neon connection string in `.env`
- ✅ `students`, `subjects`, `syllabus_points` tables seeded (Phase I)
- ✅ FastAPI application structure (`backend/src/main.py`, `routes/`, `models/`)
- ✅ UV package manager configured (`pyproject.toml`)

**External**:
- 📦 **pdfplumber** (0.11+) - PDF text extraction library
- 📦 **regex** (built-in) - Cambridge filename parsing and question delimiter detection
- 🌐 Cambridge International past papers (manual download, 10+ Economics 9708 PDFs for testing)
- 🌐 Cambridge Economics 9708 syllabus document (for seeding `syllabus_points` table)

**Phase I Prerequisites**:
- Database migrations applied (`alembic upgrade head`)
- Economics 9708 subject record created in `subjects` table
- At least 10 syllabus points seeded in `syllabus_points` for Economics 9708

---

## Technical Constraints

- **Technology Stack Locked** (per constitution): Python 3.12+, FastAPI, SQLModel, PostgreSQL 16, UV
- **Database**: All queries MUST be filtered by `student_id` when student-facing (multi-tenant isolation - Constitutional Principle V)
- **PDF Processing**: Use pdfplumber (preferred) or PyPDF2 (fallback); NO external APIs (e.g., Google Cloud Vision) to avoid vendor lock-in
- **Storage**: Questions stored in PostgreSQL (not separate vector DB or document store); JSONB for marking_scheme flexibility
- **Testing**: >80% test coverage required for phase gate (pytest, unit + integration tests)
- **MVP Subject**: Economics 9708 only; architecture should allow future subject expansion but implementation focused on Economics 9708 patterns

---

## Clarifications Needed

**[NEEDS USER CLARIFICATION]**:

1. **Diagram Handling Strategy**: For Phase II MVP, should we:
   - Option A: Extract placeholder text only `[DIAGRAM: Description]` and mark questions for manual review
   - Option B: Attempt OCR extraction for simple diagrams (e.g., supply/demand curves)
   - Option C: Skip diagram-heavy questions entirely in Phase II
   - **Recommendation**: Option A (simplest, unblocks Phase II, defers complexity to Phase III)

2. **Question Difficulty Calculation**: Should difficulty be:
   - Option A: Manual teacher assignment (easy/medium/hard) during upload
   - Option B: Calculated from historical student performance (requires Phase III marking data)
   - Option C: Estimated from question characteristics (e.g., mark value, syllabus breadth)
   - **Recommendation**: Option C for Phase II (heuristic: 8-12 marks=easy, 13-20=medium, 21-25=hard), migrate to Option B after Phase III

3. **Syllabus Seeding**: Should Economics 9708 syllabus be:
   - Option A: Manually entered into `syllabus_points` table from PDF (one-time effort)
   - Option B: Scraped from Cambridge website (requires web scraping logic)
   - Option C: Provided by user as CSV/JSON import
   - **Recommendation**: Option A for Phase II MVP (50 syllabus points, 2-3 hours of manual work), automate in Phase V

4. **Exam Generation Constraints**: When generating exams, should system:
   - Option A: Strictly enforce all criteria (fail if impossible)
   - Option B: Relax criteria and return "best effort" exam with warnings
   - Option C: Ask user to adjust criteria via interactive flow
   - **Recommendation**: Option A (fail fast with clear error messages, prevents poor-quality exams)

---

## Assumptions

1. **Cambridge PDF Format**: Assume standard Cambridge International format (2018-2024) with consistent question numbering ("Question 1", "Question 2") and marks notation "[25 marks]"

2. **Single Language**: All Economics 9708 papers are in English; no multi-language support needed

3. **Network Access**: Teachers have reliable internet for PDF uploads (no offline mode required)

4. **Manual Review**: Teacher will manually review first 10-20 extracted questions per paper to verify accuracy before relying on automation

5. **Question Immutability**: Once questions are extracted and stored, they are immutable (no editing of question text; re-upload to replace)

6. **Economics 9708 Paper Types**: Papers 1 (MCQ), 2 (Data response), 3 (Essays) have different structures; Phase II focuses on Papers 2 and 3 (extractable text questions), Paper 1 (MCQs) deferred

7. **Storage Limits**: Average question length ~500 characters, average mark scheme ~2KB; 1000 questions = ~2MB TEXT + ~2MB JSONB (negligible storage)

8. **Concurrent Users**: Phase II serves single teacher/admin; multi-teacher concurrency testing deferred to Phase IV

---

## Phase II Deliverables Checklist

**Code Deliverables**:
- [ ] `backend/src/question_extractors/cambridge_parser.py` - Filename parsing utility
- [ ] `backend/src/question_extractors/economics_9708_extractor.py` - PDF question extraction
- [ ] `backend/src/question_extractors/mark_scheme_extractor.py` - Mark scheme parsing
- [ ] `backend/src/services/question_service.py` - Question CRUD operations
- [ ] `backend/src/services/exam_generation_service.py` - Intelligent exam generation
- [ ] `backend/src/routes/questions.py` - Question API endpoints
- [ ] `backend/src/routes/exams.py` - Exam generation endpoints
- [ ] `backend/alembic/versions/002_add_questions_tables.py` - Database migration

**Database Deliverables**:
- [ ] `questions` table with JSONB fields and GIN indexes
- [ ] `syllabus_points` table seeded with 50+ Economics 9708 topics
- [ ] `exams` table with question_ids JSONB array
- [ ] `pdf_extraction_logs` table for audit trail

**Testing Deliverables**:
- [ ] Unit tests for Cambridge filename parsing (10+ test cases)
- [ ] Unit tests for Economics 9708 question extraction (5+ sample PDFs)
- [ ] Integration tests for question upload endpoint (happy path + error cases)
- [ ] Integration tests for exam generation (various criteria)
- [ ] Test coverage >80% (pytest-cov report)

**Data Deliverables**:
- [ ] 100+ Economics 9708 questions extracted and stored in database
- [ ] 50+ Economics 9708 syllabus points seeded
- [ ] 10+ mark schemes extracted and matched to questions

**Documentation Deliverables**:
- [ ] `specs/phase-2-question-bank/plan.md` - Architecture decisions (created via `/sp.plan`)
- [ ] `specs/phase-2-question-bank/tasks.md` - Atomic tasks with test cases (created via `/sp.tasks`)
- [ ] `specs/phase-2-question-bank/CLAUDE.md` - Phase II-specific AI instructions
- [ ] API documentation in `docs/api/questions.md` and `docs/api/exams.md`
- [ ] ADR for PDF extraction library choice (pdfplumber vs PyPDF2)

**Quality Gates**:
- [ ] Phase II gate script passes: `./scripts/check-phase-2-complete.sh`
- [ ] All API endpoints return correct status codes (201, 400, 409, 422)
- [ ] No secrets in code (all in `.env`)
- [ ] Pre-commit hooks pass (ruff, mypy)

---

**Next Steps**: Run `/sp.clarify` to identify missing edge cases and ambiguities in this spec, then `/sp.plan` to create architecture plan.
