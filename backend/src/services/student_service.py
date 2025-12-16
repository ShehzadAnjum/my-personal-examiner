"""
Student Service

Business logic for student management (registration, profile updates).

Constitutional Requirements:
- Multi-tenant isolation enforced - Principle V
- Email uniqueness validated - FR-001
- Passwords always hashed before storage - Principle I
"""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.models.student import Student
from src.schemas.auth import RegisterRequest, StudentResponse
from src.services.auth_service import hash_password


class EmailAlreadyExistsError(Exception):
    """Raised when attempting to register with an email that already exists"""

    pass


def create_student(session: Session, registration_data: RegisterRequest) -> Student:
    """
    Create a new student account

    Hashes password with bcrypt before storage (constitutional requirement).
    Validates email uniqueness at database level.

    Args:
        session: Database session
        registration_data: Registration request with email, password, full_name

    Returns:
        Student: Created student record (with password_hash, not plain password)

    Raises:
        EmailAlreadyExistsError: If email already exists in database

    Examples:
        >>> request = RegisterRequest(
        ...     email="john@example.com",
        ...     password="SecurePass123",
        ...     full_name="John Doe"
        ... )
        >>> student = create_student(session, request)
        >>> student.email
        'john@example.com'
        >>> student.password_hash.startswith("$2b$12$")  # Bcrypt hash
        True

    Constitutional Compliance:
        - Principle I: Password hashed with bcrypt (never plain text)
        - Principle V: Student is multi-tenant anchor entity
        - FR-001: Email uniqueness enforced
        - FR-002: Password minimum 8 chars (validated at schema level)

    Database Transaction:
        - Session must be committed by caller (FastAPI dependency handles this)
        - IntegrityError caught and converted to EmailAlreadyExistsError
    """

    # Hash password (constitutional requirement: never store plain text)
    hashed_password = hash_password(registration_data.password)

    # Create student record
    student = Student(
        email=registration_data.email,
        password_hash=hashed_password,
        full_name=registration_data.full_name,
        target_grades=None,  # Set later via profile update
    )

    try:
        # Add to session and flush to get ID
        session.add(student)
        session.flush()  # Get ID without committing transaction

        return student

    except IntegrityError as e:
        # Email uniqueness constraint violated
        session.rollback()
        raise EmailAlreadyExistsError(f"Email {registration_data.email} already registered") from e


def get_student_by_email(session: Session, email: str) -> Student | None:
    """
    Get student by email address

    Used during login to find student account.

    Args:
        session: Database session
        email: Student email address

    Returns:
        Student | None: Student if found, None otherwise

    Examples:
        >>> student = get_student_by_email(session, "john@example.com")
        >>> if student:
        ...     print(f"Found: {student.full_name}")

    Multi-Tenant Note:
        Student table is multi-tenant anchor, but email is globally unique
        (cannot have same email for different students).
    """
    statement = select(Student).where(Student.email == email)
    return session.exec(statement).first()


def student_to_response(student: Student) -> StudentResponse:
    """
    Convert Student model to StudentResponse schema

    Removes sensitive fields (password_hash) for API response.

    Args:
        student: Student database model

    Returns:
        StudentResponse: API response schema (no password_hash)

    Examples:
        >>> student = Student(...)
        >>> response = student_to_response(student)
        >>> hasattr(response, 'password_hash')  # Not exposed in API
        False

    Security:
        - password_hash NEVER included in response (security requirement)
        - Only safe fields exposed to API
    """
    return StudentResponse(
        id=student.id,
        email=student.email,
        full_name=student.full_name,
        target_grades=student.target_grades,
        created_at=student.created_at,
    )
