"""
Syllabus Model

Represents a specific syllabus version for a subject (e.g., 9708 for 2023-2025).
Third level of the hierarchy: Academic Level → Subject → Syllabus

Constitutional Requirements:
- Principle I: Subject Accuracy - syllabus code maps to official Cambridge codes
- Principle III: Syllabus Sync - year_range tracks valid syllabus period

Feature: 008-academic-level-hierarchy
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .subject import Subject
    from .syllabus_point import SyllabusPoint


class Syllabus(SQLModel, table=True):
    """
    Syllabus entity

    Represents a specific syllabus version for a subject.
    Contains the syllabus code (e.g., "9708") and year range (e.g., "2023-2025").

    Attributes:
        id: Unique identifier (UUID primary key)
        subject_id: Foreign key to parent Subject
        code: Syllabus code (e.g., "9708" for Economics)
        year_range: Valid years for this syllabus (e.g., "2023-2025")
        version: Version number for multiple syllabus versions
        is_active: Whether this is the currently active syllabus
        syllabus_resource_id: Optional link to uploaded syllabus PDF
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Examples:
        >>> syllabus = Syllabus(
        ...     subject_id=economics_subject_id,
        ...     code="9708",
        ...     year_range="2023-2025",
        ...     version=1,
        ...     is_active=True
        ... )

    Constitutional Compliance:
        - Principle I: code maps to official Cambridge syllabus codes
        - Principle III: year_range enables syllabus version tracking
    """

    __tablename__ = "syllabi"

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

    # Syllabus Identification
    code: str = Field(
        nullable=False,
        index=True,
        max_length=20,
        description="Syllabus code (e.g., '9708')",
    )

    year_range: str = Field(
        nullable=False,
        max_length=20,
        description="Valid years (e.g., '2023-2025')",
    )

    version: int = Field(
        default=1,
        nullable=False,
        description="Version number",
    )

    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Whether this is the currently active syllabus",
    )

    # Link to uploaded syllabus PDF resource
    syllabus_resource_id: UUID | None = Field(
        default=None,
        nullable=True,
        foreign_key="resources.id",
        description="Reference to uploaded syllabus PDF resource",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )

    # Relationships
    subject: "Subject" = Relationship(back_populates="syllabi")
    syllabus_points: list["SyllabusPoint"] = Relationship(back_populates="syllabus")

    # Validation methods
    def is_valid_code(self) -> bool:
        """
        Validate syllabus code format.

        Code must be alphanumeric, 1-20 characters.

        Returns:
            bool: True if code is valid
        """
        return (
            self.code is not None
            and 1 <= len(self.code) <= 20
            and self.code.isalnum()
        )

    def is_valid_year_range(self) -> bool:
        """
        Validate year range format.

        Year range should match pattern like "2023-2025".

        Returns:
            bool: True if year_range is valid
        """
        if not self.year_range:
            return False
        parts = self.year_range.split("-")
        if len(parts) != 2:
            return False
        return all(part.isdigit() and len(part) == 4 for part in parts)

    def get_display_name(self) -> str:
        """
        Get display name for the syllabus.

        Returns:
            str: Display name like "9708 (2023-2025)"
        """
        return f"{self.code} ({self.year_range})"

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Syllabus(code={self.code}, year_range={self.year_range}, active={self.is_active})>"
