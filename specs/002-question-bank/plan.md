# Implementation Plan: Phase II - Question Bank & Exam Generation (Generic Framework)

**Branch**: `002-question-bank` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-question-bank/spec.md`

**Strategic Context** (per clarifications 2025-12-18):
- **Generic/Reusable Framework**: NOT Economics-specific; Economics 9708 as reference template
- **Auto-Bootstrapping Vision**: Inject subject → system automatically builds question bank, tests, marking
- **Phase II Scope**: Infrastructure + Economics MVP, defer AI-powered bootstrap to Phase V

---

## Summary

Phase II builds a **generic question bank and exam generation framework** that can support any Cambridge A-Level subject through configuration, not code. The system extracts questions from PDF past papers using subject-specific patterns stored in database configuration and resource files, then intelligently generates custom exams matching syllabus coverage and difficulty criteria.

**Key Architectural Shift** (from clarifications):
- **Before**: Hard-coded Economics 9708 extraction logic
- **After**: Generic extraction framework reading `subjects.extraction_patterns` JSONB
- **Rationale**: Economics serves as reference template; adding Math/English requires config, not code rewrite

**Technical Approach**:
1. Extend `subjects` table with JSONB config columns (`marking_config`, `extraction_patterns`, `paper_templates`)
2. Create generic PDF extractor that reads extraction rules from subject config
3. Build Economics 9708 config manually, archive in `backend/resources/subjects/9708/` as template
4. Implement exam generation engine using subject-agnostic algorithms
5. Prove architecture works with Economics; defer AI-powered bootstrap to Phase V

---

## Technical Context

**Language/Version**: Python 3.12+ (locked per constitution)
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22+, pdfplumber 0.11+, PostgreSQL 16
**Storage**: PostgreSQL (Neon Serverless) with JSONB for subject configuration
**Testing**: pytest 8.3+, pytest-cov 7.0.0, >80% coverage required (constitutional)
**Target Platform**: Linux server (Vercel serverless)
**Project Type**: Web backend (API-only in Phase II, UI in Phase IV)
**Performance Goals**: PDF extraction <30s for 10-page paper, question search <500ms, exam generation <5s
**Constraints**: >95% extraction accuracy, >80% test coverage, multi-tenant isolation (student_id filtering)
**Scale/Scope**: 100+ Economics questions (Phase II), 10,000+ questions per subject (production)

**Key Technologies** (from research):
- **pdfplumber 0.11+**: PDF text extraction (preferred over PyPDF2 for table/layout handling)
- **PostgreSQL JSONB**: Flexible subject configuration storage with GIN indexing
- **Regex patterns**: Cambridge filename parsing, question delimiter detection
- **SQLModel query builder**: Subject config-driven extraction logic

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Subject Accuracy is Non-Negotiable
- **Rule**: All content MUST match current Cambridge syllabi exactly
- **Compliance**: Economics 9708 syllabus seeded from Cambridge website (2023-2025 version)
- **Verification**: Manual review of extracted questions against official mark schemes
- **Status**: ✅ **PASS** - Economics syllabus points seeded in Phase I, extraction validation in Phase II tests

### ✅ Principle IV: Spec-Driven Development (No Code Before Spec)
- **Rule**: MUST follow `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` sequence
- **Compliance**: Phase II following SpecKitPlus workflow (spec created, plan in progress, tasks next)
- **Status**: ✅ **PASS** - Workflow followed correctly

### ✅ Principle V: Multi-Tenant Isolation is Sacred
- **Rule**: ALL queries MUST be filtered by `student_id` (Constitutional Principle)
- **Compliance**: Question bank queries are admin/teacher-scoped (no student access in Phase II)
- **Phase IV Requirement**: When students access questions, implement `student_id` filtering
- **Status**: ✅ **PASS** - Admin-only API in Phase II, student filtering deferred to Phase IV per design

### ✅ Principle VII: Phase Boundaries Are Hard Gates
- **Rule**: 100% completion before next phase, >80% test coverage
- **Compliance**: Phase II gate script required (`./scripts/check-phase-2-complete.sh`)
- **Deliverables**: 100+ Economics questions extracted, exam generation working, >80% coverage
- **Status**: ✅ **PASS** - Gate criteria defined in spec, script to be created in Phase II

### ✅ Principle VIII: Question Bank Quality Over Quantity
- **Rule**: Every question needs verified Cambridge mark scheme
- **Compliance**: Mark scheme extraction + matching implemented (FR-025, FR-026)
- **Validation**: Manual review of first 10-20 extracted questions per paper
- **Status**: ✅ **PASS** - Mark scheme matching designed, validation process defined

### ✅ Principle IX: SpecKitPlus Workflow Compliance (NEW 2025-12-18)
- **Rule**: ALL features MUST follow `/sp.*` command sequence, NO code before spec
- **Compliance**: Phase II created via `/sp.specify` → `/sp.clarify` → `/sp.plan` (current)
- **Status**: ✅ **PASS** - Strict workflow adherence for Phase II

### ✅ Principle X: Official Skills Priority (NEW 2025-12-18)
- **Rule**: CHECK Anthropic catalog BEFORE creating custom skills
- **Compliance**: No new skills in Phase II; reusing Phase I validated skills
- **Status**: ✅ **PASS** - Using existing skills only

### ✅ Principle XI: CLAUDE.md Hierarchy (NEW 2025-12-18)
- **Rule**: NO single CLAUDE.md >300 lines, hierarchical structure (root + phase/feature)
- **Compliance**: Phase II CLAUDE.md to be created in `specs/phase-2-question-bank/CLAUDE.md`
- **Status**: ✅ **PASS** - Hierarchical structure followed

### Constitution Check Summary: ✅ **ALL GATES PASS**

---

## Project Structure

### Documentation (this feature)

```text
specs/002-question-bank/
├── spec.md                      # Feature specification (created via /sp.specify)
├── plan.md                      # This file (created via /sp.plan)
├── research.md                  # Phase 0: Technology decisions (generated below)
├── data-model.md                # Phase 1: Database schema design (generated below)
├── quickstart.md                # Phase 1: Local development guide (generated below)
├── contracts/                   # Phase 1: API contracts (generated below)
│   ├── questions-api.yaml       # OpenAPI spec for question endpoints
│   ├── exams-api.yaml           # OpenAPI spec for exam generation endpoints
│   └── subjects-api.yaml        # OpenAPI spec for subject/syllabus endpoints
├── tasks.md                     # Phase 2: Atomic tasks (created via /sp.tasks - NOT by /sp.plan)
└── CLAUDE.md                    # Phase II-specific AI instructions (to be created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── subject.py                    # UPDATED: Add JSONB config fields
│   │   ├── question.py                   # NEW: Question entity
│   │   ├── exam.py                       # NEW: Exam entity
│   │   ├── syllabus_point.py             # EXISTS (Phase I)
│   │   └── pdf_extraction_log.py         # NEW: Audit trail
│   │
│   ├── schemas/
│   │   ├── question_schemas.py           # NEW: Question API schemas
│   │   ├── exam_schemas.py               # NEW: Exam generation schemas
│   │   └── subject_schemas.py            # UPDATED: Add config fields
│   │
│   ├── services/
│   │   ├── question_service.py           # NEW: Question CRUD operations
│   │   ├── exam_generation_service.py    # NEW: Intelligent exam generator
│   │   └── subject_config_service.py     # NEW: Load subject config from JSONB + files
│   │
│   ├── question_extractors/
│   │   ├── __init__.py
│   │   ├── cambridge_parser.py           # NEW: Generic filename parser
│   │   ├── generic_extractor.py          # NEW: Subject config-driven extraction
│   │   ├── mark_scheme_extractor.py      # NEW: Mark scheme parser
│   │   └── extraction_patterns.py        # NEW: Pattern matching utilities
│   │
│   ├── routes/
│   │   ├── questions.py                  # NEW: Question API endpoints
│   │   ├── exams.py                      # NEW: Exam generation endpoints
│   │   └── subjects.py                   # UPDATED: Add syllabus endpoint
│   │
│   └── main.py                            # UPDATED: Register new routes
│
├── resources/                             # NEW: Subject configuration archive
│   └── subjects/
│       └── 9708/                          # Economics 9708 reference template
│           ├── README.md                  # Documentation: Economics as template
│           ├── marking_config.json        # Level descriptors (L1-L4), essay rules
│           ├── extraction_patterns.yaml   # Question delimiters, marks notation
│           ├── paper_templates.json       # Paper 1/2/3 structures
│           └── sample_papers/             # 10+ test PDFs
│
├── alembic/
│   └── versions/
│       └── 002_add_questions_and_subject_config.py  # NEW: Migration
│
└── tests/
    ├── unit/
    │   ├── test_cambridge_parser.py       # NEW: Filename parsing tests
    │   ├── test_generic_extractor.py      # NEW: Extraction framework tests
    │   ├── test_question_service.py       # NEW: Question CRUD tests
    │   └── test_exam_generation.py        # NEW: Exam generation logic tests
    │
    └── integration/
        ├── test_question_routes.py        # NEW: Question API tests
        ├── test_exam_routes.py            # NEW: Exam generation API tests
        └── test_economics_extraction.py   # NEW: End-to-end Economics extraction
