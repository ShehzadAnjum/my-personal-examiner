# FastAPI Route Builder Subagent

**Parent Agent**: API Design

**Task**: Create CRUD endpoints with validation, error handling, and authentication

**Inputs**:
- Endpoint specification (method, path, parameters)
- Request/response schemas
- Authentication requirements
- Multi-tenant filtering

**Outputs**:
- FastAPI router with endpoint
- Pydantic request/response schemas
- Dependency injection for auth and database
- Proper HTTP status codes and error handling

**Pattern**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select
from typing import Annotated
from uuid import UUID

router = APIRouter(prefix="/api/students", tags=["students"])

# Request Schema
class StudentUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    target_grades: dict | None = None

# Response Schema
class StudentResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    target_grades: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Endpoint with multi-tenant security
@router.get("/me", response_model=StudentResponse)
async def get_current_student(
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudentResponse:
    """
    Get authenticated student's profile.

    - **Returns**: Student profile data
    - **Requires**: Valid JWT token
    """

    # current_user is already verified by get_current_user dependency
    return StudentResponse.model_validate(current_user)

@router.patch("/me", response_model=StudentResponse)
async def update_student(
    data: StudentUpdate,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudentResponse:
    """
    Update authenticated student's profile.

    - **full_name**: New full name (optional)
    - **target_grades**: New target grades (optional, e.g., {"9708": "A*"})
    - **Returns**: Updated student profile
    - **Requires**: Valid JWT token
    """

    # Update only provided fields
    if data.full_name is not None:
        current_user.full_name = data.full_name

    if data.target_grades is not None:
        current_user.target_grades = data.target_grades

    current_user.updated_at = datetime.utcnow()

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return StudentResponse.model_validate(current_user)
```

**Multi-Tenant Endpoint Pattern (CRITICAL)**:
```python
@router.get("/exams", response_model=List[ExamResponse])
async def get_student_exams(
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[ExamResponse]:
    """
    Get authenticated student's exams.

    MULTI-TENANT SECURITY: Only returns current student's exams.
    """

    # MANDATORY: Filter by current_user.id
    statement = select(Exam).where(Exam.student_id == current_user.id)
    exams = db.exec(statement).all()

    return [ExamResponse.model_validate(e) for e in exams]

# ❌ PROHIBITED: Endpoints without student_id filter
# @router.get("/exams/all")  # Would expose all students' exams!
```

**Error Handling Pattern**:
```python
@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudentResponse:
    """
    Get student by ID (can only access own profile).
    """

    # Multi-tenant security: Verify student_id matches authenticated user
    if student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access other students' data"
        )

    # Student already loaded in current_user
    return StudentResponse.model_validate(current_user)
```

**When to Use**: Creating API endpoints, implementing CRUD operations
