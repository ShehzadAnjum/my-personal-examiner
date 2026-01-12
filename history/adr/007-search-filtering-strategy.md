# ADR-007: Search & Filtering Strategy

**Date**: 2025-12-19
**Status**: ✅ Accepted
**Phase**: Phase II - User Story 2 (Search & Filtering)
**Impact**: System Architecture, API Design, Database Performance

---

## Context and Problem Statement

Phase II Question Bank requires comprehensive search and filtering capabilities for students and teachers to find relevant questions efficiently.

**Key Requirements**:
- Search question text (full-text search)
- Filter by subject, paper, year, session, difficulty
- Filter by syllabus points (array containment)
- Filter by marks range (min/max)
- Pagination support (large result sets)
- Sorting (multiple fields, asc/desc)
- Mark scheme search
- Available filters extraction (for frontend dropdowns)

---

## Decision

**Implement SearchService with PostgreSQL-powered filtering, basic ILIKE search, and comprehensive pagination**

### Architecture

```
┌─────────────────────┐
│   SearchService     │
│  (Business Logic)   │
└──────────┬──────────┘
           │
           ├──► search_questions()
           │    - Full-text search (ILIKE)
           │    - Multiple filters (AND logic)
           │    - Pagination (page, page_size)
           │    - Sorting (year, marks, difficulty)
           │    - Syllabus point containment
           │
           ├──► search_mark_schemes()
           │    - Text search on mark_scheme_text
           │    - Basic filters (subject, year, paper)
           │    - Pagination
           │
           ├──► get_question_by_source_paper()
           │    - Direct question retrieval
           │    - By source_paper + question_number
           │
           ├──► get_mark_scheme_by_source_paper()
           │    - Direct mark scheme retrieval
           │    - Unique source_paper index
           │
           └──► get_available_filters()
                - Extract unique filter values
                - For frontend dropdown population
```

### API Endpoints

**1. Advanced Question Search** (`GET /api/questions/search`)
- Full-text search on question_text
- Multi-filter support (subject, paper, year, session, difficulty, marks range)
- Syllabus point filtering (array containment)
- Pagination (page, page_size, total_pages, has_next/prev)
- Sorting (year, max_marks, difficulty, created_at)

**2. Basic Question List** (`GET /api/questions`)
- Simplified version of search (common filters only)
- Delegates to SearchService for consistency

**3. Question Detail** (`GET /api/questions/{id}`)
- Single question retrieval by UUID

**4. Available Filters** (`GET /api/questions/filters`)
- Returns unique filter values for dropdowns
- Subject-specific or global

**5. Mark Scheme Search** (`GET /api/questions/mark-schemes/search`)
- Full-text search on mark_scheme_text
- Filters (subject, paper, year, session)
- Pagination

**6. Mark Scheme Detail** (`GET /api/questions/mark-schemes/{source_paper}`)
- Single mark scheme by source_paper identifier

---

## Key Design Decisions

### Decision 1: Basic ILIKE vs PostgreSQL Full-Text Search

**Problem**: How to implement text search on question_text?

**Options**:
- A: PostgreSQL ILIKE (case-insensitive LIKE) - chosen (Phase II)
- B: PostgreSQL full-text search (tsvector/tsquery) - deferred
- C: External search engine (Elasticsearch) - overkill for MVP

**Rationale**:
- **Phase II (MVP)**: ILIKE sufficient for basic search (simple, no additional setup)
- **Phase III+**: Migrate to tsvector/tsquery if performance degrades
- **Trade-off**: ILIKE can't handle complex queries (synonyms, stemming) but adequate for exact phrase matching

**Implementation**:
```python
if search_text:
    search_pattern = f"%{search_text}%"
    filters.append(Question.question_text.ilike(search_pattern))
```

**Future Enhancement (Phase III)**:
```sql
-- Add tsvector column
ALTER TABLE questions ADD COLUMN question_text_tsv tsvector;

-- Create GIN index
CREATE INDEX idx_question_text_fts ON questions USING GIN (question_text_tsv);

-- Auto-update trigger
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON questions FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(question_text_tsv, 'pg_catalog.english', question_text);
```

### Decision 2: Pagination Strategy

**Problem**: Handle large result sets (1000+ questions)

**Options**:
- A: Offset/Limit pagination (chosen)
- B: Cursor-based pagination (keyset)
- C: Scroll API (Elasticsearch-style)

**Rationale**:
- **Offset/Limit** simple, widely understood, works with SQL
- **Cursor-based** better performance for deep paging but complex UX
- **Trade-off**: Offset/Limit slow for large offsets (page 100+), acceptable for typical use cases

**Implementation**:
```python
offset = (page - 1) * page_size
stmt = stmt.offset(offset).limit(page_size)
```

**Pagination Metadata**:
```python
{
    "questions": [...],
    "total": 150,
    "page": 2,
    "page_size": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
}
```

**Validation**:
- `page` min: 1 (negative becomes 1)
- `page_size` min: 1, max: 100 (prevent abuse)

### Decision 3: Syllabus Point Filtering (Array Containment)

**Problem**: Filter questions by syllabus points (many-to-many relationship)

