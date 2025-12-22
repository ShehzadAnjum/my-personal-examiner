"""
Attempt Model

Represents a student's attempt at completing an exam.

Phase II/III Integration:
- Links students to exams (many-to-one relationship)
- Tracks start/submit times, overall score, and grade
- Supports multiple attempts per exam template

Phase III Enhancement:
- Graded status tracking for Marker Agent workflow
- Overall score aggregation from attempted_questions
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Attempt(SQLModel, table=True):
    """
    Attempt entity

    Represents a student's attempt at completing an exam.
    One student can have multiple attempts per exam.

    Attributes:
        id: Unique attempt identifier (UUID primary key)
        student_id: Foreign key to student (CASCADE DELETE for multi-tenant isolation)
        exam_id: Foreign key to exam (CASCADE DELETE)
        started_at: Timestamp when attempt was started
        submitted_at: Optional timestamp when attempt was submitted
        overall_score: Total marks awarded (sum from attempted_questions)
        grade: Letter grade (A*, A, B, C, D, E, U)
        status: Attempt status (IN_PROGRESS, SUBMITTED, GRADED)
        created_at: Timestamp when attempt record was created
        updated_at: Timestamp when attempt was last modified

    Examples:
        >>> attempt = Attempt(
        ...     student_id=student_uuid,
        ...     exam_id=exam_uuid,
        ...     status="IN_PROGRESS"
        ... )
        >>> # After submission and marking
        >>> attempt.submitted_at = datetime.now(timezone.utc)
        >>> attempt.overall_score = 45
        >>> attempt.grade = "A*"
        >>> attempt.status = "GRADED"

    Constitutional Compliance:
        - Multi-tenant isolation: student_id with CASCADE DELETE (Principle V)
        - A* grading standard: grade enum (Principle II)
    """

    __tablename__ = "attempts"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Keys
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True,
        description="Student ID (CASCADE DELETE for multi-tenant isolation)",
    )

    exam_id: UUID = Field(
        foreign_key="exams.id",
        nullable=False,
        index=True,
        description="Exam ID (CASCADE DELETE)",
    )

    # Attempt Lifecycle
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when attempt was started",
    )

    submitted_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when attempt was submitted (null if not submitted)",
    )

    # Scoring and Grading
    overall_score: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total marks awarded (sum from attempted_questions, null until marked)",
    )

    grade: Optional[str] = Field(
        default=None,
        max_length=5,
        description="Letter grade: A*, A, B, C, D, E, U (null until graded)",
    )

    # Status Tracking
    status: str = Field(
        default="IN_PROGRESS",
        nullable=False,
        max_length=20,
        description="Attempt status: IN_PROGRESS, SUBMITTED, GRADED",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when attempt record was created",
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when attempt was last modified",
    )

    # Validation methods
    def is_valid_status(self) -> bool:
        """
        Validate attempt status

        Returns:
            bool: True if status is valid
        """
        return self.status in ("IN_PROGRESS", "SUBMITTED", "GRADED")

    def is_valid_grade(self) -> bool:
        """
        Validate grade

        Returns:
            bool: True if grade is valid or None
        """
        if self.grade is None:
            return True
        return self.grade in ("A*", "A", "B", "C", "D", "E", "U")

    def is_submitted(self) -> bool:
        """
        Check if attempt has been submitted

        Returns:
            bool: True if submitted_at is not None
        """
        return self.submitted_at is not None

    def is_graded(self) -> bool:
        """
        Check if attempt has been graded

        Returns:
            bool: True if status is GRADED
        """
        return self.status == "GRADED"

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<Attempt(student={str(self.student_id)[:8]}, exam={str(self.exam_id)[:8]}, "
            f"status={self.status}, score={self.overall_score}, grade={self.grade})>"
        )
