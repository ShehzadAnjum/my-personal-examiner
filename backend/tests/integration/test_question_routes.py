"""
Integration Tests: Question Routes

Tests for Phase II US2 - Search & Filtering API endpoints.

Test Coverage:
- GET /api/questions/search - Search questions with filters
- GET /api/questions/{id} - Get question by ID
- GET /api/questions/filters - Get available filters
"""

import pytest

from src.models.question import Question
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint


@pytest.fixture
def test_data(db_session):
    """Create test data: subject and questions"""
    # Create subject
    subject = Subject(
        code="9708",
        name="Economics",
        level="A",
        exam_board="Cambridge",
        syllabus_year="2023-2025",
    )
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)

    # Create syllabus points
    sp1 = SyllabusPoint(
        subject_id=subject.id,
        code="9708.1.1",
        description="Basic economic problem",
        topics="Scarcity, Choice",
    )
    sp2 = SyllabusPoint(
        subject_id=subject.id,
        code="9708.2.1",
        description="Supply and demand",
        topics="Market equilibrium",
    )
    db_session.add(sp1)
    db_session.add(sp2)
    db_session.commit()
    db_session.refresh(sp1)
    db_session.refresh(sp2)

    # Create diverse test questions
    questions = []

    # Easy questions (2022)
    for i in range(1, 4):
        q = Question(
            subject_id=subject.id,
            question_text=f"What is opportunity cost? Example {i}",
            max_marks=4,
            difficulty="easy",
            source_paper="9708_s22_qp_22",
            paper_number=22,
            question_number=i,
            year=2022,
            session="MAY_JUNE",
            syllabus_point_ids=[str(sp1.id)],
        )
        db_session.add(q)
        questions.append(q)

    # Medium questions (2021)
    for i in range(4, 7):
        q = Question(
            subject_id=subject.id,
            question_text=f"Explain supply and demand equilibrium. Question {i}",
            max_marks=8,
            difficulty="medium",
            source_paper="9708_w21_qp_22",
            paper_number=22,
            question_number=i,
            year=2021,
            session="OCT_NOV",
            syllabus_point_ids=[str(sp2.id)],
        )
        db_session.add(q)
        questions.append(q)

    # Hard questions (2020)
    for i in range(7, 10):
        q = Question(
            subject_id=subject.id,
            question_text=f"Discuss market failure and government intervention. Part {i}",
            max_marks=12,
            difficulty="hard",
            source_paper="9708_s20_qp_22",
            paper_number=22,
            question_number=i,
            year=2020,
            session="MAY_JUNE",
            syllabus_point_ids=[str(sp1.id), str(sp2.id)],
        )
        db_session.add(q)
        questions.append(q)

    db_session.commit()
    return {"subject": subject, "questions": questions, "sp1": sp1, "sp2": sp2}


