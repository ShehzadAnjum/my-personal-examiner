# Testing & Visualization Guide

**Last Updated**: 2025-12-19
**Purpose**: How to test and visualize implemented features

---

## 1. LOCAL TESTING SETUP

### Start the Development Server

```bash
cd /home/anjum/dev/my_personal_examiner/backend

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will be available at**: http://localhost:8000

---

## 2. INTERACTIVE API DOCUMENTATION (Swagger UI)

### Access Swagger UI

**URL**: http://localhost:8000/docs

**Features**:
- ✅ Interactive API testing (no Postman needed!)
- ✅ Try endpoints directly in browser
- ✅ Auto-generated request/response schemas
- ✅ Authentication support (JWT tokens)

### How to Use Swagger

1. **Open**: http://localhost:8000/docs
2. **Expand an endpoint** (e.g., POST /api/auth/register)
3. **Click "Try it out"**
4. **Fill request body**:
   ```json
   {
     "email": "test@example.com",
     "password": "TestPass123",
     "full_name": "Test Student"
   }
   ```
5. **Click "Execute"**
6. **View response** (status code, body, headers)

### Alternative: ReDoc

**URL**: http://localhost:8000/redoc

Cleaner documentation view (read-only, no interactive testing).

---

## 3. MANUAL API TESTING (curl)

### Test Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "economics.student@example.com",
    "password": "SecurePass123",
    "full_name": "Alice Economics"
  }'
```

**Expected Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "economics.student@example.com",
  "full_name": "Alice Economics",
  "target_grades": null,
  "created_at": "2025-12-19T12:00:00Z"
}
```

### Test Question Upload (Mock Data)

Since we don't have real PDFs yet, let's test with mock data:

```bash
# Create a simple test PDF file
echo "Sample question paper content" > /tmp/test_9708_s22_qp_22.pdf

# Upload it
curl -X POST http://localhost:8000/api/questions/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/test_9708_s22_qp_22.pdf" \
  -F "subject_code=9708"
```

**Note**: This will fail because the PDF doesn't have real questions. See Section 5 for test data.

### Test Exam Generation

First, we need questions in the database. Let's manually insert one via Python:

```python
# In a Python shell (uv run python)
from src.database import get_engine
from src.models.question import Question
from src.models.subject import Subject
from sqlmodel import Session, select
from uuid import uuid4

engine = get_engine()

with Session(engine) as session:
    # Get Economics subject
    subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

    # Create sample question
    q = Question(
        subject_id=subject.id,
        question_text="Explain the concept of opportunity cost with examples.",
        max_marks=8,
        source_paper="9708_s22_qp_22",
        paper_number=22,
        question_number=1,
        year=2022,
        session="MAY_JUNE",
        difficulty="medium"
    )
    session.add(q)
    session.commit()
    print(f"Created question: {q.id}")
```

Then test exam generation:

```bash
curl -X POST http://localhost:8000/api/exams \
  -H "Content-Type: application/json" \
  -d '{
    "subject_code": "9708",
    "exam_type": "PRACTICE",
    "question_count": 5,
    "strategy": "balanced"
  }'
```

---

## 4. UNIT TESTS

### Run All Tests

```bash
cd /home/anjum/dev/my_personal_examiner/backend

# Run all tests with coverage
uv run pytest -v --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_exam_generation_service.py -v

# Run specific test
uv run pytest tests/unit/test_exam_generation_service.py::TestRandomStrategy::test_random_selection_exact_count -v
```

### Current Test Status

```bash
# Should see:
# - 11 tests in test_models.py ✅
# - 11 tests in test_cambridge_parser.py ✅
# - 11 tests in test_mark_scheme_extractor.py ✅
# - 11 tests in test_extraction_service.py ✅
# - 14 tests in test_search_service.py ⚠️ (mocked, need DB)
# - 18 tests in test_exam_generation_service.py ✅
# - 19 tests in test_syllabus_tagging.py ✅
#
# Total: 95 tests
```

### Coverage Report

```bash
uv run pytest --cov=src --cov-report=html

