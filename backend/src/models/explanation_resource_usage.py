"""
ExplanationResourceUsage tracking table.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Tracks which resources contributed to each generated explanation
- Enables analytics on resource usage effectiveness
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class ExplanationResourceUsage(SQLModel, table=True):
    """
    Tracks resource usage in topic explanation generation.

    Records which resources (syllabus, past papers, textbooks) contributed
    to each generated explanation and their relative contribution weight.

    Composite primary key: (explanation_id, resource_id)
    """

    __tablename__ = "explanation_resource_usage"

    explanation_id: UUID = Field(
        foreign_key="generated_explanations.id",
        primary_key=True,
        description="Explanation ID (from Feature 006)",
    )

    resource_id: UUID = Field(
        foreign_key="resources.id", primary_key=True, description="Resource ID"
    )

    contribution_weight: float = Field(
        ge=0.0,
        le=1.0,
        nullable=False,
        description="How much this resource influenced explanation (0-1)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("NOW()")},
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


    def get_contribution_percentage(self) -> float:
        """Return contribution as percentage (0-100)."""
        return self.contribution_weight * 100
