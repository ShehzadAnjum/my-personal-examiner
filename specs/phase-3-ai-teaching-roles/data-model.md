# Phase III Data Model: AI Teaching Roles

**Date**: 2025-12-20
**Purpose**: Define database schema for 3 new tables + enhancements to existing models
**Database**: PostgreSQL 16 (Neon) with JSONB support

---

## New Tables

### 1. coaching_sessions

**Purpose**: Track all tutoring sessions between students and Coach Agent

**Schema**:
```sql
CREATE TABLE coaching_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic VARCHAR(500) NOT NULL,
    struggle_description TEXT,
    session_transcript JSONB NOT NULL,
    outcome VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT valid_outcome
        CHECK (outcome IN ('in_progress', 'resolved', 'needs_more_help', 'refer_to_teacher'))
);

CREATE INDEX idx_coaching_sessions_student ON coaching_sessions(student_id);
CREATE INDEX idx_coaching_sessions_created ON coaching_sessions(created_at DESC);
```

**JSONB Field: session_transcript**
```json
[
  {
    "role": "student",
    "content": "I don't understand price elasticity of demand",
    "timestamp": "2025-01-15T10:00:00Z"
  },
  {
    "role": "coach",
    "content": "Let me help with a question: Can you explain what happens to the quantity demanded when price increases?",
    "timestamp": "2025-01-15T10:00:02Z"
  },
  {
    "role": "student",
    "content": "It decreases",
    "timestamp": "2025-01-15T10:00:30Z"
  },
  {
    "role": "coach",
    "content": "Exactly! That's the inverse relationship. Now, what determines how MUCH it decreases?",
    "timestamp": "2025-01-15T10:00:35Z"
  }
]
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID, uuid4

class MessageDict(TypedDict):
    role: str  # "student" or "coach"
    content: str
    timestamp: str  # ISO 8601

class CoachingSession(SQLModel, table=True):
    __tablename__ = "coaching_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id")
    topic: str = Field(max_length=500)
    struggle_description: Optional[str] = None
    session_transcript: List[MessageDict] = Field(sa_column=Column(JSON))
    outcome: str = Field(default="in_progress")  # Enum: in_progress, resolved, needs_more_help, refer_to_teacher
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `student_id`: Must reference valid student
- `topic`: Max 500 characters
- `session_transcript`: MUST be array of objects with {role, content, timestamp}
- `outcome`: MUST be one of 4 valid states
- `role` in transcript: MUST be "student" or "coach"

**State Transitions**:
```
in_progress → resolved (student understands)
in_progress → needs_more_help (student still stuck after session)
in_progress → refer_to_teacher (concept too complex for coaching)
```

---

### 2. study_plans

**Purpose**: Store personalized study schedules with SM-2 intervals and easiness factors

**Schema**:
```sql
CREATE TABLE study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id),
    exam_date DATE NOT NULL,
    total_days INTEGER NOT NULL CHECK (total_days > 0),
    hours_per_day FLOAT NOT NULL CHECK (hours_per_day > 0 AND hours_per_day <= 24),
    schedule JSONB NOT NULL,
    easiness_factors JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(id),

    CONSTRAINT valid_status
        CHECK (status IN ('active', 'completed', 'abandoned'))
);

CREATE INDEX idx_study_plans_student ON study_plans(student_id);
CREATE INDEX idx_study_plans_status ON study_plans(status);
CREATE INDEX idx_study_plans_exam_date ON study_plans(exam_date);
```

**JSONB Field: schedule**
```json
[
  {
    "day": 1,
    "date": "2025-01-15",
    "topics": ["9708.1.1", "9708.1.2"],
    "interval": 1,
    "activities": ["study", "practice"],
    "hours_allocated": 2.0,
    "ef": 2.5,
    "completed": false
  },
  {
    "day": 4,
    "date": "2025-01-18",
    "topics": ["9708.1.1"],
    "interval": 3,
    "activities": ["review"],
    "hours_allocated": 1.0,
    "ef": 2.5,
    "completed": false
  },
  {
    "day": 11,
    "date": "2025-01-25",
    "topics": ["9708.1.1", "9708.2.1"],
    "interval": 7,
    "activities": ["mixed_review", "practice_exam"],
    "hours_allocated": 2.5,
    "ef": 2.5,
    "completed": false
  }
]
```

**JSONB Field: easiness_factors**
```json
{
  "9708.1.1": 2.5,
  "9708.1.2": 2.2,
  "9708.2.1": 2.8,
  "9708.2.2": 2.4
}
```

**SQLModel Definition**:
```python
from typing import List, Dict

