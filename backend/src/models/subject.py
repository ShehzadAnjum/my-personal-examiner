"""
Subject Model

Represents A-Level subjects available for study.
Global entity (not scoped to students) - all students see the same subjects.

Constitutional Requirements:
- Economics 9708 must be seeded (Principle I) - FR-014
- Subject data must match current Cambridge syllabi - Principle I
- Syllabus synchronization required monthly - Principle III
"""

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class Subject(SQLModel, table=True):
    """
    Subject entity

    Represents an A-Level subject available for study.
    This is a global entity - not scoped to individual students.

    Attributes:
        id: Unique subject identifier (UUID primary key)
        code: Cambridge subject code (e.g., "9708" for Economics)
        name: Subject name (e.g., "Economics")
        level: "AS" or "A" (A-Level)
        exam_board: Exam board name (default: "Cambridge International")
        syllabus_year: Syllabus version years (e.g., "2023-2025")

    Examples:
        >>> economics = Subject(
        ...     code="9708",
        ...     name="Economics",
        ...     level="A",
        ...     exam_board="Cambridge International",
        ...     syllabus_year="2023-2025"
        ... )

    Constitutional Compliance:
        - Principle I: All subject content must match Cambridge syllabi
        - Principle III: Syllabus versions tracked with syllabus_year field
        - FR-014: Economics 9708 seeded as initial subject
    """

    __tablename__ = "subjects"
    __table_args__ = {"extend_existing": True}

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Subject Identification
    code: str = Field(
        nullable=False,
        index=True,
        max_length=10,
        description="Cambridge subject code (e.g., '9708')",
    )

    name: str = Field(
        nullable=False,
        max_length=100,
        description="Subject name (e.g., 'Economics')",
    )

    level: str = Field(
        nullable=False,
        max_length=10,
        description="Subject level: 'AS' or 'A'",
    )

    exam_board: str = Field(
        default="Cambridge International",
        nullable=False,
        max_length=50,
        description="Exam board name",
    )

    syllabus_year: str = Field(
        nullable=False,
        max_length=20,
        description="Syllabus version years (e.g., '2023-2025')",
    )

    # Phase II: Subject Configuration (JSON - compatible with SQLite for testing, uses JSONB in PostgreSQL) - AD-001
    marking_config: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Marking rubric config (level descriptors, rubric type, essay structure)",
    )

    extraction_patterns: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="PDF extraction patterns (question delimiters, marks patterns, subparts)",
    )

    paper_templates: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Paper structure templates (paper types, question counts, marks distribution)",
    )

    # Validation methods
    def is_valid_level(self) -> bool:
        """
        Validate subject level

        Returns:
            bool: True if level is "AS" or "A"
        """
        return self.level in ("AS", "A")

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Subject(code={self.code}, name={self.name}, level={self.level})>"


# Economics 9708 Seed Data (Constitutional Requirement - FR-014)
ECONOMICS_9708_SEED = {
    "code": "9708",
    "name": "Economics",
    "level": "A",
    "exam_board": "Cambridge International",
    "syllabus_year": "2023-2025",
}
