"""
Academic Levels API Routes

RESTful endpoints for managing academic levels in the hierarchy.

Feature: 008-academic-level-hierarchy

Endpoints:
    GET  /api/academic-levels          - List all academic levels
    POST /api/academic-levels          - Create academic level (admin)
    GET  /api/academic-levels/{id}     - Get academic level details
    PUT  /api/academic-levels/{id}     - Update academic level (admin)
    DELETE /api/academic-levels/{id}   - Delete academic level (admin)
    GET  /api/academic-levels/{id}/subjects - List subjects under level
    POST /api/academic-levels/{id}/subjects - Create subject under level (admin)
    GET  /api/hierarchy                - Get full hierarchy tree

Constitutional Requirements:
    - Principle V: Multi-tenant isolation (admin check required for mutations)
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.models.student import Student
from src.routes.auth_extra import get_current_student, get_optional_student
from src.schemas.academic_level_schemas import (
    AcademicLevelCreate,
    AcademicLevelDetail,
    AcademicLevelResponse,
    AcademicLevelSummary,
    AcademicLevelUpdate,
    HierarchyTree,
    SubjectCreate,
    SubjectSummaryForLevel,
)
from src.services.hierarchy_service import (
    DependencyError,
    DuplicateCodeError,
    HierarchyService,
    NotFoundError,
)

router = APIRouter(prefix="/academic-levels", tags=["Academic Levels"])


def get_hierarchy_service(
    session: Annotated[Session, Depends(get_session)],
) -> HierarchyService:
    """Dependency to get hierarchy service."""
    return HierarchyService(session)


def require_admin(student: Student = Depends(get_current_student)) -> Student:
    """Dependency to require admin privileges."""
    if not getattr(student, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return student


# ===========================================================================
# Academic Level Endpoints
# ===========================================================================


@router.get("", response_model=list[AcademicLevelSummary])
async def list_academic_levels(
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student | None, Depends(get_optional_student)],
) -> list[AcademicLevelSummary]:
    """
    List all academic levels.

    Returns academic levels with subject counts.
    No authentication required - academic levels are global resources.
    """
    return service.list_academic_levels(include_counts=True)


@router.post("", response_model=AcademicLevelResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_level(
    data: AcademicLevelCreate,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student, Depends(require_admin)],
) -> AcademicLevelResponse:
    """
    Create a new academic level.

    Admin only. Creates an academic level like "A-Level" or "IGCSE".
    """
    try:
        level = service.create_academic_level(data)
        return AcademicLevelResponse.model_validate(level)
    except DuplicateCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/{level_id}", response_model=AcademicLevelDetail)
async def get_academic_level(
    level_id: UUID,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student | None, Depends(get_optional_student)],
) -> AcademicLevelDetail:
    """
    Get an academic level by ID.

    Returns the academic level with its subjects.
    """
    try:
        return service.get_academic_level(level_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{level_id}", response_model=AcademicLevelResponse)
async def update_academic_level(
    level_id: UUID,
    data: AcademicLevelUpdate,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student, Depends(require_admin)],
) -> AcademicLevelResponse:
    """
    Update an academic level.

    Admin only. Update name, description, or exam board.
    """
    try:
        level = service.update_academic_level(level_id, data)
        return AcademicLevelResponse.model_validate(level)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_academic_level(
    level_id: UUID,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student, Depends(require_admin)],
) -> None:
    """
    Delete an academic level.

    Admin only. Cannot delete if level has subjects.
    """
    try:
        service.delete_academic_level(level_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DependencyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ===========================================================================
# Subject Endpoints (nested under academic level)
# ===========================================================================


@router.get("/{level_id}/subjects", response_model=list[SubjectSummaryForLevel])
async def list_subjects_for_level(
    level_id: UUID,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student | None, Depends(get_optional_student)],
) -> list[SubjectSummaryForLevel]:
    """
    List all subjects under an academic level.

    Returns subjects with syllabi counts.
    """
    try:
        return service.list_subjects_for_level(level_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{level_id}/subjects",
    response_model=SubjectSummaryForLevel,
    status_code=status.HTTP_201_CREATED,
)
async def create_subject_for_level(
    level_id: UUID,
    data: SubjectCreate,
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student, Depends(require_admin)],
) -> SubjectSummaryForLevel:
    """
    Create a new subject under an academic level.

    Admin only. Creates a subject like "Economics" under "A-Level".
    """
    try:
        subject = service.create_subject_for_level(level_id, data)
        return SubjectSummaryForLevel(
            id=subject.id,
            name=subject.name,
            setup_status=subject.setup_status,
            syllabi_count=0,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DuplicateCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# ===========================================================================
# Hierarchy Tree Endpoint
# ===========================================================================


# Create a separate router for /hierarchy endpoint (not nested under /academic-levels)
hierarchy_router = APIRouter(tags=["Hierarchy"])


@hierarchy_router.get("/hierarchy", response_model=HierarchyTree)
async def get_hierarchy_tree(
    service: Annotated[HierarchyService, Depends(get_hierarchy_service)],
    _: Annotated[Student | None, Depends(get_optional_student)],
) -> HierarchyTree:
    """
    Get the complete hierarchy tree.

    Returns all academic levels with their subjects and syllabi.
    """
    return service.get_hierarchy_tree()
