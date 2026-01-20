"""
StudentLearningPath Model

Tracks per-student learning progress for each topic.

Feature: 006-resource-bank
Constitutional Requirements:
- Multi-tenant isolation: All queries MUST filter by student_id - Principle V
- Learning progress tracking for adaptive learning
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel

from src.models.enums import MasteryLevel


class StudentLearningPath(SQLModel, table=True):
    """
    StudentLearningPath entity

    Tracks per-student learning progress for each topic.
    Enables adaptive learning recommendations and bookmarking.

    Attributes:
        id: Unique identifier
        student_id: Multi-tenant isolation key
        syllabus_point_id: Topic being tracked
        explanation_id: Current preferred explanation version
        view_count: Times topic viewed
        total_time_spent_seconds: Accumulated reading time
        last_viewed_at: Last view timestamp
        preferred_version: Which version student prefers
        is_bookmarked: Personal bookmark flag
        mastery_level: Learning progress enum
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Mastery Level Transitions:
        - not_started -> learning: First view
        - learning -> familiar: view_count >= 3 OR time >= 600s
        - familiar -> mastered: Manual mark OR exam performance > 80%

    Constitutional Compliance:
        - Principle V: ALWAYS filter queries by student_id
    """

    __tablename__ = "student_learning_paths"
    __table_args__ = (
        # Unique constraint: one record per (student_id, syllabus_point_id)
        Index(
            "idx_learningpath_student_syllabus",
            "student_id",
            "syllabus_point_id",
            unique=True,
        ),
        # Index for bookmarked topics per student
        Index(
            "idx_learningpath_student_bookmarked",
            "student_id",
            postgresql_where="is_bookmarked = true",
        ),
        # Index for mastery level filtering
        Index(
            "idx_learningpath_student_mastery",
            "student_id",
            "mastery_level",
        ),
        # Constraints
        CheckConstraint("view_count >= 0", name="ck_learningpath_view_count_positive"),
        CheckConstraint(
            "total_time_spent_seconds >= 0",
            name="ck_learningpath_time_spent_positive",
        ),
        CheckConstraint(
            "preferred_version >= 1",
            name="ck_learningpath_preferred_version_positive",
        ),
    )

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Multi-Tenant Isolation Key (CRITICAL)
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True,
        description="Multi-tenant isolation key - ALL queries MUST filter by this",
    )

    # Topic Reference
    syllabus_point_id: UUID = Field(
        foreign_key="syllabus_points.id",
        nullable=False,
        index=True,
        description="Topic being tracked",
    )

    # Preferred Explanation Version
    explanation_id: Optional[UUID] = Field(
        default=None,
        foreign_key="generated_explanations.id",
        nullable=True,
        description="Current preferred explanation version",
    )

    # Progress Tracking
    view_count: int = Field(
        default=0,
        nullable=False,
        description="Times topic viewed",
    )

    total_time_spent_seconds: int = Field(
        default=0,
        nullable=False,
        description="Accumulated reading time in seconds",
    )

    last_viewed_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Last view timestamp",
    )

    preferred_version: int = Field(
        default=1,
        nullable=False,
        description="Which explanation version student prefers",
    )

    is_bookmarked: bool = Field(
        default=False,
        nullable=False,
        description="Personal bookmark flag",
    )

    mastery_level: MasteryLevel = Field(
        default=MasteryLevel.NOT_STARTED,
        nullable=False,
        description="Learning progress level",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Record creation timestamp",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )

    def track_view(self) -> None:
        """
        Record a topic view and update mastery level if needed.

        Auto-transitions:
        - not_started -> learning (first view)
        - learning -> familiar (view_count >= 3)
        """
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Auto-transition mastery level
        if self.mastery_level == MasteryLevel.NOT_STARTED:
            self.mastery_level = MasteryLevel.LEARNING
        elif self.mastery_level == MasteryLevel.LEARNING and self.view_count >= 3:
            self.mastery_level = MasteryLevel.FAMILIAR

    def track_time(self, seconds: int) -> None:
        """
        Add time spent on topic and update mastery level if needed.

        Args:
            seconds: Time spent in seconds to add

        Auto-transitions:
        - learning -> familiar (total_time >= 600 seconds / 10 minutes)
        """
        if seconds > 0:
            self.total_time_spent_seconds += seconds
            self.updated_at = datetime.utcnow()

            # Auto-transition based on time
            if (
                self.mastery_level == MasteryLevel.LEARNING
                and self.total_time_spent_seconds >= 600
            ):
                self.mastery_level = MasteryLevel.FAMILIAR

    def toggle_bookmark(self) -> bool:
        """
        Toggle bookmark status.

        Returns:
            bool: New bookmark status
        """
        self.is_bookmarked = not self.is_bookmarked
        self.updated_at = datetime.utcnow()
        return self.is_bookmarked

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<StudentLearningPath(student_id={self.student_id}, "
            f"syllabus_point_id={self.syllabus_point_id}, "
            f"mastery={self.mastery_level}, views={self.view_count})>"
        )
