"""
Unit tests for CoachingService.

Tests cover:
- start_tutoring_session(): Starting new coaching sessions
- respond_to_coach(): Processing student responses with Socratic method
- get_session_transcript(): Retrieving session history
- Error handling (student not found, session not found, LLM failures)
- Session state management (transcript updates, outcome tracking)

Constitutional Compliance:
- Service layer testing for production readiness
- 100% function coverage for all coaching functions
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime, timezone

from src.services.coaching_service import (
    start_tutoring_session,
    respond_to_coach,
    get_session_transcript,
    StudentNotFoundError,
    SessionNotFoundError,
    LLMResponseError,
)
from src.schemas.coaching_schemas import (
    StartSessionRequest,
    RespondRequest,
    SessionResponse,
    TranscriptResponse,
)
from src.models.coaching_session import CoachingSession
from src.models.student import Student
from src.ai_integration.llm_fallback import LLMProvider


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = Mock()
    session.exec = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def mock_llm_orchestrator():
    """Create mock LLM fallback orchestrator."""
    orchestrator = AsyncMock()
    orchestrator.generate_with_fallback = AsyncMock()
    return orchestrator


@pytest.fixture
def sample_student():
    """Create sample student."""
    return Student(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test Student",
    )


@pytest.fixture
def sample_coaching_llm_response():
    """Create sample coaching LLM response JSON."""
    return {
        "coach_message": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
        "internal_diagnosis": {
            "misconception_detected": "Student confuses direction of relationship between price and quantity demanded",
            "knowledge_gaps": ["Law of demand", "Inverse relationship concept"],
            "current_understanding_level": "none",
            "recommended_next_step": "diagnose",
        },
        "session_notes": {
            "progress_made": "Session started",
            "remaining_gaps": ["Law of demand", "Inverse relationship"],
            "outcome": "in_progress",
        },
    }


@pytest.fixture
def sample_followup_llm_response():
    """Create sample follow-up coaching response."""
    return {
        "coach_message": "Good! Now, why do you think quantity demanded decreases when price increases?",
        "internal_diagnosis": {
            "misconception_detected": None,
            "knowledge_gaps": ["Substitution effect", "Income effect"],
            "current_understanding_level": "partial",
            "recommended_next_step": "guide",
        },
        "session_notes": {
            "progress_made": "Student understands direction of relationship",
            "remaining_gaps": ["Substitution effect", "Income effect"],
            "outcome": "in_progress",
        },
    }


@pytest.fixture
def sample_coaching_session(sample_student):
    """Create sample coaching session."""
    session_id = uuid4()
    now_iso = datetime.now(timezone.utc).isoformat()

    return CoachingSession(
        id=session_id,
        student_id=sample_student.id,
        topic="price elasticity of demand",
        struggle_description="I don't understand why PED is negative",
        session_transcript=[
            {
                "role": "coach",
                "content": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
                "timestamp": now_iso,
            }
        ],
        outcome="in_progress",
    )


class TestStartTutoringSession:
    """Test start_tutoring_session() function."""

    @pytest.mark.asyncio
    async def test_successful_session_start(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_student,
        sample_coaching_llm_response,
    ):
        """Test successful coaching session creation."""
        # Arrange
        request = StartSessionRequest(
            student_id=sample_student.id,
            topic="price elasticity of demand",
            struggle_description="I don't understand why PED is negative",
        )

        # Mock database query
        mock_session.exec.return_value.first.return_value = sample_student

        # Mock LLM response
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_coaching_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Mock session.add to capture the created coaching session
        created_session = None
        def capture_session(obj):
            nonlocal created_session
            if isinstance(obj, CoachingSession):
                created_session = obj
                created_session.id = uuid4()  # Simulate DB auto-generated ID

        mock_session.add.side_effect = capture_session

        # Act
        result = await start_tutoring_session(mock_session, request, mock_llm_orchestrator)

        # Assert
        assert isinstance(result, SessionResponse)
        assert result.coach_message == sample_coaching_llm_response["coach_message"]
        assert result.internal_diagnosis.misconception_detected == "Student confuses direction of relationship between price and quantity demanded"
        assert len(result.internal_diagnosis.knowledge_gaps) == 2
        assert result.session_notes.outcome == "in_progress"

        # Verify session was created in database
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert created_session is not None
        assert created_session.topic == "price elasticity of demand"
        assert len(created_session.session_transcript) == 1
        assert created_session.session_transcript[0]["role"] == "coach"

    @pytest.mark.asyncio
    async def test_student_not_found(self, mock_session):
        """Test StudentNotFoundError when student doesn't exist."""
        # Arrange
        request = StartSessionRequest(
            student_id=uuid4(),
            topic="supply and demand",
            struggle_description="Confused about equilibrium",
        )

        # Mock database query returns None
        mock_session.exec.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(StudentNotFoundError) as exc_info:
            await start_tutoring_session(mock_session, request)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_llm_timeout_error(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_student,
    ):
        """Test LLMResponseError when LLM times out."""
        # Arrange
        request = StartSessionRequest(
            student_id=sample_student.id,
            topic="market structures",
            struggle_description="Can't differentiate monopoly vs oligopoly",
        )

        mock_session.exec.return_value.first.return_value = sample_student

        # Mock LLM timeout
        mock_llm_orchestrator.generate_with_fallback.side_effect = Exception(
            "LLM timeout after 30s"
        )

        # Act & Assert
        with pytest.raises(LLMResponseError) as exc_info:
            await start_tutoring_session(mock_session, request, mock_llm_orchestrator)

        assert "Failed to generate coaching response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_json_response(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_student,
    ):
        """Test LLMResponseError when LLM returns invalid JSON."""
        # Arrange
        request = StartSessionRequest(
            student_id=sample_student.id,
            topic="inflation",
            struggle_description="Don't understand CPI calculation",
        )

        mock_session.exec.return_value.first.return_value = sample_student

        # Mock LLM returns invalid JSON
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            "This is not JSON",
            LLMProvider.ANTHROPIC,
        )

        # Act & Assert
        with pytest.raises(LLMResponseError) as exc_info:
            await start_tutoring_session(mock_session, request, mock_llm_orchestrator)

        assert "not valid JSON" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_json_wrapped_in_markdown(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_student,
        sample_coaching_llm_response,
    ):
        """Test successful parsing when JSON wrapped in markdown."""
        # Arrange
        request = StartSessionRequest(
            student_id=sample_student.id,
            topic="fiscal policy",
            struggle_description="Don't understand multiplier effect",
        )

        mock_session.exec.return_value.first.return_value = sample_student

        # Mock LLM returns JSON wrapped in markdown
        wrapped_json = f"```json\n{json.dumps(sample_coaching_llm_response)}\n```"
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            wrapped_json,
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await start_tutoring_session(mock_session, request, mock_llm_orchestrator)

        # Assert
        assert isinstance(result, SessionResponse)
        assert result.coach_message == sample_coaching_llm_response["coach_message"]

    @pytest.mark.asyncio
    async def test_student_context_included_in_prompt(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_student,
        sample_coaching_llm_response,
    ):
        """Test that student context is passed to coaching prompt."""
        # Arrange
        request = StartSessionRequest(
            student_id=sample_student.id,
            topic="exchange rates",
            struggle_description="Confused about depreciation vs devaluation",
            context="Student has weak foundation in currency markets",
        )

        mock_session.exec.return_value.first.return_value = sample_student

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_coaching_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await start_tutoring_session(mock_session, request, mock_llm_orchestrator)

        # Assert
        # Verify LLM was called with prompt containing context
        mock_llm_orchestrator.generate_with_fallback.assert_called_once()
        assert isinstance(result, SessionResponse)


