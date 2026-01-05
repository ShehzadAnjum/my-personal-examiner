"""
StudentResourcePreference table for personalized resource settings.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Principle V: Multi-tenant isolation (student-specific preferences)
- Enables personalized learning paths by controlling resource usage
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class StudentResourcePreference(SQLModel, table=True):
    """
    User-specific resource preferences for personalized learning.

    Allows students to enable/disable specific resources and set priority
    for resource selection during topic generation and study plans.

    Composite primary key: (student_id, resource_id)
    """

    __tablename__ = "student_resource_preferences"

    student_id: UUID = Field(
        foreign_key="students.id",
        primary_key=True,
        index=True,
        description="Student ID",
    )

    resource_id: UUID = Field(
        foreign_key="resources.id", primary_key=True, description="Resource ID"
    )

    enabled: bool = Field(
        default=True,
        nullable=False,
        description="Whether student wants to use this resource",
    )

    priority: int = Field(
        default=0,
        nullable=False,
        index=True,
        description="Ordering preference (higher = more important)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("NOW()")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("NOW()")},
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


    def is_active(self) -> bool:
        """Check if this preference is active."""
        return self.enabled