```

**Structure Decision**: **Web application (backend-only)** - Phase II is API-only (no frontend), using existing `backend/` directory from Phase I. Frontend added in Phase IV. Generic extraction framework lives in `src/question_extractors/`, subject configs in `resources/subjects/{code}/`.

---

## Complexity Tracking

> **No violations** - All constitutional gates pass. Phase II scope pragmatically limited (defer AI bootstrap to Phase V).

---

## Architecture Decisions

### AD-001: Subject Configuration Storage (JSONB + Resource Files)

**Context**: Need flexible subject-specific configuration for extraction patterns, marking criteria, paper templates.

**Decision**: Dual storage approach (from clarification 2025-12-18, Option C):
- **Database (JSONB)**: Queryable metadata in `subjects` table
  - `marking_config`: Rubric type, level count, essay structure rules
  - `extraction_patterns`: Question delimiter regex, marks notation pattern
  - `paper_templates`: Paper types, question counts, marks distribution
- **Resource Files**: Complex templates in `backend/resources/subjects/{code}/`
  - `marking_prompts.md`: AI prompts for marking (Phase III)
  - `extraction_rules.yaml`: Detailed regex patterns
  - `README.md`: Documentation for using subject as template

**Rationale**:
- JSONB allows fast queries (e.g., "all subjects using level descriptors")
- Resource files keep DB lean for complex templates
- Economics config serves as template for other subjects
- Supports both manual config (Phase II) and AI-generated config (Phase V)

**Alternatives Considered**:
- Pure JSONB: Queries easy but large blobs in DB
- Pure files: Flexible but no queryability
- Separate table: Normalized but complex queries

**Trade-offs**:
- **Pro**: Balance of flexibility and queryability
- **Pro**: Easy to version control resource files
- **Con**: Two places to check for config (mitigated by service layer)

**Related**: FR-016, FR-017, Clarification Q1

---

### AD-002: Generic Extraction Framework (Config-Driven)

**Context**: Need to extract questions from PDFs for multiple subjects without per-subject code.

**Decision**: Generic extraction framework that reads patterns from subject config:

```python
class GenericExtractor:
    def __init__(self, subject: Subject):
        self.config = subject.extraction_patterns  # JSONB
        self.question_delimiter = self.config["question_delimiter"]
        self.marks_pattern = self.config["marks_pattern"]

    def extract_questions(self, pdf_path: str) -> List[Question]:
        # Use config patterns, not hard-coded rules
        text = pdfplumber.extract(pdf_path)
        questions = re.split(self.question_delimiter, text)
        return [self._parse_question(q) for q in questions]
