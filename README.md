# My Personal Examiner 🎓

**PhD-level A-Level Teaching & Examination System**

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![ORM](https://img.shields.io/badge/ORM-SQLModel-DD0031)](https://sqlmodel.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

An AI-powered A-Level teaching and examination system that acts as a PhD-level teacher/examiner with 20+ years of experience. Provides strict A* standard marking, detailed feedback, and Cambridge-style exams.

## 🚀 Current Status

**Phase I-III Complete** (39.6% of Phase I goals)

✅ **Phase 1** - Setup & Project Initialization
✅ **Phase 2** - Foundational Infrastructure (Database Models)
✅ **Phase 3** - Student Registration (First Working Endpoint!)
⏸️ **Phase 4** - Authentication (Login + JWT)
⏸️ **Phase 5** - Subjects API
⏸️ **Phase 6** - Profile Management
⏸️ **Phase 7** - Testing & Quality Gates

### Working Features

- ✅ **POST /api/auth/register** - Student registration with bcrypt password hashing
- ✅ FastAPI backend with Swagger UI documentation
- ✅ SQLModel database models (Student, Subject, SyllabusPoint)
- ✅ Alembic database migrations
- ✅ Multi-tenant architecture (student-level isolation)
- ✅ Constitutional compliance enforcement

## 📚 Technology Stack

### Backend (Constitutional Locks)

- **Framework**: FastAPI 0.124.4
- **ORM**: SQLModel 0.0.27 (MANDATORY - Pydantic integration)
- **Database**: PostgreSQL 16 via Neon (serverless)
- **Migrations**: Alembic 1.17.2
- **Authentication**: JWT (24-hour expiration), bcrypt password hashing
- **Package Manager**: UV 0.5+ (10-100x faster than pip)
- **Testing**: pytest 8.3+ (>80% coverage required)

### Frontend (Phase IV)

- Next.js 16+ with App Router
- TypeScript 5.7+
- Tailwind CSS 4
- shadcn/ui components

## 🏗️ Architecture

### Multi-Tenant Design

```
Student (Anchor Entity)
├── Multi-tenant isolation enforced
├── student_id on all user-scoped tables
└── JWT-based authentication

Global Entities
├── Subject (Economics 9708 seeded)
└── SyllabusPoint (Learning objectives)
```

### Database Schema

- **students**: Email, password_hash (bcrypt), target_grades (JSON)
- **subjects**: Code, name, level, exam_board, syllabus_year
- **syllabus_points**: Subject FK, code, description, topics

## 🚀 Deployment Setup

### 1. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/new)
2. Import repository: `https://github.com/ShehzadAnjum/my-personal-examiner`
3. Configure build settings:
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
   - **Build Command**: `uv sync && uv run alembic upgrade head`
   - **Output Directory**: Leave empty (API routes)
   - **Install Command**: `pip install uv && uv sync`

### 2. Setup Neon PostgreSQL Database

1. Go to [Neon Console](https://console.neon.tech/)
2. Create new project: "my-personal-examiner"
3. Copy connection string (will look like):
   ```
   postgresql://user:pass@neon-host/dbname?sslmode=require
   ```

### 3. Configure Environment Variables in Vercel

Add these environment variables in Vercel project settings:

```bash
# Required
DATABASE_URL=postgresql://user:pass@neon-host/dbname?sslmode=require
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Optional (with defaults)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api
```

**Generate SECRET_KEY**:
```bash
openssl rand -hex 32
```

### 4. Deploy & Verify

After deployment, verify:
- `https://your-app.vercel.app/` - Root endpoint
- `https://your-app.vercel.app/docs` - Swagger UI
- `https://your-app.vercel.app/api/auth/register` - Registration endpoint

## 💻 Local Development

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Neon account)
- UV package manager: `pip install uv`

### Setup

```bash
# Clone repository
git clone https://github.com/ShehzadAnjum/my-personal-examiner.git
cd my-personal-examiner/backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn src.main:app --reload
```

Visit http://localhost:8000/docs for Swagger UI.

### Test Registration Endpoint

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test Student"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "full_name": "Test Student",
  "target_grades": null,
  "created_at": "2025-12-16T10:00:00Z"
}
```

## 📖 Documentation

- **Specification**: [`specs/001-phase-1-infra/spec.md`](specs/001-phase-1-infra/spec.md)
- **Implementation Plan**: [`specs/001-phase-1-infra/plan.md`](specs/001-phase-1-infra/plan.md)
- **Tasks**: [`specs/001-phase-1-infra/tasks.md`](specs/001-phase-1-infra/tasks.md)
- **Data Model**: [`specs/001-phase-1-infra/data-model.md`](specs/001-phase-1-infra/data-model.md)
- **API Contract**: [`specs/001-phase-1-infra/contracts/openapi.yaml`](specs/001-phase-1-infra/contracts/openapi.yaml)
- **Quickstart Guide**: [`specs/001-phase-1-infra/quickstart.md`](specs/001-phase-1-infra/quickstart.md)

## 🎯 Constitutional Principles

This project follows 8 non-negotiable principles (defined in [`.specify/memory/constitution.md`](.specify/memory/constitution.md)):

1. **Subject Accuracy**: All content matches Cambridge syllabi exactly
2. **A* Standard Marking**: PhD-level strictness, no compromises
3. **Syllabus Synchronization**: Monthly Cambridge updates
4. **Spec-Driven Development**: No code before specification
5. **Multi-Tenant Isolation**: Strict student data separation
6. **Constructive Feedback**: Always explain WHY and HOW to improve
7. **Phase Gates**: 100% completion + >80% test coverage required
8. **Question Quality**: Every question verified against Cambridge mark schemes

## 🧪 Testing

```bash
cd backend

