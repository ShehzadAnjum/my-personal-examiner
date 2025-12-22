"""
Coaching Schemas

Pydantic schemas for Coach Agent endpoints (personalized tutoring).

Phase III User Story 2: Students struggling with concepts can get personalized
tutoring via Socratic questioning with adaptive follow-ups.

Constitutional Requirements:
- Principle III: PhD-level pedagogy (Socratic method)
- Principle VI: Constructive feedback (guide rather than tell)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    """
    Request to start a new coaching session with Coach Agent.

    Used for POST /api/coaching/tutor-session endpoint.

    Attributes:
        student_id: UUID of student requesting coaching
        topic: Topic student is struggling with
        struggle_description: Student's description of their confusion/struggle
        context: Optional additional context (prior struggles, learning style)

    Examples:
        >>> request = StartSessionRequest(
        ...     student_id=UUID("..."),
        ...     topic="price elasticity of demand",
        ...     struggle_description="I don't understand why PED is negative",
        ...     context="I got confused when the graph showed negative slope"
        ... )

    Constitutional Compliance:
        - Principle I: topic linked to Cambridge syllabus topics
        - Principle III: struggle_description enables Socratic diagnosis
    """

    student_id: UUID = Field(
        ...,
        description="UUID of student requesting coaching",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    topic: str = Field(
        ...,
        max_length=500,
        description="Topic student is struggling with (concept name or syllabus point)",
        examples=["price elasticity of demand", "9708.2.1"],
    )

    struggle_description: str = Field(
        ...,
        max_length=2000,
        description="Student's description of their confusion or struggle",
        examples=["I don't understand why PED is negative when demand falls"],
    )

    context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional context about prior struggles or learning style",
        examples=["I usually understand graphs better than formulas"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
                "topic": "price elasticity of demand",
                "struggle_description": "I don't understand why PED is always negative",
                "context": "I got confused when the textbook showed negative values",
            }
        }
    }


class SessionMessage(BaseModel):
    """
    Single message in coaching session transcript.

    Attributes:
        role: Message sender (student or coach)
        content: Message text
        timestamp: ISO 8601 timestamp
    """

    role: str = Field(
        ...,
        description="Message sender (student or coach)",
        examples=["student", "coach"],
    )

    content: str = Field(
        ...,
        description="Message text",
        examples=["Can you explain what happens to quantity demanded when price increases?"],
    )

    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp",
        examples=["2025-01-15T10:00:00Z"],
    )


class InternalDiagnosis(BaseModel):
    """
    Coach's internal diagnosis of student understanding (not shown to student).

    Used for tracking session progress and adaptive responses.

    Attributes:
        misconception_detected: Specific misconception if identified
        knowledge_gaps: List of knowledge gaps identified
        current_understanding_level: Student's current understanding (none/partial/good)
        recommended_next_step: Coach's next recommended action
    """

    misconception_detected: Optional[str] = Field(
        default=None,
        description="Specific misconception if identified",
        examples=["Student confuses 'demand' with 'quantity demanded'"],
    )

    knowledge_gaps: List[str] = Field(
        default_factory=list,
        description="Knowledge gaps identified",
        examples=[["ceteris paribus condition", "difference between movement and shift"]],
    )

    current_understanding_level: str = Field(
        ...,
        description="Student's current understanding level",
        examples=["none", "partial", "good"],
    )

    recommended_next_step: str = Field(
        ...,
        description="Coach's next recommended action",
        examples=["diagnose", "guide", "practice", "refer"],
    )


class SessionNotes(BaseModel):
    """
    Session progress notes (internal tracking).

    Attributes:
        progress_made: What student has learned this session
        remaining_gaps: Knowledge gaps still present
        outcome: Session outcome status
    """

    progress_made: str = Field(
        ...,
        description="What student has learned this session",
        examples=["Student now understands that demand curve has negative slope"],
    )

    remaining_gaps: List[str] = Field(
        default_factory=list,
        description="Knowledge gaps still present",
        examples=[["calculating PED from data", "interpreting PED values"]],
    )

    outcome: str = Field(
        ...,
        description="Session outcome status",
        examples=["in_progress", "resolved", "needs_more_help", "refer_to_teacher"],
    )


class SessionResponse(BaseModel):
    """
    Response from Coach Agent for a tutoring session.

    Used for POST /api/coaching/tutor-session and POST /api/coaching/session/{id}/respond endpoints.

    Attributes:
        session_id: UUID of coaching session
        coach_message: Coach's Socratic response to student
        internal_diagnosis: Coach's internal diagnosis (for tracking)
        session_notes: Session progress notes
        outcome: Current session outcome status

    Examples:
        >>> response = SessionResponse(
        ...     session_id=UUID("..."),
        ...     coach_message="Let's start simple: Can you explain what happens to quantity demanded when price increases?",
        ...     internal_diagnosis=InternalDiagnosis(...),
        ...     session_notes=SessionNotes(...),
        ...     outcome="in_progress"
        ... )

    Constitutional Compliance:
        - Principle III: coach_message uses Socratic method
        - Principle VI: internal_diagnosis enables constructive feedback
    """

    session_id: UUID = Field(
        ...,
        description="UUID of coaching session",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )

    coach_message: str = Field(
        ...,
        description="Coach's Socratic response to student",
        examples=["Let's start simple: Can you explain what happens to quantity demanded when price increases?"],
    )

    internal_diagnosis: InternalDiagnosis = Field(
        ...,
        description="Coach's internal diagnosis (for tracking)",
    )

    session_notes: SessionNotes = Field(
        ...,
        description="Session progress notes",
    )

    outcome: str = Field(
        ...,
        description="Current session outcome status",
        examples=["in_progress", "resolved", "needs_more_help", "refer_to_teacher"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "770e8400-e29b-41d4-a716-446655440002",
                "coach_message": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
                "internal_diagnosis": {
                    "misconception_detected": None,
                    "knowledge_gaps": ["relationship between price and quantity demanded"],
                    "current_understanding_level": "none",
                    "recommended_next_step": "diagnose",
                },
                "session_notes": {
                    "progress_made": "Session just started",
                    "remaining_gaps": ["price-quantity relationship", "PED calculation"],
                    "outcome": "in_progress",
                },
                "outcome": "in_progress",
            }
        }
    }


class RespondRequest(BaseModel):
    """
    Student response in an ongoing coaching session.

    Used for POST /api/coaching/session/{session_id}/respond endpoint.

    Attributes:
        student_response: Student's response to coach's question
        request_hint: Whether student is requesting a hint

    Examples:
        >>> request = RespondRequest(
        ...     student_response="It decreases",
        ...     request_hint=False
        ... )

    Constitutional Compliance:
        - Principle III: Enables Socratic dialogue flow
    """

    student_response: str = Field(
        ...,
        max_length=5000,
        description="Student's response to coach's question",
        examples=["It decreases", "I think PED is negative because price and demand move in opposite directions"],
    )

    request_hint: bool = Field(
        default=False,
        description="Whether student is requesting a hint",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_response": "It decreases",
                "request_hint": False,
            }
        }
    }


class TranscriptResponse(BaseModel):
    """
    Full coaching session transcript.

    Used for GET /api/coaching/session/{session_id} endpoint.

    Attributes:
        session_id: UUID of coaching session
        student_id: UUID of student in session
        topic: Topic being coached
        struggle_description: Original struggle description
        transcript: Full session transcript (all messages)
        outcome: Final session outcome status
        created_at: Session creation timestamp
        updated_at: Session last update timestamp

    Examples:
        >>> response = TranscriptResponse(
        ...     session_id=UUID("..."),
        ...     student_id=UUID("..."),
        ...     topic="price elasticity of demand",
        ...     struggle_description="I don't understand why PED is negative",
        ...     transcript=[...],
        ...     outcome="in_progress",
        ...     created_at=datetime.now(),
        ...     updated_at=datetime.now()
        ... )

    Constitutional Compliance:
        - Principle III: Full transcript enables reflection and review
        - Principle VI: Transparent coaching process
    """

    session_id: UUID = Field(
        ...,
        description="UUID of coaching session",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )

    student_id: UUID = Field(
        ...,
        description="UUID of student in session",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    topic: str = Field(
        ...,
        description="Topic being coached",
        examples=["price elasticity of demand"],
    )

    struggle_description: Optional[str] = Field(
        default=None,
        description="Original struggle description",
        examples=["I don't understand why PED is negative"],
    )

    transcript: List[SessionMessage] = Field(
        ...,
        description="Full session transcript (all messages)",
    )

    outcome: str = Field(
        ...,
        description="Final session outcome status",
        examples=["in_progress", "resolved", "needs_more_help", "refer_to_teacher"],
    )

    created_at: datetime = Field(
        ...,
        description="Session creation timestamp",
    )

    updated_at: datetime = Field(
        ...,
        description="Session last update timestamp",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "770e8400-e29b-41d4-a716-446655440002",
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
                "topic": "price elasticity of demand",
                "struggle_description": "I don't understand why PED is negative",
                "transcript": [
                    {
                        "role": "coach",
                        "content": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
                        "timestamp": "2025-01-15T10:00:00Z",
                    },
                    {
                        "role": "student",
                        "content": "It decreases",
                        "timestamp": "2025-01-15T10:00:30Z",
                    },
                ],
                "outcome": "in_progress",
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:30Z",
            }
        }
    }
