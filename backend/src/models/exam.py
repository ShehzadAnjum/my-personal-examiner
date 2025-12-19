"""
Exam Model

Represents generated exams for practice, timed tests, or full papers.

Phase II User Story 6: Exam Generation
- Generate custom exams from question bank
- Support multiple exam types (PRACTICE, TIMED, FULL_PAPER)
- Track exam status (PENDING, IN_PROGRESS, COMPLETED)
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Exam(SQLModel, table=True):
    """
    Exam entity

    Represents a generated exam (practice, timed, or full paper).
    Links to questions via question_ids JSONB array.

    Attributes:
        id: Unique exam identifier (UUID primary key)
        student_id: Optional student ID (null for teacher-generated templates)
        subject_id: Foreign key to subject
        exam_type: Type of exam (PRACTICE, TIMED, FULL_PAPER)
        paper_number: Optional paper number (22, 31, 32, 42, etc.)
        question_ids: Array of question UUIDs (JSONB)
        total_marks: Total marks for the exam
        duration: Exam duration in minutes
        status: Exam status (PENDING, IN_PROGRESS, COMPLETED)
        created_at: Timestamp when exam was created

    Examples:
        >>> exam = Exam(
        ...     subject_id=economics_subject_id,
        ...     exam_type="PRACTICE",
        ...     paper_number=22,
        ...     question_ids=["uuid1", "uuid2", "uuid3"],
        ...     total_marks=30,
        ...     duration=60,
        ...     status="PENDING"
        ... )

    Constitutional Compliance:
        - Multi-tenant isolation: student_id for filtering (Principle V)
        - Exam types match Cambridge structure (Principle I)
    """

    __tablename__ = "exams"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Keys
    student_id: UUID | None = Field(
        default=None,
        foreign_key="students.id",
        index=True,
        description="Student ID (null for teacher-generated templates)",
    )

    subject_id: UUID = Field(
        foreign_key="subjects.id",
        nullable=False,
        index=True,
        description="Subject ID",
    )

    # Exam Configuration
    exam_type: str = Field(
        nullable=False,
        max_length=20,
        description="Exam type: PRACTICE, TIMED, FULL_PAPER",
    )

    paper_number: int | None = Field(
        default=None,
        description="Paper number (e.g., 22, 31, 42)",
    )

    # Questions (stored as JSON array of UUIDs - compatible with SQLite for testing, uses JSONB in PostgreSQL)
    question_ids: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of question UUIDs",
    )

    # Exam Metadata
    total_marks: int = Field(
        nullable=False,
        ge=1,
        description="Total marks for the exam",
    )

    duration: int = Field(
        nullable=False,
        ge=1,
        description="Exam duration in minutes",
    )

    status: str = Field(
        default="PENDING",
        nullable=False,
        max_length=20,
        description="Exam status: PENDING, IN_PROGRESS, COMPLETED",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when exam was created",
    )

    # Validation methods
    def is_valid_exam_type(self) -> bool:
        """
        Validate exam type

        Returns:
            bool: True if exam_type is valid
        """
        return self.exam_type in ("PRACTICE", "TIMED", "FULL_PAPER")

    def is_valid_status(self) -> bool:
        """
        Validate exam status

        Returns:
            bool: True if status is valid
        """
        return self.status in ("PENDING", "IN_PROGRESS", "COMPLETED")

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<Exam(type={self.exam_type}, paper={self.paper_number}, "
            f"marks={self.total_marks}, status={self.status})>"
        )
