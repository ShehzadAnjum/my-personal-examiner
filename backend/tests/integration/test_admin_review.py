"""
Integration tests for admin resource review workflow.

Feature: 007-resource-bank-files (User Story 4)
Created: 2025-12-27

Tests end-to-end approval workflow:
1. List pending resources
2. Preview PDF (first 3 pages)
3. Edit metadata
4. Approve (visibility→public)
5. Reject (delete file+record)

Constitutional Compliance:
- FR-028: Approve with one-way transition
- FR-029: Reject with deletion
- FR-030: Edit metadata before approval
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
def admin(db_session: Session):
    admin = Student(
        id=uuid4(), email="admin@test.com", full_name="Admin User",
        is_admin=True, hashed_password="hash"
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def student(db_session: Session):
    student = Student(
        id=uuid4(), email="student@test.com", full_name="Student User",
        is_admin=False, hashed_password="hash"
    )
    db_session.add(student)
    db_session.commit()
    return student


class TestAdminReviewWorkflow:
    """Test end-to-end admin review workflow."""

    def test_list_pending_resources(self, client, admin, student, db_session):
        """Admin should see pending resources with student info."""
        # Create pending resource
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Student's Notes", file_path="/fake/notes.pdf",
            uploaded_by_student_id=student.id,
            visibility=Visibility.PENDING_REVIEW, admin_approved=False,
            signature="sig_pending"
        )
        db_session.add(resource)
        db_session.commit()

        # Admin lists pending
        response = client.get(
            "/api/admin/resources/pending",
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1
        pending = next((r for r in data if r['id'] == str(resource.id)), None)
        assert pending is not None
        assert pending['title'] == "Student's Notes"
        assert pending['student_name'] == "Student User"
        assert pending['student_email'] == "student@test.com"

    def test_student_cannot_access_pending_list(self, client, student):
        """Non-admin should not access pending resources list."""
        response = client.get(
            "/api/admin/resources/pending",
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 403

    @patch('src.routes.admin_resources.convert_from_path')
    @patch('src.routes.admin_resources.PyPDF2.PdfReader')
    def test_preview_resource_first_3_pages(self, mock_reader, mock_convert, client, admin, db_session):
        """Admin should preview first 3 pages as base64 images."""
        # Create test resource
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Test PDF", file_path=temp_path,
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, signature="sig_preview"
        )
        db_session.add(resource)
        db_session.commit()

        # Mock PDF reader
        mock_pdf = type('MockPDF', (), {'pages': [None, None, None, None, None]})()
        mock_reader.return_value = mock_pdf

        # Mock image conversion
        from PIL import Image
        mock_img = Image.new('RGB', (100, 100), color='white')
        mock_convert.return_value = [mock_img, mock_img, mock_img]

        try:
            response = client.get(
                f"/api/admin/resources/{resource.id}/preview",
                headers={"Authorization": f"Bearer {admin.id}"}
            )

            assert response.status_code == 200
            data = response.json()

            assert 'pages' in data
            assert len(data['pages']) == 3
            assert data['pages'][0].startswith('data:image/png;base64,')
            assert data['page_count'] == 5
            assert data['title'] == "Test PDF"

        finally:
            os.remove(temp_path)

    def test_approve_resource_changes_visibility(self, client, admin, db_session):
        """Approving should change visibility to PUBLIC."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="To Approve", file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, admin_approved=False,
            signature="sig_approve"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/approve",
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['visibility'] == Visibility.PUBLIC.value
        assert data['admin_approved'] is True
        assert 'approval_date' in data

        # Verify in database
        db_session.refresh(resource)
        assert resource.visibility == Visibility.PUBLIC
        assert resource.admin_approved is True

    def test_cannot_approve_already_approved(self, client, admin, db_session):
        """Should reject re-approval (state machine violation)."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Already Approved", file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC, admin_approved=True,
            signature="sig_approved"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/approve",
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 400
        assert "already approved" in response.json()['detail'].lower()

    def test_reject_resource_deletes_file_and_record(self, client, admin, db_session):
        """Rejecting should delete file and database record."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
            temp.write("Test content")
            temp_path = temp.name

        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="To Reject", file_path=temp_path,
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, admin_approved=False,
            signature="sig_reject"
        )
        db_session.add(resource)
        db_session.commit()

        resource_id = resource.id

        # Verify file exists
        assert os.path.exists(temp_path)

        # Reject
        response = client.put(
            f"/api/admin/resources/{resource_id}/reject",
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 204

        # Verify file deleted
        assert not os.path.exists(temp_path)

        # Verify DB record deleted
        assert db_session.get(Resource, resource_id) is None

    def test_cannot_reject_approved_resource(self, client, admin, db_session):
        """Should reject deletion of approved resource (state violation)."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Approved", file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PUBLIC, admin_approved=True,
            signature="sig_approved2"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/reject",
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 400
        assert "state transition" in response.json()['detail'].lower()

    def test_update_metadata_before_approval(self, client, admin, db_session):
        """Admin can edit metadata before approval."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Original Title", file_path="/fake/path.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, admin_approved=False,
            signature="sig_meta"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/metadata",
            json={
                "title": "Edited Title",
                "description": "Admin-added description",
                "metadata": {"tags": ["economics", "fiscal-policy"]}
            },
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['title'] == "Edited Title"
        assert data['metadata']['description'] == "Admin-added description"
        assert 'tags' in data['metadata']

        # Verify in database
        db_session.refresh(resource)
        assert resource.title == "Edited Title"
        assert resource.resource_metadata['description'] == "Admin-added description"

    @patch('src.routes.admin_resources.extract_text_from_page_range')
    def test_extract_textbook_excerpt(self, mock_extract, client, admin, db_session):
        """Admin can extract textbook excerpt by page range."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.TEXTBOOK,
            title="Economics Textbook", file_path="/fake/textbook.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, signature="sig_excerpt"
        )
        db_session.add(resource)
        db_session.commit()

        # Mock excerpt extraction
        mock_extract.return_value = "Fiscal policy involves government spending and taxation..." * 20

        response = client.post(
            f"/api/admin/resources/{resource.id}/extract-excerpt",
            json={"start_page": 245, "end_page": 267},
            headers={"Authorization": f"Bearer {admin.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['page_range'] == "245-267"
        assert data['char_count'] > 0

        # Verify stored in metadata
        db_session.refresh(resource)
        assert 'excerpt_text' in resource.resource_metadata
        assert resource.resource_metadata['excerpt_pages'] == "245-267"


class TestAdminOnlyAccess:
    """Test that admin endpoints require admin privileges."""

    def test_approve_requires_admin(self, client, student, db_session):
        """Non-admin cannot approve resources."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Test", file_path="/fake.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, signature="sig"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/approve",
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 403

    def test_reject_requires_admin(self, client, student, db_session):
        """Non-admin cannot reject resources."""
        resource = Resource(
            id=uuid4(), resource_type=ResourceType.USER_UPLOAD,
            title="Test", file_path="/fake.pdf",
            uploaded_by_student_id=uuid4(),
            visibility=Visibility.PENDING_REVIEW, signature="sig2"
        )
        db_session.add(resource)
        db_session.commit()

        response = client.put(
            f"/api/admin/resources/{resource.id}/reject",
            headers={"Authorization": f"Bearer {student.id}"}
        )

        assert response.status_code == 403
