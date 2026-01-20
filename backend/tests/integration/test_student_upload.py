"""
Integration tests for student resource uploads.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Tests student upload workflow with quota enforcement and delete functionality.
"""

import os
import tempfile
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app
from src.models.enums import ResourceType, Visibility
from src.models.resource import Resource
from src.models.student import Student


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def student(db_session: Session):
    student = Student(
        id=uuid4(),
        email="student@test.com",
        full_name="Test Student",
        is_admin=False,
        hashed_password="hash",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestStudentUploadWorkflow:
    """Test student upload integration."""

    @patch('src.routes.resources.upload_to_s3_task.delay')
    @patch('src.routes.resources.scan_file_for_virus')
    def test_student_upload_sets_pending_review(self, mock_scan, mock_s3, client, student, db_session):
        """Student uploads should have pending_review visibility."""
        mock_scan.return_value = {"safe": True}

        pdf_content = b"%PDF-1.4 Student notes"
        pdf_file = BytesIO(pdf_content)

        response = client.post(
            "/api/resources/upload",
            data={"resource_type": ResourceType.USER_UPLOAD.value, "title": "My Notes"},
            files={"file": ("notes.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data['visibility'] == Visibility.PENDING_REVIEW.value
        assert data['admin_approved'] is False

    @patch('src.routes.resources.scan_file_for_virus')
    def test_student_quota_enforcement(self, mock_scan, client, student, db_session):
        """Should reject 101st upload."""
        mock_scan.return_value = {"safe": True}

        # Create 100 existing resources
        for i in range(100):
            resource = Resource(
                id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}", file_path=f"/fake{i}.pdf",
                uploaded_by_student_id=student.id, signature=f"sig{i}",
                visibility=Visibility.PRIVATE
            )
            db_session.add(resource)
        db_session.commit()

        pdf_file = BytesIO(b"%PDF-1.4 Test")
        response = client.post(
            "/api/resources/upload",
            data={"resource_type": ResourceType.USER_UPLOAD.value, "title": "101st"},
            files={"file": ("file.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 400
        assert "quota exceeded" in response.json()['detail'].lower()

    def test_student_can_delete_own_unapproved(self, client, student, db_session):
        """Student can delete own unapproved resource."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Test")
            temp_path = f.name

        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="My Notes", file_path=temp_path,
            uploaded_by_student_id=student.id, admin_approved=False,
            visibility=Visibility.PENDING_REVIEW, signature="sig"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.delete(
            f"/api/resources/{resource.id}",
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 204
        assert not os.path.exists(temp_path)
        assert db_session.get(Resource, resource.id) is None

    def test_student_cannot_delete_approved(self, client, student, db_session):
        """Student cannot delete approved resource."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Approved", file_path="/fake.pdf",
            uploaded_by_student_id=student.id, admin_approved=True,
            visibility=Visibility.PUBLIC, signature="sig"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.delete(
            f"/api/resources/{resource.id}",
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 403
