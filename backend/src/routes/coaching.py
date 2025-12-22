"""
Coaching Routes

API endpoints for Coach Agent (personalized tutoring).

Phase III User Story 2: Students struggling with concepts can get personalized
tutoring via Socratic questioning with adaptive follow-ups.

Constitutional Requirements:
- Principle III: PhD-level pedagogy (Socratic method)
- Principle VI: Constructive feedback (guide rather than tell)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.schemas.coaching_schemas import (
    StartSessionRequest,
    SessionResponse,
    RespondRequest,
    TranscriptResponse,
)
from src.services.coaching_service import (
    start_tutoring_session,
    respond_to_coach,
    get_session_transcript,
    StudentNotFoundError,
    SessionNotFoundError,
    LLMResponseError,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/coaching", tags=["coaching"])


# Endpoints


@router.post("/tutor-session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_tutoring_session(
    request: StartSessionRequest,
    session: Session = Depends(get_session),
) -> SessionResponse:
    """
    Start a new personalized tutoring session with Coach Agent.

    Uses Socratic method to diagnose misconceptions and guide student discovery.
    Coach's first response is always a diagnostic question, never a direct answer.

    Args:
        request: StartSessionRequest with student_id, topic, struggle_description
        session: Database session (injected)

    Returns:
        SessionResponse: First coach message with session_id and diagnosis

    Raises:
        HTTPException: 404 if student_id not found
        HTTPException: 500 if LLM fails to generate valid response

    Examples:
        >>> POST /api/coaching/tutor-session
        {
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "topic": "price elasticity of demand",
            "struggle_description": "I don't understand why PED is negative",
            "context": "I got confused when the graph showed negative slope"
        }

        >>> Response: 201 CREATED
        {
            "session_id": "770e8400-e29b-41d4-a716-446655440002",
            "coach_message": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
            "internal_diagnosis": {
                "misconception_detected": null,
                "knowledge_gaps": ["price-quantity relationship"],
                "current_understanding_level": "none",
                "recommended_next_step": "diagnose"
            },
            "session_notes": {
                "progress_made": "Session started",
                "remaining_gaps": ["price-quantity relationship", "PED calculation"],
                "outcome": "in_progress"
            },
            "outcome": "in_progress"
        }

    Constitutional Compliance:
        - Principle I: Topic validated against Cambridge Economics 9708 syllabus
        - Principle III: Uses Socratic method (CoachPrompts)
        - Principle VI: Never gives direct answers, always guides discovery
    """

    logger.info(
        f"Create tutoring session request: student_id={request.student_id}, topic={request.topic}"
    )

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call coaching service with fallback orchestration
        response = await start_tutoring_session(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully created tutoring session {response.session_id} for student {request.student_id}"
        )

        return response

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
            detail=f"Failed to generate coaching response: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in create_tutoring_session endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating tutoring session",
        )


@router.post("/session/{session_id}/respond", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def respond_in_session(
    session_id: UUID,
    request: RespondRequest,
    session: Session = Depends(get_session),
) -> SessionResponse:
    """
    Send student response and receive next Socratic question.

    Appends student response to session transcript, generates adaptive follow-up
    from Coach Agent, and updates session state.

    Args:
        session_id: UUID of coaching session
        request: RespondRequest with student_response
        session: Database session (injected)

    Returns:
        SessionResponse: Next coach message with updated diagnosis

    Raises:
        HTTPException: 404 if session_id not found
        HTTPException: 500 if LLM fails to generate valid response

    Examples:
        >>> POST /api/coaching/session/{session_id}/respond
        {
            "student_response": "It decreases",
            "request_hint": false
        }

        >>> Response: 200 OK
        {
            "session_id": "770e8400-e29b-41d4-a716-446655440002",
            "coach_message": "Great! Now, why do you think quantity demanded decreases when price increases?",
            "internal_diagnosis": {
                "misconception_detected": null,
                "knowledge_gaps": ["law of demand reasoning"],
                "current_understanding_level": "partial",
                "recommended_next_step": "guide"
            },
            "session_notes": {
                "progress_made": "Student understands inverse price-quantity relationship",
                "remaining_gaps": ["law of demand reasoning", "PED calculation"],
                "outcome": "in_progress"
            },
            "outcome": "in_progress"
        }

    Constitutional Compliance:
        - Principle III: Adaptive Socratic questioning based on student response
        - Principle VI: Celebrates correct reasoning, gently corrects misconceptions
    """

    logger.info(
        f"Respond in session request: session_id={session_id}, response_length={len(request.student_response)}"
    )

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call coaching service with fallback orchestration
        response = await respond_to_coach(
            session=session,
            session_id=session_id,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully generated coach response for session {session_id} (outcome: {response.outcome})"
        )

        return response

    except SessionNotFoundError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate coaching response: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in respond_in_session endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing student response",
        )


@router.get("/session/{session_id}", response_model=TranscriptResponse, status_code=status.HTTP_200_OK)
async def get_session(
    session_id: UUID,
    session: Session = Depends(get_session),
) -> TranscriptResponse:
    """
    Retrieve full coaching session transcript.

    Returns complete conversation history between student and coach, including
    metadata and outcome status.

    Args:
        session_id: UUID of coaching session
        session: Database session (injected)

    Returns:
        TranscriptResponse: Full session transcript with metadata

    Raises:
        HTTPException: 404 if session_id not found

    Examples:
        >>> GET /api/coaching/session/{session_id}

        >>> Response: 200 OK
        {
            "session_id": "770e8400-e29b-41d4-a716-446655440002",
            "student_id": "660e8400-e29b-41d4-a716-446655440001",
            "topic": "price elasticity of demand",
            "struggle_description": "I don't understand why PED is negative",
            "transcript": [
                {
                    "role": "coach",
                    "content": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
                    "timestamp": "2025-01-15T10:00:00Z"
                },
                {
                    "role": "student",
                    "content": "It decreases",
                    "timestamp": "2025-01-15T10:00:30Z"
                },
                {
                    "role": "coach",
                    "content": "Great! Now, why do you think quantity demanded decreases when price increases?",
                    "timestamp": "2025-01-15T10:01:00Z"
                }
            ],
            "outcome": "in_progress",
            "created_at": "2025-01-15T10:00:00Z",
            "updated_at": "2025-01-15T10:01:00Z"
        }

    Constitutional Compliance:
        - Principle VI: Transparent coaching process (full transcript available)
    """

    logger.info(f"Get session transcript request: session_id={session_id}")

    try:
        # Call coaching service to retrieve transcript
        transcript = get_session_transcript(
            session=session,
            session_id=session_id,
        )

        logger.info(
            f"Successfully retrieved session transcript {session_id} ({len(transcript.transcript)} messages)"
        )

        return transcript

    except SessionNotFoundError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_session endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving session transcript",
        )