# Open coverage report in browser
firefox htmlcov/index.html
# or
google-chrome htmlcov/index.html
```

**Coverage Breakdown**:
- **Models**: 75-95% ✅
- **Extractors**: 17-83% ⚠️
- **Services**: 13-93% ⚠️
- **Routes**: 31-48% ⚠️

---

## 5. TEST DATA CREATION

### Seed Economics 9708 Syllabus Points

Create a seed script:

```python
# scripts/seed_economics_syllabus.py
from src.database import get_engine
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint
from sqlmodel import Session, select

def seed_economics_syllabus():
    engine = get_engine()

    with Session(engine) as session:
        # Get Economics subject
        subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not subject:
            print("Economics subject not found! Run migrations first.")
            return

        syllabus_points = [
            {
                "code": "9708.1.1",
                "description": "The central economic problem",
                "topics": "Scarcity, Choice, Opportunity cost",
                "learning_outcomes": "Understand the nature of the economic problem"
            },
            {
                "code": "9708.1.2",
                "description": "The role of markets",
                "topics": "Free market economy, Mixed economy, Command economy",
                "learning_outcomes": "Understand different economic systems"
            },
            {
                "code": "9708.2.1",
                "description": "Supply and demand",
                "topics": "Demand curves, Supply curves, Market equilibrium",
                "learning_outcomes": "Analyze market mechanisms"
            },
            {
                "code": "9708.2.2",
                "description": "Price elasticity",
                "topics": "PED, PES, Income elasticity, Cross elasticity",
                "learning_outcomes": "Calculate and interpret elasticity"
            },
            {
                "code": "9708.3.1",
                "description": "Market failure",
                "topics": "Externalities, Public goods, Merit goods, Information failure",
                "learning_outcomes": "Identify and analyze market failures"
            },
        ]

        for sp_data in syllabus_points:
            # Check if already exists
            existing = session.exec(
                select(SyllabusPoint).where(
                    SyllabusPoint.code == sp_data["code"]
                )
            ).first()

            if not existing:
                sp = SyllabusPoint(
                    subject_id=subject.id,
                    **sp_data
                )
                session.add(sp)
                print(f"Created: {sp.code}")
            else:
                print(f"Already exists: {sp_data['code']}")

        session.commit()
        print("\n✅ Economics syllabus seeded successfully!")

if __name__ == "__main__":
    seed_economics_syllabus()
```

Run it:

```bash
uv run python scripts/seed_economics_syllabus.py
```

### Seed Sample Questions

```python
# scripts/seed_sample_questions.py
from src.database import get_engine
from src.models.subject import Subject
from src.models.question import Question
from src.models.syllabus_point import SyllabusPoint
from sqlmodel import Session, select

def seed_sample_questions():
    engine = get_engine()

    with Session(engine) as session:
        # Get Economics subject
        subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

        # Get syllabus points
        sp_1_1 = session.exec(select(SyllabusPoint).where(SyllabusPoint.code == "9708.1.1")).first()
        sp_2_1 = session.exec(select(SyllabusPoint).where(SyllabusPoint.code == "9708.2.1")).first()
        sp_3_1 = session.exec(select(SyllabusPoint).where(SyllabusPoint.code == "9708.3.1")).first()

        questions = [
            {
                "question_text": "Explain the concept of opportunity cost and provide two examples from your daily life.",
                "max_marks": 8,
                "difficulty": "easy",
                "paper_number": 22,
                "question_number": 1,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_1_1.id)] if sp_1_1 else []
            },
            {
                "question_text": "Using a demand and supply diagram, explain how a government subsidy affects market equilibrium.",
                "max_marks": 12,
                "difficulty": "medium",
                "paper_number": 22,
                "question_number": 2,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_2_1.id)] if sp_2_1 else []
            },
            {
                "question_text": "Discuss whether government intervention is necessary to address negative externalities. Use real-world examples.",
                "max_marks": 20,
                "difficulty": "hard",
                "paper_number": 22,
                "question_number": 3,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_3_1.id)] if sp_3_1 else []
            },
            {
                "question_text": "Define scarcity and explain why it is the central economic problem.",
                "max_marks": 4,
                "difficulty": "easy",
                "paper_number": 22,
                "question_number": 4,
                "year": 2021,
                "session": "OCT_NOV",
                "source_paper": "9708_w21_qp_22",
                "syllabus_point_ids": [str(sp_1_1.id)] if sp_1_1 else []
            },
            {
                "question_text": "Calculate the price elasticity of demand if price increases from $10 to $12 and quantity demanded falls from 100 to 80 units. Interpret your result.",
                "max_marks": 10,
                "difficulty": "medium",
                "paper_number": 22,
                "question_number": 5,
                "year": 2021,
                "session": "OCT_NOV",
                "source_paper": "9708_w21_qp_22",
                "syllabus_point_ids": []
            },
        ]

        for q_data in questions:
            q = Question(
                subject_id=subject.id,
                **q_data
            )
            session.add(q)
            print(f"Created: {q.source_paper} Q{q.question_number}")

        session.commit()
        print("\n✅ Sample questions seeded successfully!")

