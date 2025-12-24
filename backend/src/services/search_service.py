"""
Search Service

Handles complex search and filtering for questions and mark schemes.

Phase II User Story 2: Search & Filtering
- Full-text search on question text
- Filter by subject, paper, year, session, difficulty
- Filter by syllabus points (array containment)
- Pagination support
- Sorting options
"""

from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlmodel import Session, select

from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.subject import Subject


class SearchService:
    """
    Service for searching and filtering questions and mark schemes

    Provides advanced search capabilities with multiple filters,
    full-text search, pagination, and sorting.
    """

    def __init__(self, db: Session):
        """
        Initialize search service

        Args:
            db: Database session
        """
        self.db = db

    def search_questions(
        self,
        search_text: str | None = None,
        subject_code: str | None = None,
        paper_number: int | None = None,
        year: int | None = None,
        session: str | None = None,
        difficulty: str | None = None,
        syllabus_point_ids: list[str] | None = None,
        min_marks: int | None = None,
        max_marks: int | None = None,
        sort_by: str = "year",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """
        Search questions with multiple filters

        Args:
            search_text: Full-text search on question_text (case-insensitive)
            subject_code: Filter by subject code (e.g., "9708")
            paper_number: Filter by paper number (e.g., 22, 31, 42)
            year: Filter by exam year (e.g., 2022)
            session: Filter by session (MAY_JUNE, FEB_MARCH, OCT_NOV)
            difficulty: Filter by difficulty (easy, medium, hard)
            syllabus_point_ids: Filter by syllabus points (array containment)
            min_marks: Minimum marks filter
            max_marks: Maximum marks filter
            sort_by: Sort field (year, max_marks, difficulty, created_at)
            sort_order: Sort order (asc, desc)
            page: Page number (1-indexed)
            page_size: Results per page (max 100)

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
            >>> service = SearchService(db)
            >>> results = service.search_questions(
            ...     search_text="opportunity cost",
            ...     subject_code="9708",
            ...     year=2022,
            ...     page=1,
            ...     page_size=10
            ... )
            >>> results['total']
            3
            >>> len(results['questions'])
            3
        """
        # Validate pagination
        page = max(1, page)
        page_size = min(100, max(1, page_size))

        # Build base query
        stmt = select(Question)

        # Apply filters
        filters = []

        # Subject filter
        if subject_code:
            subject_stmt = select(Subject).where(Subject.code == subject_code)
            # Use scalars() to get model instances instead of Row tuples
            subject = self.db.exec(subject_stmt).first()

            if subject:
                # Get the UUID from the Subject instance
                filters.append(Question.subject_id == subject.id)

        # Basic filters
        if paper_number:
            filters.append(Question.paper_number == paper_number)

        if year:
            filters.append(Question.year == year)

        if session:
            filters.append(Question.session == session)

        if difficulty:
            filters.append(Question.difficulty == difficulty)

        # Marks range filters
        if min_marks is not None:
            filters.append(Question.max_marks >= min_marks)

        if max_marks is not None:
            filters.append(Question.max_marks <= max_marks)

        # Syllabus point filtering (PostgreSQL array containment)
        if syllabus_point_ids and len(syllabus_point_ids) > 0:
            # @> operator: array contains all elements
            filters.append(Question.syllabus_point_ids.contains(syllabus_point_ids))

        # Full-text search on question_text (case-insensitive LIKE)
        if search_text:
            # Use ILIKE for case-insensitive search
            # For production, consider PostgreSQL full-text search (tsvector)
            search_pattern = f"%{search_text}%"
            filters.append(Question.question_text.ilike(search_pattern))

        # Apply all filters
        if filters:
            stmt = stmt.where(and_(*filters))

        # Get total count (before pagination)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        # Use scalar_one() to get the integer value directly
        total = self.db.exec(count_stmt).one()

        # Apply sorting
        sort_column = {
            "year": Question.year,
            "max_marks": Question.max_marks,
            "difficulty": Question.difficulty,
            "created_at": Question.created_at,
            "paper_number": Question.paper_number,
        }.get(sort_by, Question.year)

        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute query - use scalars() to get model instances
        questions = self.db.exec(stmt).all()

        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_prev = page > 1

        # Convert questions to dict manually to avoid .dict() issues
        questions_data = []
        for q in questions:
            questions_data.append({
                "id": str(q.id),
                "subject_id": str(q.subject_id),
                "question_text": q.question_text,
                "max_marks": q.max_marks,
                "difficulty": q.difficulty,
                "source_paper": q.source_paper,
                "paper_number": q.paper_number,
                "question_number": q.question_number,
                "year": q.year,
                "session": q.session,
                "marking_scheme": q.marking_scheme,
                "syllabus_point_ids": q.syllabus_point_ids,
                "file_path": q.file_path,
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "updated_at": q.updated_at.isoformat() if q.updated_at else None,
            })

        return {
            "questions": questions_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    def search_mark_schemes(
        self,
        search_text: str | None = None,
        subject_code: str | None = None,
        paper_number: int | None = None,
        year: int | None = None,
        session: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """
        Search mark schemes with filters

        Args:
            search_text: Full-text search on mark_scheme_text
            subject_code: Filter by subject code
            paper_number: Filter by paper number
            year: Filter by exam year
            session: Filter by session
            page: Page number (1-indexed)
            page_size: Results per page (max 100)

        Returns:
            dict with:
                - mark_schemes: List of mark scheme objects
                - total: Total count
                - page: Current page
                - page_size: Results per page
                - total_pages: Total pages
                - has_next: Next page exists
                - has_prev: Previous page exists

        Examples:
            >>> service = SearchService(db)
            >>> results = service.search_mark_schemes(
            ...     search_text="Level 4",
            ...     year=2022
            ... )
        """
        # Validate pagination
        page = max(1, page)
        page_size = min(100, max(1, page_size))

        # Build base query
        stmt = select(MarkScheme)

        # Apply filters
        filters = []

        # Subject filter
        if subject_code:
            stmt_subject = select(Subject).where(Subject.code == subject_code)
            subject = self.db.exec(stmt_subject).first()
            if subject:
                filters.append(MarkScheme.subject_id == subject.id)

        # Basic filters
        if paper_number:
            filters.append(MarkScheme.paper_number == paper_number)

        if year:
            filters.append(MarkScheme.year == year)

        if session:
            filters.append(MarkScheme.session == session)

        # Full-text search on mark_scheme_text
        if search_text:
            search_pattern = f"%{search_text}%"
            filters.append(MarkScheme.mark_scheme_text.ilike(search_pattern))

        # Apply all filters
        if filters:
            stmt = stmt.where(and_(*filters))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.exec(count_stmt).one()

        # Apply sorting (by year desc by default)
        stmt = stmt.order_by(MarkScheme.year.desc())

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute query - use scalars() to get model instances
        mark_schemes = self.db.exec(stmt).all()

        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        # Convert mark schemes to dict manually to avoid .dict() issues
        mark_schemes_data = []
        for ms in mark_schemes:
            mark_schemes_data.append({
                "id": str(ms.id),
                "subject_id": str(ms.subject_id),
                "source_paper": ms.source_paper,
                "mark_scheme_text": ms.mark_scheme_text,
                "question_paper_filename": ms.question_paper_filename,
                "paper_number": ms.paper_number,
                "year": ms.year,
                "session": ms.session,
                "file_path": ms.file_path,
                "created_at": ms.created_at.isoformat() if ms.created_at else None,
                "updated_at": ms.updated_at.isoformat() if ms.updated_at else None,
            })

        return {
            "mark_schemes": mark_schemes_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    def get_question_by_source_paper(
        self, source_paper: str, question_number: int
    ) -> Question | None:
        """
        Get specific question by source paper and question number

        Args:
            source_paper: Source paper identifier (e.g., "9708_s22_qp_22")
            question_number: Question number (e.g., 1, 2, 3)

        Returns:
            Question | None: Question if found, None otherwise

        Examples:
            >>> service = SearchService(db)
            >>> q = service.get_question_by_source_paper("9708_s22_qp_22", 1)
            >>> q.question_number
            1
        """
        stmt = select(Question).where(
            and_(
                Question.source_paper == source_paper,
                Question.question_number == question_number,
            )
        )
        return self.db.exec(stmt).first()

    def get_mark_scheme_by_source_paper(self, source_paper: str) -> MarkScheme | None:
        """
        Get mark scheme by source paper identifier

        Args:
            source_paper: Source paper identifier (e.g., "9708_s22_ms_22")

        Returns:
            MarkScheme | None: Mark scheme if found, None otherwise

        Examples:
            >>> service = SearchService(db)
            >>> ms = service.get_mark_scheme_by_source_paper("9708_s22_ms_22")
            >>> ms.source_paper
            '9708_s22_ms_22'
        """
        stmt = select(MarkScheme).where(MarkScheme.source_paper == source_paper)
        return self.db.exec(stmt).first()

    def get_available_filters(self, subject_code: str | None = None) -> dict[str, Any]:
        """
        Get available filter options (for frontend dropdowns)

        Args:
            subject_code: Optional subject code to filter options

        Returns:
            dict with:
                - years: List of available years
                - sessions: List of available sessions
                - paper_numbers: List of available paper numbers
                - difficulties: List of available difficulties

        Examples:
            >>> service = SearchService(db)
            >>> filters = service.get_available_filters(subject_code="9708")
            >>> filters['years']
            [2023, 2022, 2021, 2020]
        """
        stmt = select(Question)

        # Filter by subject if provided
        if subject_code:
            stmt_subject = select(Subject).where(Subject.code == subject_code)
            subject = self.db.exec(stmt_subject).first()
            if subject:
                stmt = stmt.where(Question.subject_id == subject.id)

        questions = self.db.exec(stmt).all()

        # Extract unique values
        years = sorted(set(q.year for q in questions if q.year), reverse=True)
        sessions = sorted(set(q.session for q in questions if q.session))
        paper_numbers = sorted(set(q.paper_number for q in questions if q.paper_number))
        difficulties = sorted(set(q.difficulty for q in questions if q.difficulty))

        return {
            "years": years,
            "sessions": sessions,
            "paper_numbers": paper_numbers,
            "difficulties": difficulties,
        }
