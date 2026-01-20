"""
EmbeddingJob Model

Tracks bulk embedding generation jobs for syllabus topics.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Compliance:
- Principle V: Multi-tenant isolation via subject_id scope
- Principle III: Embeddings regenerated when syllabus updated
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlmodel import Field, SQLModel


class EmbeddingJobStatus(str, Enum):
    """Status of an embedding generation job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some embeddings failed


class EmbeddingJobType(str, Enum):
    """Type of embedding job."""
    SYLLABUS = "syllabus"  # Generate embeddings for syllabus topics
    RESOURCE = "resource"  # Generate embeddings for resources
    BULK_REGENERATE = "bulk_regenerate"  # Regenerate existing embeddings
    SINGLE = "single"  # Single topic regeneration


class EmbeddingJob(SQLModel, table=True):
    """
    Tracks bulk embedding generation jobs.

    Used to monitor progress of embedding generation after syllabus extraction
    or bulk regeneration operations. Supports retry for failed items.

    State Machine: pending → in_progress → completed | failed | partial

    Attributes:
        id: Unique job identifier
        subject_id: Subject being embedded (for scoping)
        status: Current job status
        job_type: Type of embedding operation
        total_items: Total items to embed
        completed_items: Successfully embedded count
        failed_items: Failed embedding count
        started_at: Job start time
        completed_at: Job completion time
        error_message: Error details if failed
        failed_item_ids: IDs of failed items for retry
        created_at: Job creation time
        created_by: User who triggered job

    Example:
        >>> job = EmbeddingJob(
        ...     subject_id=economics_subject_id,
        ...     job_type=EmbeddingJobType.SYLLABUS,
        ...     total_items=60,
        ... )
        >>> job.status  # EmbeddingJobStatus.PENDING
    """

    __tablename__ = "embedding_jobs"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Subject Scope (Multi-tenant isolation)
    subject_id: UUID = Field(
        foreign_key="subjects.id",
        nullable=False,
        index=True,
        description="Subject being embedded",
    )

    # Job Status
    status: EmbeddingJobStatus = Field(
        default=EmbeddingJobStatus.PENDING,
        nullable=False,
        description="Job status: pending, in_progress, completed, failed, partial",
    )

    job_type: EmbeddingJobType = Field(
        nullable=False,
        description="Type: syllabus, resource, bulk_regenerate, single",
    )

    # Progress Tracking
    total_items: int = Field(
        default=0,
        nullable=False,
        description="Total items to embed",
    )

    completed_items: int = Field(
        default=0,
        nullable=False,
        description="Successfully embedded count",
    )

    failed_items: int = Field(
        default=0,
        nullable=False,
        description="Failed embedding count",
    )

    # Timing
    started_at: Optional[datetime] = Field(
        default=None,
        description="Job start time",
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Job completion time",
    )

    # Error Tracking
    error_message: Optional[str] = Field(
        default=None,
        description="Error details if failed",
    )

    failed_item_ids: Optional[List[UUID]] = Field(
        default=None,
        sa_column=Column(ARRAY(PGUUID(as_uuid=True)), nullable=True),
        description="IDs of failed items for retry",
    )

    # Audit
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("NOW()")},
        description="Job creation time",
    )

    created_by: Optional[UUID] = Field(
        default=None,
        foreign_key="students.id",
        description="User who triggered job",
    )

    def start(self) -> None:
        """Mark job as started."""
        self.status = EmbeddingJobStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark job as completed."""
        self.completed_at = datetime.utcnow()
        if self.failed_items > 0:
            self.status = EmbeddingJobStatus.PARTIAL
        else:
            self.status = EmbeddingJobStatus.COMPLETED

    def fail(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = EmbeddingJobStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()

    def record_success(self) -> None:
        """Record successful embedding of one item."""
        self.completed_items += 1

    def record_failure(self, item_id: UUID) -> None:
        """Record failed embedding of one item."""
        self.failed_items += 1
        if self.failed_item_ids is None:
            self.failed_item_ids = []
        self.failed_item_ids.append(item_id)

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items + self.failed_items) / self.total_items * 100

    @property
    def is_complete(self) -> bool:
        """Check if job is finished (success or failure)."""
        return self.status in (
            EmbeddingJobStatus.COMPLETED,
            EmbeddingJobStatus.FAILED,
            EmbeddingJobStatus.PARTIAL,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<EmbeddingJob(id={self.id}, status={self.status.value}, "
            f"progress={self.completed_items}/{self.total_items})>"
        )