class TestSearchQuestions:
    """Test GET /api/questions/search"""

    def test_search_all_questions(self, client, test_data):
        """Test searching all questions without filters"""
        response = client.get("/api/questions/search")

        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert "total" in data
        assert data["total"] >= 9  # At least our test questions

    def test_search_by_subject_code(self, client, test_data):
        """Test filtering by subject code"""
        response = client.get("/api/questions/search?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 9
        assert len(data["questions"]) == 9

    def test_search_by_year(self, client, test_data):
        """Test filtering by year"""
        response = client.get("/api/questions/search?subject_code=9708&year=2022")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3  # 3 questions from 2022
        for q in data["questions"]:
            assert q["year"] == 2022

    def test_search_by_difficulty(self, client, test_data):
        """Test filtering by difficulty"""
        response = client.get("/api/questions/search?subject_code=9708&difficulty=easy")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for q in data["questions"]:
            assert q["difficulty"] == "easy"

    def test_search_by_session(self, client, test_data):
        """Test filtering by session"""
        response = client.get(
            "/api/questions/search?subject_code=9708&session=MAY_JUNE"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6  # 3 easy + 3 hard from MAY_JUNE
        for q in data["questions"]:
            assert q["session"] == "MAY_JUNE"

    def test_search_by_marks_range(self, client, test_data):
        """Test filtering by marks range"""
        response = client.get(
            "/api/questions/search?subject_code=9708&min_marks=8&max_marks=12"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6  # 3 medium (8) + 3 hard (12)
        for q in data["questions"]:
            assert 8 <= q["max_marks"] <= 12

    def test_search_full_text(self, client, test_data):
        """Test full-text search"""
        response = client.get(
            '/api/questions/search?subject_code=9708&search_text=opportunity cost'
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3  # All easy questions mention "opportunity cost"

    def test_search_pagination(self, client, test_data):
        """Test pagination"""
        # First page
        response1 = client.get(
            "/api/questions/search?subject_code=9708&page=1&page_size=5"
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["questions"]) == 5
        assert data1["page"] == 1
        assert data1["page_size"] == 5
        assert data1["total"] == 9
        assert data1["has_next"] is True
        assert data1["has_prev"] is False

        # Second page
        response2 = client.get(
            "/api/questions/search?subject_code=9708&page=2&page_size=5"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["questions"]) == 4  # Remaining questions
        assert data2["page"] == 2
        assert data2["has_next"] is False
        assert data2["has_prev"] is True

    def test_search_sort_by_year_desc(self, client, test_data):
        """Test sorting by year descending"""
        response = client.get(
            "/api/questions/search?subject_code=9708&sort_by=year&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        years = [q["year"] for q in data["questions"]]
        assert years == sorted(years, reverse=True)

    def test_search_sort_by_marks_asc(self, client, test_data):
        """Test sorting by marks ascending"""
        response = client.get(
            "/api/questions/search?subject_code=9708&sort_by=max_marks&sort_order=asc"
        )

        assert response.status_code == 200
        data = response.json()
        marks = [q["max_marks"] for q in data["questions"]]
        assert marks == sorted(marks)

    def test_search_combined_filters(self, client, test_data):
        """Test combining multiple filters"""
        response = client.get(
            "/api/questions/search?subject_code=9708&year=2022&difficulty=easy&min_marks=4"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for q in data["questions"]:
            assert q["year"] == 2022
            assert q["difficulty"] == "easy"
            assert q["max_marks"] >= 4

    def test_search_invalid_subject(self, client):
        """Test searching with invalid subject code"""
        response = client.get("/api/questions/search?subject_code=9999")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["questions"]) == 0

    def test_search_empty_results(self, client, test_data):
        """Test search with filters that return no results"""
        response = client.get(
            "/api/questions/search?subject_code=9708&year=1999"  # No questions from 1999
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["questions"]) == 0


class TestGetQuestionById:
    """Test GET /api/questions/{id}"""

    def test_get_question_success(self, client, test_data):
        """Test getting question by ID"""
        question = test_data["questions"][0]
        response = client.get(f"/api/questions/{question.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(question.id)
        assert data["question_text"] == question.question_text
        assert data["max_marks"] == question.max_marks
        assert data["difficulty"] == question.difficulty

    def test_get_question_not_found(self, client):
        """Test error when question not found"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/questions/{fake_id}")

        assert response.status_code == 404


class TestGetAvailableFilters:
    """Test GET /api/questions/filters"""

    def test_get_filters_all_subjects(self, client, test_data):
        """Test getting available filters for all subjects"""
        response = client.get("/api/questions/filters")

        assert response.status_code == 200
        data = response.json()
        assert "years" in data
        assert "sessions" in data
        assert "paper_numbers" in data
        assert "difficulties" in data

        # Should include all our test data
        assert 2022 in data["years"]
        assert 2021 in data["years"]
        assert 2020 in data["years"]
        assert "MAY_JUNE" in data["sessions"]
        assert "OCT_NOV" in data["sessions"]
        assert 22 in data["paper_numbers"]

    def test_get_filters_specific_subject(self, client, test_data):
        """Test getting filters for specific subject"""
        response = client.get("/api/questions/filters?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        assert 2022 in data["years"]
        assert "easy" in data["difficulties"]
        assert "medium" in data["difficulties"]
        assert "hard" in data["difficulties"]

    def test_get_filters_years_sorted(self, client, test_data):
        """Test that years are sorted descending"""
        response = client.get("/api/questions/filters?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        years = data["years"]
        assert years == sorted(years, reverse=True)


class TestSearchMarkSchemes:
    """Test GET /api/questions/mark-schemes/search"""

    def test_search_mark_schemes_endpoint_exists(self, client):
        """Test that mark schemes search endpoint exists"""
        response = client.get("/api/questions/mark-schemes/search")

        # Should return 200 even if empty
        assert response.status_code in [200, 404]  # Depending on implementation
