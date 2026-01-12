# Data Model: Academic Level Hierarchy

**Feature**: 008-academic-level-hierarchy
**Date**: 2026-01-05
**Pattern**: Adjacency List (see research.md)

---

## Entity Relationship Diagram

```
┌──────────────────────┐
│   AcademicLevel      │
├──────────────────────┤
│ id: UUID (PK)        │
│ name: str            │──┐
│ code: str (unique)   │  │ 1:N
│ description: str?    │  │
│ exam_board: str      │  │
│ created_at: datetime │  │
│ updated_at: datetime │  │
└──────────────────────┘  │
                          │
          ┌───────────────┘
          ▼
┌──────────────────────┐
│      Subject         │
├──────────────────────┤
│ id: UUID (PK)        │
│ academic_level_id:   │──┐
│   UUID (FK)          │  │
│ name: str            │  │ 1:N
│ code: str?           │  │
│ setup_status: enum   │  │
│ created_at: datetime │  │
│ updated_at: datetime │  │
└──────────────────────┘  │
                          │
          ┌───────────────┘
          ▼
┌──────────────────────┐
│      Syllabus        │
├──────────────────────┤
│ id: UUID (PK)        │
│ subject_id: UUID(FK) │──┐
│ code: str            │  │
│ year_range: str      │  │ 1:N
│ version: int         │  │
│ syllabus_resource_id:│  │
│   UUID (FK)?         │  │
│ created_at: datetime │  │
│ updated_at: datetime │  │
└──────────────────────┘  │
                          │
          ┌───────────────┘
          ▼
┌──────────────────────┐
│   SyllabusPoint      │
├──────────────────────┤
│ id: UUID (PK)        │
│ syllabus_id: UUID(FK)│
│ code: str            │
│ description: text    │
│ topics: text?        │
│ learning_outcomes:   │
│   text?              │
└──────────────────────┘
```

---

## Entity Definitions

### AcademicLevel (NEW)

**Purpose**: Represents a qualification type (A-Level, O-Level, IGCSE, IB, etc.)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Primary key |
| name | str(100) | NOT NULL | Display name (e.g., "A-Level") |
| code | str(10) | NOT NULL, UNIQUE | Short code (e.g., "A", "O", "IGCSE") |
| description | str(500) | NULL | Optional description |
| exam_board | str(100) | NOT NULL, default="Cambridge International" | Exam board name |
| created_at | datetime | NOT NULL, auto | Creation timestamp |
| updated_at | datetime | NOT NULL, auto | Last update timestamp |

**Indexes**:
- `idx_academic_levels_code` on `code` (unique)

**Validation**:
- Code must be alphanumeric, 1-10 characters
- Name must be 1-100 characters

### Subject (MODIFIED)

**Purpose**: Represents a subject area within an academic level

**Fields Removed**:
- `level` → moved to AcademicLevel
- `exam_board` → moved to AcademicLevel
- `syllabus_year` → moved to Syllabus
- `code` → moved to Syllabus (subject code like "9708")
- `syllabus_resource_id` → moved to Syllabus

**Fields Added**:
- `academic_level_id` → FK to AcademicLevel

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Primary key |
| academic_level_id | UUID | FK, NOT NULL | Parent academic level |
| name | str(100) | NOT NULL | Subject name (e.g., "Economics") |
| code | str(20) | NULL | Optional subject code (e.g., "ECON") |
| setup_status | enum | NOT NULL, default="pending" | Setup wizard status |
| marking_config | JSON | NULL | Subject-specific marking config |
| extraction_patterns | JSON | NULL | PDF extraction patterns |
| paper_templates | JSON | NULL | Paper structure templates |
| created_at | datetime | NOT NULL, auto | Creation timestamp |
| updated_at | datetime | NOT NULL, auto | Last update timestamp |

**Indexes**:
- `idx_subjects_academic_level_id` on `academic_level_id`
- `idx_subjects_name_level` on `(name, academic_level_id)` unique

**Validation**:
- Name unique within academic level
- setup_status in ("pending", "syllabus_uploaded", "topics_generated", "explanations_generated", "complete")

### Syllabus (NEW)

**Purpose**: Represents a specific syllabus version for a subject

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Primary key |
| subject_id | UUID | FK, NOT NULL | Parent subject |
| code | str(20) | NOT NULL | Syllabus code (e.g., "9708") |
| year_range | str(20) | NOT NULL | Valid years (e.g., "2023-2025") |
| version | int | NOT NULL, default=1 | Version number |
| syllabus_resource_id | UUID | FK, NULL | Uploaded PDF resource |
| is_active | bool | NOT NULL, default=true | Currently active syllabus |
| created_at | datetime | NOT NULL, auto | Creation timestamp |
| updated_at | datetime | NOT NULL, auto | Last update timestamp |

