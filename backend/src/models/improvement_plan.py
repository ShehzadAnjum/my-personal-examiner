"""Reviewer Agent - Improvement Plan Model

Links student weaknesses (AO1/AO2/AO3) to actionable improvement tasks.

Constitutional Requirements:
- Principle VI: Constructive Feedback (action_items provide concrete steps)
- Principle V: Multi-tenant isolation (student_id FK enforced)
- Principle VII: >80% test coverage (simple CRUD model, easily testable)
"""

from datetime import datetime
from typing import Dict, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON
from typing_extensions import TypedDict


class WeaknessCategory(TypedDict):
    """TypedDict for categorized weakness"""
    category: str  # e.g., "Imprecise Definitions", "Weak Application", "No Evaluation"
    examples: List[str]  # Specific examples from student answers
    severity: str  # "low", "medium", "high"
    syllabus_points: List[str]  # Affected syllabus point codes


class ActionItem(TypedDict):
    """TypedDict for actionable improvement task"""
    id: str  # Unique action ID
    action: str  # Specific task description
    target_weakness: str  # Which weakness this addresses
    due_date: str  # YYYY-MM-DD
    completed: bool
    resources: List[str]  # Teacher Agent links, practice questions, etc.


class ImprovementPlan(SQLModel, table=True):
    """
    Store weakness analysis and actionable improvement plans.

    Weaknesses are categorized by Cambridge Assessment Objectives:
    - AO1: Knowledge and understanding
    - AO2: Application
    - AO3: Analysis and evaluation

    Each weakness category links to specific remediation actions with resources.
    """

    __tablename__ = "improvement_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", nullable=False)
    attempt_id: UUID = Field(foreign_key="attempts.id", nullable=False)

    # JSONB field: {"AO1": [...], "AO2": [...], "AO3": [...]}
    weaknesses: Dict[str, List[WeaknessCategory]] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=dict
    )

    # JSONB field: Array of ActionItem objects
    action_items: List[ActionItem] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list
    )

    # JSONB field: Progress tracking {"action-1": {started, completed, notes}, ...}
    progress: Dict[str, dict] = Field(
        sa_column=Column(JSON, nullable=True),
        default_factory=dict
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "weaknesses": {
                    "AO1": [
                        {
                            "category": "Imprecise Definitions",
                            "examples": [
                                "Question 2: Defined demand as 'what people want' instead of 'quantity willing and able to purchase'"
                            ],
                            "severity": "high",
                            "syllabus_points": ["9708.2.1"]
                        }
                    ],
                    "AO2": [
                        {
                            "category": "Weak Application",
                            "examples": [
                                "Question 3: Used generic example 'some goods' instead of specific real-world case"
                            ],
                            "severity": "medium",
                            "syllabus_points": ["9708.2.2"]
                        }
                    ],
                    "AO3": [
                        {
                            "category": "No Evaluation",
                            "examples": [
                                "Question 4: Listed arguments but no conclusion or weighing"
                            ],
                            "severity": "high",
                            "syllabus_points": ["9708.3.1"]
                        }
                    ]
                },
                "action_items": [
                    {
                        "id": "action-1",
                        "action": "Memorize precise definitions for 10 core Economics terms",
                        "target_weakness": "AO1 - Imprecise Definitions",
                        "due_date": "2025-01-22",
                        "completed": False,
                        "resources": [
                            "9708 syllabus glossary",
                            "Teacher Agent: Explain concept for each term"
                        ]
                    }
                ]
            }
        }
