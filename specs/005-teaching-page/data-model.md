# Data Model: Teaching Page

**Feature**: 005-teaching-page (PhD-Level Concept Explanations)
**Date**: 2025-12-23
**Phase**: 1 (Design & Contracts)
**Purpose**: Define data structures for teaching page frontend and backend

---

## Overview

The teaching page feature uses 3 main data entities:

1. **SyllabusPoint** (backend, persisted) - Represents a single topic in the Economics 9708 syllabus
2. **SavedExplanation** (backend, persisted) - Represents a student's bookmarked explanation
3. **TopicExplanation** (frontend, transient) - AI-generated explanation structure (not persisted)

---

## Entity 1: SyllabusPoint (Backend)

**Database Table**: `syllabus_points`

**Purpose**: Store Economics 9708 syllabus topics with codes, descriptions, and learning outcomes

**Attributes**:
- `id`: UUID (primary key)
- `code`: VARCHAR(50) - Syllabus code (e.g., "3.1.2")
- `description`: TEXT - Topic description (e.g., "Price Elasticity of Demand")
- `learning_outcomes`: TEXT - Newline-separated learning outcomes from Cambridge syllabus
- `subject_id`: UUID (foreign key to `subjects.id`)
- `level`: ENUM('AS', 'A2') - AS-Level or A2-Level
- `paper_number`: INTEGER - Paper 1, 2, 3, or 4
- `section`: VARCHAR(100) - Section name (e.g., "Microeconomics")
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

**Relationships**:
- Belongs to `Subject` (Economics 9708)
- Has many `SavedExplanations`

**Constraints**:
- `code` must be unique per subject
- `level` must be 'AS' or 'A2'
- `paper_number` must be 1-4

**Indexes**:
- `idx_syllabus_points_subject_id` on `subject_id`
- `idx_syllabus_points_code` on `code`
- `idx_syllabus_points_level_paper` on `(level, paper_number)`

**Sample Data**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "3.1.2",
  "description": "Price Elasticity of Demand (PED): Definition, calculation, determinants, and applications",
  "learning_outcomes": "Define price elasticity of demand\nCalculate PED using formula and diagrams\nAnalyse determinants of PED\nEvaluate significance of PED for firms and governments",
  "subject_id": "subject-uuid",
  "level": "AS",
  "paper_number": 2,
  "section": "Microeconomics - Markets",
  "created_at": "2025-12-01T00:00:00Z",
  "updated_at": "2025-12-01T00:00:00Z"
}
```

**Frontend TypeScript Interface**:
```typescript
// frontend/lib/types/teaching.ts
export interface SyllabusTopic {
  id: string;
  code: string;
  description: string;
  learning_outcomes: string;  // Newline-separated, split client-side
  subject_id: string;
  level: 'AS' | 'A2';
  paper_number: number;
  section: string;
  created_at: string;
  updated_at: string;
}
```

---

## Entity 2: SavedExplanation (Backend)

**Database Table**: `saved_explanations`

**Purpose**: Store bookmarked explanations for students (enables review and offline access)

**Attributes**:
- `id`: UUID (primary key)
- `student_id`: UUID (foreign key to `students.id`) - Multi-tenant isolation
- `syllabus_point_id`: UUID (foreign key to `syllabus_points.id`)
- `explanation_content`: JSON - Full `TopicExplanation` object (definition, examples, etc.)
- `date_saved`: TIMESTAMP - When student bookmarked
- `date_last_viewed`: TIMESTAMP (nullable) - Last time student opened bookmark

**Relationships**:
- Belongs to `Student`
- Belongs to `SyllabusPoint`

**Constraints**:
- Unique constraint on `(student_id, syllabus_point_id)` - Prevent duplicate bookmarks
- `student_id` NOT NULL (enforces multi-tenant isolation)
- `explanation_content` NOT NULL (must have explanation data)

**Indexes**:
- `idx_saved_explanations_student_id` on `student_id` (multi-tenant queries)
- `idx_saved_explanations_syllabus_point_id` on `syllabus_point_id`

**Sample Data**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "student_id": "student-uuid",
  "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
  "explanation_content": {
    "concept_name": "Price Elasticity of Demand",
    "definition": "PED measures the responsiveness of quantity demanded to a change in price...",
    "key_terms": [...],
    "examples": [...],
    "visual_aids": [...],
    "worked_examples": [...],
    "misconceptions": [...],
    "practice_problems": [...],
    "related_concepts": [...],
    "generated_by": "anthropic"
  },
  "date_saved": "2025-12-23T10:30:00Z",
  "date_last_viewed": "2025-12-23T14:45:00Z"
}
```

**Frontend TypeScript Interface**:
```typescript
// frontend/lib/types/teaching.ts
export interface SavedExplanation {
  id: string;
  student_id: string;
  syllabus_point_id: string;
  explanation_content: TopicExplanation;  // Nested object
  date_saved: string;
  date_last_viewed: string | null;
}
```

**Multi-Tenant Isolation**:
- All queries MUST include `WHERE student_id = ?` filter
- Backend endpoints verify JWT student_id matches request student_id
- Prevents students from viewing others' bookmarks