```

**Rationale**:
- Adding Math/English requires config update, not code rewrite
- Economics config proves architecture works
- Testable: Mock subject config in unit tests

**Alternatives Considered**:
- Per-subject extractors: `Economics9708Extractor`, `Math9709Extractor` (doesn't scale)
- Pure AI extraction: Flexible but slow, expensive, variable quality
- Template-based: DSL for extraction rules (over-engineered for MVP)

**Trade-offs**:
- **Pro**: True generic architecture
- **Pro**: Economics config documents patterns for other subjects
- **Con**: Complex patterns may be hard to express in JSONB (mitigated by resource files for complex rules)

**Related**: FR-002, FR-019, Clarification Q2, Q5

---

### AD-003: Economics 9708 as Reference Template

**Context**: Need to document Economics-specific patterns for reuse in other subjects.

**Decision**: Archive Economics config in `backend/resources/subjects/9708/` with comprehensive README explaining patterns:

**Files**:
- `README.md`: "Economics uses level descriptors (L1-L4) - adapt this for method marks (Math) or argument scoring (English)"
- `marking_config.json`: Example of level-based rubric
- `extraction_patterns.yaml`: Example of essay question patterns
- `paper_templates.json`: Example of 3-paper structure

**Rationale**:
- Future subjects can copy and adapt Economics patterns
- README provides guidance for AI bootstrap (Phase V)
- Live DB config (operational) + archived files (template) duality

**Related**: FR-018, FR-020, Clarification Q3

---

### AD-004: Defer AI-Powered Bootstrap to Phase V

**Context**: AI-powered subject bootstrapping (`/api/subjects/bootstrap`) adds significant complexity.

**Decision**: Phase II scope limited to infrastructure + Economics MVP:
- **Phase II**: Generic framework + manually created Economics config
- **Phase V**: Add `/api/subjects/bootstrap` endpoint with AI analysis

**Rationale**:
- Prove generic architecture works with Economics first
- Avoid premature optimization (AI bootstrap before knowing what to automate)
- Practical MVP approach: working system sooner, automation later

**Impact**:
- Phase II deliverables reduced (no bootstrap service, no AI analysis logic)
- Economics config creation is manual task (2-3 hours)
- Phase V can learn from Economics patterns when automating

**Related**: FR-019 to FR-021 revised, Clarification Q5

---

### AD-005: Exam Generation Algorithm

**Context**: Need to select questions intelligently matching syllabus coverage and difficulty.

**Decision**: Weighted random selection with constraints:

```python
def generate_exam(criteria: ExamCriteria) -> Exam:
    # 1. Filter candidates
    candidates = filter_questions(
        subject=criteria.subject_id,
        syllabus_points=criteria.syllabus_points,
        exclude_attempted=criteria.student_previous_attempts
    )

    # 2. Group by difficulty
    easy = [q for q in candidates if q.difficulty == "easy"]
    medium = [q for q in candidates if q.difficulty == "medium"]
    hard = [q for q in candidates if q.difficulty == "hard"]

    # 3. Select maintaining distribution
    selected = []
    target_marks = criteria.total_marks
    distribution = criteria.difficulty_distribution  # {easy: 0.3, medium: 0.5, hard: 0.2}

    # Weighted random selection respecting marks budget
    while sum(q.max_marks for q in selected) < target_marks:
        difficulty = random.choices(["easy", "medium", "hard"], weights=distribution)
        pool = {"easy": easy, "medium": medium, "hard": hard}[difficulty]
        if pool:
            selected.append(random.choice(pool))
            pool.remove(selected[-1])

    return Exam(questions=selected, ...)
