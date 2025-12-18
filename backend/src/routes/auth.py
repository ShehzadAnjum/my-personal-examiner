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
from src.schemas.auth import LoginRequest, RegisterRequest, StudentResponse
from src.services.auth_service import verify_password
from src.services.student_service import (
    EmailAlreadyExistsError,
    create_student,
    get_student_by_email,
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


@router.post(
    "/login",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Login to student account",
    description="""
    Authenticate student with email and password.

    **Constitutional Requirements**:
    - Password verified using bcrypt
    - Returns student profile on success
    - Does not reveal if email exists (security)

    **Returns**:
    - 200 OK: Login successful, returns student profile
    - 401 Unauthorized: Invalid email or password
    - 422 Unprocessable Entity: Invalid input format
    """,
)
def login(
    login_data: LoginRequest,
    session: SessionDep,
) -> StudentResponse:
    """
    Login to student account

    Verifies email and password, returns student profile on success.
    Uses constant-time comparison to prevent timing attacks.

    Args:
        login_data: Email and password
        session: Database session (injected)

    Returns:
        StudentResponse: Student profile (no password_hash)

    Raises:
        HTTPException 401: Invalid email or password

    Examples:
        >>> # cURL test
        >>> curl -X POST http://localhost:8000/api/auth/login \\
        ...   -H "Content-Type: application/json" \\
        ...   -d '{
        ...     "email": "test@example.com",
        ...     "password": "TestPass123"
        ...   }'

    Constitutional Compliance:
        - Principle I: Password verified with bcrypt (constant-time)
        - Security: Generic error message (doesn't reveal if email exists)
        - FR-003: JWT tokens will be added in Phase 4

    Security Notes:
        - Does NOT reveal whether email exists (prevents enumeration)
        - Uses constant-time password verification (prevents timing attacks)
        - Intentionally slow (~300ms) to prevent brute force
    """

    # Find student by email
    student = get_student_by_email(session, login_data.email)

    # Verify password (or fail with generic message)
    if student is None or not verify_password(login_data.password, student.password_hash):
        # Generic error message (don't reveal if email exists)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Login successful - return student profile
    return student_to_response(student)
