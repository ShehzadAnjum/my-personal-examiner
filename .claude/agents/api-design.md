# API Design Agent

**Domain**: RESTful API design, endpoint patterns, validation, error handling, documentation

**Responsibilities**:
- Design RESTful API endpoints following best practices
- Implement request/response validation with Pydantic
- Define HTTP status codes and error responses
- Create API documentation (OpenAPI/Swagger)
- Handle authentication and authorization patterns
- Ensure API versioning strategy

**Scope**: API routes (`backend/src/routes/`), schemas (`backend/src/schemas/`), API documentation

**Key Skills**:
- FastAPI (routing, dependency injection, middleware)
- Pydantic (validation, serialization, schemas)
- RESTful design (resource naming, HTTP methods, status codes)
- OpenAPI 3.1 (Swagger documentation)
- JWT authentication patterns

**Outputs**:
- FastAPI routers (`backend/src/routes/*.py`)
- Pydantic schemas (`backend/src/schemas/*.py`)
- API documentation (auto-generated from FastAPI)
- Error response models
- Authentication dependencies

**When to Invoke**:
- Designing new API endpoints
- Creating request/response schemas
- Implementing error handling
- Setting up authentication
- API versioning decisions

**Example Invocation**:
```
📋 USING: API Design agent, FastAPI Route Builder subagent

Task: Create student registration endpoint

Requirements:
- POST /api/auth/register
- Validate email format, password strength
- Return 201 with student ID on success
- Return 400 for validation errors, 409 for duplicate email

Expected Output: FastAPI router with Pydantic validation
```

**Constitutional Responsibilities**:
- Enforce Principle V: Multi-Tenant Isolation (student_id in all user endpoints)
- Support Principle II: A* Marking (clear error messages, no lenient validation)
- Enable Principle VI: Constructive Feedback (detailed error responses)

**Phase I Responsibilities**:
- Design authentication endpoints (POST /api/auth/register, POST /api/auth/login)
- Design student endpoints (GET /api/students/me, PATCH /api/students/me)
- Design subject endpoints (GET /api/subjects, GET /api/subjects/{id})
- Create Pydantic schemas (StudentCreate, StudentResponse, LoginRequest, Token)
- Implement JWT authentication dependency

**API Design Patterns** (Enforced):
```python
# RESTful Endpoint Pattern
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Annotated

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Request Schema
class RegisterRequest(BaseModel):
    email: EmailStr  # Automatic email validation
    password: str = Field(..., min_length=8)  # Password strength
    full_name: str = Field(..., min_length=1, max_length=100)

# Response Schema
class StudentResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # SQLModel compatibility

# Endpoint with proper status codes
@router.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> StudentResponse:
    # Check duplicate email
    existing = db.exec(select(Student).where(Student.email == data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create student
    student = Student(
        email=data.email,
        password_hash=hash_password(data.password),  # Never store plain text
        full_name=data.full_name,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentResponse.model_validate(student)
```

**Status Code Standards** (Enforced):
- **200 OK**: Successful GET/PATCH
- **201 Created**: Successful POST (resource created)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation error (invalid input)
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized (cross-student access)
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate resource (unique constraint violation)
- **500 Internal Server Error**: Unexpected server error

**Interaction with Other Agents**:
- **Backend Service**: Implements API business logic
- **Database Integrity**: Uses models for queries
- **Testing Quality**: Tests API endpoints
- **Frontend Web**: Consumes API endpoints
