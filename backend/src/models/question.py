"""
Question Model

Represents individual exam questions extracted from Cambridge past papers.
Global entity (not scoped to students) - all students see the same questions.

Constitutional Requirements:
- Every question needs verified Cambridge mark scheme - Principle VIII
- Questions must have complete source_paper metadata - NFR-007
- Database must support syllabus tagging - FR-028
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    """
    Question entity

    Represents an individual exam question extracted from Cambridge past papers.
    This is a global entity - not scoped to individual students.

    Attributes:
        id: Unique question identifier (UUID primary key)
        subject_id: Foreign key to parent subject
        question_text: Full question text (including subparts)
        max_marks: Maximum marks for this question
        difficulty: Difficulty level (e.g., "easy", "medium", "hard")
        source_paper: Source paper identifier (e.g., "9708_s22_qp_22")
        paper_number: Paper number (e.g., 22, 31, 42)
        question_number: Question number within paper (e.g., 1, 2, 3)
        year: Exam year (e.g., 2022)
        session: Exam session (e.g., "MAY_JUNE", "FEB_MARCH", "OCT_NOV")
        marking_scheme: Detailed marking criteria (JSONB, Phase III)
        syllabus_point_ids: Array of syllabus point UUIDs (tagging, Phase II US7)
        file_path: Path to original PDF file
        created_at: Timestamp when question was extracted
        updated_at: Timestamp of last update

    Examples:
        >>> question = Question(
        ...     subject_id=economics_subject_id,
        ...     question_text="Explain the concept of opportunity cost. [8 marks]",
        ...     max_marks=8,
        ...     difficulty="medium",
        ...     source_paper="9708_s22_qp_22",
        ...     paper_number=22,
        ...     question_number=1,
        ...     year=2022,
        ...     session="MAY_JUNE"
        ... )

    Constitutional Compliance:
        - Principle VIII: Every question has source_paper for mark scheme linkage
        - NFR-007: 100% source_paper metadata completeness
        - FR-028: Syllabus tagging via syllabus_point_ids array
    """

    __tablename__ = "questions"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to Subject
    subject_id: UUID = Field(
        foreign_key="subjects.id",
        nullable=False,
        index=True,
        description="Parent subject ID",
    )

    # Question Content
    question_text: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Full question text (including subparts)",
    )

    max_marks: int = Field(
        nullable=False,
        ge=1,
        description="Maximum marks for this question",
    )

    difficulty: str = Field(
        default="medium",
        nullable=False,
        max_length=20,
        description="Difficulty level: 'easy', 'medium', 'hard'",
    )

    # Source Metadata (Constitutional Requirement - NFR-007)
    source_paper: str = Field(
        nullable=False,
        index=True,
        max_length=50,
        description="Source paper identifier (e.g., '9708_s22_qp_22')",
    )

    paper_number: int = Field(
        nullable=False,
        index=True,
        description="Paper number (e.g., 22, 31, 42)",
    )

    question_number: int = Field(
        nullable=False,
        description="Question number within paper (e.g., 1, 2, 3)",
    )

    year: int = Field(
        nullable=False,
        index=True,
        ge=2000,
        description="Exam year (e.g., 2022)",
    )

    session: str = Field(
        nullable=False,
        index=True,
        max_length=20,
        description="Exam session: 'MAY_JUNE', 'FEB_MARCH', 'OCT_NOV'",
    )

    # Phase III: Detailed Marking Criteria (JSON - compatible with SQLite for testing, uses JSONB in PostgreSQL)
    marking_scheme: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Detailed marking criteria (levels, points, rubrics) - Phase III",
    )

    # Phase II US7: Syllabus Tagging (JSON - compatible with SQLite for testing, uses ARRAY in PostgreSQL in production)
    syllabus_point_ids: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of syllabus point UUIDs for tagging",
    )

    # File Storage
    file_path: str | None = Field(
        default=None,
        max_length=500,
        description="Path to original PDF file",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when question was extracted",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp of last update",
    )

    # Validation methods
    def is_valid_difficulty(self) -> bool:
        """
        Validate difficulty level

        Returns:
            bool: True if difficulty is 'easy', 'medium', or 'hard'
        """
        return self.difficulty in ("easy", "medium", "hard")

    def is_valid_session(self) -> bool:
        """
        Validate session

        Returns:
            bool: True if session is valid Cambridge session
        """
        return self.session in ("MAY_JUNE", "FEB_MARCH", "OCT_NOV")

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<Question(source={self.source_paper}, q={self.question_number}, "
            f"marks={self.max_marks})>"
        )
