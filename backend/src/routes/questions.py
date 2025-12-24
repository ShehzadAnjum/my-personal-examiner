"""
Questions API Routes

Handles question paper and mark scheme upload, storage, and retrieval.

Phase II User Story 1: Upload & Storage
- POST /api/questions/upload - Upload question paper or mark scheme PDF
- GET /api/questions - List questions with filtering
- GET /api/questions/{id} - Get single question details
"""

import hashlib
import shutil
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlmodel import Session

from src.database import get_session
from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.subject import Subject
from src.services.extraction_service import ExtractionError, ExtractionService
from src.services.search_service import SearchService

router = APIRouter(prefix="/api/questions", tags=["questions"])

# File storage configuration
UPLOAD_DIR = Path("uploads/pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    subject_code: str = Form(...),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Upload question paper or mark scheme PDF

    Automatically detects PDF type (question paper vs mark scheme) from filename.
    Extracts questions or mark scheme text and stores in database.

    Args:
        file: PDF file (question paper or mark scheme)
        subject_code: Cambridge subject code (e.g., "9708")
        session: Database session (dependency injection)

    Returns:
        dict with:
            - type: "question_paper" or "mark_scheme"
            - questions_count: Number of questions extracted (if QP)
            - mark_scheme_id: Mark scheme UUID (if MS)
            - source_paper: Source paper identifier
            - filename: Original filename

    Raises:
        HTTPException 400: Invalid file or extraction failed
        HTTPException 404: Subject not found
        HTTPException 409: Duplicate upload (file already exists)

    Examples:
        POST /api/questions/upload
        Content-Type: multipart/form-data

        file: 9708_s22_qp_22.pdf
        subject_code: 9708

        Response:
        {
            "type": "question_paper",
            "questions_count": 4,
            "source_paper": "9708_s22_qp_22",
            "filename": "9708_s22_qp_22.pdf"
        }
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Find subject by code
    stmt = select(Subject).where(Subject.code == subject_code)
    subject = session.exec(stmt).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {subject_code} not found",
        )

    # Calculate file hash to detect duplicates
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    # Check for duplicate uploads (same file hash)
    # Check questions table
    stmt_q = select(Question).where(Question.file_path.contains(file_hash))
    existing_q = session.exec(stmt_q).first()

    # Check mark_schemes table
    stmt_ms = select(MarkScheme).where(MarkScheme.file_path.contains(file_hash))
    existing_ms = session.exec(stmt_ms).first()

    if existing_q or existing_ms:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already uploaded (duplicate detected)",
        )

    # Save file to disk
    file_dir = UPLOAD_DIR / subject_code
    file_dir.mkdir(parents=True, exist_ok=True)

    # Include hash in filename to ensure uniqueness
    file_path = file_dir / f"{file_hash[:8]}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Initialize extraction service
    extraction_service = ExtractionService()

    # Detect PDF type
    pdf_type = extraction_service.detect_pdf_type(file.filename)

    try:
        if pdf_type == "question_paper":
            # Extract questions from question paper
            if not subject.extraction_patterns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject {subject_code} has no extraction patterns configured",
                )

            questions = extraction_service.extract_question_paper(
                str(file_path), subject.id, subject.extraction_patterns
            )

            # Save questions to database
            for question in questions:
                session.add(question)

            session.commit()

            return {
                "type": "question_paper",
                "questions_count": len(questions),
                "source_paper": questions[0].source_paper if questions else None,
                "filename": file.filename,
            }

        elif pdf_type == "mark_scheme":
            # Extract mark scheme
            mark_scheme, qp_filename = extraction_service.extract_mark_scheme(
                str(file_path), subject.id
            )

            # Save mark scheme to database
            session.add(mark_scheme)
            session.commit()
            session.refresh(mark_scheme)

            return {
                "type": "mark_scheme",
                "mark_scheme_id": str(mark_scheme.id),
                "source_paper": mark_scheme.source_paper,
                "question_paper_filename": qp_filename,
                "filename": file.filename,
            }

        else:
            # Unknown PDF type
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Cambridge filename: {file.filename}. Expected format: NNNN_sYY_qp/ms_NN.pdf",
            )

    except ExtractionError as e:
        # Cleanup file on extraction failure
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extraction failed: {str(e)}",
        ) from e

    except Exception as e:
        # Cleanup file on unexpected error
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e


