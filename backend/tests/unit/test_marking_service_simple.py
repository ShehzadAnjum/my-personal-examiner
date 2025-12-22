"""
Simplified unit tests for MarkingService (T068).

Focuses on core marking functionality without complex fixtures.

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
    QuestionNotFoundError,
    MarkSchemeNotFoundError,
    LLMResponseError,
)
from src.schemas.marking_schemas import MarkAnswerRequest, MarkingResult
from src.models.question import Question
from src.ai_integration.llm_fallback import LLMProvider


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = Mock()
    session.exec = Mock()
    return session


@pytest.fixture
def mock_llm_orchestrator():
    """Create mock LLM fallback orchestrator."""
    orchestrator = AsyncMock()
    orchestrator.generate_with_fallback = AsyncMock()
    return orchestrator


class TestMarkAnswerSimple:
    """Simplified tests for mark_answer()."""

    @pytest.mark.asyncio
    async def test_question_not_found(self, mock_session):
        """Test error when question doesn't exist."""
        request = MarkAnswerRequest(
            question_id=uuid4(),
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = None

        with pytest.raises(QuestionNotFoundError):
            await mark_answer(mock_session, request)

    @pytest.mark.asyncio
    async def test_mark_scheme_not_found(self, mock_session):
        """Test error when question has no marking scheme."""
        question = Question(
            id=uuid4(),
            question_text="Test question",
            max_marks=10,
            subject_id=uuid4(),
            marking_scheme=None,  # No marking scheme
        )

        request = MarkAnswerRequest(
            question_id=question.id,
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = question

        with pytest.raises(MarkSchemeNotFoundError):
            await mark_answer(mock_session, request)

    @pytest.mark.asyncio
    async def test_llm_timeout_error(self, mock_session, mock_llm_orchestrator):
        """Test error when LLM times out."""
        question = Question(
            id=uuid4(),
            question_text="Test question",
            max_marks=10,
            subject_id=uuid4(),
            marking_scheme={"points": ["Point 1", "Point 2"]},
        )

        request = MarkAnswerRequest(
            question_id=question.id,
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = question
        mock_llm_orchestrator.generate_with_fallback.side_effect = Exception("Timeout")

        with pytest.raises(LLMResponseError):
            await mark_answer(mock_session, request, mock_llm_orchestrator)

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, mock_session, mock_llm_orchestrator):
        """Test error when LLM returns invalid JSON."""
        question = Question(
            id=uuid4(),
            question_text="Test question",
            max_marks=10,
            subject_id=uuid4(),
            marking_scheme={"points": ["Point 1", "Point 2"]},
        )

        request = MarkAnswerRequest(
            question_id=question.id,
            student_answer="Some answer",
        )

        mock_session.exec.return_value.first.return_value = question
        mock_llm_orchestrator.generate_with_fallback.return_value = (
            "Not valid JSON",
            LLMProvider.ANTHROPIC,
        )

        with pytest.raises(LLMResponseError):
            await mark_answer(mock_session, request, mock_llm_orchestrator)
