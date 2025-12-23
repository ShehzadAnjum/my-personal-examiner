"""
Feedback Schemas

Pydantic schemas for Reviewer Agent endpoints (weakness analysis, model answers, improvement plans).

Phase III User Story 5: Students see categorized weaknesses (AO1/AO2/AO3),
A* model answers with annotations, and actionable improvement plans.

Constitutional Requirements:
- Principle II: A* Standard (model answers demonstrate excellence)
- Principle VI: Constructive feedback (actionable improvement plans)
- Principle I: Subject accuracy (Cambridge syllabus alignment)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class Weakness(BaseModel):
    """
    Single weakness identified in student work.

    Attributes:
        weakness: Specific knowledge gap or skill deficit
        examples_from_answer: Direct quotes from student answer
        severity: Impact level (low/medium/high)
        syllabus_points_affected: Relevant syllabus codes
    """

    weakness: str = Field(
        ...,
        description="Specific knowledge gap or skill deficit",
        examples=["Imprecise definition - used 'what people want' instead of 'quantity willing and able to purchase'"],
    )

    examples_from_answer: List[str] = Field(
        ...,
        description="Direct quotes from student answer",
        examples=[["demand is what people want"]],
    )

    severity: str = Field(
        ...,
        description="Impact level",
        examples=["low", "medium", "high"],
    )

    syllabus_points_affected: List[str] = Field(
        default_factory=list,
        description="Relevant syllabus codes",
        examples=[["9708.2.1", "9708.2.2"]],
    )


class WeaknessAnalysis(BaseModel):
    """
    Comprehensive weakness analysis categorized by Assessment Objectives.

    Attributes:
        AO1_knowledge: Knowledge and understanding weaknesses
        AO2_application: Application weaknesses
        AO3_evaluation: Analysis and evaluation weaknesses
    """

    AO1_knowledge: List[Weakness] = Field(
        default_factory=list,
        description="Knowledge and understanding weaknesses",
    )

    AO2_application: List[Weakness] = Field(
        default_factory=list,
        description="Application weaknesses",
    )

    AO3_evaluation: List[Weakness] = Field(
        default_factory=list,
        description="Analysis and evaluation weaknesses",
    )


class ActionItem(BaseModel):
    """
    Specific, measurable improvement action.

    Attributes:
        id: Unique action identifier
        action: Specific improvement task
        target_weakness: Which weakness this addresses
        how_to_do_it: Step-by-step guidance
        success_criteria: How to measure improvement
        resources: Learning resources and practice recommendations
    """

    id: str = Field(
        ...,
        description="Unique action identifier",
        examples=["ACTION_1", "ACTION_2"],
    )

    action: str = Field(
        ...,
        description="Specific improvement task",
        examples=["Memorize precise definitions for 10 core Economics terms with ceteris paribus clauses"],
    )

    target_weakness: str = Field(
        ...,
        description="Which weakness this addresses",
        examples=["AO1 - Imprecise Definitions"],
    )

    how_to_do_it: str = Field(
        ...,
        description="Step-by-step guidance",
        examples=["1. Review syllabus glossary for exact definitions\n2. Practice writing definitions from memory\n3. Check against Cambridge mark schemes"],
    )

    success_criteria: str = Field(
        ...,
        description="How to measure improvement",
        examples=["Can write all 10 definitions with key terms and ceteris paribus clauses without notes"],
    )

    resources: List[str] = Field(
        default_factory=list,
        description="Learning resources and practice recommendations",
        examples=[["9708 syllabus glossary", "Teacher Agent: Explain concept for each term", "Past papers Q1-5"]],
    )


class PracticeRecommendation(BaseModel):
    """
    Targeted practice recommendation.

    Attributes:
        syllabus_point: Syllabus code to practice
        question_type: Type of question to attempt
        focus: What to focus on when practicing
    """

    syllabus_point: str = Field(
        ...,
        description="Syllabus code to practice",
        examples=["9708.2.1"],
    )

    question_type: str = Field(
        ...,
        description="Type of question to attempt",
        examples=["Define and explain questions", "Application essays", "Evaluation essays"],
    )

    focus: str = Field(
        ...,
        description="What to focus on when practicing",
        examples=["Include ceteris paribus assumption and all key terms in definition"],
    )


class ImprovementPlan(BaseModel):
    """
    Comprehensive improvement plan with actionable steps.

    Attributes:
        priority_areas: Top 3 areas to focus on
        action_items: 5-10 specific improvement actions
        practice_recommendations: Targeted practice suggestions
    """

    priority_areas: List[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Top 3 areas to focus on",
        examples=[["Precise definitions (AO1)", "Real-world examples with data (AO2)", "Balanced evaluation (AO3)"]],
    )

    action_items: List[ActionItem] = Field(
        ...,
        min_length=5,
        max_length=10,
        description="5-10 specific improvement actions",
    )

    practice_recommendations: List[PracticeRecommendation] = Field(
        default_factory=list,
        description="Targeted practice suggestions",
    )


class ProgressComparison(BaseModel):
    """
    Comparison with previous attempts.

    Attributes:
        compared_to_previous: Summary comparison text
        improvements: What has improved
        regressions: What has gotten worse
        trend: Overall performance trend
    """

    compared_to_previous: Optional[str] = Field(
        default=None,
        description="Summary comparison text",
        examples=["Your AO1 score improved from 12/20 (60%) to 15/20 (75%) since your last attempt"],
    )

    improvements: List[str] = Field(
        default_factory=list,
        description="What has improved",
        examples=[["AO1 definitions more precise", "Better use of economic terminology"]],
    )

    regressions: List[str] = Field(
        default_factory=list,
        description="What has gotten worse",
        examples=[["AO2 examples less specific than before", "Evaluation weaker in Question 3"]],
    )

    trend: str = Field(
        ...,
        description="Overall performance trend",
        examples=["improving", "stable", "declining"],
    )


class WeaknessReport(BaseModel):
    """
    Complete weakness analysis report with improvement plan.

    Response for POST /api/feedback/analyze-weaknesses endpoint.

    Attributes:
        improvement_plan_id: UUID of created improvement plan
        attempt_id: UUID of analyzed attempt
        overall_score: Total marks from attempt
        grade: Letter grade from attempt
        weakness_analysis: Weaknesses categorized by AO1/AO2/AO3
        improvement_plan: Actionable improvement plan
        progress_comparison: Comparison with previous attempts

    Examples:
        >>> report = WeaknessReport(
        ...     improvement_plan_id=UUID("..."),
        ...     attempt_id=UUID("..."),
        ...     overall_score=45,
        ...     grade="A",
        ...     weakness_analysis=WeaknessAnalysis(...),
        ...     improvement_plan=ImprovementPlan(...),
        ...     progress_comparison=ProgressComparison(...)
        ... )

    Constitutional Compliance:
        - Principle VI: Constructive feedback with specific actions
        - Principle I: Cambridge syllabus alignment (syllabus_points_affected)
    """

    improvement_plan_id: UUID = Field(
        ...,
        description="UUID of created improvement plan",
        examples=["aa0e8400-e29b-41d4-a716-446655440005"],
    )

    attempt_id: UUID = Field(
        ...,
        description="UUID of analyzed attempt",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )

    overall_score: int = Field(
        ...,
        ge=0,
        description="Total marks from attempt",
        examples=[45],
    )

    grade: str = Field(
        ...,
        description="Letter grade from attempt",
        examples=["A", "B", "C"],
    )

    weakness_analysis: WeaknessAnalysis = Field(
        ...,
        description="Weaknesses categorized by AO1/AO2/AO3",
    )

    improvement_plan: ImprovementPlan = Field(
        ...,
        description="Actionable improvement plan",
    )

    progress_comparison: ProgressComparison = Field(
        ...,
        description="Comparison with previous attempts",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
                            "syllabus_points_affected": ["9708.2.1"],
                        }
                    ],
                    "AO2_application": [],
                    "AO3_evaluation": [],
                },
                "improvement_plan": {
                    "priority_areas": ["Precise definitions (AO1)"],
                    "action_items": [
                        {
                            "id": "ACTION_1",
                            "action": "Memorize precise definitions for 10 core Economics terms",
                            "target_weakness": "AO1 - Imprecise Definitions",
                            "how_to_do_it": "Review syllabus glossary...",
                            "success_criteria": "Can write all 10 definitions...",
                            "resources": ["9708 syllabus glossary"],
                        }
                    ],
                    "practice_recommendations": [],
                },
                "progress_comparison": {
                    "compared_to_previous": "First attempt - no comparison available",
                    "improvements": [],
                    "regressions": [],
                    "trend": "stable",
                },
            }
        }
    }


class AnalyzeWeaknessesRequest(BaseModel):
    """
    Request to analyze weaknesses from an exam attempt.

    Used for POST /api/feedback/analyze-weaknesses endpoint.

    Attributes:
        attempt_id: UUID of exam attempt to analyze
        include_previous_attempts: Whether to compare with previous attempts

    Examples:
        >>> request = AnalyzeWeaknessesRequest(
        ...     attempt_id=UUID("..."),
        ...     include_previous_attempts=True
        ... )

    Constitutional Compliance:
        - Principle VI: Enables constructive feedback generation
    """

    attempt_id: UUID = Field(
        ...,
        description="UUID of exam attempt to analyze",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )

    include_previous_attempts: bool = Field(
        default=True,
        description="Whether to compare with previous attempts",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
                "include_previous_attempts": True,
            }
        }
    }


class MarksBreakdown(BaseModel):
    """
    Marks breakdown for model answer.

    Attributes:
        AO1_marks: Knowledge marks
        AO2_marks: Application marks
        AO3_marks: Evaluation marks
        total: Total marks
    """

    AO1_marks: int = Field(..., ge=0, description="Knowledge marks")
    AO2_marks: int = Field(..., ge=0, description="Application marks")
    AO3_marks: int = Field(..., ge=0, description="Evaluation marks")
    total: int = Field(..., ge=0, description="Total marks")


class WhyThisIsAStar(BaseModel):
    """
    Explanation of what makes the model answer A* quality.

    Attributes:
        knowledge_demonstration: What makes AO1 perfect
        application_demonstration: What makes AO2 perfect
        evaluation_demonstration: What makes AO3 perfect
        structure_excellence: Why structure is perfect
    """

    knowledge_demonstration: str = Field(
        ...,
        description="What makes AO1 perfect",
        examples=["Uses precise definition with all key terms and ceteris paribus assumption"],
    )

    application_demonstration: str = Field(
        ...,
        description="What makes AO2 perfect",
        examples=["Provides specific UK inflation example (9.1% in 2022) with cited data"],
    )

    evaluation_demonstration: str = Field(
        ...,
        description="What makes AO3 perfect",
        examples=["Weighs pros vs cons, acknowledges limitations, reaches clear justified conclusion"],
    )

    structure_excellence: str = Field(
        ...,
        description="Why structure is perfect",
        examples=["Clear introduction, logical development with signposting, strong conclusion"],
    )


class ModelAnswer(BaseModel):
    """
    A* model answer with annotations and learning points.

    Response for POST /api/feedback/generate-model-answer endpoint.

    Attributes:
        question_id: UUID of question
        model_answer: The A* answer text
        marks_breakdown: AO1/AO2/AO3 marks
        why_this_is_a_star: Explanation of A* quality
        key_features_to_learn: Features student should emulate
        student_comparison: Optional comparison with student answer

    Examples:
        >>> model = ModelAnswer(
        ...     question_id=UUID("..."),
        ...     model_answer="The law of demand states that...",
        ...     marks_breakdown=MarksBreakdown(...),
        ...     why_this_is_a_star=WhyThisIsAStar(...),
        ...     key_features_to_learn=[...],
        ...     student_comparison=None
        ... )

    Constitutional Compliance:
        - Principle II: A* standard (model answers demonstrate excellence)
        - Principle VI: Constructive feedback (key features to learn)
    """

    question_id: UUID = Field(
        ...,
        description="UUID of question",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )

    model_answer: str = Field(
        ...,
        description="The A* answer text",
        examples=["The law of demand states that as price rises, quantity demanded falls, ceteris paribus..."],
    )

    marks_breakdown: MarksBreakdown = Field(
        ...,
        description="AO1/AO2/AO3 marks",
    )

    why_this_is_a_star: WhyThisIsAStar = Field(
        ...,
        description="Explanation of A* quality",
    )

    key_features_to_learn: List[str] = Field(
        ...,
        min_length=3,
        max_length=10,
        description="Features student should emulate",
        examples=[["Always include ceteris paribus in definitions", "Use specific data with citations", "Structure: define, explain, diagram, example"]],
    )

    student_comparison: Optional[str] = Field(
        default=None,
        description="Optional comparison with student answer",
        examples=["Your answer earned 8/12. The model answer demonstrates perfect AO1 (6/6) through precise definition..."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "880e8400-e29b-41d4-a716-446655440003",
                "model_answer": "The law of demand states that as price rises, quantity demanded falls, ceteris paribus...",
                "marks_breakdown": {
                    "AO1_marks": 6,
                    "AO2_marks": 4,
                    "AO3_marks": 0,
                    "total": 10,
                },
                "why_this_is_a_star": {
                    "knowledge_demonstration": "Uses precise definition with ceteris paribus",
                    "application_demonstration": "Provides specific UK example with data",
                    "evaluation_demonstration": "N/A - no evaluation required",
                    "structure_excellence": "Clear progression from theory to application",
                },
                "key_features_to_learn": [
                    "Always include ceteris paribus in definitions",
                    "Use specific data with citations",
                ],
                "student_comparison": None,
            }
        }
    }


class GenerateModelAnswerRequest(BaseModel):
    """
    Request to generate A* model answer for a question.

    Used for POST /api/feedback/generate-model-answer endpoint.

    Attributes:
        question_id: UUID of question to answer
        attempted_question_id: Optional UUID of student's attempt (for comparison)

    Examples:
        >>> request = GenerateModelAnswerRequest(
        ...     question_id=UUID("..."),
        ...     attempted_question_id=UUID("...")
        ... )

    Constitutional Compliance:
        - Principle II: A* standard model answer generation
    """

    question_id: UUID = Field(
        ...,
        description="UUID of question to answer",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )

    attempted_question_id: Optional[UUID] = Field(
        default=None,
        description="Optional UUID of student's attempt (for comparison)",
        examples=["bb0e8400-e29b-41d4-a716-446655440006"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "880e8400-e29b-41d4-a716-446655440003",
                "attempted_question_id": "bb0e8400-e29b-41d4-a716-446655440006",
            }
        }
    }
