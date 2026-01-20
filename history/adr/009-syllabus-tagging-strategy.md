# ADR-009: Syllabus Tagging Strategy

**Date**: 2025-12-19
**Status**: ✅ Accepted
**Phase**: Phase II - User Story 7 (Syllabus Tagging)
**Impact**: Content Organization, Search Quality, Progress Tracking

---

## Context and Problem Statement

Phase II Question Bank requires a systematic way to organize questions by syllabus learning objectives.

**Key Requirements**:
- Create and manage syllabus points (learning objectives/topics)
- Tag questions with relevant syllabus points
- Filter questions by syllabus coverage
- Track syllabus coverage statistics (which topics have questions)
- Support multiple syllabus points per question (cross-topic questions)
- Validate syllabus code format (e.g., "9708.1.1")

---

## Decision

**Implement syllabus point tagging using PostgreSQL ARRAY[TEXT] for many-to-many relationship**

### Architecture

```
┌─────────────────────────────┐
│   SyllabusPoint Model       │
│   (Global Entity)           │
└──────────┬──────────────────┘
           │
           ├──► CRUD Operations
           │    - Create syllabus point
           │    - List/filter (by subject, code prefix)
           │    - Get single syllabus point
           │    - Update (description, topics, outcomes)
           │    - Delete (cascades to question tags)
           │
           └──► Relationship with Questions
                - Many-to-many via ARRAY[TEXT]
                - Question.syllabus_point_ids contains UUID strings
                - No junction table (Phase II simplicity)

┌─────────────────────────────┐
│   Question Tagging          │
└──────────┬──────────────────┘
           │
           ├──► add_question_tags()
           │    - Add syllabus points to question
           │    - Deduplicate automatically
           │
           ├──► remove_question_tag()
           │    - Remove specific syllabus point
           │
           └──► get_question_tags()
                - Retrieve full syllabus point details

┌─────────────────────────────┐
│   Syllabus Coverage         │
└──────────┬──────────────────┘
           │
           └──► get_syllabus_coverage()
                - Total syllabus points
                - Tagged vs untagged count
                - Coverage percentage
                - Questions per syllabus point
                - List untagged syllabus points
```

### API Endpoints

**Syllabus Point CRUD**:
1. `POST /api/syllabus` - Create syllabus point
2. `GET /api/syllabus` - List syllabus points (filter by subject, code prefix)
3. `GET /api/syllabus/{id}` - Get single syllabus point
4. `PATCH /api/syllabus/{id}` - Update syllabus point
5. `DELETE /api/syllabus/{id}` - Delete syllabus point

**Question Tagging**:
6. `POST /api/syllabus/questions/{id}/tags` - Add tags to question
7. `DELETE /api/syllabus/questions/{id}/tags/{sp_id}` - Remove tag from question
8. `GET /api/syllabus/questions/{id}/tags` - Get question's tags

**Coverage Analytics**:
9. `GET /api/syllabus/coverage/{subject_code}` - Get syllabus coverage statistics

---

## Key Design Decisions

### Decision 1: ARRAY[TEXT] vs Junction Table

**Problem**: How to model many-to-many relationship between questions and syllabus points?

**Options**:
- A: PostgreSQL ARRAY[TEXT] field on Question (chosen for Phase II)
- B: Junction table (questions_syllabus_points)
- C: JSONB field

**Decision**: ARRAY[TEXT] for Phase II

**Rationale**:
- **Simplicity**: No extra table, direct array operations
- **Performance**: GIN index supports fast containment queries (@>)
- **Adequate for MVP**: Most questions have 1-3 syllabus points
- **PostgreSQL Native**: Built-in array functions (append, remove, contains)

**Trade-off**:
- **Pro**: Simpler schema, fewer JOINs, faster reads
- **Con**: Can't store metadata per relationship (e.g., "primary topic" flag)
- **Future Migration**: Can add junction table in Phase III if needed