**Indexes**:
- `idx_syllabi_subject_id` on `subject_id`
- `idx_syllabi_code_subject` on `(code, subject_id)` unique
- `idx_syllabi_active` on `(subject_id, is_active)` partial where is_active=true

**Validation**:
- Code must match pattern (alphanumeric, 1-20 chars)
- year_range must match pattern (e.g., "2023-2025")
- Only one active syllabus per subject

### SyllabusPoint (MODIFIED)

**Purpose**: Represents a specific learning objective within a syllabus

**Fields Changed**:
- `subject_id` → renamed to `syllabus_id` (FK to Syllabus instead of Subject)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Primary key |
| syllabus_id | UUID | FK, NOT NULL | Parent syllabus (changed from subject_id) |
| code | str(20) | NOT NULL | Topic code (e.g., "1.1.1") |
| description | text | NOT NULL | Learning objective |
| topics | text | NULL | Comma-separated topics |
| learning_outcomes | text | NULL | Expected outcomes |

**Indexes**:
- `idx_syllabus_points_syllabus_id` on `syllabus_id`
- `idx_syllabus_points_code` on `code`

---

## State Transitions

### Subject Setup Status

```
pending
    │
    ▼ (syllabus uploaded for this subject)
syllabus_uploaded
    │
    ▼ (topics extracted and confirmed)
topics_generated
    │
    ▼ (v1 explanations generated)
explanations_generated
    │
    ▼ (all steps complete)
complete
```

---

## Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| AcademicLevel | Subject | 1:N | RESTRICT |
| Subject | Syllabus | 1:N | RESTRICT |
| Syllabus | SyllabusPoint | 1:N | CASCADE |
| Resource | Syllabus.syllabus_resource_id | 1:1 | SET NULL |

---

## Sample Data

### AcademicLevel

```json
{
  "id": "uuid-1",
  "name": "A-Level",
  "code": "A",
  "description": "Cambridge International A-Level qualifications",
  "exam_board": "Cambridge International"
}
```

### Subject

```json
{
  "id": "uuid-2",
  "academic_level_id": "uuid-1",
  "name": "Economics",
  "code": null,
  "setup_status": "complete"
}
```

### Syllabus

```json
{
  "id": "uuid-3",
  "subject_id": "uuid-2",
  "code": "9708",
  "year_range": "2023-2025",
  "version": 1,
  "is_active": true,
  "syllabus_resource_id": "uuid-4"
}
```

### SyllabusPoint

```json
{
  "id": "uuid-5",
  "syllabus_id": "uuid-3",
  "code": "1.1.1",
  "description": "Scarcity, choice and opportunity cost",
  "topics": "scarcity, choice, opportunity cost, economic problem",
  "learning_outcomes": "Understand the fundamental economic problem"
}
```

---

## Migration Notes

### Forward Migration (v14)

1. Create `academic_levels` table
2. Create `syllabi` table
3. Add `academic_level_id` to `subjects` (nullable initially)
4. Add `syllabus_id` to `syllabus_points` (nullable initially)
5. Populate `academic_levels` from distinct subject levels
6. Populate `syllabi` from subject codes and years
7. Update `subjects.academic_level_id`
8. Update `syllabus_points.syllabus_id`
9. Make new FKs NOT NULL
10. Drop old columns from `subjects`

### Backward Migration

1. Add old columns back to `subjects`
2. Populate from `academic_levels` and `syllabi` joins
3. Update `syllabus_points.subject_id` from syllabi.subject_id
4. Drop new FKs
5. Drop `syllabi` and `academic_levels` tables

---

## API Response Shapes

### GET /api/academic-levels

```json
[
  {
    "id": "uuid-1",
    "name": "A-Level",
    "code": "A",
    "description": "Cambridge International A-Level",
    "exam_board": "Cambridge International",
    "subjects_count": 1
  }
]
```

### GET /api/academic-levels/{id}

```json
{
  "id": "uuid-1",
  "name": "A-Level",
  "code": "A",
  "description": "Cambridge International A-Level",
  "exam_board": "Cambridge International",
  "subjects": [
    {
      "id": "uuid-2",
      "name": "Economics",
      "setup_status": "complete",
      "syllabi_count": 1
    }
  ]
}
```

### GET /api/hierarchy (convenience endpoint)

```json
{
  "academic_levels": [
    {
      "id": "uuid-1",
      "name": "A-Level",
      "code": "A",
      "subjects": [
        {
          "id": "uuid-2",
          "name": "Economics",
          "syllabi": [
            {
              "id": "uuid-3",
              "code": "9708",
              "year_range": "2023-2025",
              "is_active": true,
              "topics_count": 45
            }
          ]
        }
      ]
    }
  ]
}
```
