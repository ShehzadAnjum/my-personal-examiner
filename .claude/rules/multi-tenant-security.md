# Rule: Multi-Tenant Security

**Priority**: CRITICAL
**Enforcement**: Every database query

---

## Rule Statement

Every database query that accesses user-scoped data MUST include a `student_id` filter.

## Why This Matters

Students' exam results, study plans, and learning data are private. Without proper filtering, Student A could access Student B's data, violating privacy and trust.

## Examples

### Correct
```python
def get_student_exams(student_id: UUID, session: Session):
    return session.exec(
        select(Exam).where(Exam.student_id == student_id)
    ).all()
```

### Violation
```python
def get_all_exams(session: Session):
    return session.exec(select(Exam)).all()  # CONSTITUTIONAL VIOLATION
```

## Applies To

- All tables with `student_id` column
- All API endpoints returning user data
- All service methods accessing user data

## Exceptions

- Admin-only endpoints (with admin role verification)
- Aggregated analytics (no PII exposed)
