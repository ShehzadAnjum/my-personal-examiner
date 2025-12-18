"""
Unit Tests for Student Model

Tests the Student model in isolation (no database required for basic tests).

Constitutional Requirements:
- Password hash must never be plain text - Principle I
- Email must be unique - FR-001
- Profile updates must set updated_at timestamp
"""

from datetime import datetime
from uuid import uuid4

import pytest
from sqlmodel import Session, select

from src.models.student import Student


def test_student_creation():
    """Test creating a Student instance with valid data"""
    student_id = uuid4()
    student = Student(
        id=student_id,
        email="test@example.com",
        password_hash="$2b$12$hashed_password_here",
        full_name="Test Student",
        target_grades={"9708": "A*"},
    )

    assert student.id == student_id
    assert student.email == "test@example.com"
    assert student.password_hash == "$2b$12$hashed_password_here"
    assert student.full_name == "Test Student"
    assert student.target_grades == {"9708": "A*"}
    assert isinstance(student.created_at, datetime)
    assert student.updated_at is None  # Not updated yet


def test_student_auto_id_generation():
    """Test that Student auto-generates UUID if not provided"""
    student = Student(
        email="auto@example.com",
        password_hash="$2b$12$hashed",
        full_name="Auto ID Student",
    )

    assert student.id is not None
    assert isinstance(student.id, type(uuid4()))


def test_student_auto_created_at():
    """Test that created_at is automatically set"""
    before = datetime.utcnow()
    student = Student(
        email="time@example.com",
        password_hash="$2b$12$hashed",
        full_name="Time Test",
    )
    after = datetime.utcnow()

    assert before <= student.created_at <= after


def test_student_update_profile_full_name():
    """Test updating student profile (full_name only)"""
    student = Student(
        email="update@example.com",
        password_hash="$2b$12$hashed",
        full_name="Original Name",
    )

    # Initially no updated_at
    assert student.updated_at is None

    # Update profile
    student.update_profile(full_name="New Name")

    assert student.full_name == "New Name"
    assert student.updated_at is not None
    assert isinstance(student.updated_at, datetime)


def test_student_update_profile_target_grades():
    """Test updating student profile (target_grades only)"""
    student = Student(
        email="grades@example.com",
        password_hash="$2b$12$hashed",
        full_name="Grades Student",
        target_grades={"9708": "A"},
    )

    # Update target grades
    student.update_profile(target_grades={"9708": "A*", "9706": "A"})

    assert student.target_grades == {"9708": "A*", "9706": "A"}
    assert student.full_name == "Grades Student"  # Unchanged
    assert student.updated_at is not None


def test_student_update_profile_both():
    """Test updating both full_name and target_grades"""
    student = Student(
        email="both@example.com",
        password_hash="$2b$12$hashed",
        full_name="Old Name",
    )

    student.update_profile(
        full_name="New Name",
        target_grades={"9708": "A*"},
    )

    assert student.full_name == "New Name"
    assert student.target_grades == {"9708": "A*"}
    assert student.updated_at is not None


def test_student_update_profile_no_args():
    """Test calling update_profile with no arguments (should still update timestamp)"""
    student = Student(
        email="noargs@example.com",
        password_hash="$2b$12$hashed",
        full_name="Test",
    )

    original_name = student.full_name
    student.update_profile()

    assert student.full_name == original_name
    assert student.updated_at is not None  # Timestamp still updated


def test_student_repr():
    """Test string representation of Student"""
    student = Student(
        email="repr@example.com",
        password_hash="$2b$12$hashed",
        full_name="Repr Test",
    )

    repr_str = repr(student)
    assert "Student" in repr_str
    assert "repr@example.com" in repr_str
    assert "Repr Test" in repr_str
    assert str(student.id) in repr_str


# Database tests (requires session fixture)


def test_student_save_to_database(session: Session):
    """Test saving Student to database"""
    student = Student(
        email="db@example.com",
        password_hash="$2b$12$hashed",
        full_name="DB Test",
    )

    session.add(student)
    session.commit()

    # Verify saved
    statement = select(Student).where(Student.email == "db@example.com")
    saved_student = session.exec(statement).first()

    assert saved_student is not None
    assert saved_student.email == "db@example.com"
    assert saved_student.full_name == "DB Test"


def test_student_email_uniqueness(session: Session):
    """Test that duplicate emails violate unique constraint"""
    from sqlalchemy.exc import IntegrityError

    # Create first student
    student1 = Student(
        email="unique@example.com",
        password_hash="$2b$12$hashed1",
        full_name="First",
    )
    session.add(student1)
    session.commit()

    # Try to create second student with same email
    student2 = Student(
        email="unique@example.com",  # Same email!
        password_hash="$2b$12$hashed2",
        full_name="Second",
    )
    session.add(student2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        session.commit()


def test_student_target_grades_json_storage(session: Session):
    """Test that target_grades dict is properly stored as JSON"""
    target_grades = {
        "9708": "A*",
        "9706": "A",
        "9709": "B",
    }

    student = Student(
        email="json@example.com",
        password_hash="$2b$12$hashed",
        full_name="JSON Test",
        target_grades=target_grades,
    )

    session.add(student)
    session.commit()

    # Retrieve and verify JSON field
    statement = select(Student).where(Student.email == "json@example.com")
    saved_student = session.exec(statement).first()

    assert saved_student.target_grades == target_grades
    assert isinstance(saved_student.target_grades, dict)