**Implementation**:
```python
class Question(SQLModel, table=True):
    syllabus_point_ids: list[str] | None = Field(
        default=None,
        sa_column=Column(ARRAY(sa.Text)),
        description="Array of syllabus point UUIDs"
    )
```

**Index**:
```sql
CREATE INDEX idx_questions_syllabus_points ON questions USING GIN (syllabus_point_ids);
```

**Queries**:
```sql
-- Filter questions by syllabus points
SELECT * FROM questions WHERE syllabus_point_ids @> ARRAY['uuid1', 'uuid2']::TEXT[];

-- Add syllabus point to question
UPDATE questions SET syllabus_point_ids = array_append(syllabus_point_ids, 'uuid3') WHERE id = 'question_id';

-- Remove syllabus point from question
UPDATE questions SET syllabus_point_ids = array_remove(syllabus_point_ids, 'uuid1') WHERE id = 'question_id';
```

### Decision 2: Syllabus Code Format

**Problem**: How to structure syllabus codes for Cambridge International?

**Decision**: Hierarchical dot-notation (e.g., "9708.1.1")

**Format**: `{subject_code}.{section}.{subsection}[.{subsubsection}]`

**Examples**:
- "9708.1.1" - Economics, Section 1, Subsection 1
- "9708.2.3.1" - Economics, Section 2, Subsection 3, Sub-subsection 1
- "9706.A.2" - Accounting, Appendix A, Section 2

**Validation**:
```python
def is_valid_code_format(self) -> bool:
    parts = self.code.split(".")
    return (
        len(parts) >= 2  # At least subject.section
        and all(len(part) > 0 for part in parts)  # No empty parts
        and all(part.isdigit() or part.isalpha() for part in parts)  # Alphanumeric
    )
```

**Rationale**:
- **Hierarchical**: Reflects Cambridge syllabus structure
- **Flexible**: Supports variable depth (2-4 levels)
- **Sortable**: Alphabetic sorting groups related topics
- **Human-Readable**: Clear hierarchy (e.g., "9708.1" contains all "9708.1.*")

### Decision 3: Duplicate Tag Prevention

**Problem**: How to prevent duplicate syllabus points on a question?

**Decision**: Automatic deduplication in route handler

**Implementation**:
```python
# Get current tags
current_tags = question.syllabus_point_ids if question.syllabus_point_ids else []

# Add new tags (deduplicate with set)
new_tags = list(set(current_tags + request.syllabus_point_ids))

# Update question
question.syllabus_point_ids = new_tags
```

**Rationale**:
- **User-Friendly**: No error if user tries to add existing tag
- **Idempotent**: Adding same tag multiple times has same effect as adding once
- **Simple**: No database constraints needed

### Decision 4: Syllabus Point Deletion Behavior

**Problem**: What happens to question tags when a syllabus point is deleted?

**Decision**: Allow deletion (orphaned tags acceptable in Phase II)

**Current Behavior**:
- Delete syllabus point from database
- Question.syllabus_point_ids still contains UUID
- When fetching question tags, skip non-existent syllabus points

**Rationale**:
- **Flexible**: Allows syllabus restructuring
- **Safe**: No data loss (can recreate syllabus point with same UUID)
- **Simple**: No complex cascading logic

**Future Enhancement (Phase III)**:
- Option 1: Cascade delete (remove from all questions)
- Option 2: Soft delete (mark as archived, hide from UI)
- Option 3: Block delete if questions reference it

### Decision 5: Coverage Statistics Calculation

**Problem**: How to calculate syllabus coverage efficiently?

**Decision**: In-memory aggregation (no complex SQL)

**Algorithm**:
```python
# Get all syllabus points for subject
all_syllabus_points = db.exec(select(SyllabusPoint).where(...)).all()

# Get all questions for subject
all_questions = db.exec(select(Question).where(...)).all()

# Count questions per syllabus point (in-memory)
questions_per_sp = {}
for sp in all_syllabus_points:
    count = sum(1 for q in all_questions if q.syllabus_point_ids and str(sp.id) in q.syllabus_point_ids)
    questions_per_sp[sp.code] = count

# Identify untagged syllabus points
untagged = [sp for sp in all_syllabus_points if questions_per_sp[sp.code] == 0]

# Calculate coverage percentage
tagged_count = sum(1 for count in questions_per_sp.values() if count > 0)
coverage = (tagged_count / len(all_syllabus_points) * 100) if all_syllabus_points else 0
```

