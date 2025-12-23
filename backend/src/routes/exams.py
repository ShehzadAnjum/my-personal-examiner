"""
Exam Routes

API endpoints for exam generation and management.

Phase II User Story 6: Exam Generation
- Generate practice exams (custom question count)
- Generate timed exams (time-limited)
- Generate full papers (mimic real Cambridge papers)
- Support multiple generation strategies (random, difficulty-balanced, syllabus-based)
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from src.database import get_session
from src.models.exam import Exam
from src.models.subject import Subject
from src.services.exam_generation_service import ExamGenerationError, ExamGenerationService

router = APIRouter(prefix="/api/exams", tags=["exams"])


# Request/Response Schemas


class ExamGenerateRequest(BaseModel):
    """Request schema for exam generation"""

    subject_code: str = Field(..., description="Subject code (e.g., '9708')")
    exam_type: str = Field(..., description="PRACTICE, TIMED, or FULL_PAPER")
    paper_number: int | None = Field(None, description="Paper number (22, 31, 32, 42)")
    question_count: int | None = Field(None, ge=1, le=50, description="Number of questions")
    target_marks: int | None = Field(None, ge=1, description="Target total marks")
    duration: int | None = Field(None, ge=1, description="Exam duration in minutes")
    difficulty_distribution: dict[str, float] | None = Field(
        None, description="Difficulty mix (e.g., {'easy': 0.3, 'medium': 0.5, 'hard': 0.2})"
    )
    year: int | None = Field(None, description="Filter questions by year")
    session: str | None = Field(None, description="Filter questions by session")
    strategy: str = Field(
        "balanced",
        description="Selection strategy: random, balanced, or syllabus_coverage",
    )
    student_id: UUID | None = Field(None, description="Student ID (for personalized exams)")


class ExamResponse(BaseModel):
    """Response schema for exam details"""

    id: UUID
    student_id: UUID | None
    subject_id: UUID
    exam_type: str
    paper_number: int | None
    question_ids: list[str]
    total_marks: int
    duration: int
    status: str
    created_at: str

    class Config:
        from_attributes = True


class ExamStatusUpdateRequest(BaseModel):
    """Request schema for exam status update"""

    status: str = Field(..., description="New status: PENDING, IN_PROGRESS, or COMPLETED")


# Endpoints


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExamResponse)
def generate_exam(
    request: ExamGenerateRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Generate a new exam with intelligent question selection

    Supports multiple exam types and selection strategies:
    - **PRACTICE**: Custom question count, no time pressure
    - **TIMED**: Time-limited practice
    - **FULL_PAPER**: Mimics real Cambridge papers

    Selection strategies:
    - **random**: Random question selection
    - **balanced**: Difficulty-balanced (30% easy, 50% medium, 20% hard)
    - **syllabus_coverage**: Maximize topic diversity

    Examples:
        POST /api/exams
        {
            "subject_code": "9708",
            "exam_type": "PRACTICE",
            "question_count": 10,
            "target_marks": 60,
            "duration": 90,
            "strategy": "balanced"
        }
    """
    # Lookup subject by code
    stmt = select(Subject).where(Subject.code == request.subject_code)
    subject = db.exec(stmt).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with code '{request.subject_code}' not found",
        )

    # Create exam generation service
    exam_service = ExamGenerationService(db)

    try:
        # Generate exam
        exam = exam_service.generate_exam(
            subject_id=subject.id,
            exam_type=request.exam_type,
            paper_number=request.paper_number,
            question_count=request.question_count,
            target_marks=request.target_marks,
            duration=request.duration,
            difficulty_distribution=request.difficulty_distribution,
            year=request.year,
            session=request.session,
            strategy=request.strategy,
            student_id=request.student_id,
        )

        # Convert question_ids to list if it's a dict/JSONB
        question_ids_list = exam.question_ids if isinstance(exam.question_ids, list) else []

        return ExamResponse(
            id=exam.id,
            student_id=exam.student_id,
            subject_id=exam.subject_id,
            exam_type=exam.exam_type,
            paper_number=exam.paper_number,
            question_ids=question_ids_list,
            total_marks=exam.total_marks,
            duration=exam.duration,
            status=exam.status,
            created_at=exam.created_at.isoformat(),
        )

    except ExamGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[ExamResponse])
