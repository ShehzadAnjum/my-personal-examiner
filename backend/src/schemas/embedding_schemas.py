"""
Embedding Schemas

Pydantic schemas for Embedding API endpoints.
Supports embedding generation, semantic search, and content alignment.

Feature: 010-embedding-integration
Created: 2026-01-21

Constitutional Compliance:
- Principle V: Multi-tenant isolation via subject_id
- Principle XVI: Token conservation via cached embeddings
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EmbeddingJobStatus(str, Enum):
    """Status of an embedding generation job."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class EmbeddingJobType(str, Enum):
    """Type of embedding job."""

    SYLLABUS = "syllabus"
    RESOURCE = "resource"
    BULK_REGENERATE = "bulk_regenerate"
    SINGLE = "single"


# =============================================================================
# Request Schemas
# =============================================================================


class GenerateEmbeddingsRequest(BaseModel):
    """Request schema for generating embeddings."""

    force_regenerate: bool = Field(
        default=False,
        description="Regenerate even if embeddings exist",
    )


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic search."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language search query",
        examples=["market failure externalities"],
    )
    subject_id: UUID = Field(
        ...,
        description="Subject to search within (multi-tenant isolation)",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum results to return",
    )
    min_similarity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold (0-1)",
    )


class ContentAlignmentRequest(BaseModel):
    """Request schema for content-to-syllabus alignment."""

    content: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Content to align (e.g., textbook chapter)",
    )
    subject_id: UUID = Field(
        ...,
        description="Subject to align against (multi-tenant isolation)",
    )
    content_title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional title for the content",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum matching topics to return",
    )
    min_similarity: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum similarity for alignment",
    )


class BulkRegenerateRequest(BaseModel):
    """Request schema for bulk re-embedding topics."""

    topic_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Topic IDs to regenerate embeddings for",
    )
    subject_id: UUID = Field(
        ...,
        description="Subject scope for job tracking",
    )


# =============================================================================
# Response Schemas
# =============================================================================


class EmbeddingJobResponse(BaseModel):
    """Response schema for embedding job status."""

    id: UUID = Field(description="Job ID")
    subject_id: UUID = Field(description="Subject being embedded")
    status: EmbeddingJobStatus = Field(description="Job status")
    job_type: EmbeddingJobType = Field(description="Type of embedding job")
    total_items: int = Field(description="Total items to embed")
    completed_items: int = Field(description="Successfully embedded count")
    failed_items: int = Field(description="Failed embedding count")
    started_at: Optional[datetime] = Field(
        default=None,
        description="Job start time",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Job completion time",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error details if failed",
    )
    failed_item_ids: Optional[List[UUID]] = Field(
        default=None,
        description="IDs of failed items for retry",
    )
    progress_percent: float = Field(
        default=0.0,
        description="Progress percentage (0-100)",
    )

    model_config = {"from_attributes": True}

    @classmethod
    def from_job(cls, job) -> "EmbeddingJobResponse":
        """Create response from EmbeddingJob model."""
        return cls(
            id=job.id,
            subject_id=job.subject_id,
            status=EmbeddingJobStatus(job.status.value),
            job_type=EmbeddingJobType(job.job_type.value),
            total_items=job.total_items,
            completed_items=job.completed_items,
            failed_items=job.failed_items,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            failed_item_ids=job.failed_item_ids,
            progress_percent=job.progress_percent,
        )


class SearchResult(BaseModel):
    """Individual search result."""

    topic_id: str = Field(description="Topic ID")
    code: str = Field(description="Topic code (e.g., '1.1')")
    title: str = Field(description="Topic title (truncated description)")
    description: Optional[str] = Field(
        default=None,
        description="Full topic description",
    )
    section_title: Optional[str] = Field(
        default=None,
        description="Parent section title",
    )
    similarity: float = Field(
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0-1)",
    )


class SemanticSearchResponse(BaseModel):
    """Response schema for semantic search."""

    query: str = Field(description="Original search query")
    results: List[SearchResult] = Field(
        default_factory=list,
        description="Ranked search results",
    )
    search_time_ms: int = Field(description="Search execution time in milliseconds")
    total_embedded_topics: int = Field(
        default=0,
        description="Total topics with embeddings in subject",
    )


class AlignmentResult(BaseModel):
    """Individual alignment result."""

    topic_id: str = Field(description="Matched topic ID")
    code: str = Field(description="Topic code")
    title: str = Field(description="Topic title")
    similarity: float = Field(
        ge=0.0,
        le=1.0,
        description="Similarity score",
    )


class ConfidenceLevel(str, Enum):
    """Alignment confidence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContentAlignmentResponse(BaseModel):
    """Response schema for content alignment."""

    content_preview: str = Field(
        max_length=200,
        description="First 200 chars of content",
    )
    alignments: List[AlignmentResult] = Field(
        default_factory=list,
        description="Matching topics ranked by similarity",
    )
    processing_time_ms: int = Field(
        description="Processing time in milliseconds",
    )
    confidence: ConfidenceLevel = Field(
        description="Overall alignment confidence",
    )


class EmbeddingStatsResponse(BaseModel):
    """Response schema for embedding statistics."""

    subject_id: UUID = Field(description="Subject ID")
    total_topics: int = Field(description="Total topics in subject")
    embedded_topics: int = Field(description="Topics with embeddings")
    coverage_percent: float = Field(
        description="Embedding coverage percentage",
    )
    last_job_status: Optional[EmbeddingJobStatus] = Field(
        default=None,
        description="Status of most recent embedding job",
    )


# =============================================================================
# Error Schemas
# =============================================================================


class EmbeddingErrorResponse(BaseModel):
    """Error response for embedding operations."""

    error: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details",
    )
