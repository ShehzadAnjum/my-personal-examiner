"""
SyllabusPoint Model

Represents specific learning objectives or topics within a syllabus.
Supports hierarchical structure: Section → Chapter → Subtopic → Heading

Part of the three-tier hierarchy: Academic Level → Subject → Syllabus → Syllabus Point

Feature: 008-academic-level-hierarchy, 008-syllabus-agents-sdk, 010-embedding-integration

Constitutional Requirements:
- Must map to Cambridge International syllabus structure - Principle I
- Syllabus synchronization required monthly - Principle III
- Embeddings scoped to subject/syllabus for multi-tenant isolation - Principle V
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.syllabus import Syllabus


class UnitType(str, Enum):
    """Hierarchy level for syllabus points."""
    SECTION = "section"      # Top level (e.g., "1. Basic economic ideas")
    CHAPTER = "chapter"      # Was "topic" (e.g., "1.1 Scarcity, choice and opportunity cost")
    SUBTOPIC = "subtopic"    # Detailed breakdown (e.g., "1.1.1 The nature of the economic problem")
    HEADING = "heading"      # Finest granularity
    TOPIC = "topic"          # Legacy - for backward compatibility


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

    # Level and Section (NEW - 008-academic-level-hierarchy)
    level: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Level: 'AS' (AS Level only) or 'A' (A Level only)",
    )

    section_title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Parent section/chapter title (e.g., 'Basic economic ideas and resource allocation')",
    )

    # Hierarchy support (NEW - 008-syllabus-agents-sdk)
    parent_id: Optional[UUID] = Field(
        default=None,
        foreign_key="syllabus_points.id",
        index=True,
        description="Parent syllabus point ID for hierarchy (null = root/section level)",
    )

    unit_type: str = Field(
        default="topic",
        max_length=20,
        description="Hierarchy level: section, chapter, subtopic, heading, topic (legacy)",
    )

    order_index: int = Field(
        default=0,
        description="Order within parent (0-indexed)",
    )

    definition: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Brief definition extracted from syllabus PDF",
    )

    # Embedding fields (Feature 010-embedding-integration)
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(ARRAY(Float), nullable=True),
        description="768-dimension vector embedding for semantic search",
    )
    embedding_model: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Model used to generate embedding (e.g., 'gemini/text-embedding-004')",
    )
    embedded_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when embedding was generated",
    )

    # Self-referential relationships for hierarchy
    parent: Optional["SyllabusPoint"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "SyllabusPoint.id"},
    )
    children: list["SyllabusPoint"] = Relationship(back_populates="parent")

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

    def get_embedding_text(self) -> str:
        """
        Combine fields for embedding generation.

        Returns combined text from code, description, topics, and learning outcomes
        to create a rich semantic representation for embedding.

        Returns:
            str: Combined text suitable for embedding generation
        """
        parts = [self.code, self.description]
        if self.topics:
            parts.append(self.topics)
        if self.learning_outcomes:
            parts.append(self.learning_outcomes)
        if self.definition:
            parts.append(self.definition)
        return " | ".join(parts)