class DaySchedule(TypedDict):
    day: int
    date: str  # YYYY-MM-DD
    topics: List[str]  # Syllabus point codes
    interval: int  # SM-2 interval
    activities: List[str]  # "study", "practice", "review", "exam"
    hours_allocated: float
    ef: float  # Easiness factor for this day
    completed: bool

class StudyPlan(SQLModel, table=True):
    __tablename__ = "study_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id")
    subject_id: UUID = Field(foreign_key="subjects.id")
    exam_date: datetime = Field()
    total_days: int = Field(gt=0)
    hours_per_day: float = Field(gt=0, le=24)
    schedule: List[DaySchedule] = Field(sa_column=Column(JSON))
    easiness_factors: Dict[str, float] = Field(sa_column=Column(JSON))
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `exam_date`: Must be future date
- `total_days`: Must be positive integer
- `hours_per_day`: Must be 0 < x ≤ 24
- `schedule`: Array of day objects with SM-2 intervals
- `easiness_factors`: Object mapping syllabus point codes to EF values (1.3 ≤ EF ≤ 2.5)
- `status`: One of {active, completed, abandoned}

**State Transitions**:
```
active → completed (all days completed, exam taken)
active → abandoned (student stopped following plan)
```

---

### 3. improvement_plans

**Purpose**: Link student weaknesses to actionable improvement tasks

**Schema**:
```sql
CREATE TABLE improvement_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    weaknesses JSONB NOT NULL,
    action_items JSONB NOT NULL,
    progress JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_attempt
        FOREIGN KEY (attempt_id)
        REFERENCES attempts(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_improvement_plans_student ON improvement_plans(student_id);
CREATE INDEX idx_improvement_plans_attempt ON improvement_plans(attempt_id);
```

**JSONB Field: weaknesses**
```json
{
  "AO1": [
    {
      "category": "Imprecise Definitions",
      "examples": [
        "Question 2: Defined demand as 'what people want' instead of 'quantity willing and able to purchase'"
      ],
      "severity": "high",
      "syllabus_points": ["9708.2.1"]
    }
  ],
  "AO2": [
    {
      "category": "Weak Application",
      "examples": [
        "Question 3: Used generic example 'some goods' instead of specific real-world case"
      ],
      "severity": "medium",
      "syllabus_points": ["9708.2.2"]
    }
  ],
  "AO3": [
    {
      "category": "No Evaluation",
      "examples": [
        "Question 4: Listed arguments but no conclusion or weighing of significance"
      ],
      "severity": "high",
      "syllabus_points": ["9708.3.1"]
    }
  ]
}
```

**JSONB Field: action_items**
```json
[
  {
    "id": "action-1",
    "action": "Memorize precise definitions for 10 core Economics terms (demand, supply, elasticity, etc.)",
    "target_weakness": "AO1 - Imprecise Definitions",
    "due_date": "2025-01-22",
    "completed": false,
    "resources": [
      "9708 syllabus glossary",
      "Teacher Agent: Explain concept for each term"
    ]
  },
  {
    "id": "action-2",
    "action": "Practice writing AO3 evaluation paragraphs using structure: Argument → Counter-argument → Conclusion",
    "target_weakness": "AO3 - No Evaluation",
    "due_date": "2025-01-25",
    "completed": false,
    "resources": [
      "Coach Agent: Evaluation writing technique",
      "Practice: 5 evaluation questions from question bank"
    ]
  }
]
```

