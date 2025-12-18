# Phase I: Core Infrastructure - Instructions

**Phase**: I of V
**Status**: ✅ COMPLETE
**Dates**: Dec 16-18, 2025
**Deliverables**: Authentication, Database, Testing (40 tests, 82% coverage)

---

## 🎯 Phase I Objectives

**Primary Goal**: Establish foundation for multi-tenant A-Level teaching system

**Key Deliverables**:
1. ✅ SpecKitPlus structure (.specify/, specs/, history/)
2. ✅ Constitution ratified (8 → 11 principles)
3. ✅ Student authentication (register, login with bcrypt)
4. ✅ Multi-tenant database (PostgreSQL, student_id filtering)
5. ✅ Testing infrastructure (pytest, 40 tests, 82% coverage)
6. ✅ Phase gate validation script
7. ✅ Vercel deployment (production-ready)

**Technology Stack**:
- Backend: Python 3.12+, FastAPI 0.115+, SQLModel 0.0.22+
- Database: PostgreSQL 16 (Neon Serverless)
- Auth: bcrypt password hashing (work factor 12)
- Package Manager: UV 0.5+
- Testing: pytest 8.3+, pytest-cov 7.0.0
- Deployment: Vercel (serverless)

---

## 📋 Phase I-Specific Patterns

### 1. Multi-Tenant Query Pattern (CONSTITUTIONAL)

**EVERY database query MUST include student_id filter:**

```python
# ✅ CORRECT - Filtered by student_id
def get_student_exams(student_id: UUID, session: Session):
    return session.exec(
        select(Exam).where(Exam.student_id == student_id)
    ).all()

# ❌ PROHIBITED - Unfiltered query (security violation)
def get_all_exams(session: Session):
    return session.exec(select(Exam)).all()  # CONSTITUTIONAL VIOLATION
```

**Skill**: Use `.claude/skills/multi-tenant-query-pattern.md`

### 2. SQLModel Schema Design Pattern

**Pattern**: UUID primary keys, JSONB for flexible data, indexes on foreign keys

```python
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4

class Student(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)  # bcrypt hash
    target_grades: dict | None = Field(default=None, sa_column=Column(JSON))
```

**Skill**: Use `.claude/skills/sqlmodel-database-schema-design.md`

### 3. FastAPI Route Implementation Pattern

**Pattern**: Dependency injection, Pydantic validation, proper status codes

```python
@router.post("/register", response_model=StudentResponse, status_code=201)
def register(
    registration_data: RegisterRequest,
    session: SessionDep,  # Dependency injection
) -> StudentResponse:
    try:
        student = create_student(session, registration_data)
        return student_to_response(student)
    except EmailAlreadyExistsError:
        raise HTTPException(409, "Email already registered")
```

**Skill**: Use `.claude/skills/fastapi-route-implementation.md`

### 4. Password Security Pattern (CONSTITUTIONAL)

**Pattern**: bcrypt hashing (work factor 12), never store plain text

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12  # Constitutional requirement
)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**Skill**: Use `.claude/skills/bcrypt-password-hashing.md`
**Constitutional Principle**: I - Password hashing mandatory

### 5. Testing Pattern (>80% Coverage Required)

**Pattern**: conftest.py fixtures, unit + integration tests

```python
# tests/conftest.py
@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

**Skill**: Use `.claude/skills/pytest-testing-patterns.md`
**Constitutional Principle**: VII - Phase gates require >80% coverage

---

## 🔐 Phase I Security Requirements

### 1. Password Security
- ✅ bcrypt hashing (work factor 12)
- ✅ Minimum 8 characters (Pydantic validation)
- ✅ Never expose password_hash in API responses
- ✅ Constant-time verification (timing attack prevention)

### 2. Multi-Tenant Isolation
- ✅ student_id column in all user-scoped tables
- ✅ student_id index for query performance
- ✅ student_id filter in ALL queries
- ✅ JWT token verification (Phase IV)

### 3. API Security
- ✅ Email validation (EmailStr type)
- ✅ Generic error messages (don't reveal if email exists)
- ✅ No secrets in code (all in .env)
- ✅ Pre-commit hooks (block secrets)

---

## 🧪 Phase I Testing Requirements

### Coverage Targets
- **Overall**: 82% achieved (exceeds 80% target)
- **Models**: 100% coverage
- **Services**: 100% coverage
- **Routes**: 90% coverage
- **Schemas**: 100% coverage

### Test Structure
```
tests/
├── conftest.py            # Shared fixtures
├── unit/
│   ├── test_student_model.py      # 11 tests
│   └── test_student_service.py    # 11 tests
└── integration/
    └── test_auth_routes.py        # 18 tests
```

### Running Tests
```bash
cd backend

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_student_model.py -v

