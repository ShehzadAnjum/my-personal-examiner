"""
Extra Auth Routes

Additional authentication-related endpoints not part of the core auth flow.
Includes endpoints for better-auth integration and authentication dependencies.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from src.database import get_session
from src.models import Student

router = APIRouter(prefix="/api/auth", tags=["auth"])


# Authentication Dependencies


async def get_current_student(
    student_id: UUID = Query(..., description="Student ID from session"),
    session: Session = Depends(get_session),
) -> Student:
    """
    Get current authenticated student by ID.

    This dependency should be used for student-authenticated endpoints.
    It verifies the student exists.

    Args:
        student_id: UUID of the student making the request
        session: Database session (injected)

    Returns:
        Student: The student entity

    Raises:
        HTTPException 404: Student not found

    Example:
        >>> @router.get("/api/resources/my-uploads")
        >>> async def my_uploads(
        >>>     current_student: Student = Depends(get_current_student),
        >>>     session: Session = Depends(get_session),
        >>> ):
        >>>     return filter_resources_by_student(current_student.id)
    """
    statement = select(Student).where(Student.id == student_id)
    student = session.exec(statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    return student


# Routes


@router.get("/student-by-email")
async def get_student_by_email(
    email: str,
    session: Session = Depends(get_session),
):
    """
    Get student by email address.

    Used by better-auth integration to find existing student records.

    Args:
        email: Student email address
        session: Database session (injected)

    Returns:
        Student: Student record with id, email, full_name

    Raises:
        HTTPException: 404 if student not found
    """
    statement = select(Student).where(Student.email == email)
    student = session.exec(statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with email {email} not found",
        )

    return {
        "id": str(student.id),
        "email": student.email,
        "full_name": student.full_name,
        "is_admin": student.is_admin,
        "created_at": student.created_at.isoformat(),
    }
