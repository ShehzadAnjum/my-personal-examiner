"""
Unit tests for MarkingService.

Tests cover:
- mark_answer(): PhD-level strict marking with confidence scoring
- mark_attempt(): Aggregate marking of full exam attempts
- Error handling (question not found, attempt not found, no mark scheme)
- Confidence scoring integration (70% threshold for manual review)
- AO1/AO2/AO3 breakdown calculation
- Grade calculation (Cambridge boundaries)

Constitutional Compliance:
- A* Standard marking (Principle II)
- Service layer testing for production readiness
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.services.marking_service import (
    mark_answer,
    mark_attempt,
    QuestionNotFoundError,
    AttemptNotFoundError,
    MarkSchemeNotFoundError,
    LLMResponseError,
)
from src.schemas.marking_schemas import (
    MarkAnswerRequest,
    MarkAttemptRequest,
    MarkingResult,
    AttemptResult,
)
from src.models.question import Question
from src.models.attempt import Attempt
from src.models.attempted_question import AttemptedQuestion
from src.models.mark_scheme import MarkScheme
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
def sample_question():
    """Create sample question with mark scheme."""
    question_id = uuid4()
    return Question(
        id=question_id,
        question_text="Explain the law of demand with reference to the income and substitution effects. [12 marks]",
        question_number=1,
        max_marks=12,
        difficulty="medium",
        subject_id=uuid4(),
        source_paper="9708_s22_qp_22",
        paper_number=22,
        year=2022,
        session="MAY_JUNE",
        marking_scheme={
            "ao1": [
                "Define law of demand",
                "State inverse relationship between price and quantity demanded",
                "Mention ceteris paribus condition"
            ],
            "ao2": [
                "Explain substitution effect with example",
                "Explain income effect with example",
                "Link both effects to law of demand"
            ],
            "ao3": [
                "Evaluate limitations of law of demand",
                "Discuss exceptions (Giffen goods, Veblen goods)",
                "Provide real-world application"
            ]
        },
    )


@pytest.fixture
def sample_marking_llm_response():
    """Create sample marking LLM response."""
    return {
        "marks_awarded": 10,
        "ao1_score": 3,
        "ao2_score": 5,
        "ao3_score": 2,
        "points_awarded": [
            {
                "point_id": "ao1_define",
                "present": True,
                "quality": "excellent",
                "marks": 1,
                "feedback": "Clear definition provided"
            },
            {
                "point_id": "ao1_inverse",
                "present": True,
                "quality": "excellent",
                "marks": 1,
                "feedback": "Correctly stated relationship"
            },
            {
                "point_id": "ao2_substitution",
                "present": True,
                "quality": "good",
                "marks": 2,
                "feedback": "Good explanation with example"
            },
            {
                "point_id": "ao2_income",
                "present": True,
                "quality": "good",
                "marks": 2,
                "feedback": "Adequate explanation"
            },
            {
                "point_id": "ao3_limitations",
                "present": True,
                "quality": "adequate",
                "marks": 2,
                "feedback": "Some evaluation present"
            },
            {
                "point_id": "ao1_ceteris_paribus",
                "present": False,
                "quality": "missing",
                "marks": 0,
                "feedback": "Not mentioned"
            },
        ],
        "errors": [
            {
                "category": "missing_point",
                "description": "Did not mention ceteris paribus condition",
                "marks_lost": 1
            },
            {
                "category": "insufficient_evaluation",
                "description": "Limited discussion of exceptions to law of demand",
                "marks_lost": 1
            }
        ],
        "feedback": "Strong answer with good explanations of substitution and income effects. To improve: mention ceteris paribus condition and discuss Giffen/Veblen goods exceptions.",
        "identified_points": 5,
        "required_points": 9,
        "ao3_present": True,
    }


@pytest.fixture
def sample_attempt(sample_question):
    """Create sample exam attempt."""
    return Attempt(
        id=uuid4(),
        student_id=uuid4(),
        exam_id=uuid4(),
        status="completed",
    )


@pytest.fixture
def sample_attempted_questions(sample_attempt, sample_question):
    """Create sample attempted questions."""
    return [
        AttemptedQuestion(
            id=uuid4(),
            attempt_id=sample_attempt.id,
            question_id=sample_question.id,
            student_answer="The law of demand states that as price increases, quantity demanded decreases. This is due to the substitution effect (consumers switch to cheaper alternatives) and income effect (higher prices reduce real purchasing power).",
        )
    ]


class TestMarkAnswer:
    """Test mark_answer() function."""

    @pytest.mark.asyncio
    async def test_successful_marking(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_question,
        sample_marking_llm_response,
    ):
        """Test successful answer marking with confidence scoring."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=sample_question.id,
            student_answer="The law of demand states that as price increases, quantity demanded decreases due to substitution and income effects.",
        )

        # Mock database queries
        mock_session.exec.return_value.first.return_value = sample_question

        # Mock LLM response
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_marking_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await mark_answer(mock_session, request, mock_llm_orchestrator)

        # Assert
        assert isinstance(result, MarkingResult)
        assert result.marks_awarded == 10
        assert result.max_marks == 12
        assert result.percentage == pytest.approx(83.33, 0.01)
        assert result.ao1_score == 3
        assert result.ao2_score == 5
        assert result.ao3_score == 2
        assert len(result.points_awarded) == 6
        assert len(result.errors) == 2
        assert result.confidence_score > 0  # Calculated by ConfidenceScorer
        assert isinstance(result.needs_review, bool)

    @pytest.mark.asyncio
    async def test_question_not_found(self, mock_session):
        """Test QuestionNotFoundError when question doesn't exist."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=uuid4(),
            student_answer="Some answer",
        )

        # Mock database query returns None
        mock_session.exec.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(QuestionNotFoundError) as exc_info:
            await mark_answer(mock_session, request)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mark_scheme_not_found(
        self,
        mock_session,
        sample_question,
    ):
        """Test MarkSchemeNotFoundError when question has no mark scheme."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=sample_question.id,
            student_answer="Some answer",
        )

        # Question exists but has no mark scheme
        sample_question.marking_scheme = None
        mock_session.exec.return_value.first.return_value = sample_question

        # Act & Assert
        with pytest.raises(MarkSchemeNotFoundError) as exc_info:
            await mark_answer(mock_session, request)

        assert "no marking scheme" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_manual_review(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_question,
            ):
        """Test that low confidence (<70%) triggers manual review flag."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=sample_question.id,
            student_answer="Q",  # Very short answer
        )

        mock_session.exec.return_value.first.return_value = sample_question

        # Mock LLM response with low coverage
        low_confidence_response = {
            "marks_awarded": 2,
            "ao1_score": 2,
            "ao2_score": 0,
            "ao3_score": 0,
            "marked_points": [],
            "errors": [],
            "feedback": "Very brief answer",
            "identified_points": 1,  # Low coverage
            "required_points": 9,
            "ao3_present": False,
        }

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(low_confidence_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await mark_answer(mock_session, request, mock_llm_orchestrator)

        # Assert
        # Short answer + low coverage should trigger low confidence
        assert result.needs_review is True

    @pytest.mark.asyncio
    async def test_llm_timeout_error(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_question,
            ):
        """Test LLMResponseError when LLM times out."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=sample_question.id,
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = sample_question

        # Mock LLM timeout
        mock_llm_orchestrator.generate_with_fallback.side_effect = Exception("Timeout")

        # Act & Assert
        with pytest.raises(LLMResponseError):
            await mark_answer(mock_session, request, mock_llm_orchestrator)

    @pytest.mark.asyncio
    async def test_invalid_json_response(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_question,
            ):
        """Test LLMResponseError when LLM returns invalid JSON."""
        # Arrange
        request = MarkAnswerRequest(
            question_id=sample_question.id,
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = sample_question

        # Mock invalid JSON
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            "Not JSON",
            LLMProvider.ANTHROPIC,
        )

        # Act & Assert
        with pytest.raises(LLMResponseError) as exc_info:
            await mark_answer(mock_session, request, mock_llm_orchestrator)

        assert "not valid JSON" in str(exc_info.value)