**Options**:
- A: Array containment operator `@>` (chosen)
- B: Junction table (questions_syllabus_points)
- C: JSONB containment

**Rationale**:
- **Array `@>` operator** leverages PostgreSQL native arrays
- **GIN index** on ARRAY[TEXT] supports fast containment queries
- **Simpler schema** than junction table
- **Trade-off**: Less flexible than junction table (no metadata per relationship)

**Implementation**:
```python
if syllabus_point_ids:
    filters.append(Question.syllabus_point_ids.contains(syllabus_point_ids))
```

**SQL Generated**:
```sql
SELECT * FROM questions
WHERE syllabus_point_ids @> ARRAY['uuid1', 'uuid2']::TEXT[];
```

### Decision 4: Filter Combination Logic (AND vs OR)

**Problem**: How to combine multiple filters?

**Decision**: AND logic for all filters
**Rationale**:
- **AND** more useful for narrowing search (students find "Economics 2022 Paper 2 hard questions")
- **OR** creates broad results (less useful)
- **Future**: Add `match_all` parameter for OR logic if needed

**Implementation**:
```python
if filters:
    stmt = stmt.where(and_(*filters))
```

### Decision 5: Sorting Options

**Problem**: What sorting options to support?

**Decision**: year, max_marks, difficulty, created_at, paper_number
**Rationale**:
- **Year** (desc): Most recent papers first
- **Marks** (asc/desc): Find high-value or low-value questions
- **Difficulty** (asc/desc): Progressive difficulty selection
- **Created_at**: Recently uploaded questions

**Default**: year DESC (most recent first)

**Implementation**:
```python
sort_column = {
    "year": Question.year,
    "max_marks": Question.max_marks,
    "difficulty": Question.difficulty,
    "created_at": Question.created_at,
    "paper_number": Question.paper_number,
}.get(sort_by, Question.year)

if sort_order == "asc":
    stmt = stmt.order_by(sort_column.asc())
else:
    stmt = stmt.order_by(sort_column.desc())
```

### Decision 6: Available Filters Endpoint

**Problem**: Frontend needs dropdown options (which years exist? which papers?)

**Decision**: `/api/questions/filters` endpoint returns unique values
**Rationale**:
- **Dynamic**: Reflects actual data (only shows years that have questions)
- **Filterable**: Can scope to subject (show only Economics years)
- **Performance**: Single query, extracts unique values in Python

**Implementation**:
```python
years = sorted(set(q.year for q in questions if q.year), reverse=True)
sessions = sorted(set(q.session for q in questions if q.session))
paper_numbers = sorted(set(q.paper_number for q in questions if q.paper_number))
difficulties = sorted(set(q.difficulty for q in questions if q.difficulty))
```

---

## Implementation Details

### SearchService Methods

**1. `search_questions()`**
- **Parameters**: search_text, subject_code, paper_number, year, session, difficulty, syllabus_point_ids, min_marks, max_marks, sort_by, sort_order, page, page_size
- **Returns**: dict with questions array + pagination metadata
- **Logic**:
  1. Build base SQLModel select statement
  2. Lookup subject by code (if filtered)
  3. Apply all filters (AND logic)
  4. Get total count (before pagination)
  5. Apply sorting
  6. Apply pagination (offset/limit)
  7. Execute query
  8. Calculate pagination metadata
  9. Return results

**2. `search_mark_schemes()`**
- **Parameters**: search_text, subject_code, paper_number, year, session, page, page_size
- **Returns**: dict with mark_schemes array + pagination metadata
- **Logic**: Similar to search_questions but simpler (fewer filters)

**3. `get_question_by_source_paper()`**
- **Parameters**: source_paper (e.g., "9708_s22_qp_22"), question_number (1, 2, 3)
- **Returns**: Question | None
- **Use Case**: Direct question retrieval for exam generation

**4. `get_mark_scheme_by_source_paper()`**
- **Parameters**: source_paper (e.g., "9708_s22_ms_22")
- **Returns**: MarkScheme | None
- **Use Case**: Fetch mark scheme for specific paper

**5. `get_available_filters()`**
- **Parameters**: subject_code (optional)
- **Returns**: dict with years, sessions, paper_numbers, difficulties arrays
- **Use Case**: Populate frontend filter dropdowns

### Database Indexes (Created in Migration 003)

**Questions Table**:
- B-tree index on `subject_id` (foreign key lookup)
- B-tree index on `paper_number` (filter queries)
- B-tree index on `year` (filter + sort queries)
- B-tree index on `session` (filter queries)
- B-tree index on `difficulty` (filter queries)
- GIN index on `syllabus_point_ids` (array containment @>)
- B-tree index on `source_paper` (direct lookup)

**Mark Schemes Table**:
- B-tree index on `subject_id`
- B-tree index on `paper_number`
- B-tree index on `year`
- B-tree index on `session`
- Unique index on `source_paper` (direct lookup, prevents duplicates)

---

## Consequences

### Positive

1. **Simple Implementation**: ILIKE search easy to understand and debug
2. **Good Performance**: Indexed filters fast for typical datasets (<10k questions)
3. **Flexible Filtering**: Multiple filters combine naturally (AND logic)
4. **Pagination Works**: Offset/limit adequate for expected usage
5. **Frontend-Friendly**: Available filters endpoint simplifies UI

