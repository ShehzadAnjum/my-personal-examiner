"""
Extra Auth Routes

Additional authentication-related endpoints not part of the core auth flow.
Includes endpoints for better-auth integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_session
from src.models import Student

router = APIRouter(prefix="/api/auth", tags=["auth"])


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
        "created_at": student.created_at.isoformat(),
    }
