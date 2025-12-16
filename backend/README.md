# My Personal Examiner - Backend API

PhD-level A-Level Teaching & Examination System - Backend API

## Phase I: Core Infrastructure & Database

**Status**: In Development (Phase 1 - Setup)

## Technology Stack (Constitutional Locks)

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel 0.0.22+ (MANDATORY)
- **Database**: PostgreSQL 16 via Neon
- **Migrations**: Alembic 1.13+
- **Testing**: pytest 8.3+ (>80% coverage required)
- **Package Manager**: UV 0.5+

## Quick Start

See `specs/001-phase-1-infra/quickstart.md` for detailed setup instructions.

```bash
# Install dependencies
uv sync --all-extras

# Run server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest -v --cov=src
```

## Documentation

- Specification: `specs/001-phase-1-infra/spec.md`
- Implementation Plan: `specs/001-phase-1-infra/plan.md`
- Tasks: `specs/001-phase-1-infra/tasks.md`
- API Contract: `specs/001-phase-1-infra/contracts/openapi.yaml`

## Constitutional Compliance

This project follows 8 non-negotiable principles defined in `.specify/memory/constitution.md`.

**Critical Principles**:
- Principle V: Multi-Tenant Isolation (student_id filtering mandatory)
- Principle VII: Phase Gates (>80% test coverage required)

## License

Proprietary - My Personal Examiner
