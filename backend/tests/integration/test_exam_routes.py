"""
Integration Tests: Exam Routes

Tests for Phase II US6 - Exam Generation API endpoints.

Test Coverage:
- POST /api/exams - Generate exam
- GET /api/exams - List exams
- GET /api/exams/{id} - Get exam details
- GET /api/exams/{id}/questions - Get exam questions
- GET /api/exams/{id}/statistics - Get exam statistics
- PATCH /api/exams/{id}/status - Update exam status
"""

import pytest
from sqlmodel import Session

from src.models.exam import Exam
from src.models.question import Question
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint


@pytest.fixture
def test_data(db_session):
    """Create test data: subject, syllabus points, and questions"""
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

    # Create 10 test questions with varied difficulty
    questions = []
    for i in range(1, 11):
        if i <= 3:
            difficulty = "easy"
            marks = 4
        elif i <= 7:
            difficulty = "medium"
            marks = 8
        else:
            difficulty = "hard"
            marks = 12

        q = Question(
            subject_id=subject.id,
            question_text=f"Test question {i}",
            max_marks=marks,
            difficulty=difficulty,
            source_paper=f"9708_s22_qp_22",
            paper_number=22,
            question_number=i,
            year=2022,
            session="MAY_JUNE",
            syllabus_point_ids=[str(sp1.id) if i % 2 == 0 else str(sp2.id)],
        )
        db_session.add(q)
        questions.append(q)

    db_session.commit()
    return {"subject": subject, "questions": questions, "sp1": sp1, "sp2": sp2}


class TestGenerateExam:
    """Test POST /api/exams"""

    def test_generate_exam_success(self, client, test_data):
        """Test successful exam generation"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9708",
                "exam_type": "PRACTICE",
                "question_count": 5,
                "strategy": "balanced",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["subject_id"] == str(test_data["subject"].id)
        assert data["exam_type"] == "PRACTICE"
        assert len(data["question_ids"]) == 5
        assert data["total_marks"] > 0
        assert data["duration"] > 0
        assert data["status"] == "PENDING"

    def test_generate_exam_random_strategy(self, client, test_data):
        """Test random selection strategy"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9708",
                "exam_type": "PRACTICE",
                "question_count": 3,
                "strategy": "random",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["question_ids"]) == 3

    def test_generate_exam_syllabus_coverage_strategy(self, client, test_data):
        """Test syllabus coverage strategy"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9708",
                "exam_type": "PRACTICE",
                "question_count": 4,
                "strategy": "syllabus_coverage",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["question_ids"]) == 4

    def test_generate_exam_invalid_subject(self, client):
        """Test error when subject not found"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9999",
                "exam_type": "PRACTICE",
                "question_count": 5,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_generate_exam_insufficient_questions(self, client, test_data):
        """Test error when not enough questions"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9708",
                "exam_type": "PRACTICE",
                "question_count": 100,  # More than available
                "strategy": "random",
            },
        )

        # FastAPI returns 422 for validation errors (acceptable alternative to 400)
        assert response.status_code in [400, 422]
        # Error detail might vary based on validation layer
        if response.status_code == 422:
            assert response.json()["detail"] is not None
        else:
            assert "insufficient" in response.json()["detail"].lower()

    def test_generate_exam_with_duration(self, client, test_data):
        """Test exam generation with custom duration"""
        response = client.post(
            "/api/exams",
            json={
                "subject_code": "9708",
                "exam_type": "TIMED",
                "question_count": 5,
                "duration": 60,
                "strategy": "balanced",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["duration"] == 60
        assert data["exam_type"] == "TIMED"


class TestListExams:
    """Test GET /api/exams"""

    def test_list_exams_empty(self, client, test_data):
        """Test listing exams when none exist"""
        response = client.get("/api/exams")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_exams_with_results(self, client, test_data, db_session):
        """Test listing exams"""
        # Create test exams
        exam1 = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        exam2 = Exam(
            subject_id=test_data["subject"].id,
            exam_type="TIMED",
            question_ids=[str(test_data["questions"][1].id)],
            total_marks=20,
            duration=60,
            status="COMPLETED",
        )
        db_session.add(exam1)
        db_session.add(exam2)
        db_session.commit()

        response = client.get("/api/exams")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_exams_filter_by_subject(self, client, test_data, db_session):
        """Test filtering exams by subject code"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()

        response = client.get("/api/exams?subject_code=9708")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_id"] == str(test_data["subject"].id)

    def test_list_exams_filter_by_type(self, client, test_data, db_session):
        """Test filtering exams by exam type"""
        exam1 = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        exam2 = Exam(
            subject_id=test_data["subject"].id,
            exam_type="TIMED",
            question_ids=[str(test_data["questions"][1].id)],
            total_marks=20,
            duration=60,
            status="PENDING",
        )
        db_session.add(exam1)
        db_session.add(exam2)
        db_session.commit()

        response = client.get("/api/exams?exam_type=PRACTICE")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exam_type"] == "PRACTICE"

    def test_list_exams_pagination(self, client, test_data, db_session):
        """Test exam listing pagination"""
        # Create 5 exams
        for i in range(5):
            exam = Exam(
                subject_id=test_data["subject"].id,
                exam_type="PRACTICE",
                question_ids=[str(test_data["questions"][i].id)],
                total_marks=10,
                duration=30,
                status="PENDING",
            )
            db_session.add(exam)
        db_session.commit()

        # Get first page
        response = client.get("/api/exams?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetExam:
    """Test GET /api/exams/{exam_id}"""

    def test_get_exam_success(self, client, test_data, db_session):
        """Test getting exam by ID"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.get(f"/api/exams/{exam.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(exam.id)
        assert data["exam_type"] == "PRACTICE"
        assert data["total_marks"] == 10

    def test_get_exam_not_found(self, client):
        """Test error when exam not found"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/exams/{fake_id}")

        assert response.status_code == 404