class TestMarkAttempt:
    """Test mark_attempt() function."""

    @pytest.mark.asyncio
    async def test_successful_attempt_marking(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_attempt,
        sample_question,
                sample_attempted_questions,
        sample_marking_llm_response,
    ):
        """Test successful marking of full exam attempt."""
        # Arrange
        request = MarkAttemptRequest(attempt_id=sample_attempt.id)

        # Mock database queries
        mock_session.exec.return_value.first.side_effect = [
            sample_attempt,
            sample_question,
        ]
        mock_session.exec.return_value.all.return_value = sample_attempted_questions

        # Mock LLM response
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(sample_marking_llm_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await mark_attempt(mock_session, request, mock_llm_orchestrator)

        # Assert
        assert isinstance(result, AttemptResult)
        assert result.total_marks == 10
        assert result.max_marks == 12
        assert result.percentage == pytest.approx(83.33, 0.01)
        assert result.grade in ["A", "A*", "B"]  # 83% should be A or A*
        assert result.ao1_total == 3
        assert result.ao2_total == 5
        assert result.ao3_total == 2
        assert len(result.question_results) == 1

    @pytest.mark.asyncio
    async def test_attempt_not_found(self, mock_session):
        """Test AttemptNotFoundError when attempt doesn't exist."""
        # Arrange
        request = MarkAttemptRequest(attempt_id=uuid4())

        # Mock database query returns None
        mock_session.exec.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(AttemptNotFoundError) as exc_info:
            await mark_attempt(mock_session, request)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_attempt_with_no_questions(
        self,
        mock_session,
        sample_attempt,
    ):
        """Test attempt with no attempted questions returns zero result."""
        # Arrange
        request = MarkAttemptRequest(attempt_id=sample_attempt.id)

        # Mock database queries
        mock_session.exec.return_value.first.return_value = sample_attempt
        mock_session.exec.return_value.all.return_value = []  # No questions

        # Act
        result = await mark_attempt(mock_session, request)

        # Assert
        assert result.total_marks == 0
        assert result.max_marks == 0
        assert result.percentage == 0.0
        assert result.grade == "U"
        assert len(result.question_results) == 0
        assert result.needs_review is False

    @pytest.mark.asyncio
    async def test_grade_calculation_boundaries(
        self,
        mock_session,
        mock_llm_orchestrator,
        sample_attempt,
        sample_question,
                sample_attempted_questions,
    ):
        """Test grade calculation at different mark boundaries."""
        # Arrange
        request = MarkAttemptRequest(attempt_id=sample_attempt.id)

        mock_session.exec.return_value.first.side_effect = [
            sample_attempt,
            sample_question,
        ]
        mock_session.exec.return_value.all.return_value = sample_attempted_questions

        # Test A* grade (90%+)
        a_star_response = {
            "marks_awarded": 11,  # 11/12 = 92%
            "ao1_score": 4,
            "ao2_score": 5,
            "ao3_score": 2,
            "marked_points": [],
            "errors": [],
            "feedback": "Excellent answer",
            "identified_points": 9,
            "required_points": 9,
            "ao3_present": True,
        }

        mock_llm_orchestrator.generate_with_fallback.return_value = (
            json.dumps(a_star_response),
            LLMProvider.ANTHROPIC,
        )

        # Act
        result = await mark_attempt(mock_session, request, mock_llm_orchestrator)

        # Assert
        assert result.percentage >= 90.0
        assert result.grade == "A*"