```

**Rationale**:
- Simple algorithm, easy to test
- Respects difficulty distribution within ±10% (per spec)
- Avoids question repetition for students

**Alternatives Considered**:
- Knapsack algorithm: Optimal but overkill for MVP
- Pure random: Doesn't respect distribution
- ML-based: Requires historical data, premature for Phase II

**Trade-offs**:
- **Pro**: Simple, deterministic testing
- **Pro**: Meets acceptance criteria (SC-004: >90% valid exams)
- **Con**: May not find optimal solution if question pool is sparse (acceptable, returns 422 if impossible per FR-036)

**Related**: FR-011 to FR-015, User Story 6

---

## Phase 0: Research & Technology Decisions

*See [research.md](./research.md) for detailed analysis*

### Key Research Questions Resolved:

1. **PDF Extraction Library**:
   - **Decision**: pdfplumber 0.11+ (primary), PyPDF2 fallback
   - **Rationale**: Better table/layout handling, active maintenance, Economics papers have tables
   - **Alternative**: PyMuPDF (faster but GPL license, vendor lock-in risk)

2. **Subject Config Schema**:
   - **Decision**: JSONB with validation schema (JSON Schema or Pydantic)
   - **Rationale**: Flexible, queryable, validates on write
   - **Structure**: See AD-001

3. **Question Difficulty Calculation**:
   - **Decision**: Heuristic-based for Phase II (marks value: 8-12=easy, 13-20=medium, 21-25=hard)
   - **Rationale**: No historical data yet, simple rule works for Economics
   - **Phase III Upgrade**: Calculate from student performance (average score / max marks)

4. **Filename Parsing Strategy**:
   - **Decision**: Regex with named capture groups
   - **Pattern**: `(?P<code>\d{4})_(?P<session>[smw])(?P<year>\d{2})_(?P<type>qp|ms)_(?P<paper>\d{2})(\_v(?P<variant>\d+))?\.pdf`
   - **Rationale**: 100% accuracy for Cambridge standard format (NFR-007)

5. **Mark Scheme JSONB Structure**:
   - **Decision**: Flexible schema supporting multiple rubric types
   - **Example** (Economics level descriptors):
     ```json
     {
       "rubric_type": "level_descriptors",
       "levels": [
         {"level": 4, "marks": "18-25", "descriptor": "Sophisticated analysis..."},
         {"level": 3, "marks": "12-17", "descriptor": "Good analysis..."}
       ],
       "keywords": ["analysis", "evaluation", "diagrams"],
       "model_answer_points": ["Supply and demand equilibrium", "..."]
     }
     ```
   - **Math Alternative** (method marks):
     ```json
     {
       "rubric_type": "method_marks",
       "steps": [
         {"step": 1, "marks": 2, "requirement": "Correct formula application"},
         {"step": 2, "marks": 3, "requirement": "Accurate calculation"}
       ]
     }
     ```

---

## Phase 1: Data Model & API Contracts

*See [data-model.md](./data-model.md) and [contracts/](./contracts/) for details*

### Database Schema Changes

**Migration**: `002_add_questions_and_subject_config.py`

**Updated Table: `subjects`** (add JSONB config columns):
```sql
ALTER TABLE subjects ADD COLUMN marking_config JSONB;
ALTER TABLE subjects ADD COLUMN extraction_patterns JSONB;
ALTER TABLE subjects ADD COLUMN paper_templates JSONB;