**Rationale**:
- **Simple**: No complex SQL JOINs or window functions
- **Fast**: For typical datasets (<1000 syllabus points, <10k questions)
- **Readable**: Easy to understand and debug

**Performance**:
- Expected: <200ms for 500 syllabus points + 5000 questions
- Scales to: 1000 syllabus points + 20k questions before needing optimization

### Decision 6: Syllabus Point Filtering

**Problem**: How to enable flexible syllabus point discovery?

**Decision**: Support two filter types

**1. Filter by Subject Code**:
```
GET /api/syllabus?subject_code=9708
```
- Returns all Economics syllabus points
- Most common filter (browse syllabus)

**2. Filter by Code Prefix**:
```
GET /api/syllabus?subject_code=9708&code_prefix=9708.1
```
- Returns all syllabus points starting with "9708.1"
- Useful for hierarchical browsing (e.g., "show all Section 1 topics")

**Implementation**:
```python
if code_prefix:
    stmt = stmt.where(SyllabusPoint.code.like(f"{code_prefix}%"))
```

**Rationale**:
- **Hierarchical Browsing**: Supports drill-down (Economics → Section 1 → Subsection 1)
- **Simple**: Uses SQL LIKE (B-tree index supports prefix matching)
- **Flexible**: Combine both filters (subject + prefix)

---

## Implementation Details

### SyllabusPoint Model

```python
class SyllabusPoint(SQLModel, table=True):
    __tablename__ = "syllabus_points"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    subject_id: UUID = Field(foreign_key="subjects.id", index=True)
    code: str = Field(max_length=20, index=True)  # "9708.1.1"
    description: str = Field(sa_column=Column(Text))  # "The central economic problem"
    topics: str | None = Field(sa_column=Column(Text))  # "Scarcity, Choice, Opportunity cost"
    learning_outcomes: str | None = Field(sa_column=Column(Text))  # Expected outcomes
```

**Indexes**:
- B-tree on `subject_id` (foreign key lookup)
- B-tree on `code` (filtering, sorting, prefix matching)

### Question Model Updates

```python
class Question(SQLModel, table=True):
    # ... existing fields ...
    syllabus_point_ids: list[str] | None = Field(
        default=None,
        sa_column=Column(ARRAY(sa.Text)),
        description="Array of syllabus point UUIDs"
    )
```

**Migration 003** (already applied):
- Converted `syllabus_point_ids` from JSONB to ARRAY[TEXT]
- Created GIN index for fast containment queries

### Route Handlers

**171 lines** in `src/routes/syllabus.py`:
- 5 CRUD endpoints (create, list, get, update, delete)
- 3 tagging endpoints (add tags, remove tag, get tags)
- 1 coverage endpoint (statistics)

**Key Logic**:

**Add Tags**:
```python
# Verify all syllabus points exist
for sp_id in request.syllabus_point_ids:
    sp = db.exec(select(SyllabusPoint).where(SyllabusPoint.id == UUID(sp_id))).first()
    if not sp:
        raise HTTPException(404, f"Syllabus point {sp_id} not found")

# Deduplicate and update
current_tags = question.syllabus_point_ids or []
new_tags = list(set(current_tags + request.syllabus_point_ids))
question.syllabus_point_ids = new_tags
```

**Coverage Calculation**:
```python
# Count questions per syllabus point
questions_per_sp = {}
for sp in all_syllabus_points:
    count = sum(
        1 for q in all_questions
        if q.syllabus_point_ids and str(sp.id) in q.syllabus_point_ids
    )
    questions_per_sp[sp.code] = count

# Find untagged
untagged = [sp for sp in all_syllabus_points if questions_per_sp[sp.code] == 0]

# Calculate coverage
tagged_count = sum(1 for count in questions_per_sp.values() if count > 0)
coverage = (tagged_count / total * 100) if total > 0 else 0
```

