"""
Database Models Package

All SQLModel models for the application.

Models:
- Student: User accounts (multi-tenant isolation)
- Subject: A-Level subjects (global entity)
- SyllabusPoint: Syllabus learning objectives (global entity)
- Question: Exam questions (global entity)
- MarkScheme: Mark schemes (global entity)
"""

from src.models.exam import Exam
from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.student import Student
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint

__all__ = [
    "Student",
    "Subject",
    "SyllabusPoint",
    "Question",
    "MarkScheme",
    "Exam",
]