**JSONB Field: progress**
```json
{
  "action-1": {
    "started": "2025-01-16",
    "completed": null,
    "notes": "Completed 5/10 definitions"
  },
  "action-2": {
    "started": "2025-01-18",
    "completed": "2025-01-24",
    "notes": "Significant improvement in evaluation structure"
  }
}
```

**SQLModel Definition**:
```python
class WeaknessCategory(TypedDict):
    category: str
    examples: List[str]
    severity: str  # "low", "medium", "high"
    syllabus_points: List[str]

class ActionItem(TypedDict):
    id: str
    action: str
    target_weakness: str
    due_date: str  # YYYY-MM-DD
    completed: bool
    resources: List[str]

class ImprovementPlan(SQLModel, table=True):
    __tablename__ = "improvement_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id")
    attempt_id: UUID = Field(foreign_key="attempts.id")
    weaknesses: Dict[str, List[WeaknessCategory]] = Field(sa_column=Column(JSON))
    action_items: List[ActionItem] = Field(sa_column=Column(JSON))
    progress: Dict[str, dict] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `weaknesses`: Must have keys {AO1, AO2, AO3} with arrays of weakness objects
- `action_items`: Array of actionable tasks with due dates
- `progress`: Object tracking completion status per action item

---

## Enhancements to Existing Tables

### attempted_questions (Add Confidence Scoring)

**New Fields**:
```sql
ALTER TABLE attempted_questions
ADD COLUMN confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
ADD COLUMN needs_review BOOLEAN DEFAULT false,
ADD COLUMN reviewed_by UUID REFERENCES students(id),  -- Human examiner
ADD COLUMN reviewed_at TIMESTAMP WITH TIME ZONE;
```

**SQLModel Enhancement**:
```python
class AttemptedQuestion(SQLModel, table=True):
    # Existing fields...
    marks_awarded: int
    marking_feedback: dict = Field(sa_column=Column(JSON))

    # NEW: Phase III fields
    confidence_score: Optional[int] = Field(default=None, ge=0, le=100)
    needs_review: bool = Field(default=False)
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="students.id")
    reviewed_at: Optional[datetime] = None
```

**Business Logic**:
```python
# In marking_service.py
def mark_answer(question, student_answer, student_id) -> MarkingResult:
    result = mark_economics_answer(question, student_answer)
    confidence = calculate_confidence(result, question, student_answer)

    if confidence < 70:
        result.needs_review = True
        queue_for_manual_review(result)

    result.confidence_score = confidence
    return result
```

---

## Entity Relationships

```
Student (existing)
  ├── has_many CoachingSession
  ├── has_many StudyPlan
  └── has_many ImprovementPlan

Subject (existing)
  └── has_many StudyPlan

Attempt (existing)
  └── has_one ImprovementPlan

AttemptedQuestion (existing, enhanced)
  ├── confidence_score (NEW)
  └── needs_review (NEW)
```

---

## Database Migrations

### Migration 003: coaching_sessions

**File**: `backend/alembic/versions/003_create_coaching_sessions.py`

```python
"""Create coaching_sessions table

Revision ID: 003
Revises: 002
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    op.create_table(
        'coaching_sessions',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('student_id', UUID(), nullable=False),
        sa.Column('topic', sa.String(500), nullable=False),
        sa.Column('struggle_description', sa.Text(), nullable=True),
        sa.Column('session_transcript', JSONB(), nullable=False),
        sa.Column('outcome', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.CheckConstraint("outcome IN ('in_progress', 'resolved', 'needs_more_help', 'refer_to_teacher')", name='valid_outcome')
    )
    op.create_index('idx_coaching_sessions_student', 'coaching_sessions', ['student_id'])
    op.create_index('idx_coaching_sessions_created', 'coaching_sessions', [sa.text('created_at DESC')])

def downgrade():
    op.drop_index('idx_coaching_sessions_created', 'coaching_sessions')
    op.drop_index('idx_coaching_sessions_student', 'coaching_sessions')
    op.drop_table('coaching_sessions')
```

### Migration 004: study_plans

**File**: `backend/alembic/versions/004_create_study_plans.py`

```python
"""Create study_plans table

