"""
Marking Routes

API endpoints for Marker Agent (PhD-level strict marking with AO1/AO2/AO3 breakdown).

Phase III User Story 4: Economics 9708 answers receive PhD-level strict marking
with error categorization and confidence scoring for manual review queue.

Constitutional Requirements:
- Principle II: A* Standard marking always (zero tolerance for imprecision)
- Principle VI: Constructive feedback (explain WHY and HOW to improve)
- Principle I: Subject accuracy (Cambridge mark scheme alignment)
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.schemas.marking_schemas import (
    MarkAnswerRequest,
    MarkingResult,
    MarkAttemptRequest,
    AttemptResult,
)
from src.services.marking_service import (
    mark_answer,
    mark_attempt,
    QuestionNotFoundError,
    AttemptNotFoundError,
    MarkSchemeNotFoundError,
    LLMResponseError,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marking", tags=["marking"])


# Endpoints


@router.post("/mark-answer", response_model=MarkingResult, status_code=status.HTTP_200_OK)
async def mark_answer_endpoint(
    request: MarkAnswerRequest,
    session: Session = Depends(get_session),
) -> MarkingResult:
    """
    Mark a single student answer using PhD-level strict standards.

    Applies Cambridge mark scheme with zero tolerance for imprecision.
    Returns AO1/AO2/AO3 breakdown, errors identified, and confidence score.
    Flags for manual review if confidence < 70%.

    Args:
        request: MarkAnswerRequest with question_id, student_answer
        session: Database session (injected)

    Returns:
        MarkingResult: Marks, AO breakdown, errors, confidence, feedback

    Raises:
        HTTPException: 404 if question_id not found or no marking scheme
        HTTPException: 500 if LLM marking fails

    Examples:
        >>> POST /api/marking/mark-answer
        {
            "question_id": "880e8400-e29b-41d4-a716-446655440003",
            "student_answer": "The law of demand states that as price rises, quantity demanded falls, ceteris paribus. This is because...",
            "max_marks": 10
        }

        >>> Response: 200 OK
        {
            "marks_awarded": 8,
            "max_marks": 10,
            "percentage": 80.0,
            "ao1_score": 5,
            "ao1_max": 6,
            "ao2_score": 3,
            "ao2_max": 4,
            "ao3_score": 0,
            "ao3_max": 0,
            "level": "L3",
            "errors": [
                {
                    "category": "AO2 - Generic Example",
                    "description": "Used 'some goods' instead of specific example with data",
                    "marks_lost": 1
                }
            ],
            "points_awarded": [
                {
                    "point_id": "AO1-1",
                    "present": true,
                    "quality": "good",
                    "quote": "as price rises, quantity demanded falls, ceteris paribus"
                }
            ],
            "confidence_score": 85,
            "needs_review": false,
            "feedback": "Your answer demonstrated good knowledge of demand concepts (AO1: 5/6)..."
        }

    Constitutional Compliance:
        - Principle II: Zero tolerance for imprecision (A* standard)
        - Principle VI: Constructive feedback with WHY and HOW
        - Confidence scoring ensures quality control
    """

    logger.info(
        f"Mark answer request: question_id={request.question_id}, answer_length={len(request.student_answer)}"
    )

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call marking service with fallback orchestration
        result = await mark_answer(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully marked answer: {result.marks_awarded}/{result.max_marks} (confidence={result.confidence_score}%, needs_review={result.needs_review})"
        )

        return result

    except QuestionNotFoundError as e:
        logger.warning(f"Question not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except MarkSchemeNotFoundError as e:
        logger.warning(f"Mark scheme not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate marking: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in mark_answer_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while marking answer",
        )


@router.post("/mark-attempt", response_model=AttemptResult, status_code=status.HTTP_200_OK)
async def mark_attempt_endpoint(
    request: MarkAttemptRequest,
    session: Session = Depends(get_session),
) -> AttemptResult:
    """
    Mark all questions in an exam attempt and aggregate results.

    Marks each question individually using PhD-level standards, then calculates
    overall score, Cambridge grade, and AO1/AO2/AO3 totals.

    Args:
        request: MarkAttemptRequest with attempt_id
        session: Database session (injected)

    Returns:
        AttemptResult: Total marks, grade, AO totals, individual results

    Raises:
        HTTPException: 404 if attempt_id not found
        HTTPException: 500 if any question marking fails

    Examples:
        >>> POST /api/marking/mark-attempt
        {
            "attempt_id": "990e8400-e29b-41d4-a716-446655440004"
        }

        >>> Response: 200 OK
        {
            "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
            "total_marks": 45,
            "max_marks": 60,
            "percentage": 75.0,
            "grade": "A",
            "ao1_total": 18,
            "ao2_total": 15,
            "ao3_total": 12,
            "question_results": [
                {
                    "marks_awarded": 15,
                    "max_marks": 20,
                    "percentage": 75.0,
                    "ao1_score": 6,
                    "ao1_max": 8,
                    ...
                }
            ],
            "needs_review": false,
            "overall_feedback": "**Overall Performance**: 45/60 marks\\n**Strength**: AO1 (Knowledge) - 18/24 (75%)..."
        }

    Constitutional Compliance:
        - Principle II: A* standard grading (strict Cambridge boundaries)
        - Principle VI: Overall feedback for improvement
    """

    logger.info(f"Mark attempt request: attempt_id={request.attempt_id}")

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call marking service with fallback orchestration
        result = await mark_attempt(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully marked attempt {request.attempt_id}: {result.total_marks}/{result.max_marks} ({result.percentage}%, Grade {result.grade})"
        )

        return result

    except AttemptNotFoundError as e:
        logger.warning(f"Attempt not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate marking: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in mark_attempt_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while marking attempt",
        )