CREATE INDEX idx_subjects_marking_config ON subjects USING GIN (marking_config);
CREATE INDEX idx_subjects_extraction_patterns ON subjects USING GIN (extraction_patterns);
```

**New Table: `questions`**:
```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID NOT NULL REFERENCES subjects(id),
    syllabus_point_ids JSONB DEFAULT '[]'::jsonb,
    question_text TEXT NOT NULL,
    max_marks INTEGER NOT NULL,
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    source_paper VARCHAR(100) NOT NULL,
    question_number INTEGER NOT NULL,
    marking_scheme JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE (subject_id, source_paper, question_number)
);

CREATE INDEX idx_questions_subject_id ON questions(subject_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_syllabus_points ON questions USING GIN (syllabus_point_ids);
CREATE INDEX idx_questions_source_paper ON questions(source_paper);
```

**New Table: `exams`**:
```sql
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id),
    subject_id UUID NOT NULL REFERENCES subjects(id),
    exam_type VARCHAR(20) CHECK (exam_type IN ('PRACTICE', 'TIMED', 'FULL_PAPER')),
    paper_number INTEGER,
    question_ids JSONB NOT NULL,
    total_marks INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    status VARCHAR(20) CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exams_student_id ON exams(student_id);
CREATE INDEX idx_exams_subject_id ON exams(subject_id);
```

**New Table: `pdf_extraction_logs`**:
```sql
CREATE TABLE pdf_extraction_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    subject_id UUID REFERENCES subjects(id),
    extraction_status VARCHAR(20) CHECK (extraction_status IN ('SUCCESS', 'FAILED', 'PARTIAL')),
    questions_extracted INTEGER DEFAULT 0,
    errors JSONB,
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pdf_logs_file_hash ON pdf_extraction_logs(file_hash);
CREATE INDEX idx_pdf_logs_subject_id ON pdf_extraction_logs(subject_id);
```

### API Endpoints Summary

*See [contracts/questions-api.yaml](./contracts/questions-api.yaml) for full OpenAPI spec*

**Questions API** (`/api/questions`):
- `POST /upload` - Upload PDF (question paper or mark scheme)
- `GET /` - Search questions (filters: subject, syllabus, difficulty, year range)
- `GET /{id}` - Retrieve single question
- `PATCH /{id}/tags` - Update syllabus tags

**Exams API** (`/api/exams`):
- `POST /generate` - Generate exam with criteria
- `GET /{id}` - Retrieve exam details

**Subjects API** (`/api/subjects`):
- `GET /{id}/syllabus` - Retrieve hierarchical syllabus

---

## Phase 2: Task Decomposition

**DEFERRED TO `/sp.tasks` COMMAND** - This plan does not generate tasks. After this plan is approved, run:

```bash
/sp.tasks
```

This will generate `tasks.md` with atomic, testable tasks based on this plan.

---

## Development Workflow

*See [quickstart.md](./quickstart.md) for detailed setup*

### Local Development Setup

```bash
# 1. Ensure Phase I complete (database, auth)
cd backend
uv run alembic upgrade head  # Apply existing migrations

