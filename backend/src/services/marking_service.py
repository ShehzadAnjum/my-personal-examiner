"""
Marking Service

Business logic for Marker Agent (PhD-level strict marking with AO1/AO2/AO3 breakdown).

Phase III User Story 4: Economics 9708 answers receive PhD-level strict marking
with error categorization and confidence scoring for manual review queue.

Constitutional Requirements:
- Principle II: A* Standard marking always (zero tolerance for imprecision)
- Principle VI: Constructive feedback (explain WHY marks lost, HOW to improve)
- Principle I: Subject accuracy (Cambridge mark scheme alignment)
"""

import json
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlmodel import Session, select

from src.models.question import Question
from src.models.attempt import Attempt
from src.models.attempted_question import AttemptedQuestion
from src.schemas.marking_schemas import (
    MarkAnswerRequest,
    MarkingResult,
    MarkAttemptRequest,
    AttemptResult,
    MarkingError,
    MarkedPoint,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator
from src.ai_integration.prompt_templates.marker_prompts import MarkerPrompts
from src.algorithms.confidence_scoring import ConfidenceScorer

logger = logging.getLogger(__name__)


class QuestionNotFoundError(Exception):
    """Raised when question ID not found in database"""

    pass


class AttemptNotFoundError(Exception):
    """Raised when attempt ID not found in database"""

    pass


class MarkSchemeNotFoundError(Exception):
    """Raised when question has no marking scheme"""

    pass


class LLMResponseError(Exception):
    """Raised when LLM response cannot be parsed or is invalid"""

    pass


async def mark_answer(
    session: Session,
    request: MarkAnswerRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> MarkingResult:
    """
    Mark a single student answer using PhD-level strict standards.

    Applies Cambridge mark scheme with zero tolerance for imprecision.
    Calculates confidence score and flags for manual review if <70%.

    Args:
        session: Database session
        request: MarkAnswerRequest with question_id, student_answer
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        MarkingResult: Marks, AO breakdown, errors, confidence, feedback

    Raises:
        QuestionNotFoundError: If question_id not found
        MarkSchemeNotFoundError: If question has no marking scheme
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = MarkAnswerRequest(
        ...     question_id=UUID("..."),
        ...     student_answer="The law of demand states that..."
        ... )
        >>> result = await mark_answer(session, request)
        >>> result.marks_awarded
        12
        >>> result.confidence_score
        85
        >>> result.needs_review
        False

    Constitutional Compliance:
        - Principle II: Zero tolerance for imprecision (A* standard)
        - Principle VI: Constructive feedback with WHY and HOW
        - Confidence scoring ensures quality control

    LLM Workflow:
        1. Fetch question and mark scheme from database
        2. Build strict marking prompt with MarkerPrompts
        3. Call LLM with fallback (Claude → GPT-4 → Gemini)
        4. Parse JSON response (marks, AO scores, errors, points)
        5. Calculate confidence score using 6-signal heuristic
        6. Determine needs_review flag (<70% threshold)
        7. Return MarkingResult
    """

    # Step 1: Fetch question from database
    statement = select(Question).where(Question.id == request.question_id)
    question = session.exec(statement).first()

    if not question:
        raise QuestionNotFoundError(f"Question {request.question_id} not found")

    # Validate marking scheme exists
    if not question.marking_scheme:
        raise MarkSchemeNotFoundError(
            f"Question {request.question_id} has no marking scheme"
        )

    # Step 2: Determine max_marks
    max_marks = request.max_marks if request.max_marks is not None else question.max_marks

    # Step 3: Build strict marking prompt
    prompt = MarkerPrompts.mark_answer_prompt(
        question_text=question.question_text,
        max_marks=max_marks,
        marking_scheme=question.marking_scheme,
        student_answer=request.student_answer,
    )

    # Step 4: Call LLM with fallback orchestration
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Marking answer for question {request.question_id} (max_marks={max_marks})"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.1,  # Very low temperature for consistent marking
            max_tokens=3000,  # Detailed feedback
            system_prompt=MarkerPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM marking response received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate marking: {str(e)}") from e

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

    # Step 6: Calculate confidence score
    try:
        marks_awarded = response_data.get("marks_awarded", 0)

        # Build marking details for confidence scoring
        marking_details = {
            "identified_points": len([p for p in response_data.get("points_awarded", []) if p.get("present")]),
            "required_points": len(response_data.get("points_awarded", [])),
            "ao3_present": response_data.get("ao3_max", 0) > 0,
        }

        # Calculate confidence score using 6-signal heuristic
        confidence_score = ConfidenceScorer.calculate_confidence(
            marks_awarded=marks_awarded,
            max_marks=max_marks,
            student_answer=request.student_answer,
            question={"max_marks": max_marks, "marking_scheme": question.marking_scheme},
            marking_details=marking_details,
        )

        # Determine needs_review flag
        needs_review = confidence_score < ConfidenceScorer.MANUAL_REVIEW_THRESHOLD

        # Override needs_review if LLM explicitly set it
        if "needs_review" in response_data:
            needs_review = response_data["needs_review"]

        logger.info(
            f"Marking complete: {marks_awarded}/{max_marks} (confidence={confidence_score}%, needs_review={needs_review})"
        )

        # Step 7: Build MarkingResult
        return MarkingResult(
            marks_awarded=marks_awarded,
            max_marks=max_marks,
            percentage=round((marks_awarded / max_marks * 100) if max_marks > 0 else 0, 1),
            ao1_score=response_data.get("ao1_score", 0),
            ao1_max=response_data.get("ao1_max", 0),
            ao2_score=response_data.get("ao2_score", 0),
            ao2_max=response_data.get("ao2_max", 0),
            ao3_score=response_data.get("ao3_score", 0),
            ao3_max=response_data.get("ao3_max", 0),
            level=response_data.get("level"),
            errors=[
                MarkingError(**error) if isinstance(error, dict) else MarkingError(category="Error", description=str(error), marks_lost=0)
                for error in response_data.get("errors", [])
            ],
            points_awarded=[
                MarkedPoint(**point) if isinstance(point, dict) else MarkedPoint(point_id="", present=False, quality="missing")
                for point in response_data.get("points_awarded", [])
            ],
            confidence_score=confidence_score,
            needs_review=needs_review,
            feedback=response_data.get("feedback", ""),
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build MarkingResult from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


async def mark_attempt(
    session: Session,
    request: MarkAttemptRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> AttemptResult:
    """
    Mark all questions in an exam attempt and aggregate results.

    Marks each question individually, then calculates overall score,
    grade, and AO totals.

    Args:
        session: Database session
        request: MarkAttemptRequest with attempt_id
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        AttemptResult: Total marks, grade, AO totals, individual results

    Raises:
        AttemptNotFoundError: If attempt_id not found
        LLMResponseError: If any question marking fails

    Examples:
        >>> request = MarkAttemptRequest(attempt_id=UUID("..."))
        >>> result = await mark_attempt(session, request)
        >>> result.total_marks
        45
        >>> result.grade
        "A"
        >>> result.needs_review
        False

    Constitutional Compliance:
        - Principle II: A* standard grading (strict grade boundaries)
        - Principle VI: Overall feedback for improvement

    Workflow:
        1. Fetch attempt and all attempted_questions from database
        2. Mark each question individually using mark_answer()
        3. Aggregate marks, AO scores
        4. Calculate grade using Cambridge grade boundaries
        5. Determine needs_review (any question flagged)
        6. Generate overall feedback
        7. Update attempt record with scores and grade
        8. Return AttemptResult
    """

    # Step 1: Fetch attempt from database
    statement = select(Attempt).where(Attempt.id == request.attempt_id)
    attempt = session.exec(statement).first()

    if not attempt:
        raise AttemptNotFoundError(f"Attempt {request.attempt_id} not found")

    # Step 2: Fetch all attempted questions for this attempt
    statement = select(AttemptedQuestion).where(AttemptedQuestion.attempt_id == request.attempt_id)
    attempted_questions = session.exec(statement).all()

    if not attempted_questions:
        logger.warning(f"Attempt {request.attempt_id} has no attempted questions")
        # Return zero result
        return AttemptResult(
            attempt_id=attempt.id,
            total_marks=0,
            max_marks=0,
            percentage=0.0,
            grade="U",
            ao1_total=0,
            ao2_total=0,
            ao3_total=0,
            question_results=[],
            needs_review=False,
            overall_feedback="No questions attempted",
        )

    # Step 3: Mark each question individually
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    question_results: List[MarkingResult] = []
    total_marks = 0
    max_marks_total = 0
    ao1_total = 0
    ao2_total = 0
    ao3_total = 0
    any_needs_review = False

    for attempted_q in attempted_questions:
        # Skip if no answer provided
        if not attempted_q.student_answer:
            logger.info(f"Skipping attempted question {attempted_q.id} (no answer)")
            continue

        try:
            # Mark this question
            mark_request = MarkAnswerRequest(
                question_id=attempted_q.question_id,
                student_answer=attempted_q.student_answer,
            )

            result = await mark_answer(
                session=session,
                request=mark_request,
                llm_orchestrator=llm_orchestrator,
            )

            question_results.append(result)

            # Aggregate scores
            total_marks += result.marks_awarded
            max_marks_total += result.max_marks
            ao1_total += result.ao1_score
            ao2_total += result.ao2_score
            ao3_total += result.ao3_score

            if result.needs_review:
                any_needs_review = True

            # Update attempted_question record with marking feedback
            attempted_q.marks_awarded = result.marks_awarded
            attempted_q.marking_feedback = {
                "ao1_score": result.ao1_score,
                "ao2_score": result.ao2_score,
                "ao3_score": result.ao3_score,
                "errors": [{"category": e.category, "description": e.description, "marks_lost": e.marks_lost} for e in result.errors],
                "feedback": result.feedback,
                "confidence_score": result.confidence_score,
            }
            attempted_q.needs_review = result.needs_review
            attempted_q.confidence_score = result.confidence_score

            session.add(attempted_q)

        except Exception as e:
            logger.error(f"Failed to mark attempted question {attempted_q.id}: {e}")
            # Continue with other questions
            continue

    # Step 4: Calculate overall percentage and grade
    percentage = round((total_marks / max_marks_total * 100) if max_marks_total > 0 else 0, 1)
    grade = _calculate_grade(percentage)

    # Step 5: Generate overall feedback
    overall_feedback = _generate_overall_feedback(
        ao1_total=ao1_total,
        ao2_total=ao2_total,
        ao3_total=ao3_total,
        question_results=question_results,
    )

    # Step 6: Update attempt record
    attempt.overall_score = total_marks
    attempt.grade = grade
    attempt.status = "MARKED"

    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    logger.info(
        f"Marked attempt {request.attempt_id}: {total_marks}/{max_marks_total} ({percentage}%, Grade {grade})"
    )

    # Step 7: Return AttemptResult
    return AttemptResult(
        attempt_id=attempt.id,
        total_marks=total_marks,
        max_marks=max_marks_total,
        percentage=percentage,
        grade=grade,
        ao1_total=ao1_total,
        ao2_total=ao2_total,
        ao3_total=ao3_total,
        question_results=question_results,
        needs_review=any_needs_review,
        overall_feedback=overall_feedback,
    )


def _calculate_grade(percentage: float) -> str:
    """
    Calculate Cambridge A-Level grade from percentage.

    Cambridge Economics 9708 Grade Boundaries (typical):
    - A*: 90%+
    - A: 80-89%
    - B: 70-79%
    - C: 60-69%
    - D: 50-59%
    - E: 40-49%
    - U: <40%

    Args:
        percentage: Overall percentage score

    Returns:
        Letter grade
    """
    if percentage >= 90:
        return "A*"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "U"


def _generate_overall_feedback(
    ao1_total: int,
    ao2_total: int,
    ao3_total: int,
    question_results: List[MarkingResult],
) -> str:
    """
    Generate overall feedback for exam attempt.

    Summarizes strengths and weaknesses across AO1/AO2/AO3.

    Args:
        ao1_total: Total AO1 marks
        ao2_total: Total AO2 marks
        ao3_total: Total AO3 marks
        question_results: Individual question results

    Returns:
        Overall feedback summary
    """
    # Calculate AO maximums
    ao1_max = sum(r.ao1_max for r in question_results)
    ao2_max = sum(r.ao2_max for r in question_results)
    ao3_max = sum(r.ao3_max for r in question_results)

    # Calculate percentages
    ao1_pct = round((ao1_total / ao1_max * 100) if ao1_max > 0 else 0, 1)
    ao2_pct = round((ao2_total / ao2_max * 100) if ao2_max > 0 else 0, 1)
    ao3_pct = round((ao3_total / ao3_max * 100) if ao3_max > 0 else 0, 1)

    # Identify strengths and weaknesses
    ao_scores = [
        ("AO1 (Knowledge)", ao1_pct, ao1_total, ao1_max),
        ("AO2 (Application)", ao2_pct, ao2_total, ao2_max),
        ("AO3 (Evaluation)", ao3_pct, ao3_total, ao3_max),
    ]
    ao_scores_sorted = sorted(ao_scores, key=lambda x: x[1], reverse=True)

    strongest = ao_scores_sorted[0]
    weakest = ao_scores_sorted[-1]

    feedback_parts = []

    # Overall summary
    feedback_parts.append(
        f"**Overall Performance**: {ao1_total + ao2_total + ao3_total}/{ao1_max + ao2_max + ao3_max} marks"
    )

    # Strengths
    feedback_parts.append(
        f"\n**Strength**: {strongest[0]} - {strongest[2]}/{strongest[3]} ({strongest[1]}%)"
    )

    # Weaknesses
    if weakest[1] < 70:  # Only mention weakness if below 70%
        feedback_parts.append(
            f"\n**Area for Improvement**: {weakest[0]} - {weakest[2]}/{weakest[3]} ({weakest[1]}%)"
        )

    # Specific recommendations
    if ao1_pct < 70:
        feedback_parts.append(
            "\n- **AO1 Improvement**: Review key definitions and economic theory. Ensure all definitions include ceteris paribus assumptions and key terms."
        )
    if ao2_pct < 70:
        feedback_parts.append(
            "\n- **AO2 Improvement**: Use specific real-world examples with data and citations. Avoid generic examples like 'some goods'."
        )
    if ao3_pct < 70:
        feedback_parts.append(
            "\n- **AO3 Improvement**: Provide balanced arguments (for/against), weigh significance, and conclude clearly. Avoid one-sided analysis."
        )

    return "".join(feedback_parts)
