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

Resource Bank Models (006):
- GeneratedExplanation: Shared topic explanations with versioning
- StudentLearningPath: Per-student learning progress tracking
- StudentLLMConfig: Encrypted storage for student LLM API keys

Resource Bank Models (007):
- Resource: File storage with multi-source support
- SyllabusPointResource: Resource-to-syllabus mapping with relevance scores
- ExplanationResourceUsage: Track resource usage in explanations
- StudentResourcePreference: Student-specific resource preferences

Academic Level Hierarchy Models (008):
- AcademicLevel: Qualification types (A-Level, O-Level, IGCSE, IB)
- Syllabus: Syllabus versions with codes and year ranges
"""

from src.models.academic_level import AcademicLevel, DEFAULT_ACADEMIC_LEVELS
from src.models.attempt import Attempt
from src.models.attempted_question import AttemptedQuestion
from src.models.coaching_session import CoachingSession
from src.models.enums import (
    AddedBy,
    GeneratedByType,
    LLMProvider,
    MasteryLevel,
    PersonalizationStyle,
    ResourceType,
    S3SyncStatus,
    Visibility,
)
from src.models.explanation_resource_usage import ExplanationResourceUsage
from src.models.exam import Exam
from src.models.generated_explanation import GeneratedExplanation
from src.models.improvement_plan import ImprovementPlan
from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.resource import Resource
from src.models.saved_explanation import SavedExplanation
from src.models.student import Student
from src.models.student_learning_path import StudentLearningPath
from src.models.student_llm_config import StudentLLMConfig
from src.models.student_resource_preference import StudentResourcePreference
from src.models.study_plan import StudyPlan
from src.models.subject import Subject, SubjectSetupStatus
from src.models.syllabus import Syllabus
from src.models.syllabus_point import SyllabusPoint
from src.models.syllabus_point_resource import SyllabusPointResource

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
    # Resource Bank (006)
    "GeneratedExplanation",
    "StudentLearningPath",
    "StudentLLMConfig",
    # Resource Bank (007)
    "Resource",
    "SyllabusPointResource",
    "ExplanationResourceUsage",
    "StudentResourcePreference",
    # Enums (006)
    "GeneratedByType",
    "LLMProvider",
    "MasteryLevel",
    "PersonalizationStyle",
    # Enums (007)
    "AddedBy",
    "ResourceType",
    "S3SyncStatus",
    "Visibility",
    # Enums (Admin Setup)
    "SubjectSetupStatus",
    # Academic Level Hierarchy (008)
    "AcademicLevel",
    "DEFAULT_ACADEMIC_LEVELS",
    "Syllabus",
]