if __name__ == "__main__":
    seed_sample_questions()
```

Run it:

```bash
uv run python scripts/seed_sample_questions.py
```

---

## 6. VISUALIZATION OPTIONS

### Option 1: Swagger UI (Built-in) ✅ EASIEST

**Pros**:
- Already working (http://localhost:8000/docs)
- Interactive testing
- Auto-generated from code
- No setup required

**Cons**:
- Not very user-friendly for non-developers
- No data visualization (charts, graphs)

### Option 2: Postman Collection

Create a Postman collection for common workflows:

**Collection**: `My Personal Examiner API`

**Folders**:
1. **Auth**
   - POST Register Student

2. **Syllabus**
   - POST Create Syllabus Point
   - GET List Syllabus Points
   - GET Coverage Statistics

3. **Questions**
   - POST Upload PDF
   - GET Search Questions
   - GET Filters

4. **Exams**
   - POST Generate Exam (Random)
   - POST Generate Exam (Balanced)
   - POST Generate Exam (Syllabus Coverage)
   - GET Exam Details
   - GET Exam Questions
   - GET Exam Statistics

**Export to JSON** and share with team.

### Option 3: Basic Frontend (Next.js)

Create a minimal UI to visualize data:

**Pages**:
1. **Dashboard**: Overview stats (total questions, total exams, coverage %)
2. **Questions**: Search, filter, view questions
3. **Exams**: Generate exam, view exam details
4. **Syllabus**: View coverage heatmap

**Estimated Effort**: 8-12 hours

**Tech Stack**:
- Next.js 15 (App Router)
- shadcn/ui components
- Recharts for graphs
- TanStack Query for API calls

### Option 4: Database GUI (DBeaver/pgAdmin)

Connect directly to database to inspect data:

**Tool**: DBeaver (free, cross-platform)

**Connection**:
- Host: localhost (or Neon host)
- Port: 5432
- Database: my_personal_examiner
- User: (from DATABASE_URL)
- Password: (from DATABASE_URL)

**Use Cases**:
- Inspect question data directly
- View syllabus coverage
- Debug data issues
- Write custom SQL queries

### Option 5: Jupyter Notebook

Create notebooks for data exploration:

```python
# notebooks/explore_questions.ipynb
import pandas as pd
from src.database import get_engine
from sqlmodel import Session, select
from src.models.question import Question

engine = get_engine()

with Session(engine) as session:
    # Get all questions
    questions = session.exec(select(Question)).all()

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            "source_paper": q.source_paper,
            "question_number": q.question_number,
            "max_marks": q.max_marks,
            "difficulty": q.difficulty,
            "year": q.year,
            "session": q.session
        }
        for q in questions
    ])

    # Visualize
    import matplotlib.pyplot as plt

    # Distribution by difficulty
    df['difficulty'].value_counts().plot(kind='bar', title='Questions by Difficulty')
    plt.show()

    # Distribution by year
    df['year'].value_counts().sort_index().plot(kind='line', title='Questions by Year')
    plt.show()
