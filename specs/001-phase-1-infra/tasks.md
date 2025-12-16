# Implementation Tasks: Phase I - Core Infrastructure & Database

**Feature**: 001-phase-1-infra
**Branch**: `001-phase-1-infra`
**Created**: 2025-12-16
**Philosophy**: **Small, Measurable, Testable, Visible** - Each phase delivers a working, testable increment

---

## Philosophy: Incremental, Visible Progress

**Every task must be**:
- ✅ **Small**: Single file, single responsibility, <30 min
- ✅ **Measurable**: Clear acceptance criteria (endpoint works, test passes, coverage %)
- ✅ **Testable**: Can verify completion immediately
- ✅ **Visible**: Produces working artifact user can see/test

**After each user story phase, you can**:
- Test API endpoint with cURL/Postman
- See test coverage increase
- Verify database records
- Validate functionality end-to-end

---

## Task Summary

**Total Tasks**: 42
**Phases**: 7 (Setup → US1 → US2 → US3 → US4 → Polish → Gate)
**Estimated Time**: 12-16 hours (Phase I target: Days 1-4)

**Task Distribution**:
- Phase 1 (Setup): 6 tasks - Project structure, dependencies, config
- Phase 2 (Foundational): 5 tasks - Database, migrations, core services
- Phase 3 (US1 - Registration): 6 tasks - **FIRST WORKING ENDPOINT** ✨
- Phase 4 (US2 - Authentication): 6 tasks - **LOGIN WORKS** ✨
- Phase 5 (US3 - Subjects): 5 tasks - **SUBJECTS VISIBLE** ✨
- Phase 6 (US4 - Profile): 6 tasks - **FULL CRUD COMPLETE** ✨
- Phase 7 (Polish & Gate): 8 tasks - Integration tests, coverage, gate validation

**Parallel Opportunities**: 18 tasks marked [P] can run in parallel within each phase

---

## Phase 1: Setup & Project Initialization

**Goal**: Create project structure, install dependencies, verify environment

**Visible Outcome**: ✅ Backend directory exists, dependencies installed, server starts (empty API)

**Acceptance Test**:
```bash
cd backend
uv run uvicorn src.main:app --reload
# Server starts on http://localhost:8000
curl http://localhost:8000/docs  # Swagger UI loads
```

### Tasks

- [ ] T001 Create backend project structure per plan.md (backend/src/, backend/tests/, backend/alembic/)
- [ ] T002 [P] Create pyproject.toml with dependencies (FastAPI 0.115+, SQLModel 0.0.22+, Alembic 1.13+, pytest 8.3+)
- [ ] T003 [P] Create .env.example with required environment variables (DATABASE_URL, SECRET_KEY, ENVIRONMENT)
- [ ] T004 Install dependencies with UV (uv sync)
- [ ] T005 [P] Create minimal FastAPI app in backend/src/main.py (hello world endpoint)
- [ ] T006 Verify server starts successfully (uv run uvicorn src.main:app --reload)

**Checkpoint**: ✅ Server running, Swagger UI accessible at /docs

---

## Phase 2: Foundational Infrastructure (BLOCKS ALL USER STORIES)

**Goal**: Setup database, models, migrations, core dependencies

**Visible Outcome**: ✅ Database connected, tables created, seed data loaded

**Acceptance Test**:
```bash
# Database tables exist
psql $DATABASE_URL -c "\dt"
# Output: students, subjects, syllabus_points

# Economics 9708 seeded
psql $DATABASE_URL -c "SELECT code, name FROM subjects;"
# Output: 9708 | Economics
```

### Tasks

- [ ] T007 Create backend/src/config.py with Settings (database_url, secret_key, environment from .env)
- [ ] T008 Create backend/src/database.py with SQLModel engine and session management
- [ ] T009 [P] Create Student model in backend/src/models/student.py (email unique, password_hash, target_grades JSON)
- [ ] T010 [P] Create Subject model in backend/src/models/subject.py (code, name, level, syllabus_year)
- [ ] T011 [P] Create SyllabusPoint model in backend/src/models/syllabus_point.py (subject_id FK, code, description)
- [ ] T012 Initialize Alembic and create migration 001_initial_schema.py (creates 3 tables, seeds Economics 9708)
- [ ] T013 Apply migrations and verify tables created (uv run alembic upgrade head)

**Checkpoint**: ✅ Database schema complete, Economics 9708 visible in subjects table

---

