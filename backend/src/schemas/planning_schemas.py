"""
Planning Schemas

Pydantic schemas for Planner Agent endpoints (SM-2 study schedules with contextual interleaving).

Phase III User Story 6: Students receive n-day study schedules using SuperMemo 2
spaced repetition with contextual interleaving, adaptive rescheduling based on performance.

Constitutional Requirements:
- Principle III: PhD-level pedagogy (evidence-based SM-2 algorithm)
- Principle VI: Constructive feedback (clear rationale for schedule)
- Principle I: Subject accuracy (100% syllabus coverage)
"""

from datetime import date
from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class DaySchedule(BaseModel):
    """
    Single day in the study schedule.

    Attributes:
        day: Day number in plan (1-based)
        date: Date for this study session
        topics: Syllabus point codes to study (max 3 per day)
        interval: SM-2 interval (days since last review)
        activities: Study activities for the day
        hours_allocated: Hours allocated for this day
        ef: Average easiness factor for topics
        completed: Whether this day has been completed
    """

    day: int = Field(
        ...,
        ge=1,
        description="Day number in plan (1-based)",
        examples=[1, 7, 14],
    )

    date: str = Field(
        ...,
        description="Date for this study session (YYYY-MM-DD)",
        examples=["2025-01-15"],
    )

    topics: List[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Syllabus point codes to study (max 3 per day)",
        examples=[["9708.1.1", "9708.1.2"]],
    )

    interval: int = Field(
        ...,
        ge=1,
        description="SM-2 interval (days since last review)",
        examples=[1, 6, 15],
    )

    activities: List[str] = Field(
        ...,
        description="Study activities for the day",
        examples=[["study", "practice"], ["review"], ["mixed_review"]],
    )

    hours_allocated: float = Field(
        ...,
        gt=0,
        le=24,
        description="Hours allocated for this day",
        examples=[2.0, 1.5],
    )

    ef: float = Field(
        ...,
        ge=1.3,
        le=2.5,
        description="Average easiness factor for topics",
        examples=[2.5, 2.2],
    )

    completed: bool = Field(
        default=False,
        description="Whether this day has been completed",
    )


class CreateScheduleRequest(BaseModel):
    """
    Request to create a new study schedule.

    Used for POST /api/planning/create-schedule endpoint.

    Attributes:
        student_id: UUID of student
        subject_id: UUID of subject
        exam_date: Target exam date
        available_days: Number of days available for study
        hours_per_day: Hours student can study per day
        prioritize_weaknesses: Whether to prioritize topics from improvement plans

    Examples:
        >>> request = CreateScheduleRequest(
        ...     student_id=UUID("..."),
        ...     subject_id=UUID("..."),
        ...     exam_date=date(2025, 3, 15),
        ...     available_days=30,
        ...     hours_per_day=2.0,
        ...     prioritize_weaknesses=True
        ... )

    Constitutional Compliance:
        - Principle III: Evidence-based planning (SM-2 + interleaving)
        - 100% syllabus coverage requirement
    """

    student_id: UUID = Field(
        ...,
        description="UUID of student",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    subject_id: UUID = Field(
        ...,
        description="UUID of subject",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )

    exam_date: date = Field(
        ...,
        description="Target exam date",
        examples=[date(2025, 3, 15)],
    )

    available_days: int = Field(
        ...,
        ge=7,
        le=365,
        description="Number of days available for study",
        examples=[30, 60, 90],
    )

    hours_per_day: float = Field(
        ...,
        gt=0,
        le=12,
        description="Hours student can study per day",
        examples=[2.0, 1.5, 3.0],
    )

    prioritize_weaknesses: bool = Field(
        default=True,
        description="Whether to prioritize topics from improvement plans",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
                "subject_id": "770e8400-e29b-41d4-a716-446655440002",
                "exam_date": "2025-03-15",
                "available_days": 30,
                "hours_per_day": 2.0,
                "prioritize_weaknesses": True,
            }
        }
    }


