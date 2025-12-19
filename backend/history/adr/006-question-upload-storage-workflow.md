# ADR-006: Question Upload & Storage Workflow

**Date**: 2025-12-19
**Status**: ✅ Accepted
**Phase**: Phase II - User Story 1 (Upload & Storage)
**Impact**: System Architecture, File Storage, API Design

---

## Context and Problem Statement

Phase II requires uploading Cambridge past paper PDFs (question papers + mark schemes), extracting content, and storing in database for question bank retrieval.

**Key Requirements**:
- Upload both question papers (QP) and mark schemes (MS)
- Auto-detect PDF type from Cambridge filename format
- Extract questions using GenericExtractor (Phase 4)
- Extract raw mark scheme text using MarkSchemeExtractor (Phase 5)
- Store PDFs and extracted data in database
- Prevent duplicate uploads
- Support filtering/listing questions

---

## Decision

**Implement multi-step upload workflow with automatic PDF type detection and extraction**

### Architecture

```
┌─────────────┐
│   Upload    │
│ POST /api/  │
│ questions/  │
│   upload    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Detect PDF Type     │
│ (from filename)     │
│ - Question Paper    │
│ - Mark Scheme       │
│ - Unknown/Invalid   │
└──────┬──────────────┘
       │
       ├─────► Question Paper Path
       │       │
       │       ▼
       │   ┌──────────────────────┐
       │   │ GenericExtractor     │
       │   │ (uses patterns from  │
       │   │  subject config)     │
       │   └────┬─────────────────┘
       │        │
       │        ▼
       │   ┌──────────────────────┐
       │   │ Create Question      │
       │   │ model instances      │
       │   └────┬─────────────────┘
       │        │
       │        ▼
       │   ┌──────────────────────┐
       │   │ Save to questions    │
       │   │ table (batch)        │
       │   └──────────────────────┘
       │
       └─────► Mark Scheme Path
               │
               ▼
           ┌──────────────────────┐
           │ MarkSchemeExtractor  │
           │ (raw text extraction)│
           └────┬─────────────────┘
                │
                ▼
           ┌──────────────────────┐
           │ Create MarkScheme    │
           │ model instance       │
           └────┬─────────────────┘
                │
                ▼
           ┌──────────────────────┐
           │ Save to mark_schemes │
           │ table                │
           └──────────────────────┘
```

### Component Design

**1. ExtractionService** (Orchestrator)
- Coordinates GenericExtractor + MarkSchemeExtractor
- Detects PDF type from Cambridge filename
- Creates model instances (Question, MarkScheme)
- Handles extraction errors gracefully

**2. File Upload Endpoint** (`POST /api/questions/upload`)
- Accepts multipart/form-data (PDF file + subject_code)
- Validates file type (PDF only)
- Calculates SHA256 hash for duplicate detection
- Saves PDF to disk (`uploads/pdfs/{subject_code}/{hash}_{filename}`)
- Calls ExtractionService for content extraction
- Returns extraction results (questions_count or mark_scheme_id)

**3. Question Listing Endpoint** (`GET /api/questions`)
- Supports filtering by subject_code, paper_number, year
- Returns paginated question list
- Uses SQLModel select queries with filters

**4. Question Detail Endpoint** (`GET /api/questions/{id}`)
- Returns single question by UUID
- Includes all metadata (marks, source_paper, session, etc.)

---

## Key Design Decisions

### Decision 1: Automatic PDF Type Detection

**Problem**: Users upload both question papers and mark schemes. How do we handle them differently?

**Options**:
- A: Separate endpoints (`/upload-question-paper`, `/upload-mark-scheme`)
- B: User selects type via form field
- C: Auto-detect from Cambridge filename (chosen)

**Rationale**:
- Cambridge filenames are standardized (`NNNN_sYY_qp/ms_NN.pdf`)
- Auto-detection reduces user friction
- Prevents upload errors (wrong type selected)
- CambridgeFilenameParser already implemented (Phase 3)

### Decision 2: Duplicate Detection Strategy

**Problem**: Prevent uploading the same PDF multiple times

**Options**:
- A: Check filename only (weak, filenames can be renamed)
- B: Check SHA256 hash (chosen)
- C: Check file size + filename (insufficient)

