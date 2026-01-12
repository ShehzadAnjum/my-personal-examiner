"""
Syllabus Schemas

Pydantic schemas for Syllabus API endpoints.
Supports the three-tier hierarchy: Academic Level → Subject → Syllabus

Feature: 008-academic-level-hierarchy
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SyllabusCreate(BaseModel):
    """Schema for creating a new syllabus"""

    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Syllabus code (e.g., '9708')",
        examples=["9708"],
    )
    year_range: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Valid years (e.g., '2023-2025')",
        examples=["2023-2025"],
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Ensure code is alphanumeric"""
        if not v.isalnum():
            raise ValueError("Syllabus code must be alphanumeric")
        return v

    @field_validator("year_range")
    @classmethod
    def validate_year_range(cls, v: str) -> str:
        """Validate year range format (e.g., '2023-2025')"""
        parts = v.split("-")
        if len(parts) != 2:
            raise ValueError("Year range must be in format 'YYYY-YYYY'")
        for part in parts:
            if not part.isdigit() or len(part) != 4:
                raise ValueError("Year range must contain valid 4-digit years")
        if int(parts[0]) > int(parts[1]):
            raise ValueError("Start year must be before or equal to end year")
        return v


class SyllabusUpdate(BaseModel):
    """Schema for updating a syllabus"""

    year_range: str | None = Field(
        default=None,
        max_length=20,
        description="Valid years",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether this is the active syllabus",
    )

    @field_validator("year_range")
    @classmethod
    def validate_year_range(cls, v: str | None) -> str | None:
        """Validate year range format if provided"""
        if v is None:
            return v
        parts = v.split("-")
        if len(parts) != 2:
            raise ValueError("Year range must be in format 'YYYY-YYYY'")
        for part in parts:
            if not part.isdigit() or len(part) != 4:
                raise ValueError("Year range must contain valid 4-digit years")
        return v


class SyllabusResponse(BaseModel):
    """Schema for syllabus response"""

    id: UUID
    subject_id: UUID
    code: str
    year_range: str
    version: int
    is_active: bool
    syllabus_resource_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SyllabusSummary(BaseModel):
    """Summary schema for syllabus (used in lists)"""

    id: UUID
    code: str
    year_range: str
    is_active: bool
    topics_count: int = Field(default=0, description="Number of topics in this syllabus")

    model_config = {"from_attributes": True}


class SyllabusPointSummary(BaseModel):
    """Summary of a syllabus point for inclusion in syllabus detail"""

    id: UUID
    code: str
    description: str
    topics: str | None
    learning_outcomes: str | None

    model_config = {"from_attributes": True}


class SubjectSummaryForSyllabus(BaseModel):
    """Subject summary for inclusion in syllabus detail"""

    id: UUID
    name: str
    setup_status: str

    model_config = {"from_attributes": True}


class SyllabusDetail(BaseModel):
    """Detailed schema for syllabus with topics"""

    id: UUID
    subject_id: UUID
    code: str
    year_range: str
    version: int
    is_active: bool
    syllabus_resource_id: UUID | None
    created_at: datetime
    updated_at: datetime
    subject: SubjectSummaryForSyllabus | None = None
    topics: list[SyllabusPointSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}