class StudyPlanResponse(BaseModel):
    """
    Complete study plan with SM-2 intervals and contextual interleaving.

    Response for POST /api/planning/create-schedule and GET /api/planning/schedule/{id} endpoints.

    Attributes:
        plan_id: UUID of study plan
        student_id: UUID of student
        subject_id: UUID of subject
        subject_code: Subject code (e.g., "9708")
        exam_date: Target exam date
        total_days: Total days in plan
        hours_per_day: Hours allocated per day
        schedule: Day-by-day schedule with SM-2 intervals
        easiness_factors: Current EF for each syllabus point
        syllabus_coverage: Percentage of syllabus covered (0-100)
        status: Plan status (active/completed/abandoned)
        rationale: Explanation of schedule structure

    Examples:
        >>> response = StudyPlanResponse(
        ...     plan_id=UUID("..."),
        ...     student_id=UUID("..."),
        ...     subject_id=UUID("..."),
        ...     subject_code="9708",
        ...     exam_date=date(2025, 3, 15),
        ...     total_days=30,
        ...     hours_per_day=2.0,
        ...     schedule=[...],
        ...     easiness_factors={"9708.1.1": 2.5},
        ...     syllabus_coverage=100.0,
        ...     status="active",
        ...     rationale="..."
        ... )

    Constitutional Compliance:
        - Principle III: Evidence-based SM-2 algorithm
        - 100% syllabus coverage validation
    """

    plan_id: UUID = Field(
        ...,
        description="UUID of study plan",
        examples=["880e8400-e29b-41d4-a716-446655440007"],
    )

    student_id: UUID = Field(
        ...,
        description="UUID of student",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    subject_id: UUID = Field(
        ...,
        description="UUID of subject",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )

    subject_code: str = Field(
        ...,
        description="Subject code",
        examples=["9708"],
    )

    exam_date: date = Field(
        ...,
        description="Target exam date",
        examples=[date(2025, 3, 15)],
    )

    total_days: int = Field(
        ...,
        ge=1,
        description="Total days in plan",
        examples=[30],
    )

    hours_per_day: float = Field(
        ...,
        gt=0,
        le=12,
        description="Hours allocated per day",
        examples=[2.0],
    )

    schedule: List[DaySchedule] = Field(
        ...,
        description="Day-by-day schedule with SM-2 intervals",
    )

    easiness_factors: Dict[str, float] = Field(
        ...,
        description="Current EF for each syllabus point (1.3-2.5)",
        examples=[{"9708.1.1": 2.5, "9708.1.2": 2.2}],
    )

    syllabus_coverage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of syllabus covered (0-100)",
        examples=[100.0],
    )

    status: str = Field(
        ...,
        description="Plan status",
        examples=["active", "completed", "abandoned"],
    )

    rationale: str = Field(
        ...,
        description="Explanation of schedule structure and SM-2 intervals",
        examples=["Schedule uses SM-2 algorithm with I(1)=1, I(2)=6 days. Topics grouped by section for contextual interleaving (max 3/day). Weak topics (from improvement plans) prioritized early."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "plan_id": "880e8400-e29b-41d4-a716-446655440007",
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
                "subject_id": "770e8400-e29b-41d4-a716-446655440002",
                "subject_code": "9708",
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
                        "completed": False,
                    },
                    {
                        "day": 2,
                        "date": "2025-01-16",
                        "topics": ["9708.1.1", "9708.1.2"],
                        "interval": 1,
                        "activities": ["review"],
                        "hours_allocated": 1.5,
                        "ef": 2.5,
                        "completed": False,
                    },
                ],
                "easiness_factors": {"9708.1.1": 2.5, "9708.1.2": 2.5},
                "syllabus_coverage": 100.0,
                "status": "active",
                "rationale": "Schedule uses SM-2 algorithm...",
            }
        }
    }


class UpdateProgressRequest(BaseModel):
    """
    Request to update progress on a day in the study plan.

    Used for PATCH /api/planning/schedule/{plan_id}/progress endpoint.

    Attributes:
        day_number: Which day number to mark complete
        performance_percentages: Performance on each topic (0-100)
        hours_spent: Actual hours spent

    Examples:
        >>> request = UpdateProgressRequest(
        ...     day_number=1,
        ...     performance_percentages={"9708.1.1": 85.0, "9708.1.2": 90.0},
        ...     hours_spent=2.5
        ... )

    Constitutional Compliance:
        - Principle III: Adaptive learning (performance updates EF)
    """

    day_number: int = Field(
        ...,
        ge=1,
        description="Which day number to mark complete",
        examples=[1, 7],
    )

    performance_percentages: Dict[str, float] = Field(
        ...,
        description="Performance on each topic (0-100)",
        examples=[{"9708.1.1": 85.0, "9708.1.2": 90.0}],
    )

    hours_spent: float = Field(
        ...,
        gt=0,
        le=24,
        description="Actual hours spent",
        examples=[2.5],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "day_number": 1,
                "performance_percentages": {"9708.1.1": 85.0, "9708.1.2": 90.0},
                "hours_spent": 2.5,
            }
        }
    }


class ProgressUpdate(BaseModel):
    """
    Response after updating progress.

    Response for PATCH /api/planning/schedule/{plan_id}/progress endpoint.

    Attributes:
        plan_id: UUID of study plan
        day_number: Day that was marked complete
        updated_easiness_factors: New EF values after performance update
        next_review_dates: When each topic should be reviewed next
        schedule_adjusted: Whether schedule was rescheduled
        adjustment_summary: Summary of any schedule changes

    Examples:
        >>> update = ProgressUpdate(
        ...     plan_id=UUID("..."),
        ...     day_number=1,
        ...     updated_easiness_factors={"9708.1.1": 2.5, "9708.1.2": 2.6},
        ...     next_review_dates={"9708.1.1": "2025-01-22", "9708.1.2": "2025-01-22"},
        ...     schedule_adjusted=False,
        ...     adjustment_summary=""
        ... )

    Constitutional Compliance:
        - Principle III: SM-2 adaptive learning
    """

    plan_id: UUID = Field(
        ...,
        description="UUID of study plan",
        examples=["880e8400-e29b-41d4-a716-446655440007"],
    )

    day_number: int = Field(
        ...,
        ge=1,
        description="Day that was marked complete",
        examples=[1],
    )

    updated_easiness_factors: Dict[str, float] = Field(
        ...,
        description="New EF values after performance update (1.3-2.5)",
        examples=[{"9708.1.1": 2.5, "9708.1.2": 2.6}],
    )

    next_review_dates: Dict[str, str] = Field(
        ...,
        description="When each topic should be reviewed next (YYYY-MM-DD)",
        examples=[{"9708.1.1": "2025-01-22", "9708.1.2": "2025-01-22"}],
    )

    schedule_adjusted: bool = Field(
        ...,
        description="Whether schedule was rescheduled based on performance",
    )

    adjustment_summary: str = Field(
        ...,
        description="Summary of any schedule changes",
        examples=["Topics 9708.1.1 and 9708.1.2 rescheduled to Day 8 based on excellent performance (EF increased to 2.6)"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "plan_id": "880e8400-e29b-41d4-a716-446655440007",
                "day_number": 1,
                "updated_easiness_factors": {"9708.1.1": 2.5, "9708.1.2": 2.6},
                "next_review_dates": {
                    "9708.1.1": "2025-01-22",
                    "9708.1.2": "2025-01-22",
                },
                "schedule_adjusted": False,
                "adjustment_summary": "No adjustments needed - schedule remains optimal",
            }
        }
    }
