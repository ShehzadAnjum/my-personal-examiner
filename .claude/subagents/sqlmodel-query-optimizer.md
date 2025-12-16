# SQLModel Query Optimizer Subagent

**Parent Agent**: Database Integrity

**Task**: Write efficient database queries with proper indexing, eager loading, and N+1 prevention

**Inputs**:
- Query requirements (what data to fetch)
- Performance constraints (latency, throughput)
- Relationship loading needs

**Outputs**:
- Optimized SQLModel queries
- Index recommendations
- Query analysis and EXPLAIN results

**Pattern**:

**Basic Query (with multi-tenant filter)**:
```python
from sqlmodel import Session, select
from models import Exam, Student, Subject

def get_student_exams(student_id: UUID, db: Session) -> List[Exam]:
    """
    Get all exams for a student.

    MULTI-TENANT: Filtered by student_id (uses idx_student_exams index).
    """

    statement = select(Exam).where(Exam.student_id == student_id)
    exams = db.exec(statement).all()

    return exams
```

**Eager Loading (Prevent N+1 Queries)**:
```python
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

def get_student_exams_with_subject(student_id: UUID, db: Session) -> List[Exam]:
    """
    Get student's exams WITH subject data (eager loading).

    BAD: Fetching exams, then subject for each exam (N+1 queries)
    GOOD: Fetch exams with subjects in one query (2 queries total)
    """

    # ❌ N+1 PROBLEM (avoid this)
    # exams = db.exec(select(Exam).where(Exam.student_id == student_id)).all()
    # for exam in exams:
    #     print(exam.subject.name)  # Triggers separate query for EACH exam!

    # ✅ SOLUTION: Eager loading with selectinload
    statement = (
        select(Exam)
        .where(Exam.student_id == student_id)
        .options(selectinload(Exam.subject))  # Load subjects in one query
    )
    exams = db.exec(statement).all()

    return exams  # Now exam.subject is already loaded
```

**Pagination (Avoid Loading All Rows)**:
```python
def get_student_exams_paginated(
    student_id: UUID,
    page: int,
    page_size: int,
    db: Session,
) -> tuple[List[Exam], int]:
    """
    Get paginated exams for a student.

    Returns: (exams, total_count)
    """

    # Count total (for pagination metadata)
    count_statement = select(func.count()).select_from(Exam).where(Exam.student_id == student_id)
    total_count = db.exec(count_statement).one()

    # Fetch paginated results
    offset = (page - 1) * page_size
    statement = (
        select(Exam)
        .where(Exam.student_id == student_id)
        .order_by(Exam.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    exams = db.exec(statement).all()

    return exams, total_count
```

**Complex Query with Joins**:
```python
def get_student_progress_by_subject(student_id: UUID, db: Session) -> List[dict]:
    """
    Get student's average score by subject.

    SQL equivalent:
    SELECT subjects.name, AVG(attempts.overall_score) as avg_score
    FROM attempts
    JOIN exams ON attempts.exam_id = exams.id
    JOIN subjects ON exams.subject_id = subjects.id
    WHERE exams.student_id = :student_id
    GROUP BY subjects.id, subjects.name
    """

    from sqlalchemy import func

    statement = (
        select(
            Subject.name,
            func.avg(Attempt.overall_score).label("avg_score"),
            func.count(Attempt.id).label("attempt_count"),
        )
        .join(Exam, Attempt.exam_id == Exam.id)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Exam.student_id == student_id)  # Multi-tenant filter
        .group_by(Subject.id, Subject.name)
    )

    results = db.exec(statement).all()

    return [
        {
            "subject": row[0],
            "average_score": float(row[1]) if row[1] else 0.0,
            "attempts": row[2],
        }
        for row in results
    ]
```

**Index Usage Analysis**:
```python
def analyze_query_performance(statement: Select, db: Session) -> str:
    """
    Analyze query with EXPLAIN to verify index usage.

    Usage:
    statement = select(Exam).where(Exam.student_id == student_id)
    explain_result = analyze_query_performance(statement, db)
    print(explain_result)
    """

    # Get raw SQL
    compiled = statement.compile(compile_kwargs={"literal_binds": True})

    # Run EXPLAIN ANALYZE
    explain_query = f"EXPLAIN ANALYZE {compiled}"
    result = db.execute(text(explain_query))

    return "\n".join([row[0] for row in result])

# Example output:
# Index Scan using idx_student_exams on exams  (cost=0.15..8.17 rows=1 width=100)
#   Index Cond: (student_id = '...')
# ✅ GOOD: Using idx_student_exams index
```

**Performance Anti-Patterns (AVOID)**:

**❌ Loading All Rows**:
```python
# BAD: Loads entire table into memory
all_exams = db.exec(select(Exam)).all()  # Could be millions of rows!

# GOOD: Filter or paginate
student_exams = db.exec(select(Exam).where(Exam.student_id == student_id)).all()
```

**❌ N+1 Queries**:
```python
# BAD: N+1 problem
exams = db.exec(select(Exam)).all()
for exam in exams:
    print(exam.student.full_name)  # Separate query for each student!

# GOOD: Eager loading
exams = db.exec(select(Exam).options(selectinload(Exam.student))).all()
```

**❌ Missing Indexes**:
```python
# If this query is slow:
exams = db.exec(select(Exam).where(Exam.student_id == student_id)).all()

# Check if idx_student_exams index exists:
# CREATE INDEX idx_student_exams ON exams (student_id, created_at);
```

**When to Use**: Writing database queries, performance optimization, debugging slow queries
