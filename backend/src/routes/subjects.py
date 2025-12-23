"""
Subjects Routes

API endpoints for subject management.

Phase II: Basic subject listing
Phase V (US3): Full subject CRUD
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.database import get_session
from src.models.subject import Subject

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


# Response Schemas


class SubjectResponse(BaseModel):
    """Response schema for subject"""

    id: UUID
    code: str
    name: str
    level: str
    exam_board: str
    syllabus_year: str

    class Config:
        from_attributes = True


# Endpoints


@router.get("", response_model=list[SubjectResponse])
async def list_subjects(
    session: Session = Depends(get_session),
) -> list[Subject]:
    """
    List all available subjects.

    Returns:
        list[Subject]: All subjects in the database

    Examples:
        >>> GET /api/subjects
        [
            {
                "id": "uuid",
                "code": "9708",
                "name": "Economics",
                "level": "A",
                "exam_board": "Cambridge International",
                "syllabus_year": "2023-2025"
            }
        ]
    """
    statement = select(Subject).order_by(Subject.code)
    results = session.exec(statement).all()
    return results


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: UUID,
    session: Session = Depends(get_session),
) -> Subject:
    """
    Get a subject by ID.

    Args:
        subject_id: Subject UUID

    Returns:
        Subject: Subject details

    Raises:
        HTTPException: 404 if subject not found
    """
    statement = select(Subject).where(Subject.id == subject_id)
    subject = session.exec(statement).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found",
        )

    return subject
