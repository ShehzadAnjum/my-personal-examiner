"""
SyllabusPoint Model

Represents specific learning objectives or topics within a subject syllabus.
Global entity (not scoped to students) - all students see the same syllabus.

Constitutional Requirements:
- Must map to Cambridge International syllabus structure - Principle I
- Syllabus synchronization required monthly - Principle III
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class SyllabusPoint(SQLModel, table=True):
    """
    SyllabusPoint entity

    Represents a specific learning objective or topic within a subject syllabus.
    This is a global entity - not scoped to individual students.

    Attributes:
        id: Unique syllabus point identifier (UUID primary key)
        subject_id: Foreign key to parent subject
        code: Syllabus code (e.g., "9708.1.1" = Economics section 1 subsection 1)
        description: Learning objective description
        topics: Comma-separated topics covered (optional)
        learning_outcomes: Expected learning outcomes (optional)

    Examples:
        >>> syllabus_point = SyllabusPoint(
        ...     subject_id=economics_subject_id,
        ...     code="9708.1.1",
        ...     description="The central economic problem",
        ...     topics="Scarcity, Choice, Opportunity cost",
        ...     learning_outcomes="Understand the nature of the economic problem"
        ... )

    Constitutional Compliance:
        - Principle I: Must match Cambridge International syllabus exactly
        - Principle III: Syllabus version tracked via parent Subject.syllabus_year
        - FR-017: Code follows pattern {subject_code}.{section}.{subsection}
    """

    __tablename__ = "syllabus_points"

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

    # Syllabus Structure
    code: str = Field(
        nullable=False,
        index=True,
        max_length=20,
        description="Syllabus code (e.g., '9708.1.1')",
    )

    description: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Learning objective description",
    )

    topics: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Comma-separated topics covered",
    )

    learning_outcomes: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Expected learning outcomes",
    )

    # Validation methods
    def is_valid_code_format(self) -> bool:
        """
        Validate syllabus code format

        Code should follow pattern: {subject_code}.{section}.{subsection}
        Example: "9708.1.1" for Economics section 1 subsection 1

        Returns:
            bool: True if code matches expected format
        """
        parts = self.code.split(".")
        # Check: at least 2 parts, all parts non-empty, all parts alphanumeric
        return (
            len(parts) >= 2
            and all(len(part) > 0 for part in parts)
            and all(part.isdigit() or part.isalpha() for part in parts)
        )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<SyllabusPoint(code={self.code}, description={self.description[:50]}...)>"
