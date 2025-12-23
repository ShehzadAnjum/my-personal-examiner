"""
Feedback Routes

API endpoints for Reviewer Agent (weakness analysis, model answers, improvement plans).

Phase III User Story 5: Students see categorized weaknesses (AO1/AO2/AO3),
A* model answers with annotations, and actionable improvement plans.

Constitutional Requirements:
- Principle II: A* Standard (model answers demonstrate excellence)
- Principle VI: Constructive feedback (actionable improvement plans)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.schemas.feedback_schemas import (
    AnalyzeWeaknessesRequest,
    WeaknessReport,
    GenerateModelAnswerRequest,
    ModelAnswer,
)
from src.services.review_service import (
    analyze_weaknesses,
    generate_model_answer,
    AttemptNotFoundError,
    QuestionNotFoundError,
    AttemptedQuestionNotFoundError,
    LLMResponseError,
)
from src.ai_integration.llm_fallback import LLMFallbackOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


# Endpoints


@router.post("/analyze-weaknesses", response_model=WeaknessReport, status_code=status.HTTP_201_CREATED)
async def analyze_weaknesses_endpoint(
    request: AnalyzeWeaknessesRequest,
    session: Session = Depends(get_session),
) -> WeaknessReport:
    """
    Analyze student weaknesses from exam attempt and create improvement plan.

    Categorizes errors by AO1 (Knowledge), AO2 (Application), AO3 (Evaluation).
    Generates 5-10 actionable improvement items with specific resources and success criteria.
    Optionally compares with previous attempts to track progress.

    Args:
        request: AnalyzeWeaknessesRequest with attempt_id
        session: Database session (injected)

    Returns:
        WeaknessReport: Weaknesses, improvement plan, progress comparison

    Raises:
        HTTPException: 404 if attempt_id not found
        HTTPException: 500 if LLM weakness analysis fails

    Examples:
        >>> POST /api/feedback/analyze-weaknesses
        {
            "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
            "include_previous_attempts": true
        }

        >>> Response: 201 CREATED
        {
            "improvement_plan_id": "aa0e8400-e29b-41d4-a716-446655440005",
            "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
            "overall_score": 45,
            "grade": "A",
            "weakness_analysis": {
                "AO1_knowledge": [
                    {
                        "weakness": "Imprecise definition of demand",
                        "examples_from_answer": ["demand is what people want"],
                        "severity": "high",
                        "syllabus_points_affected": ["9708.2.1"]
                    }
                ],
                "AO2_application": [
                    {
                        "weakness": "Generic examples without data",
                        "examples_from_answer": ["some goods are affected"],
                        "severity": "medium",
                        "syllabus_points_affected": ["9708.2.2"]
                    }
                ],
                "AO3_evaluation": [
                    {
                        "weakness": "No conclusion after listing arguments",
                        "examples_from_answer": ["...on the other hand..."],
                        "severity": "high",
                        "syllabus_points_affected": ["9708.3.1"]
                    }
                ]
            },
            "improvement_plan": {
                "priority_areas": ["Precise definitions (AO1)", "Specific examples with data (AO2)", "Clear conclusions (AO3)"],
                "action_items": [
                    {
                        "id": "ACTION_1",
                        "action": "Memorize precise definitions for 10 core Economics terms with ceteris paribus",
                        "target_weakness": "AO1 - Imprecise Definitions",
                        "how_to_do_it": "1. Review syllabus glossary\n2. Practice writing from memory\n3. Check against mark schemes",
                        "success_criteria": "Can write all 10 definitions with key terms without notes",
                        "resources": ["9708 syllabus glossary", "Teacher Agent: Explain concept for each term"]
                    }
                ],
                "practice_recommendations": [
                    {
                        "syllabus_point": "9708.2.1",
                        "question_type": "Define and explain",
                        "focus": "Include ceteris paribus and all key terms"
                    }
                ]
            },
            "progress_comparison": {
                "compared_to_previous": "Your AO1 score improved from 12/20 (60%) to 18/24 (75%)",
                "improvements": ["More precise definitions", "Better economic terminology"],
                "regressions": ["AO2 examples less specific than previous attempt"],
                "trend": "improving"
            }
        }

    Constitutional Compliance:
        - Principle VI: Constructive feedback with specific actions
        - Principle I: Cambridge syllabus alignment (syllabus_points_affected)
    """

    logger.info(
        f"Analyze weaknesses request: attempt_id={request.attempt_id}, include_previous={request.include_previous_attempts}"
    )

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call review service with fallback orchestration
        report = await analyze_weaknesses(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully analyzed weaknesses for attempt {request.attempt_id} (improvement_plan_id={report.improvement_plan_id})"
        )

        return report

    except AttemptNotFoundError as e:
        logger.warning(f"Attempt not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weakness analysis: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in analyze_weaknesses_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing weaknesses",
        )


@router.post("/generate-model-answer", response_model=ModelAnswer, status_code=status.HTTP_200_OK)
async def generate_model_answer_endpoint(
    request: GenerateModelAnswerRequest,
    session: Session = Depends(get_session),
) -> ModelAnswer:
    """
    Generate A* model answer for a question.

    Creates perfect exemplar answer demonstrating:
    - AO1: Precise definitions with exact terminology
    - AO2: Specific real-world examples with data
    - AO3: Balanced arguments with clear conclusion

    Includes annotations explaining why it's A* quality and key features to learn.
    Optionally compares with student's actual answer if attempted_question_id provided.

    Args:
        request: GenerateModelAnswerRequest with question_id, optional attempted_question_id
        session: Database session (injected)

    Returns:
        ModelAnswer: A* answer with annotations and learning points

    Raises:
        HTTPException: 404 if question_id or attempted_question_id not found
        HTTPException: 500 if LLM model answer generation fails

    Examples:
        >>> POST /api/feedback/generate-model-answer
        {
            "question_id": "880e8400-e29b-41d4-a716-446655440003",
            "attempted_question_id": "bb0e8400-e29b-41d4-a716-446655440006"
        }

        >>> Response: 200 OK
        {
            "question_id": "880e8400-e29b-41d4-a716-446655440003",
            "model_answer": "The law of demand states that as price rises, quantity demanded falls, ceteris paribus. This occurs due to two effects: the substitution effect (consumers switch to cheaper alternatives) and the income effect (higher prices reduce real purchasing power). For example, when UK petrol prices rose from £1.20 to £1.80 per litre in 2022 (50% increase), quantity demanded fell by 8% according to Department for Transport data. This demonstrates the inverse relationship between price and quantity demanded, holding other factors constant.",
            "marks_breakdown": {
                "AO1_marks": 6,
                "AO2_marks": 4,
                "AO3_marks": 0,
                "total": 10
            },
            "why_this_is_a_star": {
                "knowledge_demonstration": "Uses precise definition with ceteris paribus assumption, identifies both substitution and income effects with exact terminology",
                "application_demonstration": "Provides specific UK example with exact data (£1.20→£1.80, 8% fall) and credible source (Dept for Transport)",
                "evaluation_demonstration": "N/A - definition question requires no evaluation",
                "structure_excellence": "Logical flow: define → explain mechanism → specific example → link back to theory"
            },
            "key_features_to_learn": [
                "Always include ceteris paribus in definitions",
                "Name both substitution and income effects (not just 'people buy less')",
                "Use specific numerical data with sources",
                "Structure: define, explain, example, conclusion"
            ],
            "student_comparison": "Your answer earned 8/10 (80%). The model answer demonstrates perfect AO1 (6/6) through precise definition with ceteris paribus and both effects named. Your AO2 was weaker (2/4) - the model shows how to use specific data with sources rather than generic examples."
        }

    Constitutional Compliance:
        - Principle II: A* standard (model answers demonstrate excellence)
        - Principle VI: Constructive feedback (key features to learn)
    """

    logger.info(
        f"Generate model answer request: question_id={request.question_id}, attempted_question_id={request.attempted_question_id}"
    )

    try:
        # Create LLM orchestrator for this request
        llm_orchestrator = LLMFallbackOrchestrator()

        # Call review service with fallback orchestration
        model = await generate_model_answer(
            session=session,
            request=request,
            llm_orchestrator=llm_orchestrator,
        )

        logger.info(
            f"Successfully generated model answer for question {request.question_id} (AO1={model.marks_breakdown.AO1_marks}, AO2={model.marks_breakdown.AO2_marks}, AO3={model.marks_breakdown.AO3_marks})"
        )

        return model

    except QuestionNotFoundError as e:
        logger.warning(f"Question not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except AttemptedQuestionNotFoundError as e:
        logger.warning(f"Attempted question not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except LLMResponseError as e:
        logger.error(f"LLM response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate model answer: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in generate_model_answer_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating model answer",
        )
