"""
Teaching Schemas

Pydantic schemas for Teacher Agent endpoints (concept explanations).

Phase III User Story 1: Students can request PhD-level explanations of
Economics 9708 syllabus concepts with examples, diagrams, and practice problems.

Constitutional Requirements:
- Principle I: Subject accuracy (Cambridge syllabus alignment)
- Principle III: PhD-level pedagogy (evidence-based teaching)
- Principle VI: Constructive feedback (clear explanations)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExplainConceptRequest(BaseModel):
    """
    Request for concept explanation from Teacher Agent.

    Used for POST /api/teaching/explain-concept endpoint.

    Attributes:
        syllabus_point_id: UUID of syllabus point to explain
        student_id: UUID of student requesting explanation
        include_diagrams: Whether to include visual aids (default: True)
        include_practice: Whether to include practice problems (default: True)
        context: Optional additional context (e.g., "struggling with graph interpretation")

    Examples:
        >>> request = ExplainConceptRequest(
        ...     syllabus_point_id=UUID("..."),
        ...     student_id=UUID("..."),
        ...     include_diagrams=True,
        ...     include_practice=True
        ... )

    Constitutional Compliance:
        - Principle I: syllabus_point_id ensures Cambridge alignment
        - Principle III: Optional context enables personalized pedagogy
    """

    syllabus_point_id: UUID = Field(
        ...,
        description="UUID of syllabus point to explain (e.g., 9708.1.1)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    student_id: UUID = Field(
        ...,
        description="UUID of student requesting explanation",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    include_diagrams: bool = Field(
        default=True,
        description="Whether to include visual aids (diagrams, graphs)",
    )

    include_practice: bool = Field(
        default=True,
        description="Whether to include practice problems",
    )

    context: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional context about student's struggle or question",
        examples=["I don't understand how to draw supply and demand curves"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
                "include_diagrams": True,
                "include_practice": True,
                "context": "I'm confused about the difference between movement along and shift of demand curve",
            }
        }
    }


class KeyTerm(BaseModel):
    """
    Definition of a key economic term.

    Attributes:
        term: The economic term
        definition: Precise definition using exact terminology
    """

    term: str = Field(
        ...,
        description="Economic term",
        examples=["Price Elasticity of Demand"],
    )

    definition: str = Field(
        ...,
        description="Precise definition",
        examples=["The responsiveness of quantity demanded to a change in price, ceteris paribus"],
    )


class Example(BaseModel):
    """
    Real-world example illustrating the concept.

    Attributes:
        title: Example title
        scenario: Real-world scenario with specific data
        analysis: How the concept applies to this scenario
        data_source: Optional citation
    """

    title: str = Field(
        ...,
        description="Example title",
        examples=["UK Petrol Demand 2022"],
    )

    scenario: str = Field(
        ...,
        description="Real-world scenario with specific data",
        examples=["When UK petrol prices rose from £1.50 to £2.00 per litre in 2022..."],
    )

    analysis: str = Field(
        ...,
        description="How the concept applies",
        examples=["This demonstrates inelastic demand (PED ≈ -0.25)..."],
    )

    data_source: Optional[str] = Field(
        default=None,
        description="Citation if available",
        examples=["ONS Transport Statistics 2022"],
    )


class VisualAid(BaseModel):
    """
    Visual aid (diagram, graph, table) to illustrate concept.

    Attributes:
        type: Type of visual aid
        title: Visual aid title
        description: What the visual shows
        mermaid_code: Optional Mermaid.js code for diagrams
        ascii_art: Optional ASCII art for simple graphs
    """

    type: str = Field(
        ...,
        description="Type of visual aid",
        examples=["diagram", "graph", "table"],
    )

    title: str = Field(
        ...,
        description="Visual aid title",
        examples=["Supply and Demand Equilibrium"],
    )

    description: str = Field(
        ...,
        description="What the visual shows",
        examples=["Shows how price and quantity adjust to reach market equilibrium"],
    )

    mermaid_code: Optional[str] = Field(
        default=None,
        description="Mermaid.js code for diagram rendering",
    )

    ascii_art: Optional[str] = Field(
        default=None,
        description="ASCII art for simple graphs",
    )


class WorkedExample(BaseModel):
    """
    Worked example with step-by-step solution.

    Attributes:
        problem: Cambridge-style exam question
        step_by_step_solution: Detailed solution with reasoning
        marks_breakdown: How marks would be awarded
    """

    problem: str = Field(
        ...,
        description="Cambridge-style exam question",
        examples=["Calculate the price elasticity of demand when price rises from £10 to £12..."],
    )

    step_by_step_solution: str = Field(
        ...,
        description="Detailed solution with reasoning",
        examples=["Step 1: Calculate percentage change in price: ((12-10)/10) × 100 = 20%..."],
    )

    marks_breakdown: str = Field(
        ...,
        description="How marks would be awarded",
        examples=["1 mark for formula, 2 marks for calculation, 1 mark for interpretation"],
    )


class Misconception(BaseModel):
    """
    Common student misconception and correction.

    Attributes:
        misconception: What students often think
        why_wrong: Why this is incorrect
        correct_understanding: What they should know instead
    """

    misconception: str = Field(
        ...,
        description="What students often think",
        examples=["'Demand' and 'quantity demanded' are the same thing"],
    )

    why_wrong: str = Field(
        ...,
        description="Why this is incorrect",
        examples=["Demand refers to the entire relationship, quantity demanded is a specific point"],
    )

    correct_understanding: str = Field(
        ...,
        description="Correct understanding",
        examples=["Demand is the curve; quantity demanded is one point on that curve"],
    )


class PracticeProblem(BaseModel):
    """
    Practice problem for student to attempt.

    Attributes:
        question: Practice question
        difficulty: Difficulty level
        answer_outline: Key points for answer
        marks: Marks allocated
    """

    question: str = Field(
        ...,
        description="Practice question",
        examples=["Explain why the demand for luxury cars is likely to be price elastic"],
    )

    difficulty: str = Field(
        ...,
        description="Difficulty level",
        examples=["easy", "medium", "hard"],
    )

    answer_outline: str = Field(
        ...,
        description="Key points for answer",
        examples=["Availability of substitutes, proportion of income, time period..."],
    )

    marks: int = Field(
        ...,
        ge=1,
        le=25,
        description="Marks allocated",
        examples=[6],
    )


class TopicExplanation(BaseModel):
    """
    Comprehensive topic explanation from Teacher Agent.

    Response for POST /api/teaching/explain-concept endpoint.

    Attributes:
        syllabus_code: Syllabus point code (e.g., "9708.2.1")
        concept_name: Name of concept
        definition: Precise definition with key terms
        key_terms: List of key economic terms with definitions
        explanation: Core principles explained
        examples: Real-world examples (at least 2)
        visual_aids: Diagrams, graphs, tables
        worked_examples: Step-by-step solutions
        common_misconceptions: Common errors students make
        practice_problems: Problems for student to attempt (3-5)
        related_concepts: Links to other syllabus points
        generated_by: LLM provider used (for tracking)

    Examples:
        >>> explanation = TopicExplanation(
        ...     syllabus_code="9708.2.1",
        ...     concept_name="Price Elasticity of Demand",
        ...     definition="...",
        ...     key_terms=[...],
        ...     explanation="...",
        ...     examples=[...],
        ...     visual_aids=[...],
        ...     worked_examples=[...],
        ...     common_misconceptions=[...],
        ...     practice_problems=[...],
        ...     related_concepts=["9708.2.2", "9708.2.3"],
        ...     generated_by="anthropic"
        ... )

    Constitutional Compliance:
        - Principle I: All content Cambridge-aligned (syllabus_code)
        - Principle III: PhD-level teaching (worked examples, misconceptions)
        - Principle VI: Constructive (practice problems with guidance)
    """

    syllabus_code: str = Field(
        ...,
        description="Syllabus point code",
        examples=["9708.2.1"],
    )

    concept_name: str = Field(
        ...,
        description="Name of concept",
        examples=["Price Elasticity of Demand"],
    )

    definition: str = Field(
        ...,
        description="Precise definition with key terms",
        examples=["The responsiveness of quantity demanded to a change in price..."],
    )

    key_terms: List[KeyTerm] = Field(
        ...,
        description="Key economic terms with definitions",
    )

    explanation: str = Field(
        ...,
        description="Core principles explained step-by-step",
    )

    examples: List[Example] = Field(
        ...,
        min_length=2,
        description="Real-world examples with data",
    )

    visual_aids: List[VisualAid] = Field(
        default_factory=list,
        description="Diagrams, graphs, tables",
    )

    worked_examples: List[WorkedExample] = Field(
        ...,
        min_length=1,
        description="Step-by-step worked examples",
    )

    common_misconceptions: List[Misconception] = Field(
        default_factory=list,
        description="Common errors and corrections",
    )

    practice_problems: List[PracticeProblem] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="Practice problems (3-5)",
    )

    related_concepts: List[str] = Field(
        default_factory=list,
        description="Related syllabus point codes",
        examples=[["9708.2.2", "9708.2.3"]],
    )

    generated_by: str = Field(
        ...,
        description="LLM provider used (anthropic|openai|gemini)",
        examples=["anthropic"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "syllabus_code": "9708.2.1",
                "concept_name": "Price Elasticity of Demand",
                "definition": "The responsiveness of quantity demanded to a change in price, ceteris paribus",
                "key_terms": [
                    {
                        "term": "PED",
                        "definition": "Percentage change in quantity demanded ÷ percentage change in price",
                    }
                ],
                "explanation": "Price elasticity measures how sensitive consumers are to price changes...",
                "examples": [
                    {
                        "title": "UK Petrol Demand 2022",
                        "scenario": "When UK petrol prices rose from £1.50 to £2.00...",
                        "analysis": "Quantity demanded fell by only 5%, demonstrating inelastic demand...",
                        "data_source": "ONS 2022",
                    }
                ],
                "visual_aids": [],
                "worked_examples": [
                    {
                        "problem": "Calculate PED when price rises from £10 to £12...",
                        "step_by_step_solution": "Step 1: Calculate % change in price...",
                        "marks_breakdown": "4 marks total: 1 for formula, 2 for calculation, 1 for interpretation",
                    }
                ],
                "common_misconceptions": [],
                "practice_problems": [
                    {
                        "question": "Explain why luxury goods have high PED",
                        "difficulty": "medium",
                        "answer_outline": "Availability of substitutes, high income proportion...",
                        "marks": 6,
                    }
                ],
                "related_concepts": ["9708.2.2", "9708.2.3"],
                "generated_by": "anthropic",
            }
        }
    }


class SaveExplanationRequest(BaseModel):
    """
    Request to save/bookmark a syllabus topic (pointer-based).

    Used for POST /api/teaching/explanations endpoint.

    Architecture: Pointer-based bookmarks
    - Stores ONLY reference to syllabus_point_id (no content duplication)
    - Explanation content cached in browser localStorage
    - Simple favorite/bookmark system

    Attributes:
        syllabus_point_id: UUID of syllabus point to bookmark
        student_id: UUID of student (from JWT in production)

    Examples:
        >>> request = SaveExplanationRequest(
        ...     syllabus_point_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     student_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
        ... )
    """

    syllabus_point_id: UUID = Field(
        ...,
        description="UUID of syllabus point to bookmark (pointer only, no content)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    student_id: UUID = Field(
        ...,
        description="UUID of student (from JWT in production)",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "syllabus_point_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }
    }
