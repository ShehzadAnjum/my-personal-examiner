"""
Syllabus Routes

API endpoints for syllabus point management and question tagging.

Phase II User Story 7: Syllabus Tagging
- CRUD operations on syllabus points
- Tag questions with syllabus points
- Filter questions by syllabus points
- Track syllabus coverage
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session, and_, func, select

from src.database import get_session
from src.models.question import Question
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint

router = APIRouter(prefix="/api/syllabus", tags=["syllabus"])


# Request/Response Schemas


class SyllabusPointCreate(BaseModel):
    """Request schema for creating syllabus point"""

    subject_code: str = Field(..., description="Subject code (e.g., '9708')")
    code: str = Field(..., max_length=20, description="Syllabus code (e.g., '9708.1.1')")
    description: str = Field(..., description="Learning objective description")
    topics: str | None = Field(None, description="Comma-separated topics")
    learning_outcomes: str | None = Field(None, description="Expected learning outcomes")


class SyllabusPointUpdate(BaseModel):
    """Request schema for updating syllabus point"""

    description: str | None = Field(None, description="Learning objective description")
    topics: str | None = Field(None, description="Comma-separated topics")
    learning_outcomes: str | None = Field(None, description="Expected learning outcomes")


class SyllabusPointResponse(BaseModel):
    """Response schema for syllabus point"""

    id: UUID
    subject_id: UUID
    code: str
    description: str
    topics: str | None
    learning_outcomes: str | None

    class Config:
        from_attributes = True


class QuestionTagRequest(BaseModel):
    """Request schema for tagging questions"""

    syllabus_point_ids: list[str] = Field(
        ..., description="List of syllabus point UUIDs to add to question"
    )


class SyllabusCoverageResponse(BaseModel):
    """Response schema for syllabus coverage statistics"""

    subject_id: UUID
    total_syllabus_points: int
    tagged_syllabus_points: int
    coverage_percentage: float
    untagged_syllabus_points: list[dict[str, Any]]
    questions_per_syllabus_point: dict[str, int]


# Syllabus Point CRUD Endpoints


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SyllabusPointResponse)
def create_syllabus_point(
    request: SyllabusPointCreate,
    db: Session = Depends(get_session),
) -> Any:
    """
    Create a new syllabus point

    Creates a new learning objective or topic within a subject syllabus.
    Code must follow pattern: {subject_code}.{section}.{subsection}

    Examples:
        POST /api/syllabus
        {
            "subject_code": "9708",
            "code": "9708.1.1",
            "description": "The central economic problem",
            "topics": "Scarcity, Choice, Opportunity cost",
            "learning_outcomes": "Understand the nature of the economic problem"
        }
    """
    # Lookup subject
    stmt = select(Subject).where(Subject.code == request.subject_code)
    subject = db.exec(stmt).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with code '{request.subject_code}' not found",
        )

    # Check for duplicate code
    existing_stmt = select(SyllabusPoint).where(
        and_(
            SyllabusPoint.subject_id == subject.id,
            SyllabusPoint.code == request.code,
        )
    )
    existing = db.exec(existing_stmt).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Syllabus point with code '{request.code}' already exists for this subject",
        )

    # Create syllabus point
    syllabus_point = SyllabusPoint(
        subject_id=subject.id,
        code=request.code,
        description=request.description,
        topics=request.topics,
        learning_outcomes=request.learning_outcomes,
    )

    db.add(syllabus_point)
    db.commit()
    db.refresh(syllabus_point)

    return syllabus_point


@router.get("", response_model=list[SyllabusPointResponse])
def list_syllabus_points(
    subject_code: str | None = Query(None, description="Filter by subject code (deprecated)"),
    subject_id: UUID | None = Query(None, description="Filter by subject UUID (deprecated)"),
    syllabus_id: UUID | None = Query(None, description="Filter by syllabus UUID (preferred)"),
    code_prefix: str | None = Query(None, description="Filter by code prefix (e.g., '1.1')"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_session),
) -> Any:
    """
    List syllabus points with optional filtering

    Feature: 008-academic-level-hierarchy (T049)

    Supports filtering by (in order of preference):
    - syllabus_id: Get syllabus points for a specific syllabus (PREFERRED)
    - subject_id: Get syllabus points for a specific subject (deprecated)
    - subject_code: Get syllabus points for a specific subject by code (deprecated)
    - code_prefix: Get syllabus points matching a code prefix

    Returns paginated results (default 50 per page, max 200).

    Examples:
        GET /api/syllabus?syllabus_id=uuid (preferred)
        GET /api/syllabus?subject_id=uuid (deprecated)
        GET /api/syllabus?subject_code=9708 (deprecated)
        GET /api/syllabus?syllabus_id=uuid&code_prefix=1.1
    """
    # Build query
    stmt = select(SyllabusPoint)

    # Apply filters - prefer syllabus_id over subject_id over subject_code
    if syllabus_id:
        # New preferred filter: by syllabus UUID
        stmt = stmt.where(SyllabusPoint.syllabus_id == syllabus_id)
    elif subject_id:
        # Deprecated: filter by subject UUID
        stmt = stmt.where(SyllabusPoint.subject_id == subject_id)
    elif subject_code:
        # Deprecated: lookup subject by code
        subject_stmt = select(Subject).where(Subject.code == subject_code)
        subject = db.exec(subject_stmt).first()
        if subject:
            stmt = stmt.where(SyllabusPoint.subject_id == subject.id)
        else:
            return []

    if code_prefix:
        # Use LIKE for prefix matching
        stmt = stmt.where(SyllabusPoint.code.like(f"{code_prefix}%"))

    # Order by code
    stmt = stmt.order_by(SyllabusPoint.code)

    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # Execute query
    syllabus_points = db.exec(stmt).all()

    return syllabus_points


@router.get("/{syllabus_point_id}", response_model=SyllabusPointResponse)
def get_syllabus_point(
    syllabus_point_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get syllabus point by ID

    Returns full syllabus point details including description, topics, and learning outcomes.

    Examples:
        GET /api/syllabus/123e4567-e89b-12d3-a456-426614174000
    """
    stmt = select(SyllabusPoint).where(SyllabusPoint.id == syllabus_point_id)
    syllabus_point = db.exec(stmt).first()

    if not syllabus_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus point with ID '{syllabus_point_id}' not found",
        )

    return syllabus_point


