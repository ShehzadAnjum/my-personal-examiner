"""
Academic Level Schemas

Pydantic schemas for Academic Level API endpoints.
Supports the three-tier hierarchy: Academic Level → Subject → Syllabus

Feature: 008-academic-level-hierarchy
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AcademicLevelCreate(BaseModel):
    """Schema for creating a new academic level"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name (e.g., 'A-Level')",
        examples=["A-Level"],
    )
    code: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Short unique code (e.g., 'A', 'O', 'IGCSE')",
        examples=["A"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description",
        examples=["Cambridge International A-Level qualifications"],
    )
    exam_board: str = Field(
        default="Cambridge International",
        max_length=100,
        description="Exam board name",
        examples=["Cambridge International"],
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Ensure code is alphanumeric"""
        clean = v.replace("-", "").replace("_", "")
        if not clean.isalnum():
            raise ValueError("Code must be alphanumeric (hyphens and underscores allowed)")
        return v.upper()


class AcademicLevelUpdate(BaseModel):
    """Schema for updating an academic level"""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Display name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description",
    )
    exam_board: str | None = Field(
        default=None,
        max_length=100,
        description="Exam board name",
    )


class AcademicLevelResponse(BaseModel):
    """Schema for academic level response"""

    id: UUID
    name: str
    code: str
    description: str | None
    exam_board: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AcademicLevelSummary(BaseModel):
    """Summary schema for academic level (used in lists)"""

    id: UUID
    name: str
    code: str
    exam_board: str
    subjects_count: int = Field(default=0, description="Number of subjects under this level")

    model_config = {"from_attributes": True}


class SubjectSummaryForLevel(BaseModel):
    """Subject summary for inclusion in academic level detail"""

    id: UUID
    name: str
    setup_status: str
    syllabi_count: int = Field(default=0, description="Number of syllabi under this subject")

    model_config = {"from_attributes": True}


class AcademicLevelDetail(BaseModel):
    """Detailed schema for academic level with subjects"""

    id: UUID
    name: str
    code: str
    description: str | None
    exam_board: str
    created_at: datetime
    updated_at: datetime
    subjects: list[SubjectSummaryForLevel] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SubjectCreate(BaseModel):
    """Schema for creating a subject under an academic level"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Subject name (e.g., 'Economics')",
        examples=["Economics"],
    )
    code: str | None = Field(
        default=None,
        max_length=20,
        description="Optional subject code (e.g., 'ECON')",
        examples=["ECON"],
    )


class HierarchyNode(BaseModel):
    """Node in the hierarchy tree"""

    id: UUID
    name: str
    code: str | None = None


class SyllabusNode(BaseModel):
    """Syllabus node in the hierarchy tree"""

    id: UUID
    code: str
    year_range: str
    is_active: bool
    topics_count: int = 0


class SubjectNode(BaseModel):
    """Subject node in the hierarchy tree"""

    id: UUID
    name: str
    syllabi: list[SyllabusNode] = Field(default_factory=list)


class AcademicLevelNode(BaseModel):
    """Academic level node in the hierarchy tree"""

    id: UUID
    name: str
    code: str
    subjects: list[SubjectNode] = Field(default_factory=list)


class HierarchyTree(BaseModel):
    """Complete hierarchy tree response"""

    academic_levels: list[AcademicLevelNode] = Field(default_factory=list)
