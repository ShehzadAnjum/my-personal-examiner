"""
Database Models Package

All SQLModel models for the application.

Phase I Models:
- Student: User accounts (multi-tenant isolation)
- Subject: A-Level subjects (global entity)
- SyllabusPoint: Syllabus learning objectives (global entity)

Phase II Models:
- Question: Exam questions (global entity)
- MarkScheme: Mark schemes (global entity)
- Exam: Generated exams (practice, timed, full paper)
- Attempt: Student exam attempts (scoring, grading)
- AttemptedQuestion: Question-level responses (marking, confidence scoring)

Phase III Models:
- CoachingSession: Tutor session transcripts (Coach Agent)
- StudyPlan: Personalized study schedules (Planner Agent, SM-2 algorithm)
- ImprovementPlan: Weakness analysis and action items (Reviewer Agent)

Phase IV Models:
- SavedExplanation: Bookmarked explanations (Teaching Page)
"""

from src.models.attempt import Attempt
from src.models.attempted_question import AttemptedQuestion
from src.models.coaching_session import CoachingSession
from src.models.exam import Exam
from src.models.improvement_plan import ImprovementPlan
from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.saved_explanation import SavedExplanation
from src.models.student import Student
from src.models.study_plan import StudyPlan
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint

__all__ = [
    # Phase I
    "Student",
    "Subject",
    "SyllabusPoint",
    # Phase II
    "Question",
    "MarkScheme",
    "Exam",
    "Attempt",
    "AttemptedQuestion",
    # Phase III
    "CoachingSession",
    "StudyPlan",
    "ImprovementPlan",
    # Phase IV
    "SavedExplanation",
]
