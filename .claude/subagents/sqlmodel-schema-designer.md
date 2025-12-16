# SQLModel Schema Designer Subagent

**Parent Agent**: Database Integrity

**Task**: Design multi-tenant database schemas with SQLModel including constraints, indexes, and relationships

**Inputs**:
- Entity description (e.g., "Student table with email, password, target grades")
- Relationships (e.g., "Student has many Exams")
- Multi-tenant requirements (student_id filtering)

**Outputs**:
- SQLModel model class with table definition
- Constraints (unique, foreign key, not null, check)
- Indexes for query performance
- Relationships (back_populates)

**Pattern**:
```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

class Student(SQLModel, table=True):
    __tablename__ = "students"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Required fields
    email: str = Field(unique=True, nullable=False, index=True, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    full_name: str = Field(nullable=False, max_length=100)

    # Optional fields
    target_grades: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # {"9708": "A*"}

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    exams: List["Exam"] = Relationship(back_populates="student", cascade_delete=True)

    # Indexes (for common queries)
    __table_args__ = (
        Index("idx_students_email", "email"),
        Index("idx_students_created_at", "created_at"),
    )
```

**Multi-Tenant Pattern (MANDATORY for user-scoped tables)**:
```python
class Exam(SQLModel, table=True):
    __tablename__ = "exams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # REQUIRED: student_id for multi-tenant isolation
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True  # CRITICAL for query performance
    )

    subject_id: UUID = Field(foreign_key="subjects.id", nullable=False)

    # Relationships
    student: "Student" = Relationship(back_populates="exams")
    subject: "Subject" = Relationship(back_populates="exams")

    # Multi-tenant index (MANDATORY)
    __table_args__ = (
        Index("idx_student_exams", "student_id", "created_at"),  # Common query pattern
    )
```

**When to Use**: Creating new database models, modifying existing schemas