@router.get("/search")
async def search_questions(
    search_text: str | None = None,
    subject_code: str | None = None,
    paper_number: int | None = None,
    year: int | None = None,
    session: str | None = None,
    difficulty: str | None = None,
    syllabus_point_ids: str | None = None,  # Comma-separated UUIDs
    min_marks: int | None = None,
    max_marks: int | None = None,
    sort_by: str = "year",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Search questions with advanced filtering

    Supports full-text search, multiple filters, pagination, and sorting.

    Args:
        search_text: Search question text (case-insensitive)
        subject_code: Filter by subject code (e.g., "9708")
        paper_number: Filter by paper number (e.g., 22, 31, 42)
        year: Filter by exam year (e.g., 2022)
        session: Filter by session (MAY_JUNE, FEB_MARCH, OCT_NOV)
        difficulty: Filter by difficulty (easy, medium, hard)
        syllabus_point_ids: Filter by syllabus points (comma-separated UUIDs)
        min_marks: Minimum marks filter
        max_marks: Maximum marks filter
        sort_by: Sort field (year, max_marks, difficulty, created_at)
        sort_order: Sort order (asc, desc)
        page: Page number (default: 1)
        page_size: Results per page (default: 20, max: 100)
        db: Database session (dependency injection)

    Returns:
        dict with:
            - questions: List of question objects
            - total: Total count (all pages)
            - page: Current page number
            - page_size: Results per page
            - total_pages: Total number of pages
            - has_next: Whether next page exists
            - has_prev: Whether previous page exists

    Examples:
        GET /api/questions/search?search_text=opportunity+cost&year=2022&page=1

        Response:
        {
            "questions": [...],
            "total": 15,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "has_next": false,
            "has_prev": false
        }
    """
    # Parse syllabus_point_ids if provided
    syllabus_points = None
    if syllabus_point_ids:
        syllabus_points = syllabus_point_ids.split(",")

    # Use SearchService for advanced filtering
    search_service = SearchService(db)
    results = search_service.search_questions(
        search_text=search_text,
        subject_code=subject_code,
        paper_number=paper_number,
        year=year,
        session=session,
        difficulty=difficulty,
        syllabus_point_ids=syllabus_points,
        min_marks=min_marks,
        max_marks=max_marks,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return results


@router.get("/")
async def list_questions(
    subject_code: str | None = None,
    paper_number: int | None = None,
    year: int | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    List questions with basic filtering (simplified version of search)

    Args:
        subject_code: Filter by subject code (e.g., "9708")
        paper_number: Filter by paper number (e.g., 22, 31, 42)
        year: Filter by exam year (e.g., 2022)
        page: Page number (default: 1)
        page_size: Results per page (default: 20, max: 100)
        db: Database session (dependency injection)

    Returns:
        dict with pagination metadata

    Examples:
        GET /api/questions?subject_code=9708&year=2022&page=1

        Response:
        {
            "questions": [...],
            "total": 12,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "has_next": false,
            "has_prev": false
        }
    """
    # Use SearchService for consistency
    search_service = SearchService(db)
    results = search_service.search_questions(
        subject_code=subject_code,
        paper_number=paper_number,
        year=year,
        page=page,
        page_size=page_size,
    )

    return results


@router.get("/filters")
async def get_available_filters(
    subject_code: str | None = None, db: Session = Depends(get_session)
) -> dict[str, Any]:
    """
    Get available filter options for frontend dropdowns

    Returns unique values for years, sessions, paper_numbers, difficulties
    to populate search filter dropdowns.

    Args:
        subject_code: Optional subject code to filter options
        db: Database session (dependency injection)

    Returns:
        dict with:
            - years: List of available years (sorted desc)
            - sessions: List of available sessions
            - paper_numbers: List of available paper numbers
            - difficulties: List of available difficulties

    Examples:
        GET /api/questions/filters?subject_code=9708

        Response:
        {
            "years": [2023, 2022, 2021],
            "sessions": ["FEB_MARCH", "MAY_JUNE", "OCT_NOV"],
            "paper_numbers": [11, 12, 21, 22, 31, 32],
            "difficulties": ["easy", "hard", "medium"]
        }
    """
    search_service = SearchService(db)
    filters = search_service.get_available_filters(subject_code=subject_code)
    return filters


@router.get("/{question_id}")
async def get_question(
    question_id: UUID, db: Session = Depends(get_session)
) -> dict[str, Any]:
    """
    Get single question by ID

    Args:
        question_id: Question UUID
        db: Database session (dependency injection)

    Returns:
        dict: Question object

    Raises:
        HTTPException 404: Question not found

    Examples:
        GET /api/questions/123e4567-e89b-12d3-a456-426614174000

        Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "question_text": "Explain...",
            "max_marks": 8,
            ...
        }
    """
    question = db.get(Question, question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found",
        )

    # Convert to dict manually to avoid serialization issues
    return {
        "id": str(question.id),
        "subject_id": str(question.subject_id),
        "question_text": question.question_text,
        "max_marks": question.max_marks,
        "difficulty": question.difficulty,
        "source_paper": question.source_paper,
        "paper_number": question.paper_number,
        "question_number": question.question_number,
        "year": question.year,
        "session": question.session,
        "marking_scheme": question.marking_scheme,
        "syllabus_point_ids": question.syllabus_point_ids,
        "file_path": question.file_path,
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "updated_at": question.updated_at.isoformat() if question.updated_at else None,
    }


# ========================================================================
# Mark Schemes Endpoints
# ========================================================================


@router.get("/mark-schemes/search")
async def search_mark_schemes(
    search_text: str | None = None,
    subject_code: str | None = None,
    paper_number: int | None = None,
    year: int | None = None,
    session: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Search mark schemes with filtering

    Args:
        search_text: Search mark scheme text (case-insensitive)
        subject_code: Filter by subject code
        paper_number: Filter by paper number
        year: Filter by exam year
        session: Filter by session
        page: Page number (default: 1)
        page_size: Results per page (default: 20, max: 100)
        db: Database session

    Returns:
        dict with pagination metadata and mark schemes

    Examples:
        GET /api/questions/mark-schemes/search?search_text=Level+4&year=2022

        Response:
        {
            "mark_schemes": [...],
            "total": 5,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "has_next": false,
            "has_prev": false
        }
    """
    search_service = SearchService(db)
    results = search_service.search_mark_schemes(
        search_text=search_text,
        subject_code=subject_code,
        paper_number=paper_number,
        year=year,
        session=session,
        page=page,
        page_size=page_size,
    )

    return results


@router.get("/mark-schemes/{source_paper}")
async def get_mark_scheme(
    source_paper: str, db: Session = Depends(get_session)
) -> dict[str, Any]:
    """
    Get mark scheme by source paper identifier

    Args:
        source_paper: Source paper identifier (e.g., "9708_s22_ms_22")
        db: Database session

    Returns:
        dict: Mark scheme object

    Raises:
        HTTPException 404: Mark scheme not found

    Examples:
        GET /api/questions/mark-schemes/9708_s22_ms_22

        Response:
        {
            "id": "...",
            "source_paper": "9708_s22_ms_22",
            "mark_scheme_text": "...",
            "question_paper_filename": "9708_s22_qp_22.pdf",
            ...
        }
    """
    search_service = SearchService(db)
    mark_scheme = search_service.get_mark_scheme_by_source_paper(source_paper)

    if not mark_scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mark scheme {source_paper} not found",
        )

    # Convert to dict manually to avoid serialization issues
    return {
        "id": str(mark_scheme.id),
        "subject_id": str(mark_scheme.subject_id),
        "source_paper": mark_scheme.source_paper,
        "mark_scheme_text": mark_scheme.mark_scheme_text,
        "question_paper_filename": mark_scheme.question_paper_filename,
        "paper_number": mark_scheme.paper_number,
        "year": mark_scheme.year,
        "session": mark_scheme.session,
        "file_path": mark_scheme.file_path,
        "created_at": mark_scheme.created_at.isoformat() if mark_scheme.created_at else None,
        "updated_at": mark_scheme.updated_at.isoformat() if mark_scheme.updated_at else None,
    }