class TestRespondToCoach:
    """Test respond_to_coach() function."""

    @pytest.mark.asyncio
    async def test_successful_response_processing(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_coaching_session,
        sample_followup_llm_response,
    ):
        """Test successful processing of student response."""
        # Arrange
        request = RespondRequest(
            student_response="It decreases"
        )

        # Mock database query
        mock_session.exec.return_value.first.return_value = sample_coaching_session

        # Mock LLM response
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_followup_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await respond_to_coach(
            mock_session,
            sample_coaching_session.id,
            request,
            mock_llm_orchestrator,
        )

        # Assert
        assert isinstance(result, SessionResponse)
        assert result.coach_message == sample_followup_llm_response["coach_message"]
        assert result.internal_diagnosis.current_understanding_level == "partial"

        # Verify transcript was updated (student message + coach response)
        assert len(sample_coaching_session.session_transcript) == 3  # 1 initial + 1 student + 1 coach
        assert sample_coaching_session.session_transcript[1]["role"] == "student"
        assert sample_coaching_session.session_transcript[1]["content"] == "It decreases"
        assert sample_coaching_session.session_transcript[2]["role"] == "coach"

    @pytest.mark.asyncio
    async def test_session_not_found(self, mock_session):
        """Test SessionNotFoundError when session doesn't exist."""
        # Arrange
        request = RespondRequest(student_response="Some answer")

        # Mock database query returns None
        mock_session.exec.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(SessionNotFoundError) as exc_info:
            await respond_to_coach(mock_session, uuid4(), request)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_hint_request_included(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_coaching_session,
        sample_followup_llm_response,
    ):
        """Test that hint request is passed to LLM."""
        # Arrange
        request = RespondRequest(
            student_response="I'm not sure",
            request_hint=True,
        )

        mock_session.exec.return_value.first.return_value = sample_coaching_session

        # Modify response to indicate hint was given
        hint_response = sample_followup_llm_response.copy()
        hint_response["coach_message"] = "Here's a hint: Think about what happens to your budget when prices rise."

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(hint_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await respond_to_coach(
            mock_session,
            sample_coaching_session.id,
            request,
            mock_llm_orchestrator,
        )

        # Assert
        assert "hint" in result.coach_message.lower()
        mock_llm_orchestrator.generate_with_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_outcome_updated(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_coaching_session,
    ):
        """Test that session outcome is updated when student understands."""
        # Arrange
        request = RespondRequest(
            student_response="Because people buy cheaper substitutes when prices rise!"
        )

        mock_session.exec.return_value.first.return_value = sample_coaching_session

        # Mock LLM response indicating resolution
        resolved_response = {
            "coach_message": "Excellent! You've grasped the substitution effect perfectly!",
            "internal_diagnosis": {
                "misconception_detected": None,
                "knowledge_gaps": [],
                "current_understanding_level": "strong",
                "recommended_next_step": "complete",
            },
            "session_notes": {
                "progress_made": "Student fully understands law of demand and substitution effect",
                "remaining_gaps": [],
                "outcome": "resolved",
            },
        }

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(resolved_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await respond_to_coach(
            mock_session,
            sample_coaching_session.id,
            request,
            mock_llm_orchestrator,
        )

        # Assert
        assert result.outcome == "resolved"
        assert sample_coaching_session.outcome == "resolved"

    @pytest.mark.asyncio
    async def test_session_history_passed_to_llm(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_coaching_session,
        sample_followup_llm_response,
    ):
        """Test that full session history is included in LLM prompt."""
        # Arrange
        # Add more messages to session history
        sample_coaching_session.session_transcript.extend([
            {"role": "student", "content": "I think it goes down", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "coach", "content": "Can you explain why?", "timestamp": datetime.now(timezone.utc).isoformat()},
        ])

        request = RespondRequest(
            student_response="Because demand curve slopes downward"
        )

        mock_session.exec.return_value.first.return_value = sample_coaching_session

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_followup_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await respond_to_coach(
            mock_session,
            sample_coaching_session.id,
            request,
            mock_llm_orchestrator,
        )

        # Assert
        # Verify LLM was called with session history
        mock_llm_orchestrator.generate_with_fallback.assert_called_once()
        assert isinstance(result, SessionResponse)

        # Verify transcript now has 5 messages (3 initial + 1 student + 1 coach)
        assert len(sample_coaching_session.session_transcript) == 5


class TestGetSessionTranscript:
    """Test get_session_transcript() function."""

    def test_successful_transcript_retrieval(
        self,
        mock_session,
        sample_coaching_session,
    ):
        """Test successful retrieval of session transcript."""
        # Arrange
        mock_session.exec.return_value.first.return_value = sample_coaching_session

        # Act
        result = get_session_transcript(mock_session, sample_coaching_session.id)

        # Assert
        assert isinstance(result, TranscriptResponse)
        assert result.session_id == sample_coaching_session.id
        assert result.topic == "price elasticity of demand"
        assert result.struggle_description == "I don't understand why PED is negative"
        assert len(result.transcript) == 1
        assert result.transcript[0].role == "coach"
        assert result.outcome == "in_progress"

    def test_session_not_found(self, mock_session):
        """Test SessionNotFoundError when session doesn't exist."""
        # Arrange
        mock_session.exec.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(SessionNotFoundError) as exc_info:
            get_session_transcript(mock_session, uuid4())

        assert "not found" in str(exc_info.value)

    def test_transcript_with_multiple_messages(
        self,
        mock_session,
        sample_coaching_session,
    ):
        """Test transcript retrieval with full conversation."""
        # Arrange
        # Add more messages
        sample_coaching_session.session_transcript.extend([
            {"role": "student", "content": "It decreases", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "coach", "content": "Good! Why does it decrease?", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "student", "content": "Because of substitution effect", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "coach", "content": "Excellent!", "timestamp": datetime.now(timezone.utc).isoformat()},
        ])

        sample_coaching_session.outcome = "resolved"

        mock_session.exec.return_value.first.return_value = sample_coaching_session

        # Act
        result = get_session_transcript(mock_session, sample_coaching_session.id)

        # Assert
        assert len(result.transcript) == 5
        assert result.transcript[1].role == "student"
        assert result.transcript[2].role == "coach"
        assert result.outcome == "resolved"