@router.patch("/{syllabus_point_id}", response_model=SyllabusPointResponse)
def update_syllabus_point(
    syllabus_point_id: UUID,
    request: SyllabusPointUpdate,
    db: Session = Depends(get_session),
) -> Any:
    """
    Update syllabus point

    Updates description, topics, or learning outcomes.
    Code and subject_id cannot be changed.

    Examples:
        PATCH /api/syllabus/123e4567-e89b-12d3-a456-426614174000
        {
            "description": "Updated description",
            "topics": "Updated topics"
        }
    """
    stmt = select(SyllabusPoint).where(SyllabusPoint.id == syllabus_point_id)
    syllabus_point = db.exec(stmt).first()

    if not syllabus_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus point with ID '{syllabus_point_id}' not found",
        )

    # Update fields
    if request.description is not None:
        syllabus_point.description = request.description
    if request.topics is not None:
        syllabus_point.topics = request.topics
    if request.learning_outcomes is not None:
        syllabus_point.learning_outcomes = request.learning_outcomes

    db.add(syllabus_point)
    db.commit()
    db.refresh(syllabus_point)

    return syllabus_point


@router.delete("/{syllabus_point_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_syllabus_point(
    syllabus_point_id: UUID,
    db: Session = Depends(get_session),
) -> None:
    """
    Delete syllabus point

    WARNING: This will remove the syllabus point from all questions that reference it.

    Examples:
        DELETE /api/syllabus/123e4567-e89b-12d3-a456-426614174000
    """
    stmt = select(SyllabusPoint).where(SyllabusPoint.id == syllabus_point_id)
    syllabus_point = db.exec(stmt).first()

    if not syllabus_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus point with ID '{syllabus_point_id}' not found",
        )

    # Delete syllabus point
    db.delete(syllabus_point)
    db.commit()


# Question Tagging Endpoints


@router.post("/questions/{question_id}/tags", status_code=status.HTTP_200_OK)
def add_question_tags(
    question_id: UUID,
    request: QuestionTagRequest,
    db: Session = Depends(get_session),
) -> Any:
    """
    Add syllabus point tags to a question

    Adds one or more syllabus points to a question's syllabus_point_ids array.
    Duplicates are automatically prevented.

    Examples:
        POST /api/syllabus/questions/123e4567-e89b-12d3-a456-426614174000/tags
        {
            "syllabus_point_ids": [
                "789e4567-e89b-12d3-a456-426614174000",
                "456e4567-e89b-12d3-a456-426614174000"
            ]
        }
    """
    # Get question
    stmt = select(Question).where(Question.id == question_id)
    question = db.exec(stmt).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' not found",
        )

    # Verify all syllabus points exist
    for sp_id in request.syllabus_point_ids:
        sp_stmt = select(SyllabusPoint).where(SyllabusPoint.id == UUID(sp_id))
        sp = db.exec(sp_stmt).first()
        if not sp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Syllabus point with ID '{sp_id}' not found",
            )

    # Get current tags (or initialize empty list)
    current_tags = question.syllabus_point_ids if question.syllabus_point_ids else []

    # Add new tags (avoid duplicates)
    new_tags = list(set(current_tags + request.syllabus_point_ids))

    # Update question
    question.syllabus_point_ids = new_tags
    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "question_id": str(question.id),
        "syllabus_point_ids": question.syllabus_point_ids,
        "tags_added": len(new_tags) - len(current_tags),
    }


