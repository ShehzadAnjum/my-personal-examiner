# Research: Academic Level Hierarchy

**Feature**: 008-academic-level-hierarchy
**Date**: 2026-01-05
**Status**: Complete

---

## Research Question 1: Best Pattern for Hierarchical Data in SQLModel

### Decision: Adjacency List Pattern

### Rationale

For a simple three-level hierarchy (Academic Level → Subject → Syllabus), the adjacency list pattern is optimal:

- **Simple to implement**: Each child table has a foreign key to its parent
- **Easy to query**: Standard SQL joins work perfectly
- **Good performance**: 3 levels max, no need for recursive queries
- **SQLModel native**: Natural fit with SQLModel relationships

### Alternatives Considered

| Pattern | Pros | Cons | Why Rejected |
|---------|------|------|--------------|
| Nested Sets | Fast subtree queries | Complex updates, integrity risks | Overkill for 3 levels |
| Materialized Path | Fast ancestry queries | String manipulation, size limits | Not needed for shallow tree |
| Closure Table | Flexible queries | Extra table overhead | Too complex for simple hierarchy |
| **Adjacency List** | Simple, performant | Deep trees slow (not our case) | **SELECTED** |

### Implementation

```python
# Academic Level (root)
class AcademicLevel(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str  # "A-Level"
    code: str  # "A"

# Subject (child of Academic Level)
class Subject(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str  # "Economics"
    academic_level_id: UUID = Field(foreign_key="academic_levels.id")

# Syllabus (child of Subject)
class Syllabus(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    code: str  # "9708"
    subject_id: UUID = Field(foreign_key="subjects.id")
```

---

## Research Question 2: Cascade Delete Behavior

### Decision: Restrict Delete (Prevent deletion if children exist)

### Rationale

For educational data integrity:
- Deleting an academic level should NOT cascade-delete subjects, syllabi, and syllabus points
- Admin must explicitly delete children first or be warned about orphaned data
- Student progress data (linked to syllabus points) must be preserved

### Implementation

```python
# PostgreSQL constraint
academic_level_id: UUID = Field(
    foreign_key="academic_levels.id",
    sa_column_kwargs={"ondelete": "RESTRICT"}
)
```

### UI Behavior

When admin tries to delete:
1. Check for children
2. If children exist: Show error "Cannot delete X - it has Y subjects. Delete them first or reassign."
3. If no children: Allow delete with confirmation

### Alternatives Considered

| Behavior | Pros | Cons | Why Rejected |
|----------|------|------|--------------|
| CASCADE | Simple, automatic | Dangerous data loss | Accidental deletion risk |
| SET NULL | Preserves children | Creates orphans | No clear parent relationship |
| **RESTRICT** | Safest, explicit | Requires manual cleanup | **SELECTED** - best for education |

---

## Research Question 3: Backward Compatibility for Existing Data

### Decision: Two-Phase Migration with Data Preservation

### Rationale

Existing `syllabus_points` table has `subject_id` FK. We need to:
1. Create new tables (academic_levels, syllabi)
2. Migrate data from subjects to syllabi
3. Update syllabus_points FK from subject_id to syllabus_id
4. Keep subject_id temporarily for rollback

### Migration Steps

```sql
-- Phase 1: Add new structures
CREATE TABLE academic_levels (...);
CREATE TABLE syllabi (...);

-- Phase 2: Populate from existing data
INSERT INTO academic_levels (id, name, code, exam_board)
SELECT DISTINCT gen_random_uuid(),
    CASE WHEN level = 'A' THEN 'A-Level' ELSE level || '-Level' END,
    level,
    exam_board
FROM subjects;

INSERT INTO syllabi (id, code, year_range, subject_id)
SELECT gen_random_uuid(), code, syllabus_year, id
FROM subjects;

-- Phase 3: Update syllabus_points
ALTER TABLE syllabus_points ADD COLUMN syllabus_id UUID;
UPDATE syllabus_points sp
SET syllabus_id = s.id
FROM syllabi s
JOIN subjects sub ON s.subject_id = sub.id
WHERE sp.subject_id = sub.id;

-- Phase 4: Make syllabus_id NOT NULL, drop old subject_id
ALTER TABLE syllabus_points ALTER COLUMN syllabus_id SET NOT NULL;
ALTER TABLE syllabus_points DROP COLUMN subject_id;
```

### Rollback Strategy

- Keep old columns with `nullable=True` during transition
- Store mapping table for reverse migration
- Test migration on copy of production data first

---

## Research Question 4: Multi-Step Wizard State Management (Frontend)

### Decision: URL-based State with React Context

### Rationale

For the 3-step wizard (Academic Level → Subject → Syllabus):
- URL params track current step and parent IDs
- React Context stores in-progress data
- TanStack Query caches API responses
- LocalStorage optional for crash recovery

### Implementation

```typescript
// URL pattern
/admin/setup/academic-levels           # Step 1: Create/select level
/admin/setup/subjects?level_id=xxx     # Step 2: Create subject under level
/admin/setup/syllabus?subject_id=xxx   # Step 3: Upload syllabus

// Context for wizard state
interface SetupWizardContext {
  academicLevel: AcademicLevel | null;
  subject: Subject | null;
  syllabus: Syllabus | null;
  step: 1 | 2 | 3;
  setStep: (step: number) => void;
}
```

### Alternatives Considered

| Approach | Pros | Cons | Why Rejected |
|----------|------|------|--------------|
| URL only | Shareable, refresh-safe | Limited data capacity | Not enough for form state |
| Context only | Rich state | Lost on refresh | Poor UX |
| **URL + Context** | Best of both | Slightly complex | **SELECTED** |
| LocalStorage | Persists across sessions | Stale data risk | Optional enhancement |

---

## Additional Research: SQLModel Relationship Patterns

### Parent-Child Relationships

```python
from sqlmodel import Relationship

class AcademicLevel(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str

    # Relationship to subjects
    subjects: list["Subject"] = Relationship(back_populates="academic_level")

class Subject(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    academic_level_id: UUID = Field(foreign_key="academic_levels.id")

    # Relationships
    academic_level: "AcademicLevel" = Relationship(back_populates="subjects")
    syllabi: list["Syllabus"] = Relationship(back_populates="subject")
```

### Query Patterns

```python
# Get full hierarchy
stmt = (
    select(AcademicLevel)
    .options(
        selectinload(AcademicLevel.subjects)
        .selectinload(Subject.syllabi)
    )
)

# Get subjects for a level
stmt = select(Subject).where(Subject.academic_level_id == level_id)
```

---

## Conclusions

All research questions resolved:

1. **Hierarchy Pattern**: Adjacency list (simple FKs between levels)
2. **Delete Behavior**: RESTRICT (prevent cascade, require explicit cleanup)
3. **Migration**: Two-phase with preserved rollback capability
4. **Frontend State**: URL params + React Context for wizard

Ready to proceed to Phase 1: Data Model design.
