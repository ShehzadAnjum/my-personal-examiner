# Skill: Multi-Tenant Query Pattern

**Type**: Security & Database Expertise
**Created**: 2025-12-18
**Domain**: Data Security
**Parent Agent**: 02-Backend-Service
**Constitutional Requirement**: Principle V (MANDATORY)

## Overview
**CRITICAL SECURITY PATTERN**: Implement student_id filtering in ALL database queries to ensure multi-tenant data isolation for My Personal Examiner project.

## Constitutional Requirement

**Principle V: Multi-Tenant Isolation is Sacred**

> Student data MUST be strictly isolated. No student can access another student's data. Every query filtered by student_id.

**Enforcement:**
- ✅ ALL student-scoped queries MUST include `WHERE student_id = ?`
- ✅ API endpoints MUST verify JWT token student_id matches request student_id
- ✅ No global queries returning all students' data
- ❌ NEVER allow queries without student_id filter on student-scoped tables

**Consequences of Violation:**
- Privacy violation = trust destroyed
- Regulatory non-compliance (GDPR)
- Security vulnerability (data leakage)
- **Result**: Legal liability, reputation damage, system shutdown

## Prerequisites
- SQLModel database models with student_id foreign keys
- JWT authentication implemented (get_current_student dependency)
- Understanding of SQL injection prevention

## Standard Patterns

### Pattern 1: Single Record Retrieval
```python
from uuid import UUID
from sqlmodel import Session, select
from src.models import Exam
from src.dependencies import get_current_student


def get_student_exam(
    session: Session,
    exam_id: UUID,
    student_id: UUID  # MUST be from authenticated user
) -> Exam | None:
    """
    Get exam by ID - ONLY if it belongs to the student.

    Args:
        session: Database session
        exam_id: Exam UUID
        student_id: Authenticated student UUID (from JWT token)

    Returns:
        Exam if found and belongs to student, None otherwise
    """
    # CRITICAL: Filter by BOTH exam_id AND student_id
    statement = select(Exam).where(
        Exam.id == exam_id,
        Exam.student_id == student_id  # Multi-tenant isolation
    )
    return session.exec(statement).first()


# ❌ WRONG - No student_id check
def get_exam_wrong(session: Session, exam_id: UUID):
    return session.get(Exam, exam_id)  # DANGEROUS - returns ANY student's exam!
```

### Pattern 2: List All Student Resources
```python
def list_student_exams(
    session: Session,
    student_id: UUID,
    subject_id: UUID | None = None,
    limit: int = 20,
    offset: int = 0
) -> list[Exam]:
    """
    List exams for authenticated student with optional filters.

    Args:
        session: Database session
        student_id: Authenticated student UUID
        subject_id: Optional subject filter
        limit: Max results
        offset: Pagination offset

    Returns:
        List of exams belonging to student
    """
    # Start with student_id filter (ALWAYS)
    statement = select(Exam).where(Exam.student_id == student_id)

    # Add optional filters
    if subject_id:
        statement = statement.where(Exam.subject_id == subject_id)

    # Pagination
    statement = statement.offset(offset).limit(limit)

    # Order by (newest first)
    statement = statement.order_by(Exam.created_at.desc())

    return session.exec(statement).all()
```

### Pattern 3: Count Student Resources
```python
from sqlmodel import func


def count_student_exams(
    session: Session,
    student_id: UUID,
    status: str | None = None
) -> int:
    """
    Count exams for authenticated student.

    Args:
        session: Database session
        student_id: Authenticated student UUID
        status: Optional status filter

    Returns:
        Count of exams
    """
    statement = select(func.count(Exam.id)).where(
        Exam.student_id == student_id
    )

    if status:
        statement = statement.where(Exam.status == status)

    return session.exec(statement).one()
```

### Pattern 4: Update Student Resource
```python
def update_student_exam(
    session: Session,
    exam_id: UUID,
    student_id: UUID,
    update_data: dict
) -> Exam | None:
    """
    Update exam - ONLY if it belongs to the student.

    Args:
        session: Database session
        exam_id: Exam UUID
        student_id: Authenticated student UUID
        update_data: Fields to update

    Returns:
        Updated exam if found and belongs to student, None otherwise
    """
    # Fetch with multi-tenant check
    statement = select(Exam).where(
        Exam.id == exam_id,
        Exam.student_id == student_id  # REQUIRED
    )
    exam = session.exec(statement).first()

    if not exam:
        return None  # Not found OR doesn't belong to student

    # Update fields
    for key, value in update_data.items():
        setattr(exam, key, value)

    session.add(exam)
    session.commit()
    session.refresh(exam)

    return exam


# ❌ WRONG - No ownership verification
def update_exam_wrong(session: Session, exam_id: UUID, data: dict):
    exam = session.get(Exam, exam_id)  # Gets ANY student's exam
    for key, value in data.items():
        setattr(exam, key, value)
    session.commit()
    return exam  # Just updated another student's exam!
```

