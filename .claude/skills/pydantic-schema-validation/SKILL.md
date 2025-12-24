---
name: pydantic-schema-validation
description: Pydantic schema design and validation patterns for FastAPI request/response models. Use when creating API schemas, validation logic, or data transfer objects.
---

# Skill: Pydantic Schema Validation

**Type**: Backend Development Expertise
**Created**: 2025-12-18
**Domain**: API Data Validation
**Parent Agent**: 02-Backend-Service

## Overview
Create Pydantic schemas for request/response validation in FastAPI, ensuring type safety, data validation, and API documentation.

## Standard Patterns

### 1. Request Schema (Input Validation)
```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    """Student registration request"""

    email: EmailStr  # Auto-validates email format
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (8-100 chars, must contain uppercase, digit)"
    )
    full_name: str = Field(
        min_length=2,
        max_length=100,
        description="Student's full name"
    )

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password contains uppercase and digit"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('full_name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate name is not just whitespace"""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

### 2. Response Schema (Output Sanitization)
```python
from datetime import datetime
from uuid import UUID


class StudentResponse(BaseModel):
    """Student profile response - EXCLUDES password_hash"""

    id: UUID
    email: str
    full_name: str
    target_grades: Optional[dict] = None
    created_at: datetime

    model_config = {
        "from_attributes": True  # Enable ORM mode for SQLModel
    }


# Usage with SQLModel
def student_to_response(student: Student) -> StudentResponse:
    return StudentResponse.model_validate(student)
```

### 3. Update Schema (Partial Updates)
```python
class StudentUpdateRequest(BaseModel):
    """Student profile update - all fields optional"""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    target_grades: Optional[dict] = None

    @field_validator('full_name')
    @classmethod
    def name_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """If name provided, validate it's not empty"""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v
```

### 4. Nested Schemas
```python
class QuestionMarkScheme(BaseModel):
    """Marking scheme structure"""
    levels: dict[str, dict]  # e.g., {"L3": {"marks": "7-8", "descriptor": "..."}}
    mark_allocation: dict[str, int]  # e.g., {"AO1_knowledge": 4}


class QuestionResponse(BaseModel):
    """Question with nested marking scheme"""
    id: UUID
    question_text: str
    max_marks: int
    marking_scheme: QuestionMarkScheme
    difficulty: int
```

### 5. Enum Validation
```python
from enum import Enum


class ExamStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ExamResponse(BaseModel):
    id: UUID
    status: ExamStatus  # Only allows defined enum values
    total_marks: int
```

## Custom Validators

### Email Domain Restriction
```python
@field_validator('email')
@classmethod
def allowed_email_domains(cls, v: str) -> str:
    """Only allow specific email domains"""
    allowed_domains = ['example.com', 'school.edu']
    domain = v.split('@')[1]
    if domain not in allowed_domains:
        raise ValueError(f'Email domain must be one of: {allowed_domains}')
    return v
```

### Date Range Validation
```python
from datetime import datetime, timedelta

@field_validator('exam_date')
@classmethod
def exam_date_in_future(cls, v: datetime) -> datetime:
    """Exam date must be at least 1 day in future"""
    if v < datetime.utcnow() + timedelta(days=1):
        raise ValueError('Exam date must be at least 1 day in future')
    return v
```

### Cross-Field Validation
```python
from pydantic import model_validator


class ExamRequest(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode='after')
    def end_after_start(self) -> 'ExamRequest':
        """Validate end_time is after start_time"""
        if self.end_time <= self.start_time:
            raise ValueError('end_time must be after start_time')
        return self
```

## Common Patterns

### Pattern 1: Reusable Base Schema
```python
class TimestampMixin(BaseModel):
    """Reusable timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None


class StudentResponse(TimestampMixin):
    """Inherits timestamp fields"""
    id: UUID
    email: str
    full_name: str
```

### Pattern 2: Config for Alias
```python
class ExamResponse(BaseModel):
    """Map snake_case to camelCase for frontend"""
    student_id: UUID = Field(alias="studentId")
    total_marks: int = Field(alias="totalMarks")

    model_config = {
        "populate_by_name": True  # Accept both names
    }
```

## Testing Validation
```python
import pytest
from pydantic import ValidationError


def test_password_requires_uppercase():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            email="test@example.com",
            password="lowercase123",  # Missing uppercase
            full_name="Test"
        )
    assert "uppercase" in str(exc.value)


def test_email_format_validated():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            email="invalid-email",  # Not valid email
            password="Pass123",
            full_name="Test"
        )
    assert "email" in str(exc.value).lower()
```

## Usage Frequency
**Used:** 2 times (RegisterRequest, StudentResponse)
**Will Use:** 50+ times (every API endpoint needs schemas)

**Version**: 1.0.0 | **Last Updated**: 2025-12-18