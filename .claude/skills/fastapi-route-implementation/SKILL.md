---
skill-name: fastapi-route-implementation
type: Backend Development Expertise
domain: API Development
parent-agent: 02-Backend-Service
version: 1.1.0
last-updated: 2025-12-24
constitutional-principles: [II, V, VI]
capabilities:
  - FastAPI router setup with prefix and tags
  - POST endpoints for resource creation (201 Created)
  - POST endpoints for authentication (200 OK with JWT)
  - GET endpoints with authentication (protected routes)
  - GET endpoints with filtering and pagination
  - PATCH endpoints for resource updates
  - DELETE endpoints with soft delete
  - Multi-tenant security (student_id verification)
  - Error handling (domain errors → HTTP errors)
  - Pydantic validation with custom validators
  - OpenAPI documentation (summary, description, examples)
---

# Skill: FastAPI Route Implementation

**Type**: Backend Development Expertise
**Created**: 2025-12-18
**Domain**: API Development
**Parent Agent**: 02-Backend-Service

## Overview
Implement RESTful API endpoints using FastAPI with proper error handling, validation, and multi-tenant security for My Personal Examiner project.

## Constitutional Requirements
- **Principle V**: Multi-tenant isolation - all routes must verify student_id
- **Principle II**: A* standard - strict validation, detailed error messages
- **Principle VI**: Constructive feedback - error messages explain WHY and HOW

## Prerequisites
- FastAPI 0.115+ installed
- Pydantic schemas defined
- SQLModel database models created
- Service layer functions implemented

## Standard Pattern

### 1. Router Setup
```python
# backend/src/routes/auth.py
from fastapi import APIRouter, HTTPException, status

from src.database import SessionDep
from src.schemas.auth import RegisterRequest, LoginRequest, StudentResponse
from src.services.student_service import (
    create_student,
    authenticate_student,
    EmailAlreadyExistsError,
    InvalidCredentialsError
)

# Create router with prefix and tags
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)
```

### 2. POST Endpoint (Create Resource)
```python
@router.post(
    "/register",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new student account",
    description="""
    Create a new student account with email and password.

    **Requirements**:
    - Email must be unique (409 if duplicate)
    - Password minimum 8 characters
    - Password hashed with bcrypt (work factor 12)

    **Returns**:
    - 201 Created: Student account created successfully
    - 400 Bad Request: Invalid email or password format
    - 409 Conflict: Email already registered
    """,
    responses={
        201: {
            "description": "Student created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "student@example.com",
                        "full_name": "John Doe",
                        "created_at": "2025-12-18T10:30:00Z"
                    }
                }
            }
        },
        409: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
def register(
    registration_data: RegisterRequest,
    session: SessionDep,
) -> StudentResponse:
    """
    Register new student account.

    Delegates to service layer for business logic.
    Service layer handles password hashing and validation.

    Args:
        registration_data: Email, password, full_name
        session: Database session (injected via dependency)

    Returns:
        StudentResponse: Created student profile (no password_hash)

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Invalid input data (handled by Pydantic)
    """
    try:
        # Delegate to service layer
        student = create_student(session, registration_data)

        # Convert to response schema (excludes password_hash)
        return student_to_response(student)

    except EmailAlreadyExistsError:
        # Domain-specific error → HTTP error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Try logging in instead."
        )

    except Exception as e:
        # Unexpected error → 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
```

### 3. POST Endpoint (Authentication)
```python
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate student and get JWT token",
)
def login(
    credentials: LoginRequest,
    session: SessionDep,
) -> TokenResponse:
    """
    Authenticate student and return JWT token.

    Args:
        credentials: Email and password
        session: Database session

    Returns:
        TokenResponse: JWT access token with expiration

    Raises:
        HTTPException 401: Invalid credentials
    """
    try:
        # Service layer handles password verification
        student = authenticate_student(session, credentials)

        # Generate JWT token (24-hour expiration)
        token = create_access_token(student.id)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=1440  # minutes
        )

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 4. GET Endpoint (Protected Route with Auth)
```python
from src.dependencies import get_current_student

@router.get(
    "/me",
    response_model=StudentResponse,
    summary="Get current student profile",
)
def get_current_student_profile(
    current_student: Student = Depends(get_current_student),
) -> StudentResponse:
    """
    Get authenticated student's profile.

    Requires valid JWT token in Authorization header.

    Args:
        current_student: Injected by get_current_student dependency

    Returns:
        StudentResponse: Student profile data
    """
    return student_to_response(current_student)
```

### 5. GET Endpoint (List Resources with Filtering)
```python
from typing import Optional
from fastapi import Query

