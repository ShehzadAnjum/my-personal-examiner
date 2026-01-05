"""
GeneratedExplanation Model

Stores all generated topic explanations as shared resources.

Feature: 006-resource-bank
Constitutional Requirements:
- Content must be Cambridge-accurate - Principle I
- Versioned content: v1=admin (system), v2+=student-generated
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Enum, Index, JSON
from sqlmodel import Field, SQLModel

from src.models.enums import GeneratedByType, LLMProvider


class GeneratedExplanation(SQLModel, table=True):
    """
    GeneratedExplanation entity

    Stores all generated topic explanations as shared resources.
    v1 = admin-generated (system), v2+ = student-generated with their API keys.

    Attributes:
        id: Unique identifier
        syllabus_point_id: Links to syllabus topic
        version: Version number (1 = admin, 2+ = student)
        content: TopicExplanation schema content (JSON)
        generated_by: 'system' or 'student'
        generator_student_id: NULL for v1, set for v2+
        llm_provider: Provider used for generation
        llm_model: Model identifier used
        token_cost: Tokens consumed for generation
        quality_rating: Optional curation rating (0.0-5.0)
        signature: SHA-256 hash for sync
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Constitutional Compliance:
        - Principle I: Content must match Cambridge syllabus
        - Principle V: generator_student_id enables multi-tenant tracking
    """

    __tablename__ = "generated_explanations"
    __table_args__ = (
        # Unique constraint: one explanation per (syllabus_point_id, version)
        Index(
            "idx_explanation_syllabus_version",
            "syllabus_point_id",
            "version",
            unique=True,
        ),
        # Index for finding student-generated content
        Index(
            "idx_explanation_generator",
            "generator_student_id",
            postgresql_where="generator_student_id IS NOT NULL",
        ),
        # Index for sync signature lookups
        Index("idx_explanation_signature", "signature"),
        # Constraints
        CheckConstraint("version >= 1", name="ck_explanation_version_positive"),
        CheckConstraint(
            "quality_rating IS NULL OR (quality_rating >= 0 AND quality_rating <= 5)",
            name="ck_explanation_quality_rating_range",
        ),
        CheckConstraint(
            "(generated_by = 'system' AND generator_student_id IS NULL) OR "
            "(generated_by = 'student' AND generator_student_id IS NOT NULL)",
            name="ck_explanation_generator_consistency",
        ),
    )

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to SyllabusPoint
    syllabus_point_id: UUID = Field(
        foreign_key="syllabus_points.id",
        nullable=False,
        index=True,
        description="Links to syllabus topic",
    )

    # Version Control
    version: int = Field(
        default=1,
        nullable=False,
        description="Version number (1 = admin, 2+ = student)",
    )

    # Content (JSON)
    content: dict = Field(
        sa_column=Column(JSON, nullable=False),
        description="TopicExplanation schema content",
    )

    # Generation Metadata
    generated_by: GeneratedByType = Field(
        sa_column=Column(
            Enum(GeneratedByType, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
        description="'system' for v1, 'student' for v2+",
    )

    generator_student_id: Optional[UUID] = Field(
        default=None,
        foreign_key="students.id",
        nullable=True,
        description="NULL for v1, set for v2+",
    )

    llm_provider: LLMProvider = Field(
        sa_column=Column(
            Enum(LLMProvider, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
        description="Provider used for generation",
    )

    llm_model: str = Field(
        nullable=False,
        max_length=100,
        description="Model identifier used (e.g., 'claude-sonnet-4-20250514')",
    )

    token_cost: int = Field(
        default=0,
        nullable=False,
        description="Tokens consumed for generation",
    )

    quality_rating: Optional[float] = Field(
        default=None,
        nullable=True,
        description="Optional curation rating (0.0-5.0)",
    )

    # Sync
    signature: str = Field(
        nullable=False,
        max_length=64,
        description="SHA-256 hash for sync",
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

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<GeneratedExplanation(id={self.id}, "
            f"syllabus_point_id={self.syllabus_point_id}, "
            f"version={self.version}, generated_by={self.generated_by})>"
        )