@router.delete("/questions/{question_id}/tags/{syllabus_point_id}", status_code=status.HTTP_200_OK)
def remove_question_tag(
    question_id: UUID,
    syllabus_point_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Remove a syllabus point tag from a question

    Removes the specified syllabus point from the question's syllabus_point_ids array.

    Examples:
        DELETE /api/syllabus/questions/123e4567-e89b-12d3-a456-426614174000/tags/789e4567-e89b-12d3-a456-426614174000
    """
    # Get question
    stmt = select(Question).where(Question.id == question_id)
    question = db.exec(stmt).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' not found",
        )

    # Get current tags
    current_tags = question.syllabus_point_ids if question.syllabus_point_ids else []

    # Remove tag (if exists)
    syllabus_point_id_str = str(syllabus_point_id)
    if syllabus_point_id_str in current_tags:
        current_tags.remove(syllabus_point_id_str)
        question.syllabus_point_ids = current_tags
        db.add(question)
        db.commit()
        db.refresh(question)
        removed = True
    else:
        removed = False

    return {
        "question_id": str(question.id),
        "syllabus_point_ids": question.syllabus_point_ids,
        "removed": removed,
    }


@router.get("/questions/{question_id}/tags", status_code=status.HTTP_200_OK)
def get_question_tags(
    question_id: UUID,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get all syllabus point tags for a question

    Returns full syllabus point details (not just IDs).

    Examples:
        GET /api/syllabus/questions/123e4567-e89b-12d3-a456-426614174000/tags
    """
    # Get question
    stmt = select(Question).where(Question.id == question_id)
    question = db.exec(stmt).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' not found",
        )

    # Get syllabus point tags
    tags = question.syllabus_point_ids if question.syllabus_point_ids else []

    if not tags:
        return {"question_id": str(question.id), "syllabus_points": []}

    # Fetch full syllabus point details
    syllabus_points = []
    for tag_id in tags:
        sp_stmt = select(SyllabusPoint).where(SyllabusPoint.id == UUID(tag_id))
        sp = db.exec(sp_stmt).first()
        if sp:
            syllabus_points.append(
                {
                    "id": str(sp.id),
                    "code": sp.code,
                    "description": sp.description,
                    "topics": sp.topics,
                    "learning_outcomes": sp.learning_outcomes,
                }
            )

    return {
        "question_id": str(question.id),
        "syllabus_points": syllabus_points,
    }


# Syllabus Coverage Endpoints


@router.get("/coverage/{subject_code}", status_code=status.HTTP_200_OK)
def get_syllabus_coverage(
    subject_code: str,
    db: Session = Depends(get_session),
) -> Any:
    """
    Get syllabus coverage statistics for a subject

    Returns:
    - Total syllabus points
    - Number of syllabus points with at least one question
    - Coverage percentage
    - List of untagged syllabus points
    - Questions per syllabus point

    Examples:
        GET /api/syllabus/coverage/9708
    """
    # Lookup subject
    subject_stmt = select(Subject).where(Subject.code == subject_code)
    subject = db.exec(subject_stmt).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with code '{subject_code}' not found",
        )

    # Get all syllabus points for this subject
    sp_stmt = select(SyllabusPoint).where(SyllabusPoint.subject_id == subject.id)
    all_syllabus_points = db.exec(sp_stmt).all()

    total_syllabus_points = len(all_syllabus_points)

    # Get all questions for this subject
    q_stmt = select(Question).where(Question.subject_id == subject.id)
    all_questions = db.exec(q_stmt).all()

    # Count questions per syllabus point
    questions_per_sp = {}
    for sp in all_syllabus_points:
        sp_id_str = str(sp.id)
        count = sum(
            1
            for q in all_questions
            if q.syllabus_point_ids and sp_id_str in q.syllabus_point_ids
        )
        questions_per_sp[sp.code] = count

    # Find untagged syllabus points
    untagged_syllabus_points = [
        {"id": str(sp.id), "code": sp.code, "description": sp.description}
        for sp in all_syllabus_points
        if questions_per_sp.get(sp.code, 0) == 0
    ]

    # Calculate coverage
    tagged_syllabus_points = sum(1 for count in questions_per_sp.values() if count > 0)
    coverage_percentage = (
        (tagged_syllabus_points / total_syllabus_points * 100)
        if total_syllabus_points > 0
        else 0.0
    )

    return {
        "subject_id": str(subject.id),
        "subject_code": subject_code,
        "total_syllabus_points": total_syllabus_points,
        "tagged_syllabus_points": tagged_syllabus_points,
        "coverage_percentage": round(coverage_percentage, 2),
        "untagged_syllabus_points": untagged_syllabus_points,
        "questions_per_syllabus_point": questions_per_sp,
    }
