"""
Integration tests for resource upload workflow.

Feature: 007-resource-bank-files
Created: 2025-12-27

Tests end-to-end flow:
1. POST multipart file upload
2. File stored locally
3. DB record created
4. S3 queued
5. Duplicate detection
"""

import os
import tempfile
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.models.student import Student


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def admin_student(db_session: Session):
    """Create admin student for testing."""
    student = Student(
        id=uuid4(),
        email="admin@test.com",
        full_name="Admin User",
        is_admin=True,
        hashed_password="fake_hash",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def regular_student(db_session: Session):
    """Create regular student for testing."""
    student = Student(
        id=uuid4(),
        email="student@test.com",
        full_name="Test Student",
        is_admin=False,
        hashed_password="fake_hash",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestResourceUploadWorkflow:
    """Test end-to-end resource upload workflow."""

    @patch('src.routes.resources.upload_to_s3_task.delay')
    @patch('src.routes.resources.scan_file_for_virus')
    def test_admin_upload_syllabus_success(
        self,
        mock_scan,
        mock_s3_upload,
        client,
        admin_student,
        db_session,
    ):
        """Admin should successfully upload syllabus with public visibility."""
        mock_scan.return_value = {"safe": True}
        
        # Create test PDF file
        pdf_content = b"%PDF-1.4 Test syllabus content"
        pdf_file = BytesIO(pdf_content)
        
        # Upload resource
        response = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.SYLLABUS.value,
                "title": "Economics 9708 Syllabus 2025",
                "source_url": "https://cambridge.org/syllabus",
            },
            files={"file": ("syllabus_9708.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {admin_student.id}"},  # Mock auth
        )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Economics 9708 Syllabus 2025"
        assert data["resource_type"] == ResourceType.SYLLABUS.value
        assert data["visibility"] == Visibility.PUBLIC.value  # Admin uploads are public
        assert data["admin_approved"] is True
        assert data["s3_sync_status"] == S3SyncStatus.PENDING.value
        
        # Verify file stored locally
        resource_id = data["id"]
        resource = db_session.get(Resource, resource_id)
        assert resource is not None
        assert os.path.exists(resource.file_path)
        
        # Verify S3 upload was queued
        mock_s3_upload.assert_called_once()
        
        # Cleanup
        if os.path.exists(resource.file_path):
            os.remove(resource.file_path)

    @patch('src.routes.resources.upload_to_s3_task.delay')
    @patch('src.routes.resources.scan_file_for_virus')
    def test_student_upload_requires_review(
        self,
        mock_scan,
        mock_s3_upload,
        client,
        regular_student,
        db_session,
    ):
        """Student uploads should have pending_review visibility."""
        mock_scan.return_value = {"safe": True}
        
        pdf_content = b"%PDF-1.4 Student notes"
        pdf_file = BytesIO(pdf_content)
        
        response = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.USER_UPLOAD.value,
                "title": "My Economics Notes",
            },
            files={"file": ("notes.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {regular_student.id}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["visibility"] == Visibility.PENDING_REVIEW.value
        assert data["admin_approved"] is False
        assert data["uploaded_by_student_id"] == str(regular_student.id)
        
        # Cleanup
        resource = db_session.get(Resource, data["id"])
        if resource and os.path.exists(resource.file_path):
            os.remove(resource.file_path)

    @patch('src.routes.resources.scan_file_for_virus')
    def test_duplicate_detection_rejects_upload(
        self,
        mock_scan,
        client,
        admin_student,
        db_session,
    ):
        """Should reject duplicate uploads with same signature."""
        mock_scan.return_value = {"safe": True}
        
        pdf_content = b"%PDF-1.4 Duplicate test"
        
        # First upload
        pdf_file1 = BytesIO(pdf_content)
        response1 = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.SYLLABUS.value,
                "title": "Original Syllabus",
            },
            files={"file": ("syllabus.pdf", pdf_file1, "application/pdf")},
            headers={"Authorization": f"Bearer {admin_student.id}"},
        )
        assert response1.status_code == 201
        
        # Second upload (duplicate)
        pdf_file2 = BytesIO(pdf_content)
        response2 = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.SYLLABUS.value,
                "title": "Duplicate Syllabus",
            },
            files={"file": ("syllabus_copy.pdf", pdf_file2, "application/pdf")},
            headers={"Authorization": f"Bearer {admin_student.id}"},
        )
        
        # Should reject duplicate
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]
        
        # Cleanup
        resource = db_session.get(Resource, response1.json()["id"])
        if resource and os.path.exists(resource.file_path):
            os.remove(resource.file_path)

    @patch('src.routes.resources.scan_file_for_virus')
    def test_file_size_limit_enforced(
        self,
        mock_scan,
        client,
        admin_student,
    ):
        """Should reject files exceeding 50MB limit."""
        # Create 51MB file (exceeds limit)
        large_content = b"x" * (51 * 1024 * 1024)
        large_file = BytesIO(large_content)
        
        response = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.SYLLABUS.value,
                "title": "Large Syllabus",
            },
            files={"file": ("large.pdf", large_file, "application/pdf")},
            headers={"Authorization": f"Bearer {admin_student.id}"},
        )
        
        assert response.status_code == 400
        assert "50MB" in response.json()["detail"]

    @patch('src.routes.resources.scan_file_for_virus')
    def test_virus_detected_rejects_upload(
        self,
        mock_scan,
        client,
        admin_student,
    ):
        """Should reject upload if virus detected."""
        mock_scan.return_value = {"safe": False, "virus": "Eicar-Test-Signature"}
        
        pdf_content = b"%PDF-1.4 Infected file"
        pdf_file = BytesIO(pdf_content)
        
        response = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.SYLLABUS.value,
                "title": "Infected Syllabus",
            },
            files={"file": ("infected.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {admin_student.id}"},
        )
        
        assert response.status_code == 400
        assert "Virus detected" in response.json()["detail"]

    @patch('src.routes.resources.upload_to_s3_task.delay')
    @patch('src.routes.resources.scan_file_for_virus')
    def test_student_quota_enforcement(
        self,
        mock_scan,
        mock_s3_upload,
        client,
        regular_student,
        db_session,
    ):
        """Should reject upload when student exceeds 100 resource quota."""
        mock_scan.return_value = {"safe": True}
        
        # Create 100 existing resources for student
        for i in range(100):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.USER_UPLOAD,
                title=f"Resource {i}",
                file_path=f"/fake/path{i}.pdf",
                uploaded_by_student_id=regular_student.id,
                signature=f"signature{i}",
                visibility=Visibility.PENDING_REVIEW,
            )
            db_session.add(resource)
        db_session.commit()
        
        # Attempt 101st upload
        pdf_content = b"%PDF-1.4 Quota test"
        pdf_file = BytesIO(pdf_content)
        
        response = client.post(
            "/api/resources/upload",
            data={
                "resource_type": ResourceType.USER_UPLOAD.value,
                "title": "101st Resource",
            },
            files={"file": ("notes.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": f"Bearer {regular_student.id}"},
        )
        
        assert response.status_code == 400
        assert "quota exceeded" in response.json()["detail"].lower()
        assert "100" in response.json()["detail"]


class TestResourceDeletionWorkflow:
    """Test resource deletion workflow."""

    def test_student_can_delete_own_unapproved_resource(
        self,
        client,
        regular_student,
        db_session,
    ):
        """Student should be able to delete own unapproved resource."""
        # Create test resource
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Test content")
            temp_path = f.name
        
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="My Notes",
            file_path=temp_path,
            uploaded_by_student_id=regular_student.id,
            admin_approved=False,
            visibility=Visibility.PENDING_REVIEW,
            signature="test_signature",
        )
        db_session.add(resource)
        db_session.commit()
        
        # Delete resource
        response = client.delete(
            f"/api/resources/{resource.id}",
            headers={"Authorization": f"Bearer {regular_student.id}"},
        )
        
        assert response.status_code == 204
        assert not os.path.exists(temp_path)
        assert db_session.get(Resource, resource.id) is None

    def test_student_cannot_delete_approved_resource(
        self,
        client,
        regular_student,
        db_session,
    ):
        """Student should not be able to delete approved resource."""
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.USER_UPLOAD,
            title="Approved Notes",
            file_path="/fake/path.pdf",
            uploaded_by_student_id=regular_student.id,
            admin_approved=True,
            visibility=Visibility.PUBLIC,
            signature="approved_signature",
        )
        db_session.add(resource)
        db_session.commit()
        
        response = client.delete(
            f"/api/resources/{resource.id}",
            headers={"Authorization": f"Bearer {regular_student.id}"},
        )
        
        assert response.status_code == 403
        assert "approved" in response.json()["detail"].lower()
