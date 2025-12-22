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
from src.schemas.teaching_schemas import ExplainConceptRequest, TopicExplanation
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
