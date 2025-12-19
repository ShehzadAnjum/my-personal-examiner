# SQLModel Query Pattern Bug Fix

**Date**: 2025-12-19
**Issue**: Search and exam generation endpoints returning 500 errors
**Root Cause**: Inconsistent SQLModel query result types across different contexts

---

## Problem Summary

When using SQLModel 0.0.22+ with SQLAlchemy 2.0+, the `Session.exec()` method returns different result types depending on the context:

### SearchService (works with `.scalars()`)
```python
# ✅ WORKS: In SearchService
subject = self.db.exec(stmt).scalars().first()  # Returns Subject instance
```

### ExamGenerationService (works WITHOUT `.scalars()`)
```python
# ❌ FAILS: Calling .scalars() twice
subject = self.db.exec(stmt).scalars().first()  # Error: ScalarResult has no .scalars()

# ✅ WORKS: Use intermediate variable
result = self.db.exec(stmt)
questions = list(result.scalars())  # Returns Question instances
```

---

## Files Fixed

### 1. `src/services/search_service.py` ✅
**Pattern**: Added `.scalars()` to 7 query locations
- Subject lookup (2 locations): `.exec(stmt).scalars().first()`
- Count queries (2 locations): Changed `.one()` to `.scalar_one()`
- Questions retrieval (2 locations): `.exec(stmt).scalars().all()`
- Mark schemes retrieval (1 location): `.exec(stmt).scalars().all()`

**Result**: All 5 search methods now return model instances correctly.

### 2. `src/services/exam_generation_service.py` ✅
**Pattern**: Used intermediate variable pattern
- Question retrieval:
  ```python
  result = self.db.exec(stmt)
  available_questions = list(result.scalars())
  ```
- Exam retrieval:
  ```python
  result = self.db.exec(stmt)
  exam = result.scalars().first()
  ```
- Question loop:
  ```python
  result_q = self.db.exec(stmt_q)
  q = result_q.scalars().first()
  ```

**Result**: Exam generation and statistics work correctly.

### 3. `src/routes/exams.py` ⚠️
**Pattern**: LEFT AS-IS (uses original `.first()` and `.all()`)
- Subject lookups: `.exec(stmt).first()`
- Exam retrievals: `.exec(stmt).all()`

**Why**: In FastAPI routes with `Depends(get_session)`, `db.exec()` appears to return `ScalarResult` directly, so `.scalars()` is not needed.

**Result**: All exam endpoints work correctly.

---

## Working Pattern Guide

### When to use `.scalars()`

**Use in Service classes with `self.db: Session`:**
```python
from sqlmodel import Session

class MyService:
    def __init__(self, db: Session):
        self.db = db

    def get_item(self, id):
        result = self.db.exec(select(Model).where(Model.id == id))
        return result.scalars().first()  # ✅ Use scalars()
```

**Don't use in FastAPI routes:**
```python
@router.get("/items/{id}")
def get_item(id: UUID, db: Session = Depends(get_session)):
    item = db.exec(select(Model).where(Model.id == id)).first()  # ✅ No scalars()
    return item
```

---

## Test Results

### Before Fix
```
❌ GET /api/questions/search?subject_code=9708
    → 500 Internal Server Error
    → AttributeError: id

❌ POST /api/exams
    → 500 Internal Server Error
    → AttributeError: difficulty
```

### After Fix
```
✅ GET /api/questions/search?subject_code=9708
    → 200 OK
    → Returns 10 questions

✅ POST /api/exams
    → 201 Created
    → Exam ID: c278a5a8-c3a9-46bf-a7f2-9c2178b07872
    → Total marks: 50, Duration: 100 minutes

✅ GET /api/exams/{id}/statistics
    → 200 OK
    → {
        "total_questions": 5,
        "difficulty_breakdown": {"easy": 2, "medium": 2, "hard": 1},
        "marks_per_difficulty": {"easy": 12, "medium": 18, "hard": 20}
      }

✅ GET /api/syllabus/coverage/9708
    → 200 OK
    → Coverage: 50.0%
```

---

## Debug Scripts Created

1. **`scripts/debug_search.py`** - Tests SearchService directly
2. **`scripts/debug_exam_generation.py`** - Tests ExamGenerationService directly
3. **`scripts/validate_all_endpoints.sh`** - Comprehensive API endpoint validation

---

## Lessons Learned

1. **SQLModel query results are context-dependent**
   - Service classes: Use `.scalars()` explicitly
   - FastAPI routes: May not need `.scalars()` (depends on `get_session()` implementation)

2. **Always use intermediate variables for clarity**
   ```python
   # ✅ GOOD: Clear and explicit
   result = self.db.exec(stmt)
   items = list(result.scalars())

   # ❌ AVOID: Chaining can fail in some contexts
   items = self.db.exec(stmt).scalars().all()
   ```

3. **Test with debug scripts before API testing**
   - Direct service testing reveals errors faster
   - Easier to see full stack traces

---

## Related Documentation

- **SQLModel 0.0.22+**: Uses SQLAlchemy 2.0 query API
- **SQLAlchemy 2.0**: `Result` vs `ScalarResult` types
- **FastAPI + SQLModel**: Dependency injection affects session behavior

---

**Fixed by**: Claude Sonnet 4.5
**Validated**: 2025-12-19 18:56 UTC