# Run all tests
uv run pytest -v --cov=src

# Run specific test file
uv run pytest tests/unit/test_models.py -v

# Check coverage
uv run pytest --cov=src --cov-report=term-missing
```

**Coverage Target**: >80% (constitutional requirement)

## 📊 Project Structure

```
my_personal_examiner/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── models/            # SQLModel database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── config.py          # Settings (Pydantic Settings)
│   │   ├── database.py        # SQLModel engine & sessions
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit, integration, E2E tests
│   └── pyproject.toml         # Dependencies (UV)
├── frontend/                   # Next.js frontend (Phase IV)
├── specs/                      # Feature specifications
│   └── 001-phase-1-infra/     # Phase I spec, plan, tasks
├── docs/                       # Documentation
├── .claude/                    # Claude AI agents & commands
└── .specify/                   # SpecKitPlus templates & scripts
```

## 🔐 Security

- ✅ Passwords hashed with bcrypt (work factor 12)
- ✅ JWT tokens with 24-hour expiration
- ✅ Email validation (RFC 5322 compliant)
- ✅ SQL injection prevention (SQLModel parameterization)
- ✅ CORS configured for frontend origin
- ✅ Environment variables for secrets (never committed)

## 📝 License

Proprietary - My Personal Examiner

## 🤝 Contributing

This project follows SpecKitPlus methodology:
1. Create specification: `/sp.specify <feature-name>`
2. Create implementation plan: `/sp.plan <feature-name>`
3. Generate tasks: `/sp.tasks <feature-name>`
4. Implement with constitutional compliance
5. Pass phase gates (100% completion + >80% coverage)

See [CLAUDE.md](CLAUDE.md) for AI development guidelines.

## 🔗 Links

- **Repository**: https://github.com/ShehzadAnjum/my-personal-examiner
- **Vercel**: (Deploy and add link here)
- **Neon Database**: (Setup and add link here)
- **Documentation**: [`specs/001-phase-1-infra/`](specs/001-phase-1-infra/)

---

**Built with** [Claude Code](https://claude.com/claude-code) | **Powered by** FastAPI + SQLModel + Neon