def list_exams(
    student_id: UUID | None = Query(None, description="Filter by student ID"),
    subject_code: str | None = Query(None, description="Filter by subject code"),
    exam_type: str | None = Query(None, description="Filter by exam type"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_session),
) -> Any:
    """
    List exams with optional filtering

    Supports filtering by:
    - student_id: Get exams for a specific student
    - subject_code: Get exams for a specific subject
    - exam_type: PRACTICE, TIMED, or FULL_PAPER
    - status: PENDING, IN_PROGRESS, or COMPLETED

    Returns paginated results (default 20 per page, max 100).

    Examples:
        GET /api/exams?student_id=123&exam_type=PRACTICE&page=1&page_size=10
    """
    # Build query
    stmt = select(Exam)

    # Apply filters
    if student_id:
        stmt = stmt.where(Exam.student_id == student_id)

    if subject_code:
        # Lookup subject
        subject_stmt = select(Subject).where(Subject.code == subject_code)
        subject = db.exec(subject_stmt).first()
        if subject:
            stmt = stmt.where(Exam.subject_id == subject.id)
        else:
            # No matching subject, return empty list
            return []

    if exam_type:
        stmt = stmt.where(Exam.exam_type == exam_type)

    if status_filter:
        stmt = stmt.where(Exam.status == status_filter)

    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # Execute query
    exams = db.exec(stmt).all()

    # Convert to response models
    return [
        ExamResponse(
            id=exam.id,
            student_id=exam.student_id,
            subject_id=exam.subject_id,
            exam_type=exam.exam_type,
            paper_number=exam.paper_number,
            question_ids=exam.question_ids if isinstance(exam.question_ids, list) else [],
            total_marks=exam.total_marks,
            duration=exam.duration,
            status=exam.status,
            created_at=exam.created_at.isoformat(),
        )
        for exam in exams
    ]


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get exam details by ID

    Returns full exam metadata including question IDs, marks, duration, and status.

    Examples:
        GET /api/exams/123e4567-e89b-12d3-a456-426614174000
    """
    stmt = select(Exam).where(Exam.id == exam_id)
    exam = db.exec(stmt).first()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with ID '{exam_id}' not found",
        )

    return ExamResponse(
        id=exam.id,
        student_id=exam.student_id,
        subject_id=exam.subject_id,
        exam_type=exam.exam_type,
        paper_number=exam.paper_number,
        question_ids=exam.question_ids if isinstance(exam.question_ids, list) else [],
        total_marks=exam.total_marks,
        duration=exam.duration,
        status=exam.status,
        created_at=exam.created_at.isoformat(),
    )


@router.get("/{exam_id}/questions")
def get_exam_questions(
    exam_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get all questions for an exam (in order)

    Returns full question objects with all metadata (text, marks, difficulty, etc.).

    Examples:
        GET /api/exams/123e4567-e89b-12d3-a456-426614174000/questions
    """
    exam_service = ExamGenerationService(db)

    try:
        questions = exam_service.get_exam_questions(exam_id)

        return {
            "exam_id": str(exam_id),
            "question_count": len(questions),
            "questions": [
                {
                    "id": str(q.id),
                    "question_text": q.question_text,
                    "max_marks": q.max_marks,
                    "difficulty": q.difficulty,
                    "source_paper": q.source_paper,
                    "paper_number": q.paper_number,
                    "question_number": q.question_number,
                    "year": q.year,
                    "session": q.session,
                    "syllabus_point_ids": q.syllabus_point_ids,
                }
                for q in questions
            ],
        }

    except ExamGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{exam_id}/statistics")
def get_exam_statistics(
    exam_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get exam statistics (difficulty breakdown, marks distribution, etc.)

    Returns:
        - total_questions: Total question count
        - total_marks: Total marks
        - difficulty_breakdown: Count per difficulty level
        - marks_per_difficulty: Marks per difficulty level
        - average_marks_per_question: Average marks

    Examples:
        GET /api/exams/123e4567-e89b-12d3-a456-426614174000/statistics
    """
    exam_service = ExamGenerationService(db)

    try:
        stats = exam_service.get_exam_statistics(exam_id)

        return {
            "exam_id": str(exam_id),
            **stats,
        }

    except ExamGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{exam_id}/status", response_model=ExamResponse)
def update_exam_status(
    exam_id: UUID,
    request: ExamStatusUpdateRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Update exam status

    Valid status transitions:
    - PENDING → IN_PROGRESS
    - IN_PROGRESS → COMPLETED
    - Any → PENDING (reset exam)

    Examples:
        PATCH /api/exams/123e4567-e89b-12d3-a456-426614174000/status
        {
            "status": "IN_PROGRESS"
        }
    """
    # Validate status
    valid_statuses = ("PENDING", "IN_PROGRESS", "COMPLETED")
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    # Get exam
    stmt = select(Exam).where(Exam.id == exam_id)
    exam = db.exec(stmt).first()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with ID '{exam_id}' not found",
        )

    # Update status
    exam.status = request.status
    db.add(exam)
    db.commit()
    db.refresh(exam)

    return ExamResponse(
        id=exam.id,
        student_id=exam.student_id,
        subject_id=exam.subject_id,
        exam_type=exam.exam_type,
        paper_number=exam.paper_number,
        question_ids=exam.question_ids if isinstance(exam.question_ids, list) else [],
        total_marks=exam.total_marks,
        duration=exam.duration,
        status=exam.status,
        created_at=exam.created_at.isoformat(),
    )