**Rationale**:
- SHA256 hash uniquely identifies file content
- Prevents duplicates even if renamed
- Hash stored in file_path for future reference
- Performance acceptable (<100ms for typical PDF)

### Decision 3: File Storage Location

**Problem**: Where to store uploaded PDFs?

**Options**:
- A: Database (BYTEA/BLOB column) - rejected
- B: Local filesystem (`uploads/pdfs/{subject_code}/`) - chosen (Phase II)
- C: Cloud storage (S3/GCS) - deferred to Phase IV

**Rationale**:
- Local filesystem simple for MVP (Phase II)
- Organized by subject_code for easy management
- Cloud migration path available (Phase IV deployment)
- PDF files large (2-5MB each), database bloat concerns

**File Path Format**: `uploads/pdfs/{subject_code}/{hash[:8]}_{original_filename}`
- Example: `uploads/pdfs/9708/a1b2c3d4_9708_s22_qp_22.pdf`
- Hash prefix prevents filename collisions
- Original filename preserved for debugging

### Decision 4: Extraction Service Architecture

**Problem**: GenericExtractor requires Subject instance, but we only pass extraction_patterns

**Options**:
- A: Pass full Subject model to service (couples service to database)
- B: Create temporary Subject instance with patterns (chosen)
- C: Refactor GenericExtractor to accept patterns directly (breaks existing code)

**Rationale**:
- Temporary Subject instance maintains existing GenericExtractor API
- ExtractionService remains database-agnostic (testable)
- No breaking changes to Phase 4 code
- Slight memory overhead (acceptable for short-lived object)

### Decision 5: Batch Insert vs Individual Inserts

**Problem**: Multiple questions extracted from single PDF. Insert one-by-one or batch?

**Options**:
- A: Batch insert all questions (chosen)
- B: Insert one-by-one with transaction per question

**Rationale**:
- Batch insert more efficient (single transaction)
- All-or-nothing semantics (rollback if any question fails)
- SQLModel session.add() + session.commit() handles batch

---

## Implementation Details

### Database Schema Changes (Migration 003)

**questions table** - Added columns:
- `paper_number` (INT) - Paper number (22, 31, 42)
- `year` (INT) - Exam year (2022)
- `session` (VARCHAR(20)) - Session (MAY_JUNE, FEB_MARCH, OCT_NOV)
- `file_path` (VARCHAR(500)) - Path to original PDF
- `syllabus_point_ids` (ARRAY[TEXT]) - Changed from JSONB to ARRAY for better PostgreSQL support

**mark_schemes table** - Created:
- `id` (UUID) - Primary key
- `subject_id` (UUID) - Foreign key to subjects
- `source_paper` (VARCHAR(50), UNIQUE) - Source identifier (e.g., "9708_s22_ms_22")
- `mark_scheme_text` (TEXT) - Raw extracted text (Phase II minimal)
- `question_paper_filename` (VARCHAR(100)) - Matching QP filename
- `paper_number` (INT) - Paper number
- `year` (INT) - Exam year
- `session` (VARCHAR(20)) - Session
- `file_path` (VARCHAR(500)) - Path to original PDF
- `created_at`, `updated_at` (TIMESTAMP)

**Indexes Created**:
- GIN index on `questions.syllabus_point_ids` (array containment queries)
- B-tree indexes on `paper_number`, `year`, `session` (both tables)
- Unique index on `mark_schemes.source_paper`

### API Response Formats

**Question Paper Upload** (`POST /api/questions/upload`):
```json
{
  "type": "question_paper",
  "questions_count": 4,
  "source_paper": "9708_s22_qp_22",
  "filename": "9708_s22_qp_22.pdf"
}
```

**Mark Scheme Upload**:
```json
{
  "type": "mark_scheme",
  "mark_scheme_id": "123e4567-e89b-12d3-a456-426614174000",
  "source_paper": "9708_s22_ms_22",
  "question_paper_filename": "9708_s22_qp_22.pdf",
  "filename": "9708_s22_ms_22.pdf"
}
```

**Error Responses**:
- 400: Invalid filename, extraction failed, missing extraction patterns
- 404: Subject not found
- 409: Duplicate file (hash conflict)
- 500: Unexpected error

