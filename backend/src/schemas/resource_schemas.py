"""
Pydantic schemas for Resource Bank API requests and responses.

Feature: 007-resource-bank-files
Created: 2025-12-27
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.enums import AddedBy, ResourceType, S3SyncStatus, Visibility


# Request Schemas


class ResourceUploadRequest(BaseModel):
    """Schema for resource upload request (multipart/form-data)."""

    resource_type: ResourceType
    title: str = Field(max_length=500)
    source_url: Optional[str] = Field(default=None, max_length=2000)


class ResourceTagRequest(BaseModel):
    """Schema for tagging resource to syllabus point."""

    syllabus_point_id: UUID
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score 0-1")


class ResourceMetadataUpdateRequest(BaseModel):
    """Schema for updating resource metadata by admin."""

    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    resource_metadata: Optional[dict] = None


class ResourceSearchRequest(BaseModel):
    """Schema for full-text search request."""

    query: str = Field(min_length=1, max_length=500)
    resource_type: Optional[ResourceType] = None
    limit: int = Field(default=20, ge=1, le=100)


# Response Schemas


class ResourceResponse(BaseModel):
    """Schema for resource details response."""

    id: UUID
    resource_type: ResourceType
    title: str
    source_url: Optional[str]
    file_path: str
    uploaded_by_student_id: Optional[UUID]
    admin_approved: bool
    visibility: Visibility
    resource_metadata: dict
    signature: str
    s3_url: Optional[str]
    s3_sync_status: S3SyncStatus
    last_synced_at: Optional[datetime]
    extracted_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ResourceListResponse(BaseModel):
    """Schema for paginated resource list."""

    total: int
    resources: list[ResourceResponse]


class SyllabusPointResourceResponse(BaseModel):
    """Schema for syllabus-point-to-resource mapping."""

    syllabus_point_id: UUID
    resource_id: UUID
    relevance_score: float
    added_by: AddedBy
    created_at: datetime
    resource: Optional[ResourceResponse] = None  # Joined resource details

    class Config:
        """Pydantic config."""

        from_attributes = True


class ResourceSearchResultResponse(BaseModel):
    """Schema for search result with ranking."""

    resource: ResourceResponse
    rank: float  # ts_rank score from PostgreSQL


class S3SyncStatusResponse(BaseModel):
    """Schema for S3 sync status endpoint."""

    pending_uploads: int
    failed_uploads: int
    s3_online: bool
    last_successful_sync: Optional[datetime]


class SyncTriggerResponse(BaseModel):
    """Schema for manual sync trigger response."""

    status: str
    message: str
    resources_queued: int
