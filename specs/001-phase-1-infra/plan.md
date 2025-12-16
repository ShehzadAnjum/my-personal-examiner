# Implementation Plan: Phase I - Core Infrastructure & Database

**Branch**: `001-phase-1-infra` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-1-infra/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase I establishes the foundational infrastructure for the PhD-level A-Level teaching system. Primary requirements:

1. **Multi-Tenant Database**: PostgreSQL 16 (via Neon) with SQLModel ORM, enforcing strict student data isolation
2. **Student Authentication**: JWT-based authentication with 24-hour token expiration, secure password hashing
3. **Core API**: RESTful FastAPI endpoints for student registration, login, profile management, and subject listing
4. **Database Migrations**: Alembic-managed schema versioning with rollback capability
5. **Testing Infrastructure**: pytest-based test suite achieving >80% coverage

**Technical Approach**: Use FastAPI + SQLModel stack (locked by constitution) with multi-tenant security pattern (student_id filters on all user-scoped queries). Prioritize user stories by dependency: authentication (P1) gates all other features, subject listing (P2) requires authentication, profile management (P3) enhances but doesn't gate.

**Success Criteria**: Students can register, authenticate, and access their profiles within 2 minutes. System prevents 100% of cross-student data access attempts. All tests pass with >80% coverage.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22+, Pydantic 2.0+, Alembic 1.13+
**Storage**: PostgreSQL 16 (Neon managed database)
**Testing**: pytest 8.3+, pytest-cov (coverage), pytest-asyncio (async support)
**Target Platform**: Linux server (Railway for Phase IV, Azure Container Apps for production)
**Project Type**: Web application (backend API + future frontend)
**Performance Goals**: API p95 latency <200ms, support 100 concurrent users (Phase I target), 1000+ users (production)
**Constraints**: <500ms for 95% of profile requests, zero data leakage between students (100% isolation), >80% test coverage mandatory
**Scale/Scope**: MVP scope - 4 models (Student, Subject, SyllabusPoint, AuthToken), 8 API endpoints, 1 initial subject (Economics 9708), ~500 LOC production code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Subject Accuracy is Non-Negotiable
**Status**: ✅ PASS
**Rationale**: Phase I does not create educational content. Economics 9708 subject data will be seeded from official Cambridge syllabus (2023-2025). All syllabus references verified against current Cambridge International website.

### Principle II: A* Standard Marking Always
**Status**: ✅ PASS (N/A for Phase I)
**Rationale**: Phase I establishes infrastructure only. No marking functionality implemented until Phase III. When marking is implemented, >85% accuracy threshold will be enforced via constitution.

### Principle III: Syllabus Synchronization First
**Status**: ✅ PASS
**Rationale**: Economics 9708 syllabus data (2023-2025) will be verified current before database seeding. Phase I includes `syllabus_year` field in Subject model to track versions. Monthly sync mechanism designed for Phase II.

### Principle IV: Spec-Driven Development (No Code Before Spec)
**Status**: ✅ PASS
**Rationale**: This plan created via `/sp.plan` command after spec created via `/sp.specify`. Tasks will be generated via `/sp.tasks` before implementation. Full SpecKit workflow followed.

### Principle V: Multi-Tenant Isolation is Sacred
**Status**: ✅ PASS (CRITICAL for Phase I)
**Rationale**: Database schema designed with student_id on all user-scoped tables (Exam, Attempt, Progress). All queries will include `WHERE student_id = :current_user_id` filter. Authentication middleware enforces JWT validation. Unit tests will verify cross-student access prevention (SC-004: 100% isolation).

**Enforcement**:
- Database indexes: `idx_student_exams (student_id, created_at)`
- API pattern: `@router.get("/exams")` filters by `current_user.id` from JWT
- Pre-commit hook: grep for unfiltered `.all()` queries
- Tests: `test_student_cannot_access_other_student_data()`