## Phase 3: User Story 1 - Student Registration (P1) **FIRST VISIBLE FEATURE** 🎯

**Goal**: Students can register accounts via API

**Visible Outcome**: ✅ POST /api/auth/register works, students can create accounts

**Acceptance Test** (cURL):
```bash
# Register new student
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","full_name":"Test Student"}'

# Expected: 201 Created with student ID
# Verify in database:
psql $DATABASE_URL -c "SELECT email, full_name FROM students WHERE email='test@example.com';"
```

**Independent Test**: This story is independently testable - registration works without login/authentication implemented yet.

### Tasks

- [ ] T014 [US1] Create Pydantic schemas in backend/src/schemas/auth.py (RegisterRequest, StudentResponse)
- [ ] T015 [US1] Create password hashing service in backend/src/services/auth_service.py (hash_password using bcrypt)
- [ ] T016 [US1] Create student service in backend/src/services/student_service.py (create_student function)
- [ ] T017 [US1] Create auth router in backend/src/routes/auth.py with POST /api/auth/register endpoint
- [ ] T018 [US1] Register auth router in backend/src/main.py
- [ ] T019 [US1] Test registration endpoint manually (cURL test from Acceptance Test above)

**Checkpoint**: ✅ POST /api/auth/register works, students created in database, passwords hashed

**Coverage Target**: 75% (models + services + routes)

---

## Phase 4: User Story 2 - Student Authentication (P1) **LOGIN WORKS** 🔐

**Goal**: Students can login and receive JWT tokens

**Visible Outcome**: ✅ POST /api/auth/login works, JWT tokens issued, authentication middleware enforces access

**Acceptance Test** (cURL):
```bash
# Login with registered student
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Expected: 200 OK with access_token
# Save token, test authentication:
curl http://localhost:8000/api/students/me \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 401 if invalid token, 200 with student data if valid
```

**Independent Test**: This story extends US1 - requires registered student but adds authentication layer.

### Tasks

- [ ] T020 [US2] Add JWT dependencies to auth_service.py (create_access_token, verify_token functions)
- [ ] T021 [US2] Create Pydantic schemas in backend/src/schemas/auth.py (LoginRequest, TokenResponse)
- [ ] T022 [US2] Implement password verification in auth_service.py (verify_password using bcrypt)
- [ ] T023 [US2] Create POST /api/auth/login endpoint in backend/src/routes/auth.py
- [ ] T024 [US2] Create authentication dependency in backend/src/dependencies.py (get_current_user from JWT)
- [ ] T025 [US2] Test login endpoint and token validation manually (cURL tests above)

**Checkpoint**: ✅ POST /api/auth/login works, JWT tokens issued, get_current_user dependency enforces auth

**Coverage Target**: 80% (auth service + routes)

---

## Phase 5: User Story 3 - View Subjects (P2) **SUBJECTS VISIBLE** 📚

**Goal**: Authenticated students can view available subjects

**Visible Outcome**: ✅ GET /api/subjects works, returns Economics 9708

**Acceptance Test** (cURL):
```bash
# Login first (from US2)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}' \
  | jq -r '.access_token')

# Get subjects list
curl http://localhost:8000/api/subjects \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with array containing Economics 9708
# [{"id":"...","code":"9708","name":"Economics","level":"A","exam_board":"Cambridge International","syllabus_year":"2023-2025"}]
```

**Independent Test**: This story requires authentication (US2) but is otherwise independent.

### Tasks

- [ ] T026 [US3] Create Pydantic schema in backend/src/schemas/subject.py (SubjectResponse)
- [ ] T027 [US3] Create subject service in backend/src/services/subject_service.py (list_subjects function)
- [ ] T028 [US3] Create subjects router in backend/src/routes/subjects.py with GET /api/subjects endpoint
- [ ] T029 [US3] Register subjects router in backend/src/main.py
- [ ] T030 [US3] Test subjects endpoint manually (cURL test above)

**Checkpoint**: ✅ GET /api/subjects works, Economics 9708 visible to authenticated students

**Coverage Target**: 82% (new routes + services)

---

## Phase 6: User Story 4 - Profile Management (P3) **FULL CRUD COMPLETE** 👤

**Goal**: Students can view and update their profiles

**Visible Outcome**: ✅ GET/PATCH /api/students/me works, profile updates persist