---

## Entity 3: TopicExplanation (Frontend, Transient)

**Purpose**: AI-generated explanation structure returned by Teacher Agent

**Storage**: NOT persisted to database (generated on-demand by POST /api/teaching/explain). Only stored in SavedExplanation.explanation_content when bookmarked.

**Attributes**:
- `syllabus_code`: string - Reference to syllabus point (e.g., "3.1.2")
- `concept_name`: string - Topic name (e.g., "Price Elasticity of Demand")
- `definition`: string - Precise PhD-level definition
- `key_terms`: KeyTerm[] - Array of economic terms with definitions
- `explanation`: string - Core principles explanation (2-3 paragraphs)
- `examples`: Example[] - 2-3 real-world examples with analysis
- `visual_aids`: VisualAid[] - Diagram descriptions (supply/demand curves, graphs)
- `worked_examples`: WorkedExample[] - Step-by-step problem solutions with marks breakdown
- `common_misconceptions`: Misconception[] - Common errors with corrections
- `practice_problems`: PracticeProblem[] - 3-5 practice questions with answer outlines
- `related_concepts`: string[] - Links to other syllabus topics
- `generated_by`: string - LLM provider ("anthropic", "openai", or "gemini")

**TypeScript Interfaces**:
```typescript
// frontend/lib/types/teaching.ts

export interface TopicExplanation {
  syllabus_code: string;
  concept_name: string;
  definition: string;
  key_terms: KeyTerm[];
  explanation: string;
  examples: Example[];
  visual_aids: VisualAid[];
  worked_examples: WorkedExample[];
  common_misconceptions: Misconception[];
  practice_problems: PracticeProblem[];
  related_concepts: string[];
  generated_by: string;
}

export interface KeyTerm {
  term: string;
  definition: string;
}

export interface Example {
  title: string;
  scenario: string;
  analysis: string;
}

export interface VisualAid {
  type: 'diagram' | 'graph' | 'table';
  title: string;
  description: string;  // Text description (no actual image rendering)
}

export interface WorkedExample {
  problem: string;
  step_by_step_solution: string;
  marks_breakdown: string;
}

export interface Misconception {
  misconception: string;
  why_wrong: string;
  correct_understanding: string;
}

export interface PracticeProblem {
  question: string;
  difficulty: 'easy' | 'medium' | 'hard';
  answer_outline: string;
  marks: number;
}
```

**Sample Data**:
```json
{
  "syllabus_code": "3.1.2",
  "concept_name": "Price Elasticity of Demand",
  "definition": "PED measures the responsiveness of quantity demanded to a change in price, calculated as % change in quantity demanded / % change in price.",
  "key_terms": [
    {
      "term": "Elastic demand",
      "definition": "PED > 1, quantity demanded changes proportionally more than price"
    },
    {
      "term": "Inelastic demand",
      "definition": "PED < 1, quantity demanded changes proportionally less than price"
    }
  ],
  "explanation": "Price elasticity of demand measures how sensitive consumers are to price changes. When demand is elastic (PED > 1), a small price increase causes a large drop in quantity demanded, as consumers have many substitutes available. Conversely, inelastic demand (PED < 1) occurs when consumers have few alternatives and continue buying despite price increases.",
  "examples": [
    {
      "title": "Elastic Demand: Luxury Cars",
      "scenario": "A 10% price increase in luxury cars leads to a 20% drop in sales (PED = 2.0)",
      "analysis": "Consumers have many substitutes (mid-range cars, public transport) and can delay purchases. Luxury cars are not necessities, making demand highly elastic."
    }
  ],
  "visual_aids": [
    {
      "type": "diagram",
      "title": "Elastic vs Inelastic Demand Curves",
      "description": "Elastic demand curve: Flatter slope (small price change → large quantity change). Inelastic demand curve: Steeper slope (large price change → small quantity change)."
    }
  ],
  "worked_examples": [
    {
      "problem": "Calculate PED if price rises from $10 to $12 and quantity demanded falls from 100 to 80 units.",
      "step_by_step_solution": "Step 1: % change in quantity = (80-100)/100 = -20%. Step 2: % change in price = (12-10)/10 = 20%. Step 3: PED = |-20%/20%| = 1.0 (unitary elastic).",
      "marks_breakdown": "1 mark: % change in quantity. 1 mark: % change in price. 1 mark: PED calculation. 1 mark: Interpretation (unitary elastic)."
    }
  ],
  "common_misconceptions": [
    {
      "misconception": "PED is always negative, so we must report negative values",
      "why_wrong": "PED is conventionally reported as absolute value to avoid confusion (economists understand the inverse relationship)",
      "correct_understanding": "Report PED as positive value (e.g., 1.5 not -1.5) and interpret magnitude (>1 elastic, <1 inelastic)"
    }
  ],
  "practice_problems": [
    {
      "question": "If PED for cigarettes is 0.3, predict the % change in quantity demanded if price increases by 10%.",
      "difficulty": "medium",
      "answer_outline": "PED = 0.3 means inelastic demand. % change in quantity = PED × % change in price = 0.3 × 10% = 3% decrease. Cigarettes are addictive (few substitutes), so quantity changes little despite price increase.",
      "marks": 4
    }
  ],
  "related_concepts": ["3.1.3 Income Elasticity of Demand", "3.1.4 Cross Elasticity of Demand", "3.2.1 Consumer Surplus"],
  "generated_by": "anthropic"
}
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  User Actions   │
└────────┬────────┘
         │
         ├─── 1. Browse Topics ───────────────────┐
         │                                        │
         │    GET /api/teaching/syllabus          │
         │    ↓                                   │
         │    Backend returns SyllabusTopic[]    │
         │    ↓                                   │
         │    Frontend displays TopicBrowser      │
         │                                        │
         ├─── 2. Request Explanation ─────────────┤
         │                                        │
         │    POST /api/teaching/explain          │
         │    { syllabus_point_id, student_id }   │
         │    ↓                                   │
         │    Teacher Agent generates AI response │
         │    ↓                                   │
         │    Backend returns TopicExplanation    │
         │    ↓                                   │
         │    Frontend displays ExplanationView   │
         │                                        │
         ├─── 3. Bookmark Explanation ────────────┤
         │                                        │
         │    POST /api/teaching/explanations     │
         │    { syllabus_point_id, explanation }  │
         │    ↓                                   │
         │    Backend creates SavedExplanation    │
         │    ↓                                   │
         │    Frontend shows "Bookmarked" state   │
         │                                        │
         └─── 4. View Saved ──────────────────────┤
                                                  │
              GET /api/teaching/explanations      │
              ↓                                   │
              Backend returns SavedExplanation[]  │
              ↓                                   │
              Frontend displays saved list        │
```

