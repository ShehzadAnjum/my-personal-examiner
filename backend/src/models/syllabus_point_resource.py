"""
SyllabusPointResource link table for resource-to-syllabus mapping.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Principle I: Links resources to specific syllabus learning outcomes
- Relevance scores enable auto-selection of best resources per topic
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field, SQLModel

from src.models.enums import AddedBy


class SyllabusPointResource(SQLModel, table=True):
    """
    Links resources to specific syllabus points with relevance scoring.

    Enables auto-selection of most relevant resources for topic generation
    based on manually tagged or system-detected relevance scores.

    Composite primary key: (syllabus_point_id, resource_id)
    """

    __tablename__ = "syllabus_point_resources"

    syllabus_point_id: UUID = Field(
        foreign_key="syllabus_points.id",
        primary_key=True,
        description="Syllabus learning outcome ID (e.g., 9708.5.1)",
    )

    resource_id: UUID = Field(
        foreign_key="resources.id", primary_key=True, description="Resource ID"
    )

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        nullable=False,
        index=True,
        description="Relevance 0-1 (1.0 = perfect match for auto-selection)",
    )

    added_by: AddedBy = Field(
        nullable=False,
        index=True,
        description="Who created link: system (auto), admin (manual tagging), student (preference)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("NOW()")},
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
