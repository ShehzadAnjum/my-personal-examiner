"""
Pydantic Schemas Package

All Pydantic schemas for API request/response validation.

Feature: 008-academic-level-hierarchy
"""

from src.schemas.academic_level_schemas import (
    AcademicLevelCreate,
    AcademicLevelDetail,
    AcademicLevelNode,
    AcademicLevelResponse,
    AcademicLevelSummary,
    AcademicLevelUpdate,
    HierarchyNode,
    HierarchyTree,
    SubjectCreate,
    SubjectNode,
    SubjectSummaryForLevel,
    SyllabusNode,
)
from src.schemas.syllabus_schemas import (
    SubjectSummaryForSyllabus,
    SyllabusCreate,
    SyllabusDetail,
    SyllabusPointSummary,
    SyllabusResponse,
    SyllabusSummary,
    SyllabusUpdate,
)

__all__ = [
    # Academic Level Schemas
    "AcademicLevelCreate",
    "AcademicLevelUpdate",
    "AcademicLevelResponse",
    "AcademicLevelSummary",
    "AcademicLevelDetail",
    "SubjectSummaryForLevel",
    "SubjectCreate",
    # Syllabus Schemas
    "SyllabusCreate",
    "SyllabusUpdate",
    "SyllabusResponse",
    "SyllabusSummary",
    "SyllabusDetail",
    "SyllabusPointSummary",
    "SubjectSummaryForSyllabus",
    # Hierarchy Tree Schemas
    "HierarchyNode",
    "SyllabusNode",
    "SubjectNode",
    "AcademicLevelNode",
    "HierarchyTree",
]
