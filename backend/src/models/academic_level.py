"""
AcademicLevel Model

Represents a qualification type (A-Level, O-Level, IGCSE, IB, etc.)
Top level of the three-tier hierarchy: Academic Level → Subject → Syllabus

Constitutional Requirements:
- Principle I: Subject Accuracy - enables proper Cambridge structure mapping
- Principle III: Syllabus Sync - exam_board tracks qualification source

Feature: 008-academic-level-hierarchy
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .subject import Subject


class AcademicLevel(SQLModel, table=True):
    """
    AcademicLevel entity

    Represents a qualification type such as A-Level, O-Level, IGCSE, or IB.
    This is the top level of the content hierarchy.

    Attributes:
        id: Unique identifier (UUID primary key)
        name: Display name (e.g., "A-Level", "IGCSE")
        code: Short unique code (e.g., "A", "O", "IGCSE")
        description: Optional description of the qualification
        exam_board: Exam board name (default: "Cambridge International")
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Examples:
        >>> a_level = AcademicLevel(
        ...     name="A-Level",
        ...     code="A",
        ...     description="Cambridge International A-Level",
        ...     exam_board="Cambridge International"
        ... )

    Constitutional Compliance:
        - Principle I: Enables accurate mapping to qualification structures
        - Principle III: exam_board tracks qualification source for sync
    """

    __tablename__ = "academic_levels"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Academic Level Identification
    name: str = Field(
        nullable=False,
        max_length=100,
        description="Display name (e.g., 'A-Level')",
    )

    code: str = Field(
        nullable=False,
        unique=True,
        index=True,
        max_length=10,
        description="Short unique code (e.g., 'A', 'O', 'IGCSE')",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the qualification",
    )

    exam_board: str = Field(
        default="Cambridge International",
        nullable=False,
        max_length=100,
        description="Exam board name",
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
    subjects: list["Subject"] = Relationship(back_populates="academic_level")

    # Validation methods
    def is_valid_code(self) -> bool:
        """
        Validate academic level code format.

        Code must be alphanumeric, 1-10 characters.

        Returns:
            bool: True if code is valid
        """
        return (
            self.code is not None
            and 1 <= len(self.code) <= 10
            and self.code.replace("-", "").replace("_", "").isalnum()
        )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<AcademicLevel(code={self.code}, name={self.name}, exam_board={self.exam_board})>"


# Default Academic Levels (Cambridge-focused but extensible)
DEFAULT_ACADEMIC_LEVELS = [
    {
        "name": "A-Level",
        "code": "A",
        "description": "Cambridge International A-Level (Advanced Level)",
        "exam_board": "Cambridge International",
    },
    {
        "name": "AS-Level",
        "code": "AS",
        "description": "Cambridge International AS-Level (Advanced Subsidiary)",
        "exam_board": "Cambridge International",
    },
    {
        "name": "O-Level",
        "code": "O",
        "description": "Cambridge International O-Level (Ordinary Level)",
        "exam_board": "Cambridge International",
    },
    {
        "name": "IGCSE",
        "code": "IGCSE",
        "description": "Cambridge International General Certificate of Secondary Education",
        "exam_board": "Cambridge International",
    },
]
