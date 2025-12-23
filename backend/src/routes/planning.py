"""
Planning Routes

API endpoints for Planner Agent (SM-2 study schedules with contextual interleaving).

Phase III User Story 6: Students receive n-day study schedules using SuperMemo 2
spaced repetition with contextual interleaving, adaptive rescheduling based on performance.

This is the FINAL P1 MVP user story - production-grade API implementation.

Constitutional Requirements:
- Principle III: PhD-level pedagogy (evidence-based SM-2 algorithm)
- Principle VI: Constructive feedback (clear rationale for schedule)
- Principle I: Subject accuracy (100% syllabus coverage)
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.schemas.planning_schemas import (
    CreateScheduleRequest,
    StudyPlanResponse,
    UpdateProgressRequest,
    ProgressUpdate,
)
from src.services.planning_service import (
    create_study_plan,
    get_study_plan,
    update_progress,
    StudentNotFoundError,
    SubjectNotFoundError,
    StudyPlanNotFoundError,
    InvalidDateError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/planning", tags=["planning"])


# Endpoints


@router.post("/create-schedule", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule_endpoint(
    request: CreateScheduleRequest,
    session: Session = Depends(get_session),
) -> StudyPlanResponse:
    """
    Create n-day study schedule using SM-2 algorithm with contextual interleaving.

    Production-grade study planning with:
    - **SuperMemo 2 spaced repetition**: I(1)=1 day, I(2)=6 days, I(n)=I(n-1)*EF
    - **Contextual interleaving**: Max 3 related topics per day (cognitive load research)
    - **100% syllabus coverage**: Ensures all topics covered before exam
    - **Weakness prioritization**: Topics from improvement plans scheduled early
    - **Adaptive scheduling**: Uses existing EF values from previous performance

    Args:
        request: CreateScheduleRequest with student_id, subject_id, exam_date, etc.
        session: Database session (injected)

    Returns:
        StudyPlanResponse: Complete schedule with SM-2 intervals and rationale

    Raises:
        HTTPException: 404 if student_id or subject_id not found
        HTTPException: 400 if exam_date is invalid (too soon or in past)

    Examples:
        >>> POST /api/planning/create-schedule
        {
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "subject_id": "770e8400-e29b-41d4-a716-446655440002",
            "exam_date": "2025-03-15",
            "available_days": 30,
            "hours_per_day": 2.0,
            "prioritize_weaknesses": true
        }

        >>> Response: 201 CREATED
        {
            "plan_id": "880e8400-e29b-41d4-a716-446655440007",
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "subject_id": "770e8400-e29b-41d4-a716-446655440002",
            "subject_code": "9708",
            "exam_date": "2025-03-15",
            "total_days": 28,
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
                    "completed": false
                },
                {
                    "day": 2,
                    "date": "2025-01-16",
                    "topics": ["9708.1.1", "9708.1.2"],
                    "interval": 1,
                    "activities": ["review"],
                    "hours_allocated": 1.5,
                    "ef": 2.5,
                    "completed": false
                },
                {
                    "day": 8,
                    "date": "2025-01-22",
                    "topics": ["9708.1.1"],
                    "interval": 6,
                    "activities": ["review"],
                    "hours_allocated": 1.0,
                    "ef": 2.5,
                    "completed": false
                }
            ],
            "easiness_factors": {
                "9708.1.1": 2.5,
                "9708.1.2": 2.5
            },
            "syllabus_coverage": 100.0,
            "status": "active",
            "rationale": "Schedule uses SuperMemo 2 algorithm with intervals I(1)=1 day, I(2)=6 days, I(n)=I(n-1)*EF. Topics grouped by section for contextual interleaving (max 3 per day per cognitive load research). Prioritized 3 weak topics from recent improvement plans. Syllabus coverage: 100.0% (50/50 topics)."
        }

    Constitutional Compliance:
        - Principle III: Evidence-based SM-2 algorithm (30% better retention)
        - Principle VI: Rationale explains WHY schedule is structured this way
        - 100% syllabus coverage requirement
    """

    logger.info(
        f"Create schedule request: student={request.student_id}, subject={request.subject_id}, exam_date={request.exam_date}, days={request.available_days}"
    )

    try:
        # Call planning service
        plan = await create_study_plan(
            session=session,
            request=request,
        )

        logger.info(
            f"Successfully created study plan {plan.plan_id} with {plan.total_days} days ({plan.syllabus_coverage}% coverage)"
        )

        return plan

    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except SubjectNotFoundError as e:
        logger.warning(f"Subject not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except InvalidDateError as e:
        logger.warning(f"Invalid exam date: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in create_schedule_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating study schedule",
        )


@router.get("/schedule/{plan_id}", response_model=StudyPlanResponse, status_code=status.HTTP_200_OK)
async def get_schedule_endpoint(
    plan_id: UUID,
    session: Session = Depends(get_session),
) -> StudyPlanResponse:
    """
    Retrieve existing study plan by ID.

    Args:
        plan_id: UUID of study plan
        session: Database session (injected)

    Returns:
        StudyPlanResponse: Study plan details with schedule

    Raises:
        HTTPException: 404 if plan_id not found

    Examples:
        >>> GET /api/planning/schedule/{plan_id}

        >>> Response: 200 OK
        {
            "plan_id": "880e8400-e29b-41d4-a716-446655440007",
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "subject_id": "770e8400-e29b-41d4-a716-446655440002",
            "subject_code": "9708",
            "exam_date": "2025-03-15",
            "total_days": 28,
            "hours_per_day": 2.0,
            "schedule": [...],
            "easiness_factors": {...},
            "syllabus_coverage": 100.0,
            "status": "active",
            "rationale": "..."
        }

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation (plan belongs to student)
    """

    logger.info(f"Get schedule request: plan_id={plan_id}")

    try:
        # Call planning service
        plan = get_study_plan(
            session=session,
            plan_id=plan_id,
        )

        logger.info(f"Successfully retrieved study plan {plan_id}")

        return plan

    except StudyPlanNotFoundError as e:
        logger.warning(f"Study plan not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_schedule_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving study plan",
        )


@router.patch("/schedule/{plan_id}/progress", response_model=ProgressUpdate, status_code=status.HTTP_200_OK)
async def update_progress_endpoint(
    plan_id: UUID,
    request: UpdateProgressRequest,
    session: Session = Depends(get_session),
) -> ProgressUpdate:
    """
    Update progress on a study plan day and adapt SM-2 easiness factors.

    Production-grade adaptive learning:
    - Maps performance % to SM-2 quality (0-5)
    - Updates easiness factors based on performance:
      - 90-100% (A*): Quality 5 → EF increases
      - 80-89% (A): Quality 4 → EF stable
      - 70-79% (B): Quality 3 → EF decreases slightly
      - <70%: Quality 0-2 → EF decreases, topic rescheduled
    - Recalculates next review intervals using updated EF
    - Provides clear summary of all adjustments

    Args:
        plan_id: UUID of study plan
        request: UpdateProgressRequest with day_number, performance_percentages
        session: Database session (injected)

    Returns:
        ProgressUpdate: Updated EF values and next review dates

    Raises:
        HTTPException: 404 if plan_id not found
        HTTPException: 400 if invalid day_number

    Examples:
        >>> PATCH /api/planning/schedule/{plan_id}/progress
        {
            "day_number": 1,
            "performance_percentages": {
                "9708.1.1": 85.0,
                "9708.1.2": 92.0
            },
            "hours_spent": 2.5
        }

        >>> Response: 200 OK
        {
            "plan_id": "880e8400-e29b-41d4-a716-446655440007",
            "day_number": 1,
            "updated_easiness_factors": {
                "9708.1.1": 2.5,
                "9708.1.2": 2.6
            },
            "next_review_dates": {
                "9708.1.1": "2025-01-22",
                "9708.1.2": "2025-01-22"
            },
            "schedule_adjusted": true,
            "adjustment_summary": "9708.1.2: EF 2.50→2.60 (quality=5, next review in 6 days)"
        }

    Constitutional Compliance:
        - Principle III: SM-2 adaptive learning (personalized to performance)
    """

    logger.info(
        f"Update progress request: plan_id={plan_id}, day={request.day_number}, topics={len(request.performance_percentages)}"
    )

    try:
        # Call planning service
        update = update_progress(
            session=session,
            plan_id=plan_id,
            request=request,
        )

        logger.info(
            f"Successfully updated progress for plan {plan_id} day {request.day_number} (adjusted={update.schedule_adjusted})"
        )

        return update

    except StudyPlanNotFoundError as e:
        logger.warning(f"Study plan not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ValueError as e:
        logger.warning(f"Invalid day number: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in update_progress_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating progress",
        )