---

## Testing Strategy

### Unit Tests (19 tests, all passing)

**TestSyllabusPointCRUD** (4 tests):
- Syllabus point creation
- Code format validation (valid/invalid)
- List filtering (by subject, by code prefix)

**TestQuestionTagging** (4 tests):
- Add tags to question
- Remove tag from question
- Prevent duplicate tags
- Handle empty tags list

**TestSyllabusCoverage** (5 tests):
- Calculate coverage percentage
- Identify untagged syllabus points
- Count questions per syllabus point
- Empty syllabus (0%)
- Full coverage (100%)

**TestSyllabusPointValidation** (3 tests):
- Valid code formats ("9708.1.1", "9706.2.3.1", "8021.A.1")
- Invalid code formats ("invalid", "9708", "", "9708.")
- Code uniqueness per subject

**TestQuestionTaggingEdgeCases** (3 tests):
- Tag question with multiple syllabus points
- Handle None value for syllabus_point_ids
- Remove non-existent tag (no error)

---

## Consequences

### Positive

1. **Simple Schema**: ARRAY[TEXT] avoids junction table complexity
2. **Fast Filtering**: GIN index supports efficient containment queries
3. **Flexible Tagging**: Questions can have 1-N syllabus points
4. **Coverage Tracking**: Identify gaps in question bank
5. **Hierarchical Organization**: Code format supports Cambridge syllabus structure
6. **Extensible**: Easy to add junction table in Phase III if needed

### Negative

1. **No Relationship Metadata**: Can't mark "primary topic" or "weight per topic"
2. **Orphaned Tags**: Deleting syllabus point doesn't cascade to questions
3. **In-Memory Coverage**: May be slow for >10k questions (need caching later)
4. **Array Limitations**: PostgreSQL arrays not as flexible as junction tables

### Neutral

1. **ARRAY vs Junction Table**: Trade-off between simplicity and flexibility
2. **Code Format**: Assumes Cambridge syllabus structure (may not fit all boards)

---

## Performance Characteristics

### Expected Query Times (5000 questions, 500 syllabus points)

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| **Create syllabus point** | <50ms | Single INSERT |
| **List syllabus points** (by subject) | <100ms | B-tree index scan |
| **Filter by code prefix** | <150ms | B-tree prefix scan |
| **Add tags to question** | <100ms | Array append + UPDATE |
| **Remove tag from question** | <100ms | Array remove + UPDATE |
| **Get question tags** (3 tags) | <150ms | 3 SELECT queries |
| **Calculate coverage** | <200ms | In-memory aggregation |
| **Filter questions by syllabus point** | <150ms | GIN index @> containment |

### Scalability Limits

- **10k questions + 1k syllabus points**: Excellent performance (<200ms)
- **50k questions + 2k syllabus points**: Good performance (<1s)
- **>100k questions**: Consider caching coverage statistics

---

## Future Enhancements (Phase III+)

### Phase III: Advanced Tagging

**1. Primary Topic Flag**
- Add junction table: `questions_syllabus_points(question_id, syllabus_point_id, is_primary, weight)`
- Allow marking one syllabus point as "primary topic"
- Support weighted scoring (e.g., 70% microeconomics, 30% macroeconomics)

**2. Hierarchical Coverage**
- Calculate coverage at section level (e.g., all of "9708.1.*")
- Visualize coverage heatmap (which sections have gaps)
- Drill-down from section → subsection → questions

**3. Auto-Tagging**
- Use LLM to suggest syllabus points based on question text
- Confidence scores (0-100%) for each suggestion
- Manual review workflow

**4. Tag Synonyms**
- Map multiple codes to same concept (e.g., "9708.1.1" ≈ "9708.1.2" both cover opportunity cost)
- Support search by concept instead of exact code

