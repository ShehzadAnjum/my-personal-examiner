"""
Authentication Schemas

Pydantic schemas for authentication endpoints (register, login).
Separate from database models for API request/response validation.

Constitutional Requirements:
- Password minimum 8 characters - FR-002
- Email must be valid format - FR-001
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Student registration request

    Used for POST /api/auth/register endpoint.

    Attributes:
        email: Student email address (must be unique)
        password: Plain text password (will be hashed before storage)
        full_name: Student's full name

    Examples:
        >>> request = RegisterRequest(
        ...     email="john@example.com",
        ...     password="SecurePass123",
        ...     full_name="John Doe"
        ... )

    Constitutional Compliance:
        - FR-001: Email validation (EmailStr ensures valid format)
        - FR-002: Password minimum 8 characters
    """

    email: EmailStr = Field(
        ...,
        description="Student email address (must be unique)",
        examples=["student@example.com"],
    )

    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123"],
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Student's full name",
        examples=["John Doe"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe",
            }
        }
    }


class LoginRequest(BaseModel):
    """
    Student login request

    Used for POST /api/auth/login endpoint.

    Attributes:
        email: Student email address
        password: Plain text password (will be verified against stored hash)

    Examples:
        >>> request = LoginRequest(
        ...     email="john@example.com",
        ...     password="SecurePass123"
        ... )

    Constitutional Compliance:
        - FR-001: Email validation (EmailStr ensures valid format)
        - FR-002: Password minimum 8 characters
    """

    email: EmailStr = Field(
        ...,
        description="Student email address",
        examples=["student@example.com"],
    )

    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123",
            }
        }
    }


class StudentResponse(BaseModel):
    """
    Student profile response

    Used for successful registration and profile endpoints.
    Does NOT include password_hash (security).

    Attributes:
        id: Unique student identifier
        email: Student email address
        full_name: Student's full name
        target_grades: Target grades by subject (optional)
        created_at: Account creation timestamp

    Examples:
        >>> response = StudentResponse(
        ...     id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     email="john@example.com",
        ...     full_name="John Doe",
        ...     target_grades={"9708": "A*"},
        ...     created_at=datetime.utcnow()
        ... )
    """

    id: UUID = Field(
        ...,
        description="Unique student identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    email: str = Field(
        ...,
        description="Student email address",
        examples=["student@example.com"],
    )

    full_name: str = Field(
        ...,
        description="Student's full name",
        examples=["John Doe"],
    )

    target_grades: Optional[dict[str, str]] = Field(
        default=None,
        description="Target grades by subject code",
        examples=[{"9708": "A*", "9706": "A"}],
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        examples=["2025-12-16T10:00:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "student@example.com",
                "full_name": "John Doe",
                "target_grades": {"9708": "A*"},
                "created_at": "2025-12-16T10:00:00Z",
            }
        }
    }