**Acceptance Test** (cURL):
```bash
# Login (from US2)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}' \
  | jq -r '.access_token')

# Get profile
curl http://localhost:8000/api/students/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with student profile

# Update profile
curl -X PATCH http://localhost:8000/api/students/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target_grades":{"9708":"A*"}}'

# Expected: 200 OK with updated profile

# Verify update persisted
curl http://localhost:8000/api/students/me \
  -H "Authorization: Bearer $TOKEN" | jq '.target_grades'

# Expected: {"9708":"A*"}
```

**Independent Test**: This story requires authentication (US2) but is otherwise independent.

### Tasks

- [ ] T031 [US4] Create Pydantic schemas in backend/src/schemas/student.py (StudentUpdate)
- [ ] T032 [US4] Extend student service with get_student and update_student functions
- [ ] T033 [US4] Create students router in backend/src/routes/students.py with GET /api/students/me endpoint
- [ ] T034 [US4] Add PATCH /api/students/me endpoint to students router
- [ ] T035 [US4] Register students router in backend/src/main.py
- [ ] T036 [US4] Test profile endpoints manually (cURL tests above)

**Checkpoint**: ✅ GET/PATCH /api/students/me works, profile updates visible in database

**Coverage Target**: 85% (all routes + services)

---

## Phase 7: Polish, Integration Tests & Phase Gate

**Goal**: Achieve >80% coverage, all integration tests pass, phase gate validates completion

**Visible Outcome**: ✅ All tests pass, coverage >80%, phase gate script confirms Phase I complete

**Acceptance Test**:
```bash
# Run all tests
cd backend
uv run pytest -v --cov=src --cov-report=term-missing

# Expected: All tests pass, coverage >80%

# Run phase gate
cd ..
./scripts/check-phase-1-complete.sh

# Expected: ALL CHECKS PASS
```

### Tasks

#### Integration Tests (End-to-End User Journeys)

- [ ] T037 Create pytest fixtures in backend/tests/conftest.py (db_session, test_client, test_user)
- [ ] T038 [P] Write unit tests in backend/tests/unit/test_models.py (test all 3 models, password hashing)
- [ ] T039 [P] Write integration test in backend/tests/integration/test_auth_routes.py (register + login flow)
- [ ] T040 [P] Write integration test in backend/tests/integration/test_student_routes.py (profile GET/PATCH)
- [ ] T041 [P] Write integration test in backend/tests/integration/test_subject_routes.py (subjects list)
- [ ] T042 Write E2E test in backend/tests/e2e/test_student_journey.py (register → login → subjects → profile update)

#### Quality Gates

- [ ] T043 Run all tests and verify >80% coverage (uv run pytest --cov=src)
- [ ] T044 Run linting and type checking (uv run ruff check . && uv run mypy src/)
- [ ] T045 Create phase gate script at scripts/check-phase-1-complete.sh (validates all requirements)
- [ ] T046 Run phase gate script and verify PASS
- [ ] T047 Update docs/SESSION_HANDOFF.md with Phase I completion status
- [ ] T048 Create Phase I completion PHR

**Checkpoint**: ✅ All tests pass, coverage 85%+, phase gate PASS, ready for Phase II

---

## Dependencies & Execution Order

