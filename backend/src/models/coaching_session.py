"""Coach Agent - Coaching Session Model

Constitutional Requirements:
- Principle V: Multi-tenant isolation (student_id FK enforced)
- Principle VII: >80% test coverage (simple CRUD model, easily testable)
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON
from typing_extensions import TypedDict


class MessageDict(TypedDict):
    """TypedDict for session transcript messages"""
    role: str  # "student" or "coach"
    content: str
    timestamp: str  # ISO 8601 format


class CoachingSession(SQLModel, table=True):
    """
    Store tutoring sessions between students and Coach Agent.

    Uses Socratic method to diagnose misconceptions and provide scaffolded learning.
    Session transcript stored as JSONB array for flexibility and queryability.

    State Machine:
    - in_progress → resolved (student understands)
    - in_progress → needs_more_help (student still stuck after session)
    - in_progress → refer_to_teacher (concept too complex for coaching)
    """

    __tablename__ = "coaching_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    student_id: UUID = Field(foreign_key="students.id", nullable=False)
    topic: str = Field(max_length=500, nullable=False)
    struggle_description: Optional[str] = Field(default=None)

    # JSONB field: Array of {role: "student"|"coach", content: str, timestamp: ISO8601}
    session_transcript: List[MessageDict] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list
    )

    # Enum: in_progress, resolved, needs_more_help, refer_to_teacher
    outcome: str = Field(default="in_progress", max_length=50)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "price elasticity of demand",
                "struggle_description": "I don't understand why PED is negative",
                "session_transcript": [
                    {
                        "role": "coach",
                        "content": "Let's start simple: Can you explain what happens to quantity demanded when price increases?",
                        "timestamp": "2025-01-15T10:00:00Z"
                    },
                    {
                        "role": "student",
                        "content": "It decreases",
                        "timestamp": "2025-01-15T10:00:30Z"
                    }
                ],
                "outcome": "in_progress"
            }
        }
