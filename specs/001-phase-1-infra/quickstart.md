# Phase I Quickstart: Development Environment Setup

**Feature**: 001-phase-1-infra (Core Infrastructure & Database)
**Date**: 2025-12-16
**Estimated Setup Time**: 20-30 minutes

## Overview

This guide walks through setting up the Phase I development environment, running the backend API locally, and executing tests. By the end, you'll have a working FastAPI backend connected to a local PostgreSQL database.

---

## Prerequisites

**Required**:
- Python 3.12+ installed (`python --version`)
- PostgreSQL 16+ installed locally OR Neon database account
- Git installed
- UV 0.5+ installed (`pip install uv` or see https://docs.astral.sh/uv/getting-started/installation/)

**Recommended**:
- VS Code with Python extension
- Postman or cURL for API testing
- pgAdmin or DBeaver for database exploration

---

## Step 1: Clone Repository and Checkout Branch

```bash
# Clone repository
git clone <repository-url>
cd my_personal_examiner

# Checkout Phase I feature branch
git checkout 001-phase-1-infra

# Verify you're on the correct branch
git branch --show-current
# Should output: 001-phase-1-infra
```

---

## Step 2: Setup Backend Environment

### Install Dependencies

```bash
cd backend

# Install dependencies with UV
uv sync

# Verify installation
uv run python --version
# Should output: Python 3.12.x
```

**What this does**: Installs FastAPI, SQLModel, Alembic, pytest, and all Phase I dependencies from `pyproject.toml`.

### Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env  # or vim .env, code .env, etc.
```

**Required environment variables**:
```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/mypersonalexaminer_dev
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ENVIRONMENT=development
```

**Generate SECRET_KEY**:
```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Step 3: Setup Database

### Option A: Local PostgreSQL

```bash
# Create database
createdb mypersonalexaminer_dev

# Or via psql
psql -U postgres -c "CREATE DATABASE mypersonalexaminer_dev;"
```

### Option B: Neon (Cloud PostgreSQL)

1. Go to https://neon.tech/
2. Create free account
3. Create new project: "my-personal-examiner"
4. Copy connection string
5. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@neon-host/dbname?sslmode=require
   ```

---

## Step 4: Run Database Migrations

```bash
cd backend

# Initialize Alembic (first time only)
uv run alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: students, subjects, syllabus_points
```

**What this does**: Creates database tables from SQLModel models using Alembic migrations.

### Seed Initial Data

```bash
# Economics 9708 is auto-seeded in migration 001_initial_schema.py
# Verify with:
psql $DATABASE_URL -c "SELECT code, name FROM subjects;"
# Should output:
#  code |   name
# ------+-----------
#  9708 | Economics
```

---

## Step 5: Run Backend Server

```bash
cd backend

# Start FastAPI development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Application startup complete.
```

**Test server is running**:
```bash
# Open new terminal
curl http://localhost:8000/docs

# Or visit in browser:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

---

## Step 6: Test API Endpoints

### 1. Register a Student

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test Student"
  }'
```

**Expected response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "full_name": "Test Student",
  "target_grades": null,
  "created_at": "2025-12-16T10:00:00Z"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

**Expected response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Copy the `access_token` for next requests.**

### 3. Get Profile

```bash
# Replace <TOKEN> with access_token from login response
curl http://localhost:8000/api/students/me \
  -H "Authorization: Bearer <TOKEN>"
```

### 4. List Subjects

```bash
curl http://localhost:8000/api/subjects \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected response**:
```json
[
  {
    "id": "...",
    "code": "9708",
    "name": "Economics",
    "level": "A",
    "exam_board": "Cambridge International",
    "syllabus_year": "2023-2025"
  }
]
```

---

## Step 7: Run Tests

```bash
cd backend

# Run all tests with coverage
uv run pytest -v --cov=src --cov-report=term-missing

# Run specific test files
uv run pytest tests/unit/test_models.py -v
uv run pytest tests/integration/test_auth_routes.py -v

# Run with detailed output
uv run pytest -vv -s
```

