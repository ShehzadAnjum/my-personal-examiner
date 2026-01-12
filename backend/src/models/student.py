"""
Student Model

Multi-tenant anchor entity for the system.
All user-scoped data must be filtered by student_id (Constitutional Principle V).

Constitutional Requirements:
- Passwords MUST be bcrypt-hashed (never plain text) - Principle I
- Email MUST be unique - FR-001
- Multi-tenant isolation enforced - Principle V
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    """
    Student entity

    Represents a student user of the system.
    This is the anchor entity for multi-tenant architecture.

    Attributes:
        id: Unique student identifier (UUID primary key)
        email: Student email address (unique, used for login)
        password_hash: bcrypt-hashed password (work factor 12)
        full_name: Student's full name
        target_grades: Target grades by subject code, e.g., {"9708": "A*"}
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp

    Examples:
        >>> student = Student(
        ...     email="john@example.com",
        ...     password_hash="$2b$12$...",  # bcrypt hash
        ...     full_name="John Doe",
        ...     target_grades={"9708": "A*", "9706": "A"}
        ... )

    Constitutional Compliance:
        - Principle V: This is the multi-tenant anchor entity
        - Principle I: password_hash must always be bcrypt, never plain text
        - FR-001 to FR-004: Email validation, password requirements enforced
    """

    __tablename__ = "students"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Authentication Fields (SECURITY CRITICAL)
    email: str = Field(
        unique=True,
        nullable=False,
        index=True,
        max_length=255,
        description="Student email address (login credential)",
    )

    password_hash: str = Field(
        nullable=False,
        max_length=255,
        description="bcrypt-hashed password (work factor 12)",
    )

    # Profile Fields
    full_name: str = Field(
        nullable=False,
        max_length=100,
        description="Student's full name",
    )

    target_grades: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description='Target grades by subject, e.g., {"9708": "A*"}',
    )

    # Admin Flag (Resource Bank feature - 006)
    is_admin: bool = Field(
        default=False,
        nullable=False,
        description="Whether student has admin privileges for content generation",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Account creation timestamp",
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last profile update timestamp",
    )

    # Validation methods
    def update_profile(self, full_name: Optional[str] = None, target_grades: Optional[dict] = None) -> None:
        """
        Update student profile

        Args:
            full_name: New full name (optional)
            target_grades: New target grades dict (optional)
        """
        if full_name is not None:
            self.full_name = full_name
        if target_grades is not None:
            self.target_grades = target_grades
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Student(id={self.id}, email={self.email}, name={self.full_name})>"