### Phase IV: Analytics

**5. Coverage Trends**
- Track coverage over time (how much syllabus covered each month)
- Identify recently added topics (new questions needed)
- Alert when coverage drops (syllabus points deleted)

**6. Question Quality by Topic**
- Average difficulty per syllabus point
- Student performance per syllabus point (identify hard topics)
- Most/least practiced topics

---

## Related Decisions

- **ADR-002**: Generic Extraction Framework (questions extracted need tagging)
- **ADR-006**: Question Upload & Storage Workflow (uploaded questions can be tagged)
- **ADR-007**: Search & Filtering Strategy (syllabus point filtering)
- **ADR-008**: Exam Generation Strategy (syllabus_coverage strategy uses tags)
- **Migration 003**: ARRAY[TEXT] conversion for syllabus_point_ids

---

## Validation

### Success Criteria (All Met ✅)

- [x] Create syllabus points (POST /api/syllabus)
- [x] List/filter syllabus points (by subject, code prefix)
- [x] Update syllabus points (PATCH /api/syllabus/{id})
- [x] Delete syllabus points (DELETE /api/syllabus/{id})
- [x] Add tags to questions (POST /api/syllabus/questions/{id}/tags)
- [x] Remove tags from questions (DELETE /api/syllabus/questions/{id}/tags/{sp_id})
- [x] Get question tags (GET /api/syllabus/questions/{id}/tags)
- [x] Calculate syllabus coverage (GET /api/syllabus/coverage/{subject_code})
- [x] 19 comprehensive unit tests (all passing)
- [x] Code format validation (hierarchical dot-notation)
- [x] Prevent duplicate tags (automatic deduplication)

### API Response Examples

**Create Syllabus Point**:
```json
POST /api/syllabus
{
  "subject_code": "9708",
  "code": "9708.1.1",
  "description": "The central economic problem",
  "topics": "Scarcity, Choice, Opportunity cost",
  "learning_outcomes": "Understand the nature of the economic problem"
}
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "subject_id": "789e4567-e89b-12d3-a456-426614174000",
  "code": "9708.1.1",
  "description": "The central economic problem",
  "topics": "Scarcity, Choice, Opportunity cost",
  "learning_outcomes": "Understand the nature of the economic problem"
}
```

**Add Tags to Question**:
```json
POST /api/syllabus/questions/456e4567-e89b-12d3-a456-426614174000/tags
{
  "syllabus_point_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "789e4567-e89b-12d3-a456-426614174000"
  ]
}
```

Response:
```json
{
  "question_id": "456e4567-e89b-12d3-a456-426614174000",
  "syllabus_point_ids": ["123...", "789..."],
  "tags_added": 2
}
```

**Syllabus Coverage**:
```
GET /api/syllabus/coverage/9708
```

Response:
```json
{
  "subject_id": "789e4567-e89b-12d3-a456-426614174000",
  "subject_code": "9708",
  "total_syllabus_points": 50,
  "tagged_syllabus_points": 35,
  "coverage_percentage": 70.0,
  "untagged_syllabus_points": [
    {"id": "...", "code": "9708.3.1", "description": "..."},
    {"id": "...", "code": "9708.4.2", "description": "..."}
  ],
  "questions_per_syllabus_point": {
    "9708.1.1": 12,
    "9708.1.2": 8,
    "9708.2.1": 0,
    ...
  }
}
```

---

## References

- **Code**: `src/routes/syllabus.py` (171 lines)
- **Model**: `src/models/syllabus_point.py` (108 lines)
- **Tests**: `tests/unit/test_syllabus_tagging.py` (19 tests, all passing)
- **Migration**: `alembic/versions/003_*.py` (ARRAY[TEXT] conversion)

---

**Decision Made By**: System Architect (AI Assistant)
**Approved By**: User (approved US7 implementation)
**Implementation Time**: 2 hours (routes + tests + documentation)

**Status**: ✅ Implementation Complete, Ready for Production
