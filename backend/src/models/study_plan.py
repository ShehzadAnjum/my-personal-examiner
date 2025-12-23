"""Planner Agent - Study Plan Model

Uses SuperMemo 2 (SM-2) spaced repetition algorithm with contextual interleaving.

Constitutional Requirements:
- Principle V: Multi-tenant isolation (student_id FK enforced)
- Principle VII: >80% test coverage (simple CRUD model, easily testable)
"""

from datetime import date, datetime
from typing import Dict, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON
from typing_extensions import TypedDict


class DaySchedule(TypedDict):
    """TypedDict for daily schedule entry"""
    day: int  # Day number in plan (1-based)
    date: str  # YYYY-MM-DD
    topics: List[str]  # Syllabus point codes (max 3 per day)
    interval: int  # SM-2 interval (days since last review)
    activities: List[str]  # "study", "practice", "review", "mixed_review", "mock_exam"
    hours_allocated: float
    ef: float  # Easiness factor for this day (1.3-2.5)
    completed: bool


class StudyPlan(SQLModel, table=True):
    """
    Store personalized n-day study schedules with SM-2 spaced repetition.

    SuperMemo 2 Formula:
    - I(1) = 1 day
    - I(2) = 6 days
    - I(n) = I(n-1) * EF for n ≥ 3
    - EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    - EF min = 1.3, max = 2.5

    Contextual Interleaving:
    - Max 3 related topics per day (same syllabus section)
    - Pattern: A→B→A→C (mixed practice)
    - Respects cognitive load limits

    State Machine:
    - active → completed (all days completed, exam taken)
    - active → abandoned (student stopped following plan)
    """

    __tablename__ = "study_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", nullable=False)
    subject_id: UUID = Field(foreign_key="subjects.id", nullable=False)

    exam_date: date = Field(nullable=False)
    total_days: int = Field(gt=0, nullable=False)
    hours_per_day: float = Field(gt=0, le=24, nullable=False)

    # JSONB field: Array of DaySchedule objects
    schedule: List[DaySchedule] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list
    )

    # JSONB field: Map of syllabus_point_code -> easiness_factor
    # Example: {"9708.1.1": 2.5, "9708.1.2": 2.2}
    easiness_factors: Dict[str, float] = Field(
        sa_column=Column(JSON, nullable=True),
        default_factory=dict
    )

    # Enum: active, completed, abandoned
    status: str = Field(default="active", max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "exam_date": "2025-03-15",
                "total_days": 30,
                "hours_per_day": 2.0,
                "schedule": [
                    {
                        "day": 1,
                        "date": "2025-01-15",
                        "topics": ["9708.1.1", "9708.1.2"],
                        "interval": 1,
                        "activities": ["study", "practice"],
                        "hours_allocated": 2.0,
                        "ef": 2.5,
                        "completed": False
                    },
                    {
                        "day": 4,
                        "date": "2025-01-18",
                        "topics": ["9708.1.1"],
                        "interval": 3,
                        "activities": ["review"],
                        "hours_allocated": 1.0,
                        "ef": 2.5,
                        "completed": False
                    }
                ],
                "easiness_factors": {
                    "9708.1.1": 2.5,
                    "9708.1.2": 2.5
                },
                "status": "active"
            }
        }
