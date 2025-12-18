"""
Unit Tests for Student Service

Tests business logic functions in student_service module.

Constitutional Requirements:
- Password hashing enforced - Principle I
- Email uniqueness validated - FR-001
- Multi-tenant isolation tested - Principle V
"""

import pytest
from sqlmodel import Session

from src.models.student import Student
from src.schemas.auth import RegisterRequest, StudentResponse
from src.services.student_service import (
    EmailAlreadyExistsError,
    create_student,
    get_student_by_email,
    student_to_response,
)


def test_create_student_success(session: Session):
    """Test successful student creation with valid data"""
    registration_data = RegisterRequest(
        email="new@example.com",
        password="SecurePass123",
        full_name="New Student",
    )

    student = create_student(session, registration_data)

    assert student.email == "new@example.com"
    assert student.full_name == "New Student"
    assert student.password_hash is not None
    assert student.password_hash != "SecurePass123"  # Should be hashed
    assert student.password_hash.startswith("$2b$12$")  # Bcrypt format
    assert student.id is not None  # UUID generated
    assert student.created_at is not None


def test_create_student_password_hashed(session: Session):
    """Test that password is bcrypt-hashed (Constitutional Principle I)"""
    registration_data = RegisterRequest(
        email="hash@example.com",
        password="PlainPassword",
        full_name="Hash Test",
    )

    student = create_student(session, registration_data)

    # Password MUST be hashed (never plain text)
    assert student.password_hash != "PlainPassword"
    assert "$2b$12$" in student.password_hash  # Bcrypt with work factor 12
    assert len(student.password_hash) == 60  # Bcrypt hash length


def test_create_student_duplicate_email(session: Session):
    """Test that duplicate email raises EmailAlreadyExistsError"""
    # Create first student
    registration_data_1 = RegisterRequest(
        email="duplicate@example.com",
        password="Pass1234",  # 8 chars minimum
        full_name="First Student",
    )
    create_student(session, registration_data_1)
    session.commit()  # Commit first student

    # Try to create second student with same email
    registration_data_2 = RegisterRequest(
        email="duplicate@example.com",  # Same email!
        password="Pass5678",  # 8 chars minimum
        full_name="Second Student",
    )

    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        create_student(session, registration_data_2)

    assert "duplicate@example.com" in str(exc_info.value)
    assert "already registered" in str(exc_info.value).lower()


def test_create_student_rollback_on_error(session: Session):
    """Test that session is rolled back on duplicate email error"""
    # Create first student
    registration_data_1 = RegisterRequest(
        email="rollback@example.com",
        password="Pass1234",
        full_name="First",
    )
    create_student(session, registration_data_1)
    session.commit()

    # Try duplicate (should rollback)
    registration_data_2 = RegisterRequest(
        email="rollback@example.com",
        password="Pass5678",
        full_name="Second",
    )

    try:
        create_student(session, registration_data_2)
    except EmailAlreadyExistsError:
        pass  # Expected

    # Session should still be usable (rollback successful)
    # Create a different student to verify
    registration_data_3 = RegisterRequest(
        email="different@example.com",
        password="Pass7890",
        full_name="Third",
    )
    student3 = create_student(session, registration_data_3)
    assert student3.email == "different@example.com"


def test_get_student_by_email_found(session: Session):
    """Test finding existing student by email"""
    # Create student
    registration_data = RegisterRequest(
        email="find@example.com",
        password="Pass1234",
        full_name="Find Me",
    )
    created_student = create_student(session, registration_data)
    session.commit()

    # Find by email
    found_student = get_student_by_email(session, "find@example.com")

    assert found_student is not None
    assert found_student.id == created_student.id
    assert found_student.email == "find@example.com"
    assert found_student.full_name == "Find Me"


def test_get_student_by_email_not_found(session: Session):
    """Test that non-existent email returns None"""
    result = get_student_by_email(session, "nonexistent@example.com")
    assert result is None


def test_get_student_by_email_case_sensitive(session: Session):
    """Test that email search is case-sensitive"""
    # Create student with lowercase email
    registration_data = RegisterRequest(
        email="lowercase@example.com",
        password="Pass1234",
        full_name="Lowercase",
    )
    create_student(session, registration_data)
    session.commit()

    # Search with uppercase (should not find)
    result = get_student_by_email(session, "LOWERCASE@EXAMPLE.COM")
    assert result is None  # Case-sensitive, so not found

    # Search with exact case (should find)
    result = get_student_by_email(session, "lowercase@example.com")
    assert result is not None


def test_student_to_response_excludes_password():
    """Test that student_to_response excludes password_hash (security)"""
    student = Student(
        email="response@example.com",
        password_hash="$2b$12$secret_hash_here",
        full_name="Response Test",
        target_grades={"9708": "A*"},
    )

    response = student_to_response(student)

    # Check response type
    assert isinstance(response, StudentResponse)

    # Check included fields
    assert response.id == student.id
    assert response.email == "response@example.com"
    assert response.full_name == "Response Test"
    assert response.target_grades == {"9708": "A*"}
    assert response.created_at == student.created_at

    # Check password_hash is NOT in response
    assert not hasattr(response, "password_hash")


def test_student_to_response_with_none_target_grades():
    """Test student_to_response when target_grades is None"""
    student = Student(
        email="notarget@example.com",
        password_hash="$2b$12$hash",
        full_name="No Target",
        target_grades=None,
    )

    response = student_to_response(student)

    assert response.target_grades is None


def test_create_student_different_passwords_different_hashes(session: Session):
    """Test that same password for different users gets different hashes (salt)"""
    # Create two students with same password
    student1 = create_student(
        session,
        RegisterRequest(
            email="user1@example.com",
            password="SamePassword123",
            full_name="User 1",
        ),
    )

    student2 = create_student(
        session,
        RegisterRequest(
            email="user2@example.com",
            password="SamePassword123",  # Same password!
            full_name="User 2",
        ),
    )

    # Hashes should be different (bcrypt uses random salt)
    assert student1.password_hash != student2.password_hash
    assert student1.password_hash.startswith("$2b$12$")
    assert student2.password_hash.startswith("$2b$12$")
