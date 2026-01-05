"""
Admin Authentication Middleware

FastAPI dependencies for admin-only endpoint protection.

Feature: 006-resource-bank (US2: Admin Generates Baseline Content)

Constitutional Requirements:
- Principle V: Multi-tenant isolation (admin check per student)
- Only students with is_admin=True can access admin endpoints
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from sqlmodel import Session, select

from src.database import get_session
from src.models import Student

logger = logging.getLogger(__name__)


class AdminRequiredError(Exception):
    """Raised when admin privileges are required but not present."""
    pass


class StudentNotFoundError(Exception):
    """Raised when student is not found in database."""
    pass


async def get_admin_student(
    student_id: UUID = Query(..., description="Student ID for admin verification"),
    session: Session = Depends(get_session),
) -> Student:
    """
    Get student and verify admin status.

    This dependency fetches the student by ID and verifies they exist.
    Does NOT check admin status - use require_admin for that.

    Args:
        student_id: UUID of the student making the request
        session: Database session (injected)

    Returns:
        Student: The student entity

    Raises:
        HTTPException 404: Student not found
        HTTPException 422: Invalid student_id format

    Example:
        >>> @router.get("/admin/endpoint")
        >>> async def admin_endpoint(student: Student = Depends(get_admin_student)):
        >>>     return {"is_admin": student.is_admin}
    """
    statement = select(Student).where(Student.id == student_id)
    student = session.exec(statement).first()

    if not student:
        logger.warning(f"Admin check failed: Student {student_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    return student


async def require_admin(
    student_id: UUID = Query(..., description="Student ID (must be admin)"),
    session: Session = Depends(get_session),
) -> Student:
    """
    Require admin privileges for endpoint access.

    This dependency should be used for admin-only endpoints.
    It verifies the student exists AND has is_admin=True.

    Args:
        student_id: UUID of the student making the request
        session: Database session (injected)

    Returns:
        Student: The admin student entity

    Raises:
        HTTPException 404: Student not found
        HTTPException 403: Student is not an admin

    Example:
        >>> @router.post("/admin/resources/generate-v1")
        >>> async def generate_v1(
        >>>     admin: Student = Depends(require_admin),
        >>>     session: Session = Depends(get_session),
        >>> ):
        >>>     # Only admins can reach here
        >>>     return {"generated_by": admin.full_name}

    Constitutional Compliance:
        - Principle V: Verifies student identity before admin check
        - US2: Ensures only admins can generate v1 content
    """
    # First, get the student
    statement = select(Student).where(Student.id == student_id)
    student = session.exec(statement).first()

    if not student:
        logger.warning(f"Admin access denied: Student {student_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    # Check admin status
    if not student.is_admin:
        logger.warning(
            f"Admin access denied: Student {student_id} ({student.email}) is not an admin"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required. This endpoint is restricted to administrators.",
        )

    logger.info(f"Admin access granted: {student.email}")
    return student


def check_admin_status(student: Student) -> bool:
    """
    Simple utility to check if a student is an admin.

    Args:
        student: Student entity to check

    Returns:
        bool: True if student is an admin, False otherwise

    Example:
        >>> if check_admin_status(student):
        >>>     # Show admin UI elements
        >>>     pass
    """
    return student.is_admin