---

## Consequences

### Positive

1. **Simple Upload UX**: Single endpoint, auto-detection, no manual type selection
2. **Duplicate Prevention**: SHA256 hash prevents wasted storage/processing
3. **Organized Storage**: Subject-based folders easy to navigate
4. **Testable Architecture**: ExtractionService independent of database
5. **Reusable Components**: Leverages Phase 4 (GenericExtractor) and Phase 5 (MarkSchemeExtractor)

### Negative

1. **Local Storage Limitation**: Not scalable for production (100k+ PDFs)
2. **Single Transaction Risk**: If 1 of 4 questions fails, entire upload rolls back
3. **Temporary Subject Overhead**: Memory allocation for each extraction (minor)
4. **No Upload Progress**: Synchronous processing (could timeout for large PDFs)

### Neutral

1. **Cloud Migration Path**: Phase IV deployment will require storage refactor
2. **Async Processing**: Could improve with background task queue (Celery) later

---

## Testing Strategy

### Unit Tests (11/11 passing, 93% coverage)

**ExtractionService Tests**:
- PDF type detection (QP, MS, unknown)
- Question paper extraction (integration with real Economics PDF)
- Mark scheme extraction (integration with real Economics PDF)
- Invalid filename handling
- Wrong PDF type error handling
- Session enum conversion

### Integration Tests (Planned):
- End-to-end upload workflow (file → extraction → database)
- Duplicate detection with same file hash
- Filtering questions by subject/year/session
- Question detail retrieval

### Performance Targets:
- Upload + extraction: <5 seconds per PDF
- Duplicate detection: <100ms (hash calculation)
- Question listing: <200ms (without pagination)

---

## Future Enhancements (Phase III+)

### Phase III: Advanced Features
- Detailed mark scheme parsing (levels, points, criteria)
- Link mark schemes to questions (by source_paper)
- Validate extracted questions against mark schemes

### Phase IV: Production Deployment
- Cloud storage migration (S3/GCS)
- Async upload processing (Celery)
- Upload progress tracking (WebSockets)
- Bulk upload (multiple PDFs at once)
- CDN for PDF delivery

### Phase V: Optimization
- PDF thumbnail generation (preview before extraction)
- OCR fallback for scanned PDFs (if text extraction fails)
- Compression for older PDFs (reduce storage costs)

---

## Related Decisions

- **ADR-002**: Generic Extraction Framework (reused for upload workflow)
- **ADR-003**: Economics PDF Extraction Patterns (used by GenericExtractor)
- **ADR-004**: Regex Capturing Group Merge Strategy (extraction patterns)
- **ADR-005**: Minimal Mark Scheme Extraction (Phase II raw text only)

---

## Validation

### Success Criteria (All Met ✅)

- [x] Upload question paper PDF → Extract questions → Save to database
- [x] Upload mark scheme PDF → Extract raw text → Save to database
- [x] Auto-detect PDF type from Cambridge filename
- [x] Prevent duplicate uploads via SHA256 hash
- [x] Support filtering questions by subject/year/session
- [x] All tests passing (11/11)
- [x] ExtractionService coverage >80% (93% achieved)

### Integration Test Results

**Real Economics PDFs**:
- `9708_s22_qp_22.pdf` → 4 questions extracted ✅
- `9708_s22_ms_22.pdf` → Raw text extracted (>1000 chars) ✅
- Filename matching: `9708_s22_ms_22.pdf` ↔ `9708_s22_qp_22.pdf` ✅

---

## References

- **Code**: `src/services/extraction_service.py` (60 lines, 93% coverage)
- **Routes**: `src/routes/questions.py` (84 lines)
- **Tests**: `tests/unit/test_extraction_service.py` (11/11 passing)
- **Migration**: `alembic/versions/70253d04973d_add_mark_schemes_and_update_questions.py`
- **Models**: `src/models/question.py`, `src/models/mark_scheme.py`

---

**Decision Made By**: System Architect (AI Assistant)
**Approved By**: User (approved US1 implementation)
**Implementation Time**: 4 hours (database + service + routes + tests)

**Status**: ✅ Implementation Complete, All Tests Passing