@router.get(
    "/questions",
    response_model=list[QuestionResponse],
    summary="List questions with filters",
)
def list_questions(
    session: SessionDep,
    subject_id: Optional[UUID] = Query(None, description="Filter by subject"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty (1-5)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> list[QuestionResponse]:
    """
    List questions with optional filters.

    Query parameters:
    - subject_id: Filter by subject UUID
    - difficulty: Filter by difficulty (1-5)
    - limit: Max results (1-100, default 20)
    - offset: Pagination offset (default 0)

    Returns:
        List of questions matching filters
    """
    questions = list_questions_service(
        session,
        subject_id=subject_id,
        difficulty=difficulty,
        limit=limit,
        offset=offset
    )
    return [question_to_response(q) for q in questions]
```

### 6. PATCH Endpoint (Update Resource)
```python
@router.patch(
    "/me",
    response_model=StudentResponse,
    summary="Update current student profile",
)
def update_student_profile(
    update_data: StudentUpdateRequest,
    session: SessionDep,
    current_student: Student = Depends(get_current_student),
) -> StudentResponse:
    """
    Update authenticated student's profile.

    Only updates provided fields (partial update).

    Args:
        update_data: Fields to update (all optional)
        current_student: Authenticated student

    Returns:
        StudentResponse: Updated student profile
    """
    updated_student = update_student_service(
        session,
        student_id=current_student.id,
        update_data=update_data
    )
    return student_to_response(updated_student)
```

### 7. DELETE Endpoint (Soft Delete)
```python
@router.delete(
    "/exams/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete exam attempt",
)
def delete_exam(
    exam_id: UUID,
    session: SessionDep,
    current_student: Student = Depends(get_current_student),
) -> None:
    """
    Delete exam attempt (soft delete).

    Verifies exam belongs to current student before deletion.

    Args:
        exam_id: UUID of exam to delete
        current_student: Authenticated student

    Raises:
        HTTPException 404: Exam not found or doesn't belong to student
    """
    try:
        delete_exam_service(
            session,
            exam_id=exam_id,
            student_id=current_student.id  # Multi-tenant check
        )
    except ExamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or access denied"
        )
```

## Multi-Tenant Security Pattern

### ALWAYS Verify Ownership
```python
@router.get("/exams/{exam_id}")
def get_exam(
    exam_id: UUID,
    session: SessionDep,
    current_student: Student = Depends(get_current_student),
) -> ExamResponse:
    """Get exam details - verifies ownership"""

    # CRITICAL: Filter by BOTH exam_id AND student_id
    statement = select(Exam).where(
        Exam.id == exam_id,
        Exam.student_id == current_student.id  # Multi-tenant isolation
    )
    exam = session.exec(statement).first()

    if not exam:
        # Don't reveal if exam exists but belongs to another student
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"  # Generic message for security
        )

    return exam_to_response(exam)
```

## Error Handling Best Practices

### 1. Domain Errors → HTTP Errors
```python
# Service layer raises domain exception
class EmailAlreadyExistsError(Exception):
    """Email is already registered"""
    pass

# Route translates to HTTP exception
except EmailAlreadyExistsError:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered. Try logging in instead."
    )
```

### 2. Validation Errors (Automatic via Pydantic)
```python
# Pydantic schema with validators
class RegisterRequest(BaseModel):
    email: EmailStr  # Auto-validates email format
    password: str = Field(min_length=8, max_length=100)

    @field_validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

# FastAPI automatically returns 422 Unprocessable Entity with details
# {
#   "detail": [
#     {
#       "loc": ["body", "password"],
#       "msg": "Password must contain uppercase letter",
#       "type": "value_error"
#     }
#   ]
# }
```

### 3. Structured Error Responses
```python
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    detail: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

@router.post("/register")
def register(...):
    try:
        ...
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail=ErrorDetail(
                detail="Email already registered",
                field="email",
                suggestion="Try logging in with this email instead"
            ).model_dump()
        )
```

## Common Pitfalls

### ❌ Wrong: Missing Multi-Tenant Check
```python
@router.get("/exams/{exam_id}")
def get_exam(exam_id: UUID, session: SessionDep):
    # DANGEROUS - no student_id verification
    exam = session.get(Exam, exam_id)
    return exam
```

### ✅ Correct: Always Verify Ownership
```python
@router.get("/exams/{exam_id}")
def get_exam(
    exam_id: UUID,
    session: SessionDep,
    current_student: Student = Depends(get_current_student),
):
    statement = select(Exam).where(
        Exam.id == exam_id,
        Exam.student_id == current_student.id  # REQUIRED
    )
    exam = session.exec(statement).first()
    if not exam:
        raise HTTPException(404, "Exam not found")
    return exam
```

---

### ❌ Wrong: Exposing Internal Errors
```python
except Exception as e:
    raise HTTPException(500, detail=str(e))  # Leaks stack traces
```

### ✅ Correct: Generic Error Messages
```python
except Exception as e:
    logger.error(f"Registration failed: {e}")  # Log internally
    raise HTTPException(500, "Registration failed. Please try again.")
```

---

### ❌ Wrong: No Response Schema
```python
@router.get("/students/me")
def get_profile():
    return student  # Returns SQLModel with password_hash!
```

### ✅ Correct: Response Schema Excludes Sensitive Data
```python
@router.get("/students/me", response_model=StudentResponse)
def get_profile():
    return student  # FastAPI uses StudentResponse schema (no password_hash)
```

## Router Registration

```python
# backend/src/main.py
from src.routes import auth, students, questions, exams

app = FastAPI(...)

# Register all routers with API prefix
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(students.router, prefix="/api", tags=["students"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(exams.router, prefix="/api", tags=["exams"])
```

## Testing Routes

```python
# tests/unit/test_auth.py
from fastapi.testclient import TestClient

def test_register_success(client: TestClient):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test Student"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data  # Verify not leaked


def test_register_duplicate_email(client: TestClient, existing_student):
    response = client.post("/api/auth/register", json={
        "email": existing_student.email,  # Already exists
        "password": "TestPass123",
        "full_name": "Duplicate"
    })
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]
```

## Constitutional Compliance

**Principle V**: Multi-Tenant Isolation
- ✅ All student-scoped routes verify student_id via get_current_student
- ✅ All queries filter by student_id before returning data
- ✅ 404 errors don't reveal existence of other students' data

**Principle VI**: Constructive Feedback
- ✅ Error messages explain WHY (e.g., "Email already registered")
- ✅ Error messages suggest HOW to fix (e.g., "Try logging in instead")

## Version History

- **1.1.0** (2025-12-24): Restructured to /SKILL.md format with YAML frontmatter, added capabilities list
- **1.0.0** (2025-12-18): Initial skill creation

**Usage Frequency**: Used 1 time in Phase I (registration endpoint), will use 30+ times in Phases II-V (all API endpoints)