### Critical Path (Sequential)

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3+ (User Stories in any order)
```

**IMPORTANT**: Phase 2 MUST complete before ANY user story work begins (database required for all stories)

### User Story Independence

After Phase 2, user stories CAN be implemented in parallel or any order:

```
┌─ US1 (Registration) ────────────┐
│                                  │
├─ US2 (Authentication) ──────────┤──→ Phase 7 (Tests & Gate)
│                                  │
├─ US3 (Subjects) [depends on US2]│
│                                  │
└─ US4 (Profile) [depends on US2] ┘
```

**Dependencies**:
- US1 (Registration): No dependencies (can implement first)
- US2 (Authentication): Requires US1 (need registered students to login)
- US3 (Subjects): Requires US2 (authentication required)
- US4 (Profile): Requires US2 (authentication required)

**Recommended Order**: US1 → US2 → US3 → US4 (priority-driven)

### Parallel Execution Opportunities

**Within Phase 1 (Setup)**:
- T002, T003, T005 can run in parallel (different files)

**Within Phase 2 (Foundational)**:
- T009, T010, T011 can run in parallel (independent models)

**Within Each User Story Phase**:
- Schema creation [P] tasks can run in parallel with service creation

**Within Phase 7 (Polish)**:
- T038, T039, T040, T041 can run in parallel (independent test files)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**For fastest time-to-value, implement in this order**:

1. **Phase 1 + Phase 2** (Foundational) - **Required for all stories**
2. **Phase 3 (US1 - Registration)** - **First visible endpoint** ✨
3. **Phase 4 (US2 - Authentication)** - **Authentication works** ✨
4. **Phase 7 (Basic Tests)** - **Verify it works** ✅

**MVP Delivery**: After Step 4, you have:
- ✅ Students can register
- ✅ Students can login
- ✅ Authentication enforced
- ✅ Tests verify it works
- ✅ **First deliverable increment complete!**

Then proceed with US3 and US4 for full Phase I completion.

### Incremental Delivery Philosophy

**After each user story phase**:
1. ✅ **Test manually** with cURL (Acceptance Test)
2. ✅ **Verify in database** (psql commands)
3. ✅ **Run tests** (pytest for that phase)
4. ✅ **Check coverage** (should increase 5-10%)
5. ✅ **Demo to stakeholder** (show working endpoint)

**Benefits**:
- **Visibility**: Working features at each step
- **Controllability**: Can pause/resume at any phase
- **Testability**: Each phase has acceptance tests
- **Measurability**: Coverage % tracks progress
- **Risk Reduction**: Issues discovered early

---

## Validation Checklist (Per Phase)

**After completing each phase, verify**:

### Phase 1 (Setup) ✅
- [ ] Backend directory structure matches plan.md
- [ ] Dependencies installed (uv sync succeeds)
- [ ] Server starts (uvicorn runs without errors)
- [ ] Swagger UI accessible at /docs

### Phase 2 (Foundational) ✅
- [ ] Database tables exist (psql \dt shows 3 tables)
- [ ] Economics 9708 seeded (SELECT * FROM subjects)
- [ ] Models importable (from src.models import Student)
- [ ] Migrations applied (alembic current shows version)

### Phase 3 (US1 - Registration) ✅
- [ ] POST /api/auth/register returns 201
- [ ] Student created in database (SELECT * FROM students)
- [ ] Password hashed (not plain text in DB)
- [ ] Duplicate email rejected (409 Conflict)
- [ ] Coverage >75%

### Phase 4 (US2 - Authentication) ✅
- [ ] POST /api/auth/login returns 200 with token
- [ ] Invalid credentials rejected (401 Unauthorized)
- [ ] get_current_user dependency works
- [ ] Invalid token rejected (401 Unauthorized)
- [ ] Coverage >80%

### Phase 5 (US3 - Subjects) ✅
- [ ] GET /api/subjects returns Economics 9708
- [ ] Unauthenticated request rejected (401)
- [ ] Response matches OpenAPI schema
- [ ] Coverage >82%

### Phase 6 (US4 - Profile) ✅
- [ ] GET /api/students/me returns student profile
- [ ] PATCH /api/students/me updates profile
- [ ] Changes persist in database
- [ ] Cross-student access blocked (403 Forbidden)
- [ ] Coverage >85%

### Phase 7 (Polish & Gate) ✅
- [ ] All tests pass (pytest exit code 0)
- [ ] Coverage >80% (constitutional requirement)
- [ ] No linting errors (ruff check passes)
- [ ] No type errors (mypy passes)
- [ ] Phase gate script PASS
- [ ] SESSION_HANDOFF.md updated

---

## Success Metrics

**Phase I Complete When**:
- ✅ All 48 tasks completed
- ✅ All 4 user stories implemented and tested
- ✅ All API endpoints functional (register, login, subjects, profile)
- ✅ Test coverage >80%
- ✅ Phase gate script passes
- ✅ User can test all endpoints with cURL

**Measurable Outcomes** (from spec.md):
- ✅ SC-001: Students can register/login within 2 minutes ✨
- ✅ SC-004: 100% multi-tenant isolation (no cross-student access) ✨
- ✅ SC-007: >80% test coverage ✨
- ✅ SC-011: 100% password hashing (zero plain text) ✨

**Next Phase**: Phase II - Question Bank & Exam Generation (after Phase I gate passes and user approves)

---

## Notes

**Task Numbering**: T001-T048 in execution order
**Story Labels**: [US1], [US2], [US3], [US4] map to spec.md user stories
**Parallel Marker**: [P] indicates task can run in parallel within its phase
**File Paths**: All tasks include exact file paths for implementation
**Acceptance Tests**: Every phase has cURL test examples to verify completion

**Remember**: **Small, Measurable, Testable, Visible** - User can see progress after every phase! 🚀