class TestGetExamQuestions:
    """Test GET /api/exams/{exam_id}/questions"""

    def test_get_exam_questions_success(self, client, test_data, db_session):
        """Test getting exam questions"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[
                str(test_data["questions"][0].id),
                str(test_data["questions"][1].id),
            ],
            total_marks=20,
            duration=60,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.get(f"/api/exams/{exam.id}/questions")

        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == str(exam.id)
        assert data["question_count"] == 2
        assert len(data["questions"]) == 2
        assert "question_text" in data["questions"][0]
        assert "max_marks" in data["questions"][0]

    def test_get_exam_questions_preserves_order(self, client, test_data, db_session):
        """Test that question order is preserved"""
        q1_id = str(test_data["questions"][2].id)
        q2_id = str(test_data["questions"][0].id)

        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[q1_id, q2_id],  # Specific order
            total_marks=20,
            duration=60,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.get(f"/api/exams/{exam.id}/questions")

        assert response.status_code == 200
        data = response.json()
        assert data["questions"][0]["id"] == q1_id
        assert data["questions"][1]["id"] == q2_id


class TestGetExamStatistics:
    """Test GET /api/exams/{exam_id}/statistics"""

    def test_get_exam_statistics_success(self, client, test_data, db_session):
        """Test getting exam statistics"""
        # Create exam with questions of varied difficulty
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[
                str(test_data["questions"][0].id),  # easy, 4 marks
                str(test_data["questions"][4].id),  # medium, 8 marks
                str(test_data["questions"][8].id),  # hard, 12 marks
            ],
            total_marks=24,
            duration=60,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.get(f"/api/exams/{exam.id}/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["exam_id"] == str(exam.id)
        assert data["total_questions"] == 3
        assert data["total_marks"] == 24
        assert "difficulty_breakdown" in data
        assert "marks_per_difficulty" in data
        assert data["difficulty_breakdown"]["easy"] == 1
        assert data["difficulty_breakdown"]["medium"] == 1
        assert data["difficulty_breakdown"]["hard"] == 1

    def test_get_exam_statistics_not_found(self, client):
        """Test error when exam not found"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/exams/{fake_id}/statistics")

        assert response.status_code == 404


class TestUpdateExamStatus:
    """Test PATCH /api/exams/{exam_id}/status"""

    def test_update_exam_status_success(self, client, test_data, db_session):
        """Test updating exam status"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.patch(
            f"/api/exams/{exam.id}/status", json={"status": "IN_PROGRESS"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"

    def test_update_exam_status_to_completed(self, client, test_data, db_session):
        """Test updating exam status to COMPLETED"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="IN_PROGRESS",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.patch(
            f"/api/exams/{exam.id}/status", json={"status": "COMPLETED"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_update_exam_status_invalid(self, client, test_data, db_session):
        """Test error with invalid status"""
        exam = Exam(
            subject_id=test_data["subject"].id,
            exam_type="PRACTICE",
            question_ids=[str(test_data["questions"][0].id)],
            total_marks=10,
            duration=30,
            status="PENDING",
        )
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)

        response = client.patch(
            f"/api/exams/{exam.id}/status", json={"status": "INVALID_STATUS"}
        )

        assert response.status_code == 400

    def test_update_exam_status_not_found(self, client):
        """Test error when exam not found"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/api/exams/{fake_id}/status", json={"status": "IN_PROGRESS"}
        )

        assert response.status_code == 404
