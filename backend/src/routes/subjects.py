"""
Subjects Routes

API endpoints for subject management.

Feature: 008-academic-level-hierarchy
Updated to support three-tier hierarchy: Academic Level → Subject → Syllabus
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.database import get_session
from src.models.academic_level import AcademicLevel
from src.models.subject import Subject
from src.schemas.syllabus_schemas import SyllabusCreate, SyllabusSummary, SyllabusResponse
from src.services.hierarchy_service import (
    HierarchyService,
    NotFoundError,
    DuplicateCodeError,
)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


# Response Schemas


class SubjectResponse(BaseModel):
    """Response schema for subject (updated for hierarchy)"""

    id: UUID
    name: str
    academic_level_id: UUID
    setup_status: str

    class Config:
        from_attributes = True


class SubjectWithLevelResponse(BaseModel):
    """Response schema for subject with academic level info"""

    id: UUID
    name: str
    academic_level_id: UUID
    academic_level_name: str
    academic_level_code: str
    setup_status: str

    class Config:
        from_attributes = True


# Endpoints


@router.get("", response_model=list[SubjectWithLevelResponse])
async def list_subjects(
    session: Session = Depends(get_session),
    academic_level_id: Optional[UUID] = Query(
        default=None,
        description="Filter subjects by academic level ID",
    ),
) -> list[SubjectWithLevelResponse]:
    """
    List all available subjects.

    Args:
        academic_level_id: Optional filter by academic level UUID

    Returns:
        list[SubjectWithLevelResponse]: All subjects (optionally filtered)

    Examples:
        >>> GET /api/subjects
        >>> GET /api/subjects?academic_level_id=uuid
    """
    # Build query with optional filter
    statement = select(Subject, AcademicLevel).join(
        AcademicLevel, Subject.academic_level_id == AcademicLevel.id
    )

    if academic_level_id:
        statement = statement.where(Subject.academic_level_id == academic_level_id)

    statement = statement.order_by(AcademicLevel.name, Subject.name)
    results = session.exec(statement).all()

    return [
        SubjectWithLevelResponse(
            id=subject.id,
            name=subject.name,
            academic_level_id=subject.academic_level_id,
            academic_level_name=level.name,
            academic_level_code=level.code,
            setup_status=subject.setup_status,
        )
        for subject, level in results
    ]


@router.get("/{subject_id}", response_model=SubjectWithLevelResponse)
async def get_subject(
    subject_id: UUID,
    session: Session = Depends(get_session),
) -> SubjectWithLevelResponse:
    """
    Get a subject by ID.

    Args:
        subject_id: Subject UUID

    Returns:
        SubjectWithLevelResponse: Subject details with academic level info

    Raises:
        HTTPException: 404 if subject not found
    """
    statement = (
        select(Subject, AcademicLevel)
        .join(AcademicLevel, Subject.academic_level_id == AcademicLevel.id)
        .where(Subject.id == subject_id)
    )
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found",
        )

    subject, level = result
    return SubjectWithLevelResponse(
        id=subject.id,
        name=subject.name,
        academic_level_id=subject.academic_level_id,
        academic_level_name=level.name,
        academic_level_code=level.code,
        setup_status=subject.setup_status,
    )


# ===========================================================================
# Syllabus Endpoints (T041, T042)
# ===========================================================================


@router.get("/{subject_id}/syllabi", response_model=list[SyllabusSummary])
async def list_syllabi_for_subject(
    subject_id: UUID,
    session: Session = Depends(get_session),
) -> list[SyllabusSummary]:
    """
    List all syllabi for a subject.

    Args:
        subject_id: Subject UUID

    Returns:
        list[SyllabusSummary]: All syllabi for the subject with topic counts

    Raises:
        HTTPException: 404 if subject not found
    """
    service = HierarchyService(session)
    try:
        syllabi = service.list_syllabi_for_subject(subject_id)
        return syllabi
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{subject_id}/syllabi", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
async def create_syllabus_for_subject(
    subject_id: UUID,
    data: SyllabusCreate,
    session: Session = Depends(get_session),
) -> SyllabusResponse:
    """
    Create a new syllabus for a subject.

    Args:
        subject_id: Subject UUID
        data: Syllabus creation data (code, year_range)

    Returns:
        SyllabusResponse: Created syllabus

    Raises:
        HTTPException: 404 if subject not found
        HTTPException: 409 if syllabus code already exists
    """
    service = HierarchyService(session)
    try:
        syllabus = service.create_syllabus_for_subject(subject_id, data)
        return SyllabusResponse(
            id=syllabus.id,
            subject_id=syllabus.subject_id,
            code=syllabus.code,
            year_range=syllabus.year_range,
            version=syllabus.version,
            is_active=syllabus.is_active,
            syllabus_resource_id=syllabus.syllabus_resource_id,
            created_at=syllabus.created_at,
            updated_at=syllabus.updated_at,
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
