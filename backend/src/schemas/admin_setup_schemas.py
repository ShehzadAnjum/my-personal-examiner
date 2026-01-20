"""
Pydantic schemas for Admin Setup Wizard API.

Feature: Admin-First Topic Generation
Updated: 008-academic-level-hierarchy

Schemas for syllabus upload, topic extraction, and explanation generation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Syllabus Upload Schemas
# ============================================================================


class SyllabusUploadResponse(BaseModel):
    """Response after syllabus PDF upload.

    Updated for 008-academic-level-hierarchy:
    - Added syllabus_id (Syllabus model)
    - Renamed subject_code to syllabus_code
    """

    subject_id: UUID
    syllabus_id: UUID  # NEW - 008-academic-level-hierarchy
    resource_id: UUID
    file_name: str
    page_count: int
    syllabus_code: str  # Renamed from subject_code
    subject_name: str
    syllabus_year: str
    topics_extracted: int
    low_confidence_count: int
    warnings: list[str]
    message: str


class ExtractedTopicPreview(BaseModel):
    """Preview of an extracted topic for admin confirmation."""

    code: str
    title: str
    description: str
    learning_outcomes: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    parent_section: Optional[str] = None


class SyllabusParsePreviewResponse(BaseModel):
    """Preview of parsed syllabus before confirmation.

    Updated for 008-academic-level-hierarchy:
    - Added syllabus_id
    - Renamed subject_code to syllabus_code
    """

    syllabus_id: UUID  # NEW - 008-academic-level-hierarchy
    subject_id: UUID  # NEW - for reference
    syllabus_code: str  # Renamed from subject_code
    subject_name: str
    syllabus_year: str
    topics: list[ExtractedTopicPreview]
    total_topics: int
    high_confidence_count: int
    low_confidence_count: int
    warnings: list[str]


# ============================================================================
# Topic Confirmation Schemas
# ============================================================================


class TopicEditRequest(BaseModel):
    """Request to edit a single topic before confirmation."""

    code: str
    title: str
    description: str
    learning_outcomes: list[str]


class TopicConfirmationRequest(BaseModel):
    """Request to confirm extracted topics (with optional edits).

    Updated for 008-academic-level-hierarchy:
    - Added syllabus_id (required) - topics belong to syllabus
    - subject_id still included for backward compatibility query
    """

    syllabus_id: UUID  # NEW - 008-academic-level-hierarchy
    subject_id: UUID  # Kept for backward compat
    topics: list[TopicEditRequest]
    delete_topic_codes: list[str] = Field(default_factory=list)


class TopicConfirmationResponse(BaseModel):
    """Response after topics are confirmed.

    Updated for 008-academic-level-hierarchy:
    - Added syllabus_id
    """

    syllabus_id: UUID  # NEW - 008-academic-level-hierarchy
    subject_id: UUID
    topics_created: int
    topics_deleted: int
    setup_status: str
    message: str


# ============================================================================
# Explanation Generation Schemas
# ============================================================================


class GenerateExplanationsRequest(BaseModel):
    """Request to generate v1 explanations."""

    subject_id: UUID
    syllabus_point_ids: list[UUID] = Field(
        default_factory=list,
        description="Specific topics to generate. Empty = all topics."
    )
    resource_ids: list[UUID] = Field(
        default_factory=list,
        description="Resources to use as context for generation."
    )


class ExplanationGenerationProgress(BaseModel):
    """Progress update during explanation generation."""

    syllabus_point_id: UUID
    topic_code: str
    status: str  # "pending", "generating", "complete", "failed"
    error_message: Optional[str] = None


class GenerateExplanationsResponse(BaseModel):
    """Response after explanation generation (or batch start)."""

    subject_id: UUID
    total_topics: int
    generated_count: int
    failed_count: int
    skipped_count: int  # Already has v1
    setup_status: str
    message: str


# ============================================================================
# Setup Status Schemas
# ============================================================================


class SubjectSetupStatusResponse(BaseModel):
    """Response for subject setup status check.

    Updated for 008-academic-level-hierarchy:
    - Removed subject_code (Subject no longer has code)
    - Added syllabi_count (number of syllabi under subject)
    """

    subject_id: UUID
    subject_name: str
    academic_level_name: str  # NEW - from parent level
    setup_status: str
    syllabi_count: int  # NEW - how many syllabi
    syllabus_uploaded: bool  # True if at least one syllabus uploaded
    topics_count: int
    explanations_count: int
    can_proceed_to_topics: bool
    can_proceed_to_explanations: bool
    is_complete: bool


class AllSubjectsSetupStatusResponse(BaseModel):
    """Response for all subjects setup status."""

    subjects: list[SubjectSetupStatusResponse]
    all_complete: bool
    total_subjects: int


# ============================================================================
# v2+ Relinking Schemas (for syllabus regeneration)
# ============================================================================


class RelinkResultItem(BaseModel):
    """Result for a single explanation relinking attempt."""

    explanation_id: UUID
    old_topic_code: str
    new_topic_id: Optional[UUID] = None
    new_topic_code: Optional[str] = None
    status: str  # "relinked", "archived", "failed"
    reason: Optional[str] = None


class RelinkExplanationsResponse(BaseModel):
    """Response after v2+ explanation relinking."""

    total_processed: int
    relinked_count: int
    archived_count: int
    failed_count: int
    results: list[RelinkResultItem]
    message: str