**Expected output**:
```
====================== test session starts ======================
collected 25 items

tests/unit/test_models.py::test_student_creation PASSED    [ 4%]
tests/unit/test_models.py::test_password_hashing PASSED    [ 8%]
tests/integration/test_auth_routes.py::test_register PASSED [12%]
tests/integration/test_auth_routes.py::test_login PASSED   [16%]
...

---------- coverage: platform linux, python 3.12.0 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/main.py                    20      0   100%
src/models/student.py          35      2    94%   45-46
src/routes/auth.py             50      3    94%   78-80
src/services/auth_service.py   40      1    98%   92
---------------------------------------------------------
TOTAL                         450     12    97%

====================== 25 passed in 3.45s =======================
```

**Coverage target**: >80% (constitutional requirement)

---

## Step 8: Code Quality Checks

```bash
cd backend

# Linting (Ruff)
uv run ruff check .

# Type checking (mypy)
uv run mypy src/

# Format code (Ruff format)
uv run ruff format .
```

**All checks should pass before committing.**

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Run `uv sync` from `backend/` directory

### Issue: "Could not connect to database"

**Solution**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in `.env` is correct
3. Test connection: `psql $DATABASE_URL`

### Issue: "Alembic migration fails"

**Solution**:
1. Drop database: `dropdb mypersonalexaminer_dev`
2. Recreate: `createdb mypersonalexaminer_dev`
3. Re-run migrations: `uv run alembic upgrade head`

### Issue: "Tests fail with 'No module named pytest'"

**Solution**: Install dev dependencies: `uv sync --all-extras`

### Issue: "JWT token expired"

**Solution**: Tokens expire after 24 hours. Re-login to get new token.

---

## Development Workflow

### Daily Workflow

1. **Morning**: Run `docs/DAILY_CHECKLIST.md`
2. **Start server**: `uv run uvicorn src.main:app --reload`
3. **Make changes**: Edit code in `src/`
4. **Test changes**: `uv run pytest -v`
5. **Commit**: `git add . && git commit -m "feat: ..."` (pre-commit hook runs tests)
6. **Evening**: Update `docs/SESSION_HANDOFF.md`

### Adding New Endpoint

1. Create route in `src/routes/`
2. Add Pydantic schemas in `src/schemas/`
3. Add business logic in `src/services/`
4. Write tests in `tests/integration/`
5. Update OpenAPI docs (auto-generated by FastAPI)
6. Run tests: `uv run pytest -v`

### Database Changes

1. Modify SQLModel model in `src/models/`
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review migration in `alembic/versions/`
4. Apply migration: `uv run alembic upgrade head`
5. Test rollback: `uv run alembic downgrade -1` then `upgrade head`

---

## Next Steps

Once Phase I setup is complete:

1. ✅ Verify all tests pass: `uv run pytest -v`
2. ✅ Verify coverage >80%: `uv run pytest --cov=src`
3. ✅ Test API manually with Postman/cURL
4. ✅ Read `SESSION_HANDOFF.md` for current state
5. ➡️  Phase II: Question Bank & Exam Generation (after Phase I gate passes)

---

## Useful Commands Cheat Sheet

```bash
# Backend server
uv run uvicorn src.main:app --reload

# Tests
uv run pytest -v                    # All tests
uv run pytest -k "test_auth"        # Tests matching pattern
uv run pytest --cov=src             # With coverage

# Database
uv run alembic upgrade head         # Apply migrations
uv run alembic downgrade -1         # Rollback one
uv run alembic current              # Current version
psql $DATABASE_URL                  # Open database shell

# Code quality
uv run ruff check .                 # Lint
uv run ruff format .                # Format
uv run mypy src/                    # Type check

# Dependencies
uv add <package>                    # Add dependency
uv remove <package>                 # Remove dependency
uv sync                             # Install all dependencies
```

---

## Support

**Issues**: Report bugs at [GitHub Issues]
**Documentation**: See `docs/` directory
**Constitution**: Read `.specify/memory/constitution.md` for project principles

---

**Setup Complete!** 🎉 You now have a working Phase I backend. Time to build! 🚀
