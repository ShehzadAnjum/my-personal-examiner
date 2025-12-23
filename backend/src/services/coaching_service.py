"""
Coaching Service

Business logic for Coach Agent (personalized tutoring).

Phase III User Story 2: Students struggling with concepts can get personalized
tutoring via Socratic questioning with adaptive follow-ups.

Constitutional Requirements:
- Principle III: PhD-level pedagogy (Socratic method, misconception diagnosis)
- Principle VI: Constructive feedback (guide rather than tell, never say "wrong")
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy.orm.attributes import flag_modified

from src.models.coaching_session import CoachingSession, MessageDict
from src.models.student import Student
from src.schemas.coaching_schemas import (
    StartSessionRequest,
    SessionResponse,
    RespondRequest,
    TranscriptResponse,
    InternalDiagnosis,
    SessionNotes,
    SessionMessage,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator
from src.ai_integration.prompt_templates.coach_prompts import (
    CoachPrompts,
    create_tutoring_prompt,
)

logger = logging.getLogger(__name__)


class StudentNotFoundError(Exception):
    """Raised when student ID not found in database"""

    pass


class SessionNotFoundError(Exception):
    """Raised when coaching session ID not found in database"""

    pass


class LLMResponseError(Exception):
    """Raised when LLM response cannot be parsed or is invalid"""

    pass


async def start_tutoring_session(
    session: Session,
    request: StartSessionRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> SessionResponse:
    """
    Start a new personalized tutoring session with Coach Agent.

    Uses Socratic method to diagnose misconceptions and provide scaffolded learning.
    First message from coach is always a diagnostic question.

    Args:
        session: Database session
        request: StartSessionRequest with student_id, topic, struggle_description
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        SessionResponse: First coach message with diagnosis and session ID

    Raises:
        StudentNotFoundError: If student_id not found
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = StartSessionRequest(
        ...     student_id=UUID("..."),
        ...     topic="price elasticity of demand",
        ...     struggle_description="I don't understand why PED is negative"
        ... )
        >>> response = await start_tutoring_session(session, request)
        >>> response.coach_message
        "Let's start simple: Can you explain what happens to quantity demanded when price increases?"

    Constitutional Compliance:
        - Principle I: topic validated against Cambridge syllabus (future enhancement)
        - Principle III: Uses Socratic method (CoachPrompts.tutor_session_prompt)
        - Principle VI: Diagnostic questions rather than direct answers

    LLM Workflow:
        1. Fetch student and context from database
        2. Build Socratic tutoring prompt with CoachPrompts
        3. Call LLM with fallback (Claude → GPT-4 → Gemini)
        4. Parse JSON response (coach_message, internal_diagnosis, session_notes)
        5. Create CoachingSession record with initial coach message
        6. Return SessionResponse with session_id
    """

    # Step 1: Fetch student from database
    statement = select(Student).where(Student.id == request.student_id)
    student = session.exec(statement).first()

    if not student:
        raise StudentNotFoundError(f"Student {request.student_id} not found")

    # Step 2: Build student context (weaknesses from previous sessions)
    student_context: Dict[str, Any] = {}
    if request.context:
        student_context["context"] = request.context

    # TODO: Query improvement_plans table for student weaknesses when available
    # For now, just pass context from request

    # Step 3: Create Socratic tutoring prompt (initial diagnosis)
    prompt = create_tutoring_prompt(
        topic=request.topic,
        struggle_description=request.struggle_description,
        student_context=student_context if student_context else None,
        session_history=None,  # No history for new session
    )

    # Step 4: Call LLM with fallback orchestration
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Starting tutoring session for student {request.student_id} on topic '{request.topic}'"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.7,  # Higher temperature for conversational responses
            max_tokens=1500,  # Shorter responses than teacher (Socratic questions)
            system_prompt=CoachPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate coaching response: {str(e)}") from e

    # Step 5: Parse JSON response
    try:
        # Extract JSON from response (LLM might wrap in markdown code blocks)
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()

        response_data = json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Response text: {response_text[:500]}...")
        raise LLMResponseError(f"LLM response not valid JSON: {str(e)}") from e

    # Step 6: Create CoachingSession record
    try:
        coach_message = response_data.get("coach_message", "")
        internal_diagnosis_data = response_data.get("internal_diagnosis", {})
        session_notes_data = response_data.get("session_notes", {})

        # Create initial transcript with coach's first message
        now_iso = datetime.now(timezone.utc).isoformat()
        initial_transcript: List[MessageDict] = [
            {
                "role": "coach",
                "content": coach_message,
                "timestamp": now_iso,
            }
        ]

        # Create database record
        coaching_session = CoachingSession(
            student_id=request.student_id,
            topic=request.topic,
            struggle_description=request.struggle_description,
            session_transcript=initial_transcript,
            outcome=session_notes_data.get("outcome", "in_progress"),
        )

        session.add(coaching_session)
        session.commit()
        session.refresh(coaching_session)

        logger.info(
            f"Created coaching session {coaching_session.id} for student {request.student_id}"
        )

        # Step 7: Build SessionResponse
        return SessionResponse(
            session_id=coaching_session.id,
            coach_message=coach_message,
            internal_diagnosis=InternalDiagnosis(
                misconception_detected=internal_diagnosis_data.get("misconception_detected"),
                knowledge_gaps=internal_diagnosis_data.get("knowledge_gaps", []),
                current_understanding_level=internal_diagnosis_data.get(
                    "current_understanding_level", "none"
                ),
                recommended_next_step=internal_diagnosis_data.get(
                    "recommended_next_step", "diagnose"
                ),
            ),
            session_notes=SessionNotes(
                progress_made=session_notes_data.get("progress_made", "Session started"),
                remaining_gaps=session_notes_data.get("remaining_gaps", []),
                outcome=session_notes_data.get("outcome", "in_progress"),
            ),
            outcome=coaching_session.outcome,
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build SessionResponse from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


async def respond_to_coach(
    session: Session,
    session_id: UUID,
    request: RespondRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> SessionResponse:
    """
    Process student response and generate next Socratic question.

    Appends student response to session transcript, calls Coach Agent for
    adaptive follow-up, and updates session state.

    Args:
        session: Database session
        session_id: UUID of coaching session
        request: RespondRequest with student_response
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        SessionResponse: Next coach message with updated diagnosis

    Raises:
        SessionNotFoundError: If session_id not found
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = RespondRequest(student_response="It decreases")
        >>> response = await respond_to_coach(session, session_id, request)
        >>> response.coach_message
        "Great! Now, why do you think quantity demanded decreases when price increases?"

    Constitutional Compliance:
        - Principle III: Adaptive Socratic questioning based on student response
        - Principle VI: Never says "wrong" - guides discovery gently

    LLM Workflow:
        1. Fetch existing coaching session from database
        2. Append student response to session transcript
        3. Build prompt with full session history (last 5 messages)
        4. Call LLM with fallback for next Socratic question
        5. Parse response and update session transcript
        6. Update session outcome if resolved/needs_more_help/refer_to_teacher
        7. Return SessionResponse
    """

    # Step 1: Fetch existing coaching session
    statement = select(CoachingSession).where(CoachingSession.id == session_id)
    coaching_session = session.exec(statement).first()

    if not coaching_session:
        raise SessionNotFoundError(f"Coaching session {session_id} not found")

    # Step 2: Append student response to transcript
    now_iso = datetime.now(timezone.utc).isoformat()
    student_message: MessageDict = {
        "role": "student",
        "content": request.student_response,
        "timestamp": now_iso,
    }

    coaching_session.session_transcript.append(student_message)
    flag_modified(coaching_session, "session_transcript")  # Tell SQLAlchemy the JSON changed

    # Step 3: Build prompt with session history
    session_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in coaching_session.session_transcript
    ]

    hint_request = " (Student is requesting a hint)" if request.request_hint else ""

    prompt = create_tutoring_prompt(
        topic=coaching_session.topic,
        struggle_description=f"{coaching_session.struggle_description}{hint_request}",
        student_context=None,  # Context already in session history
        session_history=session_history,
    )

    # Step 4: Call LLM with fallback
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Generating coach response for session {session_id} (message #{len(session_history)})"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500,
            system_prompt=CoachPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate coaching response: {str(e)}") from e

    # Step 5: Parse JSON response
    try:
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()

        response_data = json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Response text: {response_text[:500]}...")
        raise LLMResponseError(f"LLM response not valid JSON: {str(e)}") from e

    # Step 6: Append coach response to transcript and update session
    try:
        coach_message = response_data.get("coach_message", "")
        session_notes_data = response_data.get("session_notes", {})

        coach_response: MessageDict = {
            "role": "coach",
            "content": coach_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        coaching_session.session_transcript.append(coach_response)
        flag_modified(coaching_session, "session_transcript")  # Tell SQLAlchemy the JSON changed
        coaching_session.outcome = session_notes_data.get("outcome", "in_progress")
        coaching_session.updated_at = datetime.now(timezone.utc)

        session.add(coaching_session)
        session.commit()
        session.refresh(coaching_session)

        logger.info(
            f"Updated coaching session {session_id} (outcome: {coaching_session.outcome})"
        )

        # Step 7: Build SessionResponse
        internal_diagnosis_data = response_data.get("internal_diagnosis", {})

        return SessionResponse(
            session_id=coaching_session.id,
            coach_message=coach_message,
            internal_diagnosis=InternalDiagnosis(
                misconception_detected=internal_diagnosis_data.get("misconception_detected"),
                knowledge_gaps=internal_diagnosis_data.get("knowledge_gaps", []),
                current_understanding_level=internal_diagnosis_data.get(
                    "current_understanding_level", "partial"
                ),
                recommended_next_step=internal_diagnosis_data.get(
                    "recommended_next_step", "guide"
                ),
            ),
            session_notes=SessionNotes(
                progress_made=session_notes_data.get("progress_made", ""),
                remaining_gaps=session_notes_data.get("remaining_gaps", []),
                outcome=session_notes_data.get("outcome", "in_progress"),
            ),
            outcome=coaching_session.outcome,
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build SessionResponse from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


def get_session_transcript(
    session: Session,
    session_id: UUID,
) -> TranscriptResponse:
    """
    Retrieve full coaching session transcript.

    Args:
        session: Database session
        session_id: UUID of coaching session

    Returns:
        TranscriptResponse: Full session transcript with metadata

    Raises:
        SessionNotFoundError: If session_id not found

    Examples:
        >>> transcript = get_session_transcript(session, session_id)
        >>> len(transcript.transcript)
        5  # 3 student messages, 2 coach messages

    Constitutional Compliance:
        - Principle VI: Transparent coaching process (full transcript available)
    """

    # Fetch coaching session
    statement = select(CoachingSession).where(CoachingSession.id == session_id)
    coaching_session = session.exec(statement).first()

    if not coaching_session:
        raise SessionNotFoundError(f"Coaching session {session_id} not found")

    # Build TranscriptResponse
    transcript = [
        SessionMessage(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"],
        )
        for msg in coaching_session.session_transcript
    ]

    return TranscriptResponse(
        session_id=coaching_session.id,
        student_id=coaching_session.student_id,
        topic=coaching_session.topic,
        struggle_description=coaching_session.struggle_description,
        transcript=transcript,
        outcome=coaching_session.outcome,
        created_at=coaching_session.created_at,
        updated_at=coaching_session.updated_at,
    )