### Principle VI: Feedback is Constructive and Detailed
**Status**: ✅ PASS (N/A for Phase I)
**Rationale**: Phase I establishes API infrastructure. No feedback generation until Phase III. When implemented, feedback will follow WHY + HOW structure per constitution.

### Principle VII: Phase Boundaries Are Hard Gates
**Status**: ✅ PASS
**Rationale**: Phase I gate script (`scripts/check-phase-1-complete.sh`) will verify:
- All tests passing (>80% coverage)
- All database migrations applied
- All API endpoints functional
- No secrets in code
- SESSION_HANDOFF.md updated

Phase II work cannot begin until Phase I gate passes and user approves.

### Principle VIII: Question Bank Quality Over Quantity
**Status**: ✅ PASS (N/A for Phase I)
**Rationale**: No questions created in Phase I. Database schema includes `source_paper` field for future question tracking (Phase II). All questions will cite Cambridge source.

**Constitution Check Result**: ✅ ALL PRINCIPLES PASS - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment configuration
│   ├── database.py                # SQLModel engine, session management
│   │
│   ├── models/                    # SQLModel database models
│   │   ├── __init__.py
│   │   ├── student.py             # Student model (multi-tenant anchor)
│   │   ├── subject.py             # Subject model (Economics 9708, etc.)
│   │   └── syllabus_point.py      # SyllabusPoint model (learning objectives)
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── student.py             # StudentCreate, StudentResponse, StudentUpdate
│   │   ├── auth.py                # LoginRequest, TokenResponse, RegisterRequest
│   │   └── subject.py             # SubjectResponse
│   │
│   ├── routes/                    # FastAPI routers
│   │   ├── __init__.py
│   │   ├── auth.py                # POST /api/auth/register, /api/auth/login
│   │   ├── students.py            # GET/PATCH /api/students/me
│   │   └── subjects.py            # GET /api/subjects
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # JWT generation, password hashing
│   │   └── student_service.py     # Student CRUD operations
│   │
│   └── dependencies.py            # FastAPI dependencies (get_db, get_current_user)
│
├── alembic/                       # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py  # Create students, subjects, syllabus_points tables
│   ├── env.py
│   └── script.py.mako
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures (db_session, test_client, test_user)
│   │
│   ├── unit/                      # Unit tests (models, services)
│   │   ├── test_models.py         # Test Student, Subject, SyllabusPoint models
│   │   └── test_services.py       # Test auth_service, student_service
│   │
│   ├── integration/               # Integration tests (API endpoints)
│   │   ├── test_auth_routes.py    # Test registration, login endpoints
│   │   ├── test_student_routes.py # Test profile get/update endpoints
│   │   └── test_subject_routes.py # Test subject listing endpoint
│   │
│   └── e2e/                       # End-to-end tests (user flows)
│       └── test_student_journey.py # Test register → login → profile flow
│
├── pyproject.toml                 # UV dependencies (FastAPI, SQLModel, pytest)
├── uv.lock                        # UV lock file
├── alembic.ini                    # Alembic configuration
├── .env.example                   # Environment variables template
└── README.md                      # Backend setup instructions

frontend/                          # (Phase IV - not implemented in Phase I)
├── app/                           # Next.js 16 App Router
├── components/                    # React components
└── package.json                   # npm dependencies
```

**Structure Decision**: Web application architecture (Option 2) selected because:
1. **Backend-first approach**: Phase I focuses on API foundation before UI (Phase IV)
2. **Separation of concerns**: Backend (FastAPI/Python) and frontend (Next.js/TypeScript) have distinct toolchains
3. **Independent deployment**: Backend to Railway/Azure, frontend to Vercel
4. **Multi-tenant security**: Backend enforces student_id isolation before frontend exists
5. **SpecKitPlus pattern**: evolution_to_do uses backend/ + frontend/ for web apps

Phase I implements **backend/** only. Frontend structure defined but not implemented until Phase IV.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No constitutional violations detected.** All 8 principles pass. No complexity justification required.
