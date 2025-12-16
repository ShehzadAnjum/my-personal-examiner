"""
Authentication Routes

API endpoints for student authentication:
- POST /api/auth/register - Register new student account
- POST /api/auth/login - Authenticate and get JWT token (Phase 4)

Constitutional Requirements:
- Email uniqueness enforced - FR-001
- Password minimum 8 characters - FR-002
- Passwords hashed with bcrypt - Principle I
"""

from fastapi import APIRouter, HTTPException, status

from src.database import SessionDep
from src.schemas.auth import RegisterRequest, StudentResponse
from src.services.student_service import (
    EmailAlreadyExistsError,
    create_student,
    student_to_response,
)

# Router for authentication endpoints
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/register",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new student account",
    description="""
    Create a new student account with email and password.

    **Constitutional Requirements**:
    - Email must be unique (409 if duplicate)
    - Password minimum 8 characters
    - Password hashed with bcrypt (work factor 12)

    **Returns**:
    - 201 Created: Student account created successfully
    - 400 Bad Request: Invalid email or password format
    - 409 Conflict: Email already registered
    """,
)
def register(
    registration_data: RegisterRequest,
    session: SessionDep,
) -> StudentResponse:
    """
    Register new student account

    Creates a new student account with hashed password.
    This is the FIRST WORKING ENDPOINT in Phase I! 🎯

    Args:
        registration_data: Email, password, full_name
        session: Database session (injected)

    Returns:
        StudentResponse: Created student profile (no password_hash)

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Invalid input data

    Examples:
        >>> # cURL test
        >>> curl -X POST http://localhost:8000/api/auth/register \\
        ...   -H "Content-Type: application/json" \\
        ...   -d '{
        ...     "email": "test@example.com",
        ...     "password": "TestPass123",
        ...     "full_name": "Test Student"
        ...   }'

    Constitutional Compliance:
        - FR-001: Email uniqueness enforced (409 on duplicate)
        - FR-002: Password minimum 8 chars (validated by Pydantic)
        - Principle I: Password hashed before storage (never plain text)
        - Principle V: Student is multi-tenant anchor entity
    """

    try:
        # Create student with hashed password
        student = create_student(session, registration_data)

        # Convert to response (excludes password_hash)
        return student_to_response(student)

    except EmailAlreadyExistsError:
        # Email already exists (unique constraint violated)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


# POST /api/auth/login endpoint will be added in Phase 4 (US2)