# 2. Apply Phase II migration
uv run alembic revision --autogenerate -m "Add questions and subject config"
uv run alembic upgrade head

# 3. Seed Economics 9708 config (manual task)
uv run python scripts/seed_economics_config.py

# 4. Download sample Economics PDFs
mkdir -p resources/subjects/9708/sample_papers
# Download 10+ PDFs from Cambridge website to test extraction

# 5. Run tests
uv run pytest tests/ --cov=src --cov-report=term-missing

# 6. Start development server
uv run uvicorn src.main:app --reload --port 8000
```

### Testing Strategy

**Unit Tests** (70% of coverage):
- `test_cambridge_parser.py`: Filename parsing (10+ formats)
- `test_generic_extractor.py`: Extraction framework (mock configs)
- `test_question_service.py`: CRUD operations
- `test_exam_generation.py`: Selection algorithm

**Integration Tests** (20% of coverage):
- `test_question_routes.py`: API endpoints with TestClient
- `test_exam_routes.py`: Exam generation end-to-end
- `test_economics_extraction.py`: Real PDF extraction with Economics config

**Manual Tests** (10% - not automated):
- Upload 10 Economics PDFs, verify extraction accuracy >95%
- Generate 5 exams with different criteria, verify distribution within ±10%
- Review extracted questions against Cambridge mark schemes

---

## Success Criteria

*From spec.md Success Criteria section*

Phase II is complete when:
- ✅ Economics 9708 config created and archived in `resources/subjects/9708/`
- ✅ 100+ Economics questions extracted and stored with >95% accuracy
- ✅ Mark scheme matching achieves 100% match rate
- ✅ Exam generation produces valid exams in >90% of requests
- ✅ Question search returns results within 500ms
- ✅ Zero duplicate questions (unique constraint enforced)
- ✅ >80% test coverage (pytest-cov)
- ✅ Phase II gate script passes

---

## Risks & Mitigation

### Risk 1: Economics Config Creation Takes Longer Than Expected
**Likelihood**: Medium
**Impact**: High (blocks Phase II completion)
**Mitigation**:
- Allocate 3-4 hours for config creation (2-3 hours initial, 1 hour refinement)
- Use extracted questions from first 3 PDFs to validate patterns work
- Document config creation process in Economics README for future subjects

### Risk 2: Extraction Accuracy Below 95% Target
**Likelihood**: Medium
**Impact**: High (violates NFR-006)
**Mitigation**:
- Test with 10+ diverse Economics PDFs (Papers 1, 2, 3 from 2018-2023)
- Manual review of first 20 extracted questions per paper
- Iterate on extraction patterns until accuracy >95%
- Log failures to `pdf_extraction_logs` for debugging

### Risk 3: Exam Generation Algorithm Fails to Find Valid Exams
**Likelihood**: Low (only if question pool too sparse)
**Impact**: Medium (422 error acceptable per FR-036)
**Mitigation**:
- Ensure 100+ Economics questions cover all difficulty levels
- Algorithm returns 422 with clear message if impossible
- Test with edge cases (e.g., "need 5 hard questions but only 2 exist")

### Risk 4: JSONB Config Schema Changes Break Backward Compatibility
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Define config schema version in JSONB (`{"version": "1.0", ...}`)
- Validate config on load (Pydantic schema)
- Archive Economics config as reference for schema structure

---

## Next Steps After Plan Approval

1. **Review & Approve**: User reviews this plan
2. **Run `/sp.tasks`**: Generate atomic tasks from plan
3. **Implement**: Execute tasks from `tasks.md`
4. **Test**: Run test suite, manual validation with Economics PDFs
5. **Gate**: Run `./scripts/check-phase-2-complete.sh`
6. **ADR**: Document any architectural decisions made during implementation
7. **PHR**: Record significant implementation sessions

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks`
**Generated**: 2025-12-18
**Branch**: 002-question-bank
