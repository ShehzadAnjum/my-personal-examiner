"""
Resource model for Resource Bank file storage.

Feature: 007-resource-bank-files
Created: 2025-12-27

Constitutional Compliance:
- Principle I: Signature field ensures content integrity (SHA-256)
- Principle V: Multi-tenant isolation via visibility + uploaded_by_student_id
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Computed, Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlmodel import Field, SQLModel

from src.models.enums import ResourceType, S3SyncStatus, Visibility


class Resource(SQLModel, table=True):
    """
    Central entity for all learning materials in the Resource Bank.

    Stores official Cambridge resources (syllabus, past papers),
    textbooks, YouTube videos, and user uploads with multi-tenant isolation.

    State Machine: uploaded → pending_review → approved OR rejected
    """

    __tablename__ = "resources"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Resource Classification
    resource_type: ResourceType = Field(
        sa_column=Column(
            SQLEnum(ResourceType, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            index=True,
        ),
        description="Type: syllabus, textbook, past_paper, video, article, user_upload",
    )

    title: str = Field(max_length=500, nullable=False, index=True)

    source_url: Optional[str] = Field(
        default=None, max_length=2000, description="Original source URL (Cambridge, YouTube, etc.)"
    )

    file_path: str = Field(
        max_length=1000, nullable=False, description="Local file path: backend/resources/..."
    )

    # Multi-Tenant Isolation
    uploaded_by_student_id: Optional[UUID] = Field(
        default=None,
        foreign_key="students.id",
        index=True,
        description="Student who uploaded (NULL for official resources)",
    )

    admin_approved: bool = Field(
        default=False, nullable=False, description="Approval status (user uploads only)"
    )

    visibility: Visibility = Field(
        default=Visibility.PENDING_REVIEW,
        sa_column=Column(
            SQLEnum(Visibility, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            index=True,
            server_default="pending_review",
        ),
        description="Access control: public, private, pending_review",
    )

    # Flexible Metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    resource_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="{}"),
        description="Type-specific fields: page_range, chapter, video_duration, etc.",
    )

    # Content Integrity & Deduplication
    signature: str = Field(
        max_length=64,
        nullable=False,
        unique=True,
        index=True,
        description="SHA-256 hash for duplicate detection and integrity",
    )

    # S3 Background Upload Tracking
    s3_url: Optional[str] = Field(
        default=None, max_length=2000, description="S3 object URL after background upload"
    )

    s3_sync_status: S3SyncStatus = Field(
        default=S3SyncStatus.PENDING,
        sa_column=Column(
            SQLEnum(S3SyncStatus, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            index=True,
            server_default="pending",
        ),
        description="Upload status: pending, success, failed, pending_retry",
    )

    last_synced_at: Optional[datetime] = Field(
        default=None, description="Last successful S3 upload timestamp"
    )

    # Full-Text Search
    extracted_text: Optional[str] = Field(
        default=None, description="Text from PDF parsing or OCR"
    )

    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "search_vector",
            TSVECTOR,
            Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, ''))"),
        ),
        description="Computed full-text search vector (PostgreSQL tsvector)",
    )

    # Timestamps
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


    def is_public(self) -> bool:
        """Check if resource is publicly visible."""
        return self.visibility == Visibility.PUBLIC

    def is_owned_by(self, student_id: UUID) -> bool:
        """Check if resource is owned by given student."""
        return self.uploaded_by_student_id == student_id

    def can_be_accessed_by(self, student_id: Optional[UUID], is_admin: bool = False) -> bool:
        """
        Check if student can access this resource.

        Multi-tenant isolation rules:
        - Public: Visible to all
        - Private: Only uploader + admin
        - Pending Review: Only uploader + admin
        """
        if is_admin:
            return True

        if self.visibility == Visibility.PUBLIC:
            return True

        if student_id and self.uploaded_by_student_id == student_id:
            return True

        return False
