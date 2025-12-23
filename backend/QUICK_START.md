# Quick Start Guide

**Last Updated**: 2025-12-19
**Time Required**: 10 minutes to validate everything works

---

## 🚀 Get Everything Running (5 minutes)

### 1. Start the Server

```bash
cd /home/anjum/dev/my_personal_examiner/backend

# Start server
uv run uvicorn src.main:app --reload
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['/home/anjum/dev/my_personal_examiner/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
🚀 My Personal Examiner API starting up...
📚 Phase I: Core Infrastructure & Database
INFO:     Application startup complete.
```

### 2. Verify API is Working

Open browser: http://localhost:8000/docs

You should see:
- ✅ Swagger UI interface
- ✅ 22 API endpoints listed
- ✅ Interactive "Try it out" buttons

---

## 📊 Load Test Data (3 minutes)

### Step 1: Seed Syllabus Points

```bash
# In a NEW terminal (keep server running)
cd /home/anjum/dev/my_personal_examiner/backend
uv run python scripts/seed_economics_syllabus.py
```

**Expected Output**:
```
✅ Found subject: Economics (9708)

✅ Created: 9708.1.1 - The central economic problem
✅ Created: 9708.1.2 - The role of markets
✅ Created: 9708.2.1 - Supply and demand
...

📊 Summary:
   Created: 10
   Already existed: 0
   Total: 10

✅ Economics syllabus seeded successfully!
```

### Step 2: Seed Sample Questions

```bash
uv run python scripts/seed_sample_questions.py
```

**Expected Output**:
```
✅ Found subject: Economics (9708)

✅ Created: 9708_s22_qp_22 Q1 (8 marks, easy)
✅ Created: 9708_w21_qp_22 Q4 (4 marks, easy)
...

📊 Summary:
   Total questions created: 10
   Easy: 3
   Medium: 4
   Hard: 3

✅ Sample questions seeded successfully!
```

---

## ✅ Test Everything (2 minutes)

### Test 1: Search Questions

**In Swagger UI** (http://localhost:8000/docs):

1. Find **GET /api/questions/search**
2. Click "Try it out"
3. Set `subject_code` = `9708`
4. Click "Execute"

**Expected Response**:
```json
{
  "questions": [
    {
      "id": "...",
      "question_text": "Explain the concept of opportunity cost...",
      "max_marks": 8,
      "difficulty": "easy",
      ...
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "has_next": false,
  "has_prev": false
}
```

### Test 2: Generate an Exam

**In Swagger UI**:

1. Find **POST /api/exams**
2. Click "Try it out"
3. Paste this request body:
   ```json
   {
     "subject_code": "9708",
     "exam_type": "PRACTICE",
     "question_count": 5,
     "strategy": "balanced"
   }
   ```
4. Click "Execute"

**Expected Response**:
```json
{
  "id": "...",
  "subject_id": "...",
  "exam_type": "PRACTICE",
  "question_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"],
  "total_marks": 48,
  "duration": 96,
  "status": "PENDING",
  "created_at": "2025-12-19T..."
}
```

### Test 3: Get Exam Statistics

**In Swagger UI**:

1. Copy the `id` from the exam you just created
2. Find **GET /api/exams/{exam_id}/statistics**
3. Click "Try it out"
4. Paste the exam ID
5. Click "Execute"

**Expected Response**:
```json
{
  "exam_id": "...",
  "total_questions": 5,
  "total_marks": 48,
  "difficulty_breakdown": {
    "easy": 1,
    "medium": 3,
    "hard": 1
  },
  "marks_per_difficulty": {
    "easy": 8,
    "medium": 28,
    "hard": 12
  },
  "average_marks_per_question": 9.6
}
```

### Test 4: Syllabus Coverage

**In Swagger UI**:

1. Find **GET /api/syllabus/coverage/{subject_code}**
2. Click "Try it out"
3. Set `subject_code` = `9708`
4. Click "Execute"

**Expected Response**:
```json
{
  "subject_code": "9708",
  "total_syllabus_points": 10,
  "tagged_syllabus_points": 5,
  "coverage_percentage": 50.0,
  "untagged_syllabus_points": [
    {"code": "9708.4.1", "description": "Macroeconomic objectives"},
    ...
  ],
  "questions_per_syllabus_point": {
    "9708.1.1": 2,
    "9708.2.1": 2,
    "9708.2.2": 2,
    "9708.3.1": 1,
    "9708.3.2": 4,
    ...
  }
}
```

---

## 🧪 Run Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_exam_generation_service.py -v
```

**Expected Output**:
```
========================= test session starts ==========================
collected 95 items

tests/unit/test_models.py::test_student_model PASSED           [  1%]
tests/unit/test_models.py::test_subject_model PASSED           [  2%]
...
tests/unit/test_syllabus_tagging.py::test_full_coverage PASSED [100%]

========================= 95 passed in 2.45s ===========================
```

---

## 📚 What You've Just Validated

✅ **Backend API** (22 endpoints working)
✅ **Database** (7 tables populated)
✅ **Syllabus Tagging** (10 syllabus points, coverage tracking)
✅ **Question Bank** (10 sample questions, 3 difficulty levels)
✅ **Exam Generation** (3 strategies: random, balanced, syllabus_coverage)
✅ **Search & Filtering** (multi-filter search, pagination)
✅ **Unit Tests** (95 tests passing)

---

## 📖 Next Steps

1. **Read the docs**:
   - [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - What's done vs planned
   - [TESTING_AND_VISUALIZATION.md](TESTING_AND_VISUALIZATION.md) - Detailed testing guide
   - [ADRs in history/adr/](history/adr/) - Architecture decisions (9 ADRs)

2. **Add more data**:
   - Download real Cambridge PDFs (Economics 9708 papers)
   - Upload via POST /api/questions/upload
   - Test PDF extraction

3. **Build integration tests**:
   - Test full workflows (upload → search → generate exam)
   - Boost coverage from 36% to 80%

4. **Deploy to Vercel**:
   - Test production deployment
   - Verify Neon database connection

5. **Build frontend** (Phase IV):
   - Next.js dashboard
   - Question search UI
   - Exam generation wizard

---

## 🆘 Troubleshooting

### Server won't start

```bash
# Check database connection
uv run alembic current

# Apply migrations
uv run alembic upgrade head

# Restart server
uv run uvicorn src.main:app --reload
```

### No questions showing up

```bash
# Re-run seed scripts
uv run python scripts/seed_economics_syllabus.py
uv run python scripts/seed_sample_questions.py

# Check database directly
uv run python -c "from src.database import get_engine; from sqlmodel import Session, select; from src.models.question import Question; engine = get_engine(); session = Session(engine); questions = session.exec(select(Question)).all(); print(f'Found {len(questions)} questions')"
```

### Tests failing

```bash
# Install test dependencies
uv add --group dev pytest-mock

# Run with verbose output
uv run pytest -v --tb=short
```

---

**Ready to continue?** Check [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for next priorities!

---

**Prepared by**: AI Assistant (Claude Sonnet 4.5)
**Review Date**: 2025-12-19