### Negative

1. **ILIKE Performance**: Degrades with large datasets or complex patterns
2. **No Advanced Search**: Can't search "opportunity OR scarcity", no fuzzy matching
3. **Offset/Limit Limitation**: Deep pagination (page 100+) slow
4. **No Relevance Scoring**: Results not ranked by match quality

### Neutral

1. **Future Migration Path**: Can upgrade to full-text search without API changes
2. **Database-Dependent**: PostgreSQL-specific (array operators, ILIKE)

---

## Performance Characteristics

### Expected Query Times (10k questions)

| Query Type | Expected Time | Notes |
|------------|---------------|-------|
| **Basic filter** (year=2022) | <50ms | B-tree index scan |
| **Multi-filter** (subject+year+paper) | <100ms | Multiple index scans |
| **Text search** (ILIKE) | <200ms | Sequential scan (no FTS) |
| **Syllabus filter** (array @>) | <150ms | GIN index scan |
| **Pagination** (page 1-10) | <100ms | Small offset |
| **Pagination** (page 50+) | <500ms | Large offset (degrades) |
| **Count query** | <50ms | Index-only scan |

### Scalability Limits

- **10k questions**: Excellent performance (<200ms)
- **100k questions**: Good performance (<1s with indexes)
- **1M+ questions**: Consider full-text search migration

---

## Testing Strategy

### Unit Tests (Created but require mocking setup)

**Pagination Tests**:
- First page metadata (has_next=true, has_prev=false)
- Middle page metadata (has_next=true, has_prev=true)
- Last page metadata (has_next=false, has_prev=true)
- Page validation (negative → 1)
- Page size limits (max 100)

**Filtering Tests**:
- Subject code filter
- Year filter
- Marks range filter (min/max)
- Syllabus point array containment

**Sorting Tests**:
- Sort by year DESC (default)
- Sort by max_marks ASC

**Search Tests**:
- Case-insensitive search (ILIKE)
- Mark scheme text search

**Utility Tests**:
- Available filters extraction
- Get question by source_paper
- Get mark scheme by source_paper

### Integration Tests (Recommended for Phase III)

1. Upload 50 Economics questions from real PDFs
2. Search by text: "opportunity cost" → verify results
3. Filter by year: 2022 → count matches
4. Paginate through 50 results (page_size=10) → verify 5 pages
5. Sort by marks ASC → verify ordering
6. Filter by syllabus points → verify containment

---

## Future Enhancements (Phase III+)

### Phase III: Full-Text Search

**Implementation**:
```sql
-- Add tsvector column
ALTER TABLE questions ADD COLUMN question_text_tsv tsvector;

-- GIN index
CREATE INDEX idx_question_text_fts ON questions USING GIN (question_text_tsv);

-- Auto-update trigger
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON questions FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(question_text_tsv, 'pg_catalog.english', question_text);
```

**Benefits**:
- Stemming (search "running" finds "run")
- Ranking (relevance scoring)
- Multi-language support
- Boolean operators (AND, OR, NOT)

### Phase IV: Advanced Features

- **Faceted search**: Show counts per filter (e.g., "2022 (15 questions)")
- **Saved searches**: Store search criteria for quick access
- **Search history**: Track what students search
- **Autocomplete**: Suggest queries as user types

### Phase V: Elasticsearch Migration

**When to Consider**:
- >100k questions
- Multiple languages (non-English subjects)
- Complex search queries (fuzzy, proximity, wildcards)
- Advanced analytics (search trends, popular questions)

---

## Related Decisions

- **ADR-002**: Generic Extraction Framework (questions extracted need search)
- **ADR-006**: Question Upload & Storage Workflow (uploaded questions searchable)
- **Migration 003**: Database schema with indexes for search performance

---

## Validation

### Success Criteria (All Met ✅)

- [x] Search questions by text (ILIKE)
- [x] Filter by subject, paper, year, session, difficulty
- [x] Filter by marks range (min/max)
- [x] Filter by syllabus points (array containment)
- [x] Pagination support (page, page_size, metadata)
- [x] Sorting (multiple fields, asc/desc)
- [x] Mark scheme search
- [x] Available filters endpoint
- [x] SearchService created (comprehensive filtering logic)
- [x] API endpoints updated (search, filters, mark-schemes)

### API Response Examples

**Search Request**:
```
GET /api/questions/search?search_text=opportunity+cost&year=2022&difficulty=medium&page=1&page_size=10
```

**Search Response**:
```json
{
  "questions": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

---

## References

- **Code**: `src/services/search_service.py` (305 lines)
- **Routes**: `src/routes/questions.py` (updated with search endpoints)
- **Tests**: `tests/unit/test_search_service.py` (14 tests, require mocking setup)

---

**Decision Made By**: System Architect (AI Assistant)
**Approved By**: User (approved US2 implementation)
**Implementation Time**: 2 hours (search service + routes + tests)

**Status**: ✅ Implementation Complete, Ready for Integration Testing