```

---

## 7. RECOMMENDED TESTING WORKFLOW

### Workflow 1: Quick Validation (5 minutes)

1. **Start server**: `uv run uvicorn src.main:app --reload`
2. **Open Swagger**: http://localhost:8000/docs
3. **Test registration**: POST /api/auth/register
4. **Test syllabus list**: GET /api/syllabus?subject_code=9708
5. **Verify**: Check responses are 200 OK

### Workflow 2: Full Feature Test (30 minutes)

1. **Seed data**:
   ```bash
   uv run python scripts/seed_economics_syllabus.py
   uv run python scripts/seed_sample_questions.py
   ```

2. **Test search**:
   - GET /api/questions/search?subject_code=9708
   - GET /api/questions/filters?subject_code=9708

3. **Test exam generation**:
   - POST /api/exams (balanced strategy)
   - GET /api/exams/{id}/questions
   - GET /api/exams/{id}/statistics

4. **Test syllabus tagging**:
   - POST /api/syllabus/questions/{id}/tags
   - GET /api/syllabus/coverage/9708

5. **Verify coverage**: `uv run pytest --cov=src`

### Workflow 3: Integration Test (1 hour)

1. **Upload real PDF** (when available):
   - Download Economics 9708 paper from Cambridge website
   - POST /api/questions/upload

2. **Verify extraction**:
   - Check questions table in database
   - Verify question_text, max_marks extracted correctly

3. **Generate exam**:
   - POST /api/exams with uploaded questions
   - Verify exam.question_ids matches uploaded questions

4. **Test end-to-end**:
   - Student registers → searches questions → generates exam → takes exam (Phase III)

---

## 8. TROUBLESHOOTING

### Issue: Server won't start

**Check**:
1. Database running? `pg_isready` or check Neon status
2. Migrations applied? `uv run alembic upgrade head`
3. Dependencies installed? `uv sync`

**Fix**:
```bash
# Check migrations status
uv run alembic current

# Apply migrations
uv run alembic upgrade head

# Restart server
uv run uvicorn src.main:app --reload
```

### Issue: Tests failing

**Check**:
1. Database connection string in .env?
2. Test database separate from dev database?
3. pytest-mock installed? `uv add --group dev pytest-mock`

**Fix**:
```bash
# Run tests with verbose output
uv run pytest -v --tb=short

# Run specific failing test
uv run pytest tests/unit/test_exam_generation_service.py::TestRandomStrategy -v
```

### Issue: Coverage below 80%

**Current Status**: 36-45% overall

**Gaps**:
- Routes: 31-48% (need integration tests with TestClient)
- Services: 13-93% (SearchService needs real DB tests)
- Extractors: 17-83% (GenericExtractor needs PDF test files)

**Fix**:
1. Add integration tests with TestClient (FastAPI)
2. Add test PDFs to `tests/fixtures/`
3. Mock complex dependencies (OpenAI, file system)

---

## 9. NEXT STEPS FOR TESTING

### Priority 1: Integration Tests (8 hours)

Create `tests/integration/test_upload_workflow.py`:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_question_paper():
    # Upload PDF
    with open("tests/fixtures/9708_s22_qp_22.pdf", "rb") as f:
        response = client.post(
            "/api/questions/upload",
            files={"file": f},
            data={"subject_code": "9708"}
        )

    assert response.status_code == 201
    assert response.json()["type"] == "question_paper"
    assert response.json()["questions_count"] > 0

def test_search_uploaded_questions():
    # Search questions
    response = client.get("/api/questions/search?subject_code=9708")

    assert response.status_code == 200
    assert len(response.json()["questions"]) > 0
```

### Priority 2: Test Data (2 hours)

Download real Cambridge PDFs:
1. Economics 9708 May/June 2022 Paper 22 (QP + MS)
2. Place in `tests/fixtures/`
3. Use in integration tests

### Priority 3: Visual UI (8 hours - Optional)

Create Next.js frontend:
- Dashboard with stats
- Question search interface
- Exam generation wizard
- Syllabus coverage heatmap

---

**Prepared by**: AI Assistant (Claude Sonnet 4.5)
**Review Date**: 2025-12-19