---

## Validation Rules

### SyllabusPoint
- `code`: Must match pattern `/^\d+\.\d+(\.\d+)?$/` (e.g., "3.1" or "3.1.2")
- `level`: Must be 'AS' or 'A2'
- `paper_number`: Must be 1, 2, 3, or 4
- `learning_outcomes`: Cannot be empty string

### SavedExplanation
- `student_id`: Must exist in `students` table (foreign key constraint)
- `syllabus_point_id`: Must exist in `syllabus_points` table
- Unique constraint prevents duplicate bookmarks per student+topic
- `explanation_content`: Must be valid JSON matching TopicExplanation schema

### TopicExplanation (Frontend Validation)
- `key_terms`: Minimum 3 terms (spec requirement)
- `examples`: Minimum 2 examples (spec requirement)
- `practice_problems`: Minimum 1 problem
- All string fields: Maximum 10,000 characters (prevent overflow)

---

## State Transitions

### Bookmark State Machine
```
[No Bookmark]
     ↓ (User clicks "Bookmark")
     POST /api/teaching/explanations
     ↓
[Bookmarked]
     ↓ (User clicks "Remove Bookmark")
     DELETE /api/teaching/explanations/:id
     ↓
[No Bookmark]
```

### Explanation Lifecycle
```
[Topic Selected]
     ↓
[Loading] (ExplanationSkeleton shown, 5-10 seconds)
     ↓
     POST /api/teaching/explain
     ↓
[Explanation Generated]
     ↓
[Cached in TanStack Query] (5-minute staleTime)
     ↓
[Reused for same topic] (if requested within 5 minutes)
```

---

## Multi-Tenant Data Isolation

**Critical Rule**: Every database query for SavedExplanation MUST filter by `student_id`

**Backend Query Pattern**:
```python
# ✅ CORRECT: Includes student_id filter
statement = select(SavedExplanation).where(
    SavedExplanation.student_id == current_user.id
)

# ❌ WRONG: Missing student_id filter (security violation)
statement = select(SavedExplanation)  # Returns ALL students' bookmarks
```

**Frontend API Pattern**:
```typescript
// ✅ CORRECT: JWT token includes student_id (backend extracts)
const response = await fetch('/api/teaching/explanations', {
  headers: { Authorization: `Bearer ${token}` }
});

// ❌ WRONG: Manually passing student_id allows tampering
const response = await fetch(`/api/teaching/explanations?student_id=${otherId}`);
```

---

## Performance Considerations

### Database Indexes
- `idx_saved_explanations_student_id`: Critical for multi-tenant queries (retrieves user's bookmarks)
- `idx_syllabus_points_code`: Speeds up topic lookups by syllabus code
- `idx_syllabus_points_level_paper`: Enables fast filtering by AS/A2 and paper number

### JSON Storage
- SavedExplanation.explanation_content stored as JSON (5-10KB per bookmark)
- Trade-off: Larger storage vs faster retrieval (no JOIN required to reconstruct explanation)
- PostgreSQL JSONB type enables efficient queries on nested fields (future search within bookmarks)

### Caching Strategy (TanStack Query)
- SyllabusTopics cached 1 hour (rarely change)
- TopicExplanations cached 5 minutes (expensive AI generation)
- SavedExplanations cached 1 minute (user actions need quick reflection)

---

**Data Model Complete**: All entities, relationships, and validation rules defined.

**Next Phase**: Create contracts/ directory with API and UI component contracts.