### Pattern 5: Delete Student Resource (Soft Delete)
```python
from datetime import datetime


def delete_student_exam(
    session: Session,
    exam_id: UUID,
    student_id: UUID
) -> bool:
    """
    Soft delete exam - ONLY if it belongs to the student.

    Args:
        session: Database session
        exam_id: Exam UUID
        student_id: Authenticated student UUID

    Returns:
        True if deleted, False if not found or access denied
    """
    statement = select(Exam).where(
        Exam.id == exam_id,
        Exam.student_id == student_id,
        Exam.deleted_at.is_(None)  # Not already deleted
    )
    exam = session.exec(statement).first()

    if not exam:
        return False

    # Soft delete
    exam.deleted_at = datetime.utcnow()
    session.add(exam)
    session.commit()

    return True
```

### Pattern 6: Join with Student Verification
```python
from src.models import AttemptedQuestion, Question


def get_student_attempt_with_question(
    session: Session,
    attempted_question_id: UUID,
    student_id: UUID
) -> tuple[AttemptedQuestion, Question] | None:
    """
    Get attempted question with full question details.

    Verifies attempt belongs to student via attempt -> exam -> student chain.

    Args:
        session: Database session
        attempted_question_id: AttemptedQuestion UUID
        student_id: Authenticated student UUID

    Returns:
        Tuple of (AttemptedQuestion, Question) if found and authorized
    """
    from src.models import Attempt, Exam

    statement = (
        select(AttemptedQuestion, Question)
        .join(Question, AttemptedQuestion.question_id == Question.id)
        .join(Attempt, AttemptedQuestion.attempt_id == Attempt.id)
        .join(Exam, Attempt.exam_id == Exam.id)
        .where(
            AttemptedQuestion.id == attempted_question_id,
            Exam.student_id == student_id  # Multi-tenant check via join chain
        )
    )

    result = session.exec(statement).first()
    return result if result else None
```

### Pattern 7: Aggregations with Student Scope
```python
def get_student_progress_stats(
    session: Session,
    student_id: UUID,
    subject_id: UUID
) -> dict:
    """
    Calculate student's progress statistics for a subject.

    Args:
        session: Database session
        student_id: Authenticated student UUID
        subject_id: Subject UUID

    Returns:
        Dict with average_score, total_attempts, etc.
    """
    from src.models import Attempt

    # Average score across all attempts for this subject
    avg_score_stmt = (
        select(func.avg(Attempt.overall_score))
        .join(Exam, Attempt.exam_id == Exam.id)
        .where(
            Exam.student_id == student_id,  # REQUIRED
            Exam.subject_id == subject_id
        )
    )
    avg_score = session.exec(avg_score_stmt).one()

    # Total attempts
    count_stmt = (
        select(func.count(Attempt.id))
        .join(Exam, Attempt.exam_id == Exam.id)
        .where(
            Exam.student_id == student_id,  # REQUIRED
            Exam.subject_id == subject_id
        )
    )
    total_attempts = session.exec(count_stmt).one()

    return {
        "average_score": avg_score or 0,
        "total_attempts": total_attempts,
        "subject_id": subject_id
    }
```

## Integration with FastAPI Routes

### Correct Pattern: Inject Current Student
```python
from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import get_current_student
from src.models import Student

router = APIRouter()


@router.get("/exams/{exam_id}")
def get_exam_endpoint(
    exam_id: UUID,
    session: SessionDep,
    current_student: Student = Depends(get_current_student)  # JWT verification
):
    """Get exam - automatically filtered by student_id from JWT token"""

    exam = get_student_exam(
        session,
        exam_id=exam_id,
        student_id=current_student.id  # From authenticated token
    )

    if not exam:
        # Generic error - don't reveal if exam exists for another student
        raise HTTPException(404, "Exam not found")

    return exam_to_response(exam)


# ❌ WRONG - No authentication, student_id from path parameter
@router.get("/students/{student_id}/exams/{exam_id}")
def get_exam_wrong(student_id: UUID, exam_id: UUID, session: SessionDep):
    # DANGEROUS - anyone can query any student's data by changing student_id in URL
    exam = get_student_exam(session, exam_id, student_id)
    return exam
```

