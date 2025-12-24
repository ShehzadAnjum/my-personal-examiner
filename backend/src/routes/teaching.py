"""
Teaching Routes

API endpoints for Teacher Agent (concept explanations).

Phase III User Story 1: Students request PhD-level explanations of
Economics 9708 syllabus concepts with examples, diagrams, and practice problems.

Constitutional Requirements:
- Principle I: Subject accuracy (Cambridge syllabus alignment)
- Principle III: PhD-level pedagogy (evidence-based teaching)
- Principle VI: Constructive feedback (clear explanations)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.schemas.teaching_schemas import (
    ExplainConceptRequest,
    TopicExplanation,
    SaveExplanationRequest,
)
from src.services.teaching_service import (
    explain_concept,
    SyllabusPointNotFoundError,
    StudentNotFoundError,
    LLMResponseError,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/teaching", tags=["teaching"])


# Endpoints


@router.post("/explain-concept", response_model=TopicExplanation, status_code=status.HTTP_200_OK)
async def explain_concept_endpoint(
    request: ExplainConceptRequest,
    session: Session = Depends(get_session),
) -> TopicExplanation:
    """
    Generate PhD-level explanation for a syllabus concept.

    Teacher Agent provides comprehensive explanations with:
    - Precise definitions and key terms
    - Real-world examples with data
    - Visual aids (diagrams, graphs)
    - Worked examples with step-by-step solutions
    - Common misconceptions and corrections
    - Practice problems (3-5) for student to attempt

    Args:
        request: ExplainConceptRequest with syllabus_point_id, student_id, options
        session: Database session (injected)

    Returns:
        TopicExplanation: Structured explanation with all components

    Raises:
        HTTPException: 404 if syllabus_point_id or student_id not found
        HTTPException: 500 if LLM fails to generate valid response

    Examples:
        >>> POST /api/teaching/explain-concept
        {
            "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "include_diagrams": true,
            "include_practice": true,
            "context": "I'm confused about the difference between movement along and shift of demand curve"
        }

        >>> Response: 200 OK
        {
            "syllabus_code": "9708.2.1",
            "concept_name": "Price Elasticity of Demand",
            "definition": "The responsiveness of quantity demanded to a change in price...",
            "key_terms": [...],
            "explanation": "...",
            "examples": [...],
            "visual_aids": [...],
            "worked_examples": [...],
            "common_misconceptions": [...],
            "practice_problems": [...],
            "related_concepts": ["9708.2.2", "9708.2.3"],
            "generated_by": "anthropic"
        }

    Constitutional Compliance:
        - Principle I: Validates syllabus point exists (Cambridge alignment)
        - Principle III: Uses PhD-level prompts (TeacherPrompts)
        - Principle VI: Returns structured, actionable explanation
    """

    logger.info(
        f"Explain concept request: syllabus_point_id={request.syllabus_point_id}, student_id={request.student_id}"
    )

    try:
        # Create LLM orchestrator for this request
        # (reuses same instance for potential retries)
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call teaching service with fallback orchestration
        explanation = await explain_concept(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully generated explanation for {explanation.syllabus_code} "
            f"({len(explanation.examples)} examples, {len(explanation.practice_problems)} practice problems)"
        )

        return explanation

    except SyllabusPointNotFoundError as e:
        logger.warning(f"Syllabus point not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except StudentNotFoundError as e:
        logger.warning(f"Student not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in explain_concept endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating explanation",
        )


# ============================================================================
# Saved Explanation Endpoints (Bookmark Feature)
# Feature: 005-teaching-page (User Story 3)
# ============================================================================


@router.get("/explanations", status_code=status.HTTP_200_OK)
async def get_saved_explanations(
    student_id: str,  # TODO: Extract from JWT in production
    session: Session = Depends(get_session),
) -> dict:
    """
    Get all saved explanations for a student

    Returns list of bookmarked explanations with full content.
    Multi-tenant: Filtered by student_id to ensure data isolation.

    Args:
        student_id: UUID of student (from JWT in production)
        session: Database session (injected)

    Returns:
        dict: { "saved_explanations": [SavedExplanation, ...] }

    Examples:
        >>> GET /api/teaching/explanations?student_id=660e8400...
        {
            "saved_explanations": [
                {
                    "id": "770e8400-...",
                    "student_id": "660e8400-...",
                    "syllabus_point_id": "550e8400-...",
                    "explanation_content": { /* TopicExplanation JSON */ },
                    "date_saved": "2025-12-23T10:30:00Z",
                    "date_last_viewed": "2025-12-23T14:45:00Z"
                }
            ]
        }

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation (student_id filter required)
    """
    from src.models.saved_explanation import SavedExplanation
    from sqlmodel import select
    from uuid import UUID

    logger.info(f"Get saved explanations for student_id={student_id}")

    try:
        student_uuid = UUID(student_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student_id format",
        )

    # Multi-tenant query: MUST filter by student_id
    statement = select(SavedExplanation).where(
        SavedExplanation.student_id == student_uuid
    ).order_by(SavedExplanation.date_saved.desc())

    saved_explanations = session.exec(statement).all()

    logger.info(f"Found {len(saved_explanations)} saved explanations for student {student_id}")

    return {
        "saved_explanations": [
            {
                "id": str(se.id),
                "student_id": str(se.student_id),
                "syllabus_point_id": str(se.syllabus_point_id),
                "date_saved": se.date_saved.isoformat(),
                "date_last_viewed": se.date_last_viewed.isoformat() if se.date_last_viewed else None,
            }
            for se in saved_explanations
        ]
    }


@router.post("/explanations", status_code=status.HTTP_201_CREATED)
async def save_explanation(
    request: SaveExplanationRequest,
    session: Session = Depends(get_session),
) -> dict:
    """
    Bookmark a syllabus topic for later review (pointer-based)

    Creates a SavedExplanation record with ONLY a reference to syllabus_point_id.
    Explanation content is cached in browser localStorage (not duplicated in DB).
    Prevents duplicates via unique constraint on (student_id, syllabus_point_id).

    Architecture: Pointer-based bookmarks
    - Database stores only the bookmark reference
    - Explanation content lives in localStorage
    - Simple, efficient favorite system

    Args:
        syllabus_point_id: UUID of syllabus topic to bookmark
        student_id: UUID of student (from JWT in production)
        session: Database session (injected)

    Returns:
        dict: { "saved_explanation": SavedExplanation (pointer only) }

    Raises:
        HTTPException: 409 if already bookmarked, 404 if syllabus point not found

    Examples:
        >>> POST /api/teaching/explanations
        {
            "syllabus_point_id": "550e8400-...",
            "student_id": "660e8400-..."
        }

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation (student_id required)
        - FR-012: Prevent duplicate bookmarks
    """
    from src.models.saved_explanation import SavedExplanation
    from src.models.syllabus_point import SyllabusPoint
    from sqlmodel import select
    from uuid import UUID
    from sqlalchemy.exc import IntegrityError

    logger.info(f"Save explanation: student_id={request.student_id}, syllabus_point_id={request.syllabus_point_id}")

    # Verify syllabus point exists
    sp_statement = select(SyllabusPoint).where(SyllabusPoint.id == request.syllabus_point_id)
    syllabus_point = session.exec(sp_statement).first()

    if not syllabus_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus point {request.syllabus_point_id} not found",
        )

    # Create SavedExplanation (pointer-based bookmark)
    saved_explanation = SavedExplanation(
        student_id=request.student_id,
        syllabus_point_id=request.syllabus_point_id,
    )

    try:
        session.add(saved_explanation)
        session.commit()
        session.refresh(saved_explanation)

        logger.info(f"Successfully bookmarked topic {saved_explanation.id}")

        return {
            "saved_explanation": {
                "id": str(saved_explanation.id),
                "student_id": str(saved_explanation.student_id),
                "syllabus_point_id": str(saved_explanation.syllabus_point_id),
                "date_saved": saved_explanation.date_saved.isoformat(),
                "date_last_viewed": None,
            }
        }

    except IntegrityError:
        session.rollback()
        logger.warning(f"Duplicate bookmark attempt: student={request.student_id}, topic={request.syllabus_point_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explanation already bookmarked",
        )


@router.delete("/explanations/{saved_explanation_id}", status_code=status.HTTP_200_OK)
async def remove_saved_explanation(
    saved_explanation_id: str,
    student_id: str,  # TODO: Extract from JWT in production
    session: Session = Depends(get_session),
) -> dict:
    """
    Remove a bookmarked explanation

    Deletes SavedExplanation record. Multi-tenant check ensures student can only
    delete their own bookmarks.

    Args:
        saved_explanation_id: UUID of SavedExplanation to delete
        student_id: UUID of student (from JWT in production)
        session: Database session (injected)

    Returns:
        dict: { "success": True }

    Raises:
        HTTPException: 404 if not found or not owned by student

    Examples:
        >>> DELETE /api/teaching/explanations/770e8400-...?student_id=660e8400-...
        { "success": true }

    Constitutional Compliance:
        - Principle V: Multi-tenant isolation (verify student_id match)
    """
    from src.models.saved_explanation import SavedExplanation
    from sqlmodel import select
    from uuid import UUID

    logger.info(f"Remove saved explanation: id={saved_explanation_id}, student_id={student_id}")

    try:
        saved_uuid = UUID(saved_explanation_id)
        student_uuid = UUID(student_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format",
        )

    # Multi-tenant query: MUST verify student_id matches
    statement = select(SavedExplanation).where(
        SavedExplanation.id == saved_uuid,
        SavedExplanation.student_id == student_uuid,  # Security check
    )

    saved_explanation = session.exec(statement).first()

    if not saved_explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved explanation not found or not owned by student",
        )

    session.delete(saved_explanation)
    session.commit()

    logger.info(f"Successfully removed saved explanation {saved_explanation_id}")

    return {"success": True}
