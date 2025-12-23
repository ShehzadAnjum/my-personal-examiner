"""
Marking Schemas

Pydantic schemas for Marker Agent endpoints (strict marking with AO1/AO2/AO3 breakdown).

Phase III User Story 4: Economics 9708 answers receive PhD-level strict marking
with AO1/AO2/AO3 breakdown, error categorization, and confidence scoring.

Constitutional Requirements:
- Principle II: A* Standard marking always (zero tolerance for imprecision)
- Principle VI: Constructive feedback (explain WHY and HOW to improve)
- Principle I: Subject accuracy (Cambridge mark scheme alignment)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MarkedPoint(BaseModel):
    """
    Single mark scheme point assessment.

    Attributes:
        point_id: Mark scheme point identifier (e.g., "AO1-1")
        present: Whether point is present in answer
        quality: Quality of answer for this point
        quote: Exact quote from student answer (if present)
    """

    point_id: str = Field(
        ...,
        description="Mark scheme point identifier",
        examples=["AO1-1", "AO2-3", "AO3-1"],
    )

    present: bool = Field(
        ...,
        description="Whether point is present in answer",
    )

    quality: str = Field(
        ...,
        description="Quality of answer for this point",
        examples=["good", "weak", "missing"],
    )

    quote: Optional[str] = Field(
        default=None,
        description="Exact quote from student answer (if present)",
        examples=["The law of demand states that as price rises, quantity demanded falls, ceteris paribus"],
    )


class MarkingError(BaseModel):
    """
    Error identified in student answer.

    Categorized by Assessment Objective (AO1/AO2/AO3).

    Attributes:
        category: Error category (AO type + description)
        description: Detailed error explanation
        marks_lost: Marks lost due to this error
    """

    category: str = Field(
        ...,
        description="Error category (AO type + description)",
        examples=["AO1 - Imprecise Definition", "AO2 - Generic Example", "AO3 - Missing Evaluation"],
    )

    description: str = Field(
        ...,
        description="Detailed error explanation",
        examples=["Defined demand as 'what people want' instead of 'quantity willing and able to purchase at given price, ceteris paribus'"],
    )

    marks_lost: int = Field(
        ...,
        ge=0,
        description="Marks lost due to this error",
        examples=[2, 1, 3],
    )


class MarkingResult(BaseModel):
    """
    Result of marking a single answer.

    Response for POST /api/marking/mark-answer endpoint.

    Attributes:
        marks_awarded: Total marks awarded
        max_marks: Maximum possible marks
        percentage: Percentage score
        ao1_score: AO1 (Knowledge) marks awarded
        ao1_max: Maximum AO1 marks available
        ao2_score: AO2 (Application) marks awarded
        ao2_max: Maximum AO2 marks available
        ao3_score: AO3 (Evaluation) marks awarded
        ao3_max: Maximum AO3 marks available
        level: Level descriptor (L1/L2/L3/L4)
        errors: List of errors identified
        points_awarded: Mark scheme points assessment
        confidence_score: Confidence in marking (0-100)
        needs_review: Whether answer needs manual review (<70% confidence)
        feedback: Constructive feedback explaining marks and improvements

    Examples:
        >>> result = MarkingResult(
        ...     marks_awarded=12,
        ...     max_marks=15,
        ...     percentage=80.0,
        ...     ao1_score=5,
        ...     ao1_max=6,
        ...     ao2_score=4,
        ...     ao2_max=5,
        ...     ao3_score=3,
        ...     ao3_max=4,
        ...     level="L3",
        ...     errors=[...],
        ...     points_awarded=[...],
        ...     confidence_score=85,
        ...     needs_review=False,
        ...     feedback="..."
        ... )

    Constitutional Compliance:
        - Principle II: Zero tolerance for imprecision (A* standard)
        - Principle VI: Constructive feedback with WHY and HOW
    """

    marks_awarded: int = Field(
        ...,
        ge=0,
        description="Total marks awarded",
        examples=[12],
    )

    max_marks: int = Field(
        ...,
        ge=0,
        description="Maximum possible marks",
        examples=[15],
    )

    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage score",
        examples=[80.0],
    )

    ao1_score: int = Field(
        ...,
        ge=0,
        description="AO1 (Knowledge) marks awarded",
        examples=[5],
    )

    ao1_max: int = Field(
        ...,
        ge=0,
        description="Maximum AO1 marks available",
        examples=[6],
    )

    ao2_score: int = Field(
        ...,
        ge=0,
        description="AO2 (Application) marks awarded",
        examples=[4],
    )

    ao2_max: int = Field(
        ...,
        ge=0,
        description="Maximum AO2 marks available",
        examples=[5],
    )

    ao3_score: int = Field(
        ...,
        ge=0,
        description="AO3 (Evaluation) marks awarded",
        examples=[3],
    )

    ao3_max: int = Field(
        ...,
        ge=0,
        description="Maximum AO3 marks available",
        examples=[4],
    )

    level: Optional[str] = Field(
        default=None,
        description="Level descriptor (L1/L2/L3/L4)",
        examples=["L3"],
    )

    errors: List[MarkingError] = Field(
        default_factory=list,
        description="List of errors identified",
    )

    points_awarded: List[MarkedPoint] = Field(
        default_factory=list,
        description="Mark scheme points assessment",
    )

    confidence_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence in marking (0-100)",
        examples=[85],
    )

    needs_review: bool = Field(
        ...,
        description="Whether answer needs manual review (<70% confidence)",
    )

    feedback: str = Field(
        ...,
        description="Constructive feedback explaining marks and improvements",
        examples=["Your answer demonstrated good knowledge of demand concepts (AO1: 5/6) but lacked specific real-world examples with data (AO2: 4/5)..."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "marks_awarded": 12,
                "max_marks": 15,
                "percentage": 80.0,
                "ao1_score": 5,
                "ao1_max": 6,
                "ao2_score": 4,
                "ao2_max": 5,
                "ao3_score": 3,
                "ao3_max": 4,
                "level": "L3",
                "errors": [
                    {
                        "category": "AO1 - Missing Key Term",
                        "description": "Failed to mention 'ceteris paribus' assumption",
                        "marks_lost": 1,
                    }
                ],
                "points_awarded": [
                    {
                        "point_id": "AO1-1",
                        "present": True,
                        "quality": "good",
                        "quote": "The law of demand states that as price rises, quantity demanded falls",
                    }
                ],
                "confidence_score": 85,
                "needs_review": False,
                "feedback": "Your answer demonstrated good knowledge of demand concepts (AO1: 5/6)...",
            }
        }
    }


class MarkAnswerRequest(BaseModel):
    """
    Request to mark a single answer.

    Used for POST /api/marking/mark-answer endpoint.

    Attributes:
        question_id: UUID of question being answered
        student_answer: Student's written answer
        max_marks: Maximum marks for question (optional, from question if not provided)

    Examples:
        >>> request = MarkAnswerRequest(
        ...     question_id=UUID("..."),
        ...     student_answer="The law of demand states that...",
        ...     max_marks=10
        ... )

    Constitutional Compliance:
        - Principle I: question_id ensures Cambridge mark scheme alignment
        - Principle II: Strict marking with zero tolerance
    """

    question_id: UUID = Field(
        ...,
        description="UUID of question being answered",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )

    student_answer: str = Field(
        ...,
        max_length=10000,
        description="Student's written answer",
        examples=["The law of demand states that as price rises, quantity demanded falls..."],
    )

    max_marks: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum marks for question (optional, from question if not provided)",
        examples=[10],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "880e8400-e29b-41d4-a716-446655440003",
                "student_answer": "The law of demand states that as price rises, quantity demanded falls, ceteris paribus. This is because consumers substitute towards cheaper alternatives and the real income effect reduces purchasing power.",
                "max_marks": 10,
            }
        }
    }


class AttemptResult(BaseModel):
    """
    Result of marking an entire exam attempt (multiple questions).

    Response for POST /api/marking/mark-attempt endpoint.

    Attributes:
        attempt_id: UUID of exam attempt
        total_marks: Total marks awarded across all questions
        max_marks: Maximum possible marks for attempt
        percentage: Overall percentage score
        grade: Letter grade (A*, A, B, C, D, E, U)
        ao1_total: Total AO1 marks across all questions
        ao2_total: Total AO2 marks across all questions
        ao3_total: Total AO3 marks across all questions
        question_results: Individual question marking results
        needs_review: Whether any question needs manual review
        overall_feedback: Summary feedback for entire attempt

    Examples:
        >>> result = AttemptResult(
        ...     attempt_id=UUID("..."),
        ...     total_marks=45,
        ...     max_marks=60,
        ...     percentage=75.0,
        ...     grade="A",
        ...     ao1_total=18,
        ...     ao2_total=15,
        ...     ao3_total=12,
        ...     question_results=[...],
        ...     needs_review=False,
        ...     overall_feedback="Strong knowledge (AO1) but needs more evaluation (AO3)..."
        ... )

    Constitutional Compliance:
        - Principle II: A* standard grading (strict grade boundaries)
        - Principle VI: Overall feedback for improvement
    """

    attempt_id: UUID = Field(
        ...,
        description="UUID of exam attempt",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )

    total_marks: int = Field(
        ...,
        ge=0,
        description="Total marks awarded across all questions",
        examples=[45],
    )

    max_marks: int = Field(
        ...,
        ge=0,
        description="Maximum possible marks for attempt",
        examples=[60],
    )

    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall percentage score",
        examples=[75.0],
    )

    grade: str = Field(
        ...,
        description="Letter grade (A*, A, B, C, D, E, U)",
        examples=["A"],
    )

    ao1_total: int = Field(
        ...,
        ge=0,
        description="Total AO1 marks across all questions",
        examples=[18],
    )

    ao2_total: int = Field(
        ...,
        ge=0,
        description="Total AO2 marks across all questions",
        examples=[15],
    )

    ao3_total: int = Field(
        ...,
        ge=0,
        description="Total AO3 marks across all questions",
        examples=[12],
    )

    question_results: List[MarkingResult] = Field(
        ...,
        description="Individual question marking results",
    )

    needs_review: bool = Field(
        ...,
        description="Whether any question needs manual review",
    )

    overall_feedback: str = Field(
        ...,
        description="Summary feedback for entire attempt",
        examples=["Strong knowledge (AO1: 18/24) but needs more evaluation (AO3: 12/20)..."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
                "total_marks": 45,
                "max_marks": 60,
                "percentage": 75.0,
                "grade": "A",
                "ao1_total": 18,
                "ao2_total": 15,
                "ao3_total": 12,
                "question_results": [],
                "needs_review": False,
                "overall_feedback": "Strong knowledge (AO1: 18/24) but needs more evaluation (AO3: 12/20)...",
            }
        }
    }


class MarkAttemptRequest(BaseModel):
    """
    Request to mark an entire exam attempt.

    Used for POST /api/marking/mark-attempt endpoint.

    Attributes:
        attempt_id: UUID of exam attempt to mark

    Examples:
        >>> request = MarkAttemptRequest(
        ...     attempt_id=UUID("...")
        ... )

    Constitutional Compliance:
        - Principle II: A* standard marking for full exam
        - Principle V: Multi-tenant isolation (attempt belongs to student)
    """

    attempt_id: UUID = Field(
        ...,
        description="UUID of exam attempt to mark",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "attempt_id": "990e8400-e29b-41d4-a716-446655440004",
            }
        }
    }
