"""
SyllabusPoint Model

Represents specific learning objectives or topics within a syllabus.
Part of the three-tier hierarchy: Academic Level → Subject → Syllabus → Syllabus Point

Feature: 008-academic-level-hierarchy

Constitutional Requirements:
- Must map to Cambridge International syllabus structure - Principle I
- Syllabus synchronization required monthly - Principle III
"""

from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.syllabus import Syllabus


class SyllabusPoint(SQLModel, table=True):
    """
    SyllabusPoint entity

    Represents a specific learning objective or topic within a syllabus.
    This is a global entity - not scoped to individual students.

    Three-Tier Hierarchy:
        Academic Level → Subject → Syllabus → Syllabus Point

    Attributes:
        id: Unique syllabus point identifier (UUID primary key)
        syllabus_id: Foreign key to parent syllabus (NEW)
        subject_id: Foreign key to parent subject (DEPRECATED - kept for backward compatibility)
        code: Syllabus code (e.g., "1.1" = section 1 subsection 1)
        description: Learning objective description
        topics: Comma-separated topics covered (optional)
        learning_outcomes: Expected learning outcomes (optional)

    Relationships:
        syllabus: Parent Syllabus entity

    Examples:
        >>> syllabus_point = SyllabusPoint(
        ...     syllabus_id=economics_9708_syllabus_id,
        ...     code="1.1",
        ...     description="The central economic problem",
        ...     topics="Scarcity, Choice, Opportunity cost",
        ...     learning_outcomes="Understand the nature of the economic problem"
        ... )

    Constitutional Compliance:
        - Principle I: Must match Cambridge International syllabus exactly
        - Principle III: Syllabus version tracked via parent Syllabus.year_range
        - FR-017: Code follows pattern {section}.{subsection}
    """

    __tablename__ = "syllabus_points"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to Syllabus (NEW - 008-academic-level-hierarchy)
    syllabus_id: UUID = Field(
        foreign_key="syllabi.id",
        nullable=False,
        index=True,
        description="Parent syllabus ID",
    )

    # Foreign Key to Subject (DEPRECATED - kept for backward compatibility during transition)
    # TODO: Remove in future migration after all code paths use syllabus_id
    subject_id: UUID = Field(
        foreign_key="subjects.id",
        nullable=False,
        index=True,
        description="Parent subject ID (DEPRECATED - use syllabus_id instead)",
    )

    # Relationship to Syllabus (NEW - 008-academic-level-hierarchy)
    syllabus: "Syllabus" = Relationship(back_populates="syllabus_points")

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
