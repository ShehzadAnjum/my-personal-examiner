"""
Review Service

Business logic for Reviewer Agent (weakness analysis, model answers, improvement plans).

Phase III User Story 5: Students see categorized weaknesses (AO1/AO2/AO3),
A* model answers with annotations, and actionable improvement plans.

Constitutional Requirements:
- Principle II: A* Standard (model answers demonstrate excellence)
- Principle VI: Constructive feedback (actionable improvement plans)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

import json
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select

from src.models.attempt import Attempt
from src.models.attempted_question import AttemptedQuestion
from src.models.question import Question
from src.models.improvement_plan import ImprovementPlan
from src.schemas.feedback_schemas import (
    AnalyzeWeaknessesRequest,
    WeaknessReport,
    GenerateModelAnswerRequest,
    ModelAnswer,
    WeaknessAnalysis,
    Weakness,
    ImprovementPlan as ImprovementPlanSchema,
    ActionItem,
    PracticeRecommendation,
    ProgressComparison,
    MarksBreakdown,
    WhyThisIsAStar,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator
from src.ai_integration.prompt_templates.reviewer_prompts import ReviewerPrompts

logger = logging.getLogger(__name__)


class AttemptNotFoundError(Exception):
    """Raised when attempt ID not found in database"""

    pass


class QuestionNotFoundError(Exception):
    """Raised when question ID not found in database"""

    pass


class AttemptedQuestionNotFoundError(Exception):
    """Raised when attempted question ID not found in database"""

    pass


class LLMResponseError(Exception):
    """Raised when LLM response cannot be parsed or is invalid"""

    pass


async def analyze_weaknesses(
    session: Session,
    request: AnalyzeWeaknessesRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> WeaknessReport:
    """
    Analyze student weaknesses from exam attempt and create improvement plan.

    Categorizes errors by AO1/AO2/AO3, generates actionable improvement items,
    and optionally compares with previous attempts.

    Args:
        session: Database session
        request: AnalyzeWeaknessesRequest with attempt_id
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        WeaknessReport: Weaknesses, improvement plan, progress comparison

    Raises:
        AttemptNotFoundError: If attempt_id not found
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = AnalyzeWeaknessesRequest(
        ...     attempt_id=UUID("..."),
        ...     include_previous_attempts=True
        ... )
        >>> report = await analyze_weaknesses(session, request)
        >>> len(report.weakness_analysis.AO1_knowledge)
        3

    Constitutional Compliance:
        - Principle VI: Constructive feedback with specific actions
        - Principle I: Cambridge syllabus alignment (syllabus_points_affected)

    LLM Workflow:
        1. Fetch attempt and all attempted questions from database
        2. Fetch previous attempts if requested (for comparison)
        3. Build weakness analysis prompt with ReviewerPrompts
        4. Call LLM with fallback (Claude → GPT-4 → Gemini)
        5. Parse JSON response (weaknesses, improvement plan, progress)
        6. Create ImprovementPlan database record
        7. Return WeaknessReport
    """

    # Step 1: Fetch attempt from database
    statement = select(Attempt).where(Attempt.id == request.attempt_id)
    attempt = session.exec(statement).first()

    if not attempt:
        raise AttemptNotFoundError(f"Attempt {request.attempt_id} not found")

    # Step 2: Fetch all attempted questions for this attempt
    statement = select(AttemptedQuestion).where(
        AttemptedQuestion.attempt_id == request.attempt_id
    )
    attempted_questions = session.exec(statement).all()

    # Step 3: Build attempted questions data for prompt
    attempted_questions_data = []
    for aq in attempted_questions:
        # Fetch question details
        statement = select(Question).where(Question.id == aq.question_id)
        question = session.exec(statement).first()

        if question:
            attempted_questions_data.append({
                "question_text": question.question_text,
                "max_marks": question.max_marks,
                "student_answer": aq.student_answer,
                "marks_awarded": aq.marks_awarded or 0,
                "marking_feedback": aq.marking_feedback or {},
            })

    # Step 4: Fetch previous attempts if requested
    previous_attempts_data = []
    if request.include_previous_attempts:
        statement = (
            select(Attempt)
            .where(Attempt.student_id == attempt.student_id)
            .where(Attempt.id != request.attempt_id)
            .where(Attempt.submitted_at.isnot(None))
            .order_by(Attempt.submitted_at.desc())
            .limit(3)  # Last 3 attempts
        )
        previous_attempts = session.exec(statement).all()

        for prev_att in previous_attempts:
            previous_attempts_data.append({
                "overall_score": prev_att.overall_score or 0,
                "grade": prev_att.grade or "U",
                "submitted_at": prev_att.submitted_at.isoformat() if prev_att.submitted_at else "",
            })

    # Step 5: Build weakness analysis prompt
    attempt_data = {
        "overall_score": attempt.overall_score or 0,
        "grade": attempt.grade or "Pending",
        "exam_type": "Economics 9708",
    }

    prompt = ReviewerPrompts.analyze_weaknesses_prompt(
        attempt_data=attempt_data,
        attempted_questions=attempted_questions_data,
        previous_attempts=previous_attempts_data if previous_attempts_data else None,
    )

    # Step 6: Call LLM with fallback orchestration
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Analyzing weaknesses for attempt {request.attempt_id} (score={attempt.overall_score})"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.3,  # Low temperature for consistent analysis
            max_tokens=4000,  # Detailed analysis
            system_prompt=ReviewerPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM weakness analysis received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate weakness analysis: {str(e)}") from e

    # Step 7: Parse JSON response
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

    # Step 8: Build WeaknessAnalysis
    try:
        weakness_analysis_data = response_data.get("weakness_analysis", {})

        weakness_analysis = WeaknessAnalysis(
            AO1_knowledge=[
                Weakness(**w) if isinstance(w, dict) else Weakness(
                    weakness=str(w),
                    examples_from_answer=[],
                    severity="medium",
                )
                for w in weakness_analysis_data.get("AO1_knowledge", [])
            ],
            AO2_application=[
                Weakness(**w) if isinstance(w, dict) else Weakness(
                    weakness=str(w),
                    examples_from_answer=[],
                    severity="medium",
                )
                for w in weakness_analysis_data.get("AO2_application", [])
            ],
            AO3_evaluation=[
                Weakness(**w) if isinstance(w, dict) else Weakness(
                    weakness=str(w),
                    examples_from_answer=[],
                    severity="medium",
                )
                for w in weakness_analysis_data.get("AO3_evaluation", [])
            ],
        )

        # Step 9: Build ImprovementPlan
        improvement_plan_data = response_data.get("improvement_plan", {})

        improvement_plan = ImprovementPlanSchema(
            priority_areas=improvement_plan_data.get("priority_areas", []),
            action_items=[
                ActionItem(**item) if isinstance(item, dict) else ActionItem(
                    id=f"ACTION_{i}",
                    action=str(item),
                    target_weakness="General",
                    how_to_do_it="",
                    success_criteria="",
                    resources=[],
                )
                for i, item in enumerate(improvement_plan_data.get("action_items", []), 1)
            ],
            practice_recommendations=[
                PracticeRecommendation(**rec) if isinstance(rec, dict) else PracticeRecommendation(
                    syllabus_point="",
                    question_type=str(rec),
                    focus="",
                )
                for rec in improvement_plan_data.get("practice_recommendations", [])
            ],
        )

        # Step 10: Build ProgressComparison
        progress_data = response_data.get("progress_comparison", {})

        progress_comparison = ProgressComparison(
            compared_to_previous=progress_data.get("compared_to_previous"),
            improvements=progress_data.get("improvements", []),
            regressions=progress_data.get("regressions", []),
            trend=progress_data.get("trend", "stable"),
        )

        # Step 11: Create ImprovementPlan database record
        db_improvement_plan = ImprovementPlan(
            student_id=attempt.student_id,
            attempt_id=attempt.id,
            weaknesses={
                "AO1": [
                    {
                        "category": w.weakness,
                        "examples": w.examples_from_answer,
                        "severity": w.severity,
                        "syllabus_points": w.syllabus_points_affected,
                    }
                    for w in weakness_analysis.AO1_knowledge
                ],
                "AO2": [
                    {
                        "category": w.weakness,
                        "examples": w.examples_from_answer,
                        "severity": w.severity,
                        "syllabus_points": w.syllabus_points_affected,
                    }
                    for w in weakness_analysis.AO2_application
                ],
                "AO3": [
                    {
                        "category": w.weakness,
                        "examples": w.examples_from_answer,
                        "severity": w.severity,
                        "syllabus_points": w.syllabus_points_affected,
                    }
                    for w in weakness_analysis.AO3_evaluation
                ],
            },
            action_items=[
                {
                    "id": item.id,
                    "action": item.action,
                    "target_weakness": item.target_weakness,
                    "due_date": "",  # Set by planner or student
                    "completed": False,
                    "resources": item.resources,
                }
                for item in improvement_plan.action_items
            ],
        )

        session.add(db_improvement_plan)
        session.commit()
        session.refresh(db_improvement_plan)

        logger.info(
            f"Created improvement plan {db_improvement_plan.id} for attempt {request.attempt_id}"
        )

        # Step 12: Return WeaknessReport
        return WeaknessReport(
            improvement_plan_id=db_improvement_plan.id,
            attempt_id=attempt.id,
            overall_score=attempt.overall_score or 0,
            grade=attempt.grade or "U",
            weakness_analysis=weakness_analysis,
            improvement_plan=improvement_plan,
            progress_comparison=progress_comparison,
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build WeaknessReport from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


async def generate_model_answer(
    session: Session,
    request: GenerateModelAnswerRequest,
    llm_orchestrator: Optional[LLMFallbackOrchestrator] = None,
) -> ModelAnswer:
    """
    Generate A* model answer for a question.

    Creates perfect exemplar answer with annotations explaining why it's A* quality.
    Optionally compares with student's actual answer if attempted_question_id provided.

    Args:
        session: Database session
        request: GenerateModelAnswerRequest with question_id, optional attempted_question_id
        llm_orchestrator: Optional LLM orchestrator (created if not provided)

    Returns:
        ModelAnswer: A* answer with annotations and learning points

    Raises:
        QuestionNotFoundError: If question_id not found
        AttemptedQuestionNotFoundError: If attempted_question_id not found
        LLMResponseError: If LLM response invalid or cannot be parsed

    Examples:
        >>> request = GenerateModelAnswerRequest(
        ...     question_id=UUID("..."),
        ...     attempted_question_id=UUID("...")
        ... )
        >>> model = await generate_model_answer(session, request)
        >>> model.marks_breakdown.total
        10

    Constitutional Compliance:
        - Principle II: A* standard (model answers demonstrate excellence)
        - Principle VI: Constructive feedback (key features to learn)

    LLM Workflow:
        1. Fetch question and mark scheme from database
        2. Optionally fetch student's answer if attempted_question_id provided
        3. Build model answer prompt with ReviewerPrompts
        4. Call LLM with fallback (Claude → GPT-4 → Gemini)
        5. Parse JSON response (model_answer, breakdown, annotations)
        6. Generate comparison with student answer if applicable
        7. Return ModelAnswer
    """

    # Step 1: Fetch question from database
    statement = select(Question).where(Question.id == request.question_id)
    question = session.exec(statement).first()

    if not question:
        raise QuestionNotFoundError(f"Question {request.question_id} not found")

    # Step 2: Optionally fetch student's answer
    student_answer = None
    marks_awarded = None

    if request.attempted_question_id:
        statement = select(AttemptedQuestion).where(
            AttemptedQuestion.id == request.attempted_question_id
        )
        attempted_question = session.exec(statement).first()

        if not attempted_question:
            raise AttemptedQuestionNotFoundError(
                f"Attempted question {request.attempted_question_id} not found"
            )

        student_answer = attempted_question.student_answer
        marks_awarded = attempted_question.marks_awarded

    # Step 3: Build model answer prompt
    prompt = ReviewerPrompts.generate_model_answer_prompt(
        question_text=question.question_text,
        max_marks=question.max_marks,
        marking_scheme=question.marking_scheme or {},
        student_answer=student_answer,
        marks_awarded=marks_awarded,
    )

    # Step 4: Call LLM with fallback orchestration
    if llm_orchestrator is None:
        llm_orchestrator = LLMFallbackOrchestrator()

    try:
        logger.info(
            f"Generating model answer for question {request.question_id} (max_marks={question.max_marks})"
        )

        response_text, provider = await llm_orchestrator.generate_with_fallback(
            prompt=prompt,
            temperature=0.2,  # Low temperature for consistent A* quality
            max_tokens=3000,  # Detailed model answer
            system_prompt=ReviewerPrompts.SYSTEM_PROMPT,
        )

        logger.info(f"LLM model answer received from {provider.value}")

    except Exception as e:
        logger.error(f"LLM fallback failed: {e}")
        raise LLMResponseError(f"Failed to generate model answer: {str(e)}") from e

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

    # Step 6: Build ModelAnswer
    try:
        marks_breakdown_data = response_data.get("marks_breakdown", {})
        why_a_star_data = response_data.get("why_this_is_a_star", {})

        marks_breakdown = MarksBreakdown(
            AO1_marks=marks_breakdown_data.get("AO1_marks", 0),
            AO2_marks=marks_breakdown_data.get("AO2_marks", 0),
            AO3_marks=marks_breakdown_data.get("AO3_marks", 0),
            total=marks_breakdown_data.get("total", question.max_marks),
        )

        why_this_is_a_star = WhyThisIsAStar(
            knowledge_demonstration=why_a_star_data.get("knowledge_demonstration", ""),
            application_demonstration=why_a_star_data.get("application_demonstration", ""),
            evaluation_demonstration=why_a_star_data.get("evaluation_demonstration", ""),
            structure_excellence=why_a_star_data.get("structure_excellence", ""),
        )

        # Generate comparison with student answer if provided
        student_comparison = None
        if student_answer and marks_awarded is not None:
            student_comparison = _generate_comparison(
                student_marks=marks_awarded,
                max_marks=question.max_marks,
                model_breakdown=marks_breakdown,
            )

        logger.info(
            f"Generated model answer for question {request.question_id} (AO1={marks_breakdown.AO1_marks}, AO2={marks_breakdown.AO2_marks}, AO3={marks_breakdown.AO3_marks})"
        )

        return ModelAnswer(
            question_id=question.id,
            model_answer=response_data.get("model_answer", ""),
            marks_breakdown=marks_breakdown,
            why_this_is_a_star=why_this_is_a_star,
            key_features_to_learn=response_data.get("key_features_to_learn", []),
            student_comparison=student_comparison,
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to build ModelAnswer from LLM response: {e}")
        logger.debug(f"Response data: {response_data}")
        raise LLMResponseError(f"LLM response structure invalid: {str(e)}") from e


def _generate_comparison(
    student_marks: int,
    max_marks: int,
    model_breakdown: MarksBreakdown,
) -> str:
    """
    Generate comparison between student answer and model answer.

    Args:
        student_marks: Marks student received
        max_marks: Maximum marks possible
        model_breakdown: Model answer marks breakdown

    Returns:
        Comparison text
    """
    student_pct = round((student_marks / max_marks * 100) if max_marks > 0 else 0, 1)

    comparison_parts = [
        f"Your answer earned {student_marks}/{max_marks} ({student_pct}%).",
        f"The model answer demonstrates perfect execution: AO1 ({model_breakdown.AO1_marks}/{model_breakdown.AO1_marks}), AO2 ({model_breakdown.AO2_marks}/{model_breakdown.AO2_marks}), AO3 ({model_breakdown.AO3_marks}/{model_breakdown.AO3_marks}).",
    ]

    # Add specific guidance
    if student_pct < 70:
        comparison_parts.append(
            "Focus on the key features highlighted above to reach A* standard."
        )
    elif student_pct < 90:
        comparison_parts.append(
            "You're close to A* standard - pay attention to the precision and depth demonstrated in the model answer."
        )

    return " ".join(comparison_parts)
