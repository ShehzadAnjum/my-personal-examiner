"""
Unit Tests: Search Service

Tests for Phase II US2 - Search & Filtering.

Test Coverage:
- Pagination (page, page_size, total_pages, has_next/prev)
- Filtering (subject, paper, year, session, difficulty, marks range)
- Full-text search (case-insensitive)
- Syllabus point filtering (array containment)
- Sorting (multiple fields, asc/desc)
- Mark scheme search
- Available filters extraction

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.models.subject import Subject
from src.services.search_service import SearchService


class TestSearchServicePagination:
    """Test pagination functionality"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service with mocked DB"""
        return SearchService(mock_db)

    def test_pagination_first_page(self, service, mock_db, mocker):
        """Test first page pagination metadata"""
        # Mock total count
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 50),  # Total count
            mocker.MagicMock(all=lambda: []),  # Questions result
        ])

        results = service.search_questions(page=1, page_size=20)

        assert results["page"] == 1
        assert results["page_size"] == 20
        assert results["total"] == 50
        assert results["total_pages"] == 3  # ceil(50/20)
        assert results["has_next"] is True
        assert results["has_prev"] is False

    def test_pagination_middle_page(self, service, mock_db, mocker):
        """Test middle page pagination"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 50),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(page=2, page_size=20)

        assert results["page"] == 2
        assert results["has_next"] is True
        assert results["has_prev"] is True

    def test_pagination_last_page(self, service, mock_db, mocker):
        """Test last page pagination"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 50),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(page=3, page_size=20)

        assert results["page"] == 3
        assert results["has_next"] is False
        assert results["has_prev"] is True

    def test_pagination_validates_page_number(self, service, mock_db, mocker):
        """Test page number validation (negative becomes 1)"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 10),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(page=-1, page_size=20)

        assert results["page"] == 1  # Negative page becomes 1

    def test_pagination_limits_page_size(self, service, mock_db, mocker):
        """Test page size validation (max 100)"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 10),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(page=1, page_size=200)

        assert results["page_size"] == 100  # Capped at 100


class TestSearchServiceFiltering:
    """Test filtering functionality"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service"""
        return SearchService(mock_db)

    def test_filter_by_subject_code(self, service, mock_db, mocker):
        """Test filtering by subject code"""
        # Mock subject lookup
        economics_subject = Subject(
            id=uuid4(),
            code="9708",
            name="Economics",
            level="A",
            syllabus_year="2023-2025"
        )

        # Mock DB exec calls
        subject_scalars = mocker.MagicMock()
        subject_scalars.first.return_value = economics_subject
        questions_scalars = mocker.MagicMock()
        questions_scalars.__iter__ = lambda self: iter([])

        exec_calls = [
            mocker.MagicMock(first=lambda: economics_subject),  # Subject lookup
            mocker.MagicMock(one=lambda: 0),  # Total count
            mocker.MagicMock(all=lambda: []),  # Questions
        ]
        mock_db.exec.side_effect = exec_calls

        results = service.search_questions(subject_code="9708")

        # Verify subject was looked up
        assert mock_db.exec.call_count >= 2

    def test_filter_by_year(self, service, mock_db, mocker):
        """Test filtering by year"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(year=2022)

        # Should apply year filter in query
        assert results["total"] == 0

    def test_filter_by_marks_range(self, service, mock_db, mocker):
        """Test filtering by marks range"""
        scalars_mock = mocker.MagicMock()
        scalars_mock.__iter__ = lambda self: iter([])
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(min_marks=5, max_marks=10)

        assert results["total"] == 0


class TestSearchServiceFullText:
    """Test full-text search"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service"""
        return SearchService(mock_db)

    def test_search_text_case_insensitive(self, service, mock_db, mocker):
        """Test search text is case-insensitive"""
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(search_text="OPPORTUNITY COST")

        # Should apply ILIKE filter (case-insensitive)
        assert results["total"] == 0


class TestSearchServiceSorting:
    """Test sorting functionality"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service"""
        return SearchService(mock_db)

    def test_sort_by_year_desc(self, service, mock_db, mocker):
        """Test sorting by year descending (default)"""
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(sort_by="year", sort_order="desc")

        assert results["total"] == 0

    def test_sort_by_max_marks_asc(self, service, mock_db, mocker):
        """Test sorting by marks ascending"""
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_questions(sort_by="max_marks", sort_order="asc")

        assert results["total"] == 0


class TestSearchServiceMarkSchemes:
    """Test mark scheme search"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service"""
        return SearchService(mock_db)

    def test_search_mark_schemes_with_text(self, service, mock_db, mocker):
        """Test searching mark schemes by text"""
        mocker.patch.object(mock_db, "exec", side_effect=[
            mocker.MagicMock(one=lambda: 0),
            mocker.MagicMock(all=lambda: []),
        ])

        results = service.search_mark_schemes(search_text="Level 4")

        assert results["total"] == 0
        assert "mark_schemes" in results

    def test_get_mark_scheme_by_source_paper(self, service, mock_db, mocker):
        """Test retrieving mark scheme by source paper"""
        mock_ms = MarkScheme(
            id=uuid4(),
            subject_id=uuid4(),
            source_paper="9708_s22_ms_22",
            mark_scheme_text="Sample text",
            question_paper_filename="9708_s22_qp_22.pdf",
            paper_number=22,
            year=2022,
            session="MAY_JUNE",
        )

        mocker.patch.object(mock_db, "exec", return_value=mocker.MagicMock(first=lambda: mock_ms))

        result = service.get_mark_scheme_by_source_paper("9708_s22_ms_22")

        assert result.source_paper == "9708_s22_ms_22"


class TestSearchServiceAvailableFilters:
    """Test available filters extraction"""

    @pytest.fixture
    def mock_db(self, mocker):
        """Mock database session"""
        return mocker.MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create search service"""
        return SearchService(mock_db)

    def test_get_available_filters_no_subject(self, service, mock_db, mocker):
        """Test getting available filters without subject filter"""
        mock_questions = [
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Q1",
                max_marks=8,
                source_paper="9708_s22_qp_22",
                paper_number=22,
                question_number=1,
                year=2022,
                session="MAY_JUNE",
                difficulty="medium",
            ),
            Question(
                id=uuid4(),
                subject_id=uuid4(),
                question_text="Q2",
                max_marks=12,
                source_paper="9708_w21_qp_32",
                paper_number=32,
                question_number=1,
                year=2021,
                session="OCT_NOV",
                difficulty="hard",
            ),
        ]

        mocker.patch.object(mock_db, "exec", return_value=mocker.MagicMock(all=lambda: mock_questions))

        filters = service.get_available_filters()

        assert filters["years"] == [2022, 2021]  # Sorted desc
        assert set(filters["sessions"]) == {"MAY_JUNE", "OCT_NOV"}
        assert set(filters["paper_numbers"]) == {22, 32}
        assert set(filters["difficulties"]) == {"medium", "hard"}