## Testing Multi-Tenant Isolation

```python
# tests/integration/test_multi_tenant.py
import pytest
from uuid import uuid4


def test_student_cannot_access_other_student_exam(client, session):
    """CRITICAL TEST: Verify students can't access each other's data"""

    # Create two students
    student_a = create_student(session, email="alice@example.com", ...)
    student_b = create_student(session, email="bob@example.com", ...)

    # Student A creates an exam
    exam_a = create_exam(session, student_id=student_a.id, ...)

    # Student B tries to access Student A's exam
    token_b = create_access_token(student_b.id)

    response = client.get(
        f"/api/exams/{exam_a.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    # Should return 404, not 403 (don't reveal existence)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_student_list_only_shows_own_exams(client, session):
    """Verify list endpoints only return authenticated student's data"""

    student_a = create_student(session, email="alice@example.com", ...)
    student_b = create_student(session, email="bob@example.com", ...)

    # Create 3 exams for Student A
    for _ in range(3):
        create_exam(session, student_id=student_a.id, ...)

    # Create 5 exams for Student B
    for _ in range(5):
        create_exam(session, student_id=student_b.id, ...)

    # Student A lists exams
    token_a = create_access_token(student_a.id)
    response = client.get(
        "/api/exams",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    exams = response.json()
    assert len(exams) == 3  # Only Student A's exams
    assert all(e["student_id"] == str(student_a.id) for e in exams)
```

## Common Pitfalls

### ❌ Pitfall 1: Using student_id from Path Parameter
```python
@router.get("/students/{student_id}/exams")
def list_exams(student_id: UUID, session: SessionDep):
    # DANGEROUS - no verification that JWT token matches student_id
    return list_student_exams(session, student_id)
```

### ✅ Correct: Always Use Authenticated Student
```python
@router.get("/exams")  # No student_id in path
def list_exams(
    session: SessionDep,
    current_student: Student = Depends(get_current_student)
):
    return list_student_exams(session, current_student.id)
```

---

### ❌ Pitfall 2: Forgetting student_id in Complex Queries
```python
# WRONG - Missing student_id filter in subquery
def get_recent_attempts(session: Session, subject_id: UUID, student_id: UUID):
    subquery = (
        select(Attempt.id)
        .join(Exam)
        .where(Exam.subject_id == subject_id)  # Missing Exam.student_id == student_id !
        .limit(10)
    )
    return session.exec(select(Attempt).where(Attempt.id.in_(subquery))).all()
```

### ✅ Correct: student_id in All Subqueries
```python
def get_recent_attempts(session: Session, subject_id: UUID, student_id: UUID):
    subquery = (
        select(Attempt.id)
        .join(Exam)
        .where(
            Exam.subject_id == subject_id,
            Exam.student_id == student_id  # REQUIRED
        )
        .limit(10)
    )
    return session.exec(select(Attempt).where(Attempt.id.in_(subquery))).all()
```

---

### ❌ Pitfall 3: Revealing Existence via Error Messages
```python
# WRONG - Leaks information
exam = get_student_exam(session, exam_id, student_id)
if not exam:
    raise HTTPException(403, "You don't have access to this exam")  # Reveals it exists!
```

### ✅ Correct: Generic 404 Error
```python
exam = get_student_exam(session, exam_id, student_id)
if not exam:
    raise HTTPException(404, "Exam not found")  # Doesn't reveal existence
```

## Audit Checklist

**Before deploying ANY query, verify:**
- [ ] Query filters by `student_id` if accessing student-scoped table
- [ ] `student_id` comes from `get_current_student()` dependency (JWT token)
- [ ] Never uses `student_id` from path/query parameters without verification
- [ ] All JOINs maintain student_id filtering chain
- [ ] Subqueries include student_id filters
- [ ] Error messages don't reveal existence of other students' data
- [ ] Integration tests verify isolation between students

## Constitutional Compliance

**Principle V: Multi-Tenant Isolation is Sacred**
- ✅ Every student-scoped query filtered by student_id
- ✅ student_id from authenticated JWT token only
- ✅ No leakage of other students' data existence
- ✅ Integration tests verify isolation

**Enforcement**: Code review MUST flag any query missing student_id filter

## Usage Frequency
**Must Use:** 100% of student-scoped database queries
**Current Usage:** Every query in Phase I (registration, future login)
**Future Usage:** Every query in Phases II-V (exams, attempts, progress, etc.)

**Version**: 1.0.0 | **Last Updated**: 2025-12-18
