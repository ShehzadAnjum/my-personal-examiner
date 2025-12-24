"""
SavedExplanation Model

Represents a student's bookmarked/favorited syllabus topic.
Multi-tenant entity (scoped to individual students) - each student sees only their own bookmarks.

Feature: 005-teaching-page (User Story 3 - Bookmark Explanations)

Architecture: Pointer-based bookmarks
- Stores ONLY reference to syllabus_point_id (no explanation content duplication)
- Explanation content cached in browser localStorage
- If localStorage cleared, user can regenerate explanation on-demand

Constitutional Requirements:
- Multi-tenant isolation required - Principle V
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class SavedExplanation(SQLModel, table=True):
    """
    SavedExplanation entity (Pointer-based bookmark)

    Represents a bookmarked syllabus topic that a student has favorited for quick access.
    This is a multi-tenant entity - each student can only access their own bookmarks.

    Architecture:
        - Stores ONLY a reference to syllabus_point_id (no content duplication)
        - Explanation content is cached in browser localStorage
        - If cache missing, user can regenerate explanation on-demand

    Attributes:
        id: Unique bookmark identifier (UUID primary key)
        student_id: Foreign key to student who bookmarked this topic
        syllabus_point_id: Foreign key to syllabus topic (pointer only, no content)
        date_saved: When student bookmarked this topic
        date_last_viewed: Last time student accessed this bookmark (nullable)

    Examples:
        >>> saved = SavedExplanation(
        ...     student_id=student_uuid,
        ...     syllabus_point_id=ped_topic_uuid,
        ... )

    Constitutional Compliance:
        - Principle V: student_id foreign key enforces multi-tenant isolation
        - FR-012: Unique constraint prevents duplicate bookmarks per student+topic
    """

    __tablename__ = "saved_explanations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to Student (Multi-tenant isolation)
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True,
        description="Student who saved this explanation (multi-tenant)",
    )

    # Foreign Key to SyllabusPoint
    syllabus_point_id: UUID = Field(
        foreign_key="syllabus_points.id",
        nullable=False,
        index=True,
        description="Syllabus topic bookmark reference (pointer only, no content stored)",
    )

    # Timestamps
    date_saved: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When student bookmarked this explanation",
    )

    date_last_viewed: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Last time student opened this saved explanation",
    )

    # Table-level Constraints
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "syllabus_point_id",
            name="uq_saved_explanation_student_topic",
        ),
    )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<SavedExplanation(student={self.student_id}, topic={self.syllabus_point_id})>"
