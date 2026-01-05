"""
Subject Model

Represents subjects available for study within an academic level.
Part of the three-tier hierarchy: Academic Level → Subject → Syllabus

Feature: 008-academic-level-hierarchy

Constitutional Requirements:
- Subject data must match current Cambridge syllabi - Principle I
- Syllabus synchronization required monthly - Principle III

Admin Setup Flow:
- setup_status tracks admin setup wizard progress
- Syllabus PDF linking now on Syllabus model (not Subject)
"""

from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.academic_level import AcademicLevel
    from src.models.syllabus import Syllabus


class SubjectSetupStatus(str, Enum):
    """
    Admin setup wizard status for a subject.

    Flow: pending → syllabus_uploaded → topics_generated → explanations_generated → complete
    """

    PENDING = "pending"  # Initial state, no syllabus uploaded
    SYLLABUS_UPLOADED = "syllabus_uploaded"  # Syllabus PDF uploaded, awaiting topic extraction
    TOPICS_GENERATED = "topics_generated"  # Topics extracted and confirmed by admin
    EXPLANATIONS_GENERATED = "explanations_generated"  # v1 explanations generated
    COMPLETE = "complete"  # Setup complete, ready for students


class Subject(SQLModel, table=True):
    """
    Subject entity

    Represents a subject within an academic level (e.g., "Economics" under "A-Level").
    This is a global entity - not scoped to individual students.

    Three-Tier Hierarchy:
        Academic Level → Subject → Syllabus → Syllabus Point

    Attributes:
        id: Unique subject identifier (UUID primary key)
        academic_level_id: Foreign key to parent academic level
        name: Subject name (e.g., "Economics")
        setup_status: Admin setup wizard progress

    Relationships:
        academic_level: Parent AcademicLevel entity
        syllabi: Child Syllabus entities

    Examples:
        >>> economics = Subject(
        ...     academic_level_id=a_level_id,
        ...     name="Economics",
        ... )

    Constitutional Compliance:
        - Principle I: All subject content must match Cambridge syllabi
        - Principle III: Syllabus versions tracked via Syllabus.year_range
    """

    __tablename__ = "subjects"
    __table_args__ = {"extend_existing": True}

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to Academic Level (NEW - 008-academic-level-hierarchy)
    academic_level_id: UUID = Field(
        foreign_key="academic_levels.id",
        nullable=False,
        index=True,
        description="Parent academic level ID (e.g., A-Level, IGCSE)",
    )

    # Subject Identification
    name: str = Field(
        nullable=False,
        max_length=100,
        description="Subject name (e.g., 'Economics')",
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

    # Admin Setup Flow
    setup_status: str = Field(
        default=SubjectSetupStatus.PENDING.value,
        nullable=False,
        max_length=50,
        description="Admin setup wizard status: pending → syllabus_uploaded → topics_generated → explanations_generated → complete",
    )

    # Relationships (NEW - 008-academic-level-hierarchy)
    academic_level: "AcademicLevel" = Relationship(back_populates="subjects")
    syllabi: list["Syllabus"] = Relationship(back_populates="subject")

    def is_setup_complete(self) -> bool:
        """
        Check if admin setup is complete for this subject.

        Returns:
            bool: True if setup_status is 'complete'
        """
        return self.setup_status == SubjectSetupStatus.COMPLETE.value

    def requires_syllabus(self) -> bool:
        """
        Check if syllabus upload is required before proceeding.

        Returns:
            bool: True if setup_status is 'pending'
        """
        return self.setup_status == SubjectSetupStatus.PENDING.value

    def can_generate_topics(self) -> bool:
        """
        Check if topics can be generated (syllabus uploaded).

        Returns:
            bool: True if syllabus has been uploaded
        """
        return self.setup_status in (
            SubjectSetupStatus.SYLLABUS_UPLOADED.value,
            SubjectSetupStatus.TOPICS_GENERATED.value,
            SubjectSetupStatus.EXPLANATIONS_GENERATED.value,
            SubjectSetupStatus.COMPLETE.value,
        )

    def can_generate_explanations(self) -> bool:
        """
        Check if explanations can be generated (topics exist).

        Returns:
            bool: True if topics have been generated
        """
        return self.setup_status in (
            SubjectSetupStatus.TOPICS_GENERATED.value,
            SubjectSetupStatus.EXPLANATIONS_GENERATED.value,
            SubjectSetupStatus.COMPLETE.value,
        )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Subject(name={self.name}, academic_level_id={self.academic_level_id}, setup={self.setup_status})>"
