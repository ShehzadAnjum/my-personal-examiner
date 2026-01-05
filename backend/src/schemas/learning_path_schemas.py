"""
Learning Path Schemas

Pydantic schemas for Learning Path API endpoints.

Feature: 006-resource-bank
Based on: specs/006-resource-bank/contracts/learning-path-api.yaml
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.enums import MasteryLevel


# ============================================================================
# Request Schemas
# ============================================================================


class TrackViewRequest(BaseModel):
    """Request to track topic view."""

    syllabus_point_id: UUID = Field(..., description="Topic viewed")
    explanation_version: Optional[int] = Field(
        1, ge=1, description="Which version was viewed"
    )


class TrackTimeRequest(BaseModel):
    """Request to track time spent on topic."""

    syllabus_point_id: UUID = Field(..., description="Topic studied")
    duration_seconds: int = Field(
        ...,
        ge=1,
        le=7200,
        description="Time spent in seconds (max 2 hours per session)",
    )


class UpdateProgressRequest(BaseModel):
    """Request to update topic progress."""

    preferred_version: Optional[int] = Field(None, ge=1, description="Set preferred version")
    mastery_level: Optional[MasteryLevel] = Field(
        None, description="Manually set mastery level"
    )

    class Config:
        json_schema_extra = {
            "example": {"preferred_version": 2, "mastery_level": "familiar"}
        }


# ============================================================================
# Response Schemas
# ============================================================================


class TopicProgress(BaseModel):
    """Progress data for a single topic."""

    id: UUID
    syllabus_point_id: UUID
    syllabus_point_name: Optional[str] = Field(None, description="Topic name for display")
    view_count: int = Field(..., ge=0)
    total_time_spent_seconds: int = Field(..., ge=0)
    total_time_spent_display: Optional[str] = Field(
        None, description="Human-readable (e.g., '15 min')"
    )
    last_viewed_at: Optional[datetime] = None
    preferred_version: int = Field(..., ge=1)
    is_bookmarked: bool
    mastery_level: MasteryLevel
    has_personalized_version: bool = Field(
        default=False, description="Whether student has v2+ version"
    )

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    """Response for learning path listing."""

    items: list[TopicProgress]
    total: int = Field(..., ge=0, description="Total items before pagination")
    limit: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)


class TrackViewResponse(BaseModel):
    """Response after tracking view."""

    syllabus_point_id: UUID
    new_view_count: int = Field(..., ge=1)
    mastery_level: MasteryLevel
    mastery_changed: bool = Field(..., description="Whether mastery level was upgraded")


class TrackTimeResponse(BaseModel):
    """Response after tracking time."""

    syllabus_point_id: UUID
    new_total_seconds: int = Field(..., ge=0)
    mastery_level: MasteryLevel
    mastery_changed: bool = Field(..., description="Whether mastery level was upgraded")


class TopicProgressResponse(BaseModel):
    """Response for single topic progress."""

    progress: TopicProgress


class MasteryDistribution(BaseModel):
    """Distribution of mastery levels."""

    not_started: int = Field(default=0, ge=0)
    learning: int = Field(default=0, ge=0)
    familiar: int = Field(default=0, ge=0)
    mastered: int = Field(default=0, ge=0)


class LearningSummaryResponse(BaseModel):
    """Response for learning summary statistics."""

    total_topics_available: int = Field(..., ge=0, description="Total topics in syllabus")
    topics_viewed: int = Field(..., ge=0, description="Topics viewed at least once")
    topics_bookmarked: int = Field(..., ge=0)
    total_time_spent_seconds: int = Field(..., ge=0)
    total_time_spent_display: str = Field(..., description="Human-readable")
    mastery_distribution: MasteryDistribution
    completion_percentage: float = Field(..., ge=0, le=100)
    streak_days: int = Field(default=0, ge=0, description="Consecutive days with activity")


class Recommendation(BaseModel):
    """Single topic recommendation."""

    syllabus_point_id: UUID
    syllabus_point_name: str
    reason: str = Field(..., description="Why this topic is recommended")
    priority: int = Field(..., ge=1, le=10, description="Higher = more important")


class RecommendationsResponse(BaseModel):
    """Response for topic recommendations."""

    recommendations: list[Recommendation]


class BookmarkItem(BaseModel):
    """Single bookmark entry."""

    syllabus_point_id: UUID
    syllabus_point_name: str
    bookmarked_at: datetime
    mastery_level: MasteryLevel


class BookmarkListResponse(BaseModel):
    """Response for bookmark listing."""

    bookmarks: list[BookmarkItem]


class BookmarkResponse(BaseModel):
    """Response after adding bookmark."""

    syllabus_point_id: UUID
    bookmarked_at: datetime


# ============================================================================
# Query Parameter Schemas
# ============================================================================


class LearningPathQuery(BaseModel):
    """Query parameters for learning path listing."""

    mastery_level: Optional[MasteryLevel] = Field(
        None, description="Filter by mastery level"
    )
    bookmarked_only: bool = Field(False, description="Return only bookmarked topics")
    limit: int = Field(50, ge=1, le=100, description="Max items to return")
    offset: int = Field(0, ge=0, description="Items to skip")