Revision ID: 004
Revises: 003
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    op.create_table(
        'study_plans',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('student_id', UUID(), nullable=False),
        sa.Column('subject_id', UUID(), nullable=False),
        sa.Column('exam_date', sa.Date(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('hours_per_day', sa.Float(), nullable=False),
        sa.Column('schedule', JSONB(), nullable=False),
        sa.Column('easiness_factors', JSONB(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id']),
        sa.CheckConstraint('total_days > 0', name='valid_total_days'),
        sa.CheckConstraint('hours_per_day > 0 AND hours_per_day <= 24', name='valid_hours_per_day'),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned')", name='valid_status')
    )
    op.create_index('idx_study_plans_student', 'study_plans', ['student_id'])
    op.create_index('idx_study_plans_status', 'study_plans', ['status'])
    op.create_index('idx_study_plans_exam_date', 'study_plans', ['exam_date'])

def downgrade():
    op.drop_index('idx_study_plans_exam_date', 'study_plans')
    op.drop_index('idx_study_plans_status', 'study_plans')
    op.drop_index('idx_study_plans_student', 'study_plans')
    op.drop_table('study_plans')
```

### Migration 005: improvement_plans + attempted_questions enhancements

**File**: `backend/alembic/versions/005_create_improvement_plans.py`

```python
"""Create improvement_plans table and enhance attempted_questions

Revision ID: 005
Revises: 004
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    # Create improvement_plans table
    op.create_table(
        'improvement_plans',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('student_id', UUID(), nullable=False),
        sa.Column('attempt_id', UUID(), nullable=False),
        sa.Column('weaknesses', JSONB(), nullable=False),
        sa.Column('action_items', JSONB(), nullable=False),
        sa.Column('progress', JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], ondelete='CASCADE')
    )
    op.create_index('idx_improvement_plans_student', 'improvement_plans', ['student_id'])
    op.create_index('idx_improvement_plans_attempt', 'improvement_plans', ['attempt_id'])

    # Enhance attempted_questions with confidence scoring
    op.add_column('attempted_questions', sa.Column('confidence_score', sa.Integer(), nullable=True))
    op.add_column('attempted_questions', sa.Column('needs_review', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('attempted_questions', sa.Column('reviewed_by', UUID(), nullable=True))
    op.add_column('attempted_questions', sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True), nullable=True))

    op.create_check_constraint('valid_confidence_score', 'attempted_questions', 'confidence_score BETWEEN 0 AND 100')
    op.create_foreign_key('fk_attempted_questions_reviewed_by', 'attempted_questions', 'students', ['reviewed_by'], ['id'])

def downgrade():
    # Remove attempted_questions enhancements
    op.drop_constraint('fk_attempted_questions_reviewed_by', 'attempted_questions', type_='foreignkey')
    op.drop_constraint('valid_confidence_score', 'attempted_questions', type_='check')
    op.drop_column('attempted_questions', 'reviewed_at')
    op.drop_column('attempted_questions', 'reviewed_by')
    op.drop_column('attempted_questions', 'needs_review')
    op.drop_column('attempted_questions', 'confidence_score')

    # Remove improvement_plans table
    op.drop_index('idx_improvement_plans_attempt', 'improvement_plans')
    op.drop_index('idx_improvement_plans_student', 'improvement_plans')
    op.drop_table('improvement_plans')
```

---

## Data Model Summary

| Table | Purpose | Key JSONB Fields | Multi-Tenant |
|-------|---------|------------------|--------------|
| **coaching_sessions** | Track tutoring conversations | session_transcript (messages) | ✅ student_id |
| **study_plans** | SM-2 schedules with EF tracking | schedule (days), easiness_factors | ✅ student_id |
| **improvement_plans** | Link weaknesses to actions | weaknesses (AO1/2/3), action_items | ✅ student_id |
| **attempted_questions** (enhanced) | Add confidence scoring | marking_feedback + confidence_score | ✅ student_id |

**All tables enforce multi-tenant isolation via student_id foreign keys and cascade deletes.**

---

**Data Model Status**: COMPLETE
**Next Phase**: API Contracts (contracts/ directory)
**Date**: 2025-12-20