# Phase gate validation
cd ..
./scripts/check-phase-1-complete.sh
```

---

## 📦 Phase I Dependencies

### Backend (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "psycopg[binary]>=3.2.0",
    "python-dotenv>=1.0.0",
    "passlib[bcrypt]>=1.7.0",
    "bcrypt>=4.0.0,<5.0.0",  # 4.x for passlib compatibility
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

### Critical Version Constraints
- ✅ `bcrypt>=4.0.0,<5.0.0` (5.x breaks passlib)
- ✅ `sqlmodel>=0.0.22` (Field import fix)
- ✅ `fastapi>=0.115.0` (ASGI support)

---

## 🚀 Phase I Deployment

### Vercel Configuration
**File**: `backend/vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Vercel Entry Point
**File**: `backend/api/index.py`
```python
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from src.main import app  # Vercel detects ASGI automatically
```

**Skill**: Use `.claude/skills/vercel-fastapi-deployment.md`

### Environment Variables (Vercel)
```bash
DATABASE_URL="postgresql://..."  # Neon PostgreSQL
SECRET_KEY="..."                  # JWT secret (Phase IV)
ENVIRONMENT="production"
```

---

## ✅ Phase Gate Validation

### Script Location
`/home/anjum/dev/my_personal_examiner/scripts/check-phase-1-complete.sh`

### Checks Performed
1. ✅ Test coverage >80%
2. ✅ All tests passing
3. ✅ POST /api/auth/register implemented
4. ✅ POST /api/auth/login implemented
5. ✅ Student model exists
6. ✅ Multi-tenant anchor (student_id) present
7. ✅ Password hashing with bcrypt
8. ✅ Alembic migrations created
9. ✅ Environment configuration (.env.example)
10. ✅ Dependencies configured (pyproject.toml)

### Running Phase Gate
```bash
cd /home/anjum/dev/my_personal_examiner
./scripts/check-phase-1-complete.sh
```

**Result**: ✅ All gates passed (2025-12-18)

---

## 📚 Phase I Skills & Agents

### Primary Agents Used
- **Agent 02 - Backend Service** (FastAPI, SQLModel, database)
- **Agent 07 - Testing Quality** (pytest, coverage, test strategy)
- **Agent 09 - Deployment** (Vercel, serverless configuration)

### Skills Created
1. `vercel-fastapi-deployment` - Vercel serverless deployment
2. `sqlmodel-database-schema-design` - Multi-tenant DB schemas
3. `fastapi-route-implementation` - REST API endpoints
4. `multi-tenant-query-pattern` - student_id filtering
5. `pydantic-schema-validation` - API validation
6. `bcrypt-password-hashing` - Password security
7. `pytest-testing-patterns` - Testing infrastructure
8. `uv-package-management` - Dependency management
9. `alembic-migration-creation` - Database migrations

---

## 🔄 Lessons Learned (Phase I)

### What Worked Well
1. ✅ SQLModel + FastAPI integration (clean, type-safe)
2. ✅ Neon PostgreSQL (serverless, no cold starts)
3. ✅ UV package manager (10x faster than pip)
4. ✅ pytest + TestClient (easy integration testing)
5. ✅ Constitutional principles (prevented security issues)

### What Needed Correction
1. ⚠️ Methodology: Skipped /sp.specify → /sp.plan workflow (fixed)
2. ⚠️ CLAUDE.md: Monolithic 936-line file (now hierarchical)
3. ⚠️ Skills: Created without checking official catalog (now mandatory)
4. ⚠️ Pre-commit hook: pytest not installed initially (fixed)

### What to Carry Forward
1. ✅ Phase gate validation (excellent quality control)
2. ✅ Multi-tenant pattern (security-first approach)
3. ✅ Skills documentation (enables reuse)
4. ✅ 82% test coverage (exceeds target)

---

## 🚦 Phase I → Phase II Transition

### Prerequisites for Phase II
1. ✅ Phase I gate script passes
2. ✅ All 40 tests passing
3. ✅ 82% test coverage achieved
4. ✅ Vercel deployment successful
5. ✅ Constitution updated (11 principles)
6. ✅ CLAUDE.md reorganized (hierarchical)

### Phase II Preparation
**MUST use SpecKitPlus workflow**:
1. `/sp.specify phase-2-question-bank`
2. `/sp.clarify` (PDF formats, question numbering)
3. `/sp.plan` (architecture)
4. `/sp.tasks` (atomic tasks)
5. `/sp.implement` (execute tasks)

**See**: `specs/phase-2-question-bank/CLAUDE.md` (to be created)

---

**Phase I Status**: ✅ COMPLETE
**Next Phase**: Phase II (Question Bank & Exam Generation)
**Version**: 1.0.0 | **Last Updated**: 2025-12-18
