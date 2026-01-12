"""
Integration tests for daily Cambridge sync workflow.

Feature: 007-resource-bank-files (User Story 2)
Created: 2025-12-27

Tests end-to-end sync flow:
1. Trigger Celery sync task
2. Download past papers from mocked Cambridge website
3. Create database records
4. Link mark schemes to question papers
5. Queue S3 uploads
6. Verify statistics and status
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.models.student import Student
from src.services.sync_service import sync_cambridge_resources


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def admin_student(db_session: Session):
    """Create admin student for API testing."""
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
    """Create regular student for authorization testing."""
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


class TestDailySyncWorkflow:
    """Test end-to-end daily sync workflow."""

    @patch('src.services.sync_service.scrape_cambridge_website')
    @patch('src.services.sync_service.download_past_paper')
    @patch('src.services.sync_service.calculate_signature')
    @patch('src.services.sync_service.save_file_to_local')
    def test_sync_downloads_new_past_papers(
        self,
        mock_save,
        mock_signature,
        mock_download,
        mock_scrape,
        db_session: Session
    ):
        """Should download new past papers and create database records."""
        # Mock Cambridge website scraping
        mock_scrape.return_value = [
            {
                'url': 'https://example.com/9708_m24_qp_12.pdf',
                'filename': '9708_m24_qp_12.pdf',
                'year': '2024',
                'session': 'm',
                'paper': '12',
                'type': 'question_paper',
                'title': 'Economics 9708 May/June 2024 Paper 12'
            },
            {
                'url': 'https://example.com/9708_m24_ms_12.pdf',
                'filename': '9708_m24_ms_12.pdf',
                'year': '2024',
                'session': 'm',
                'paper': '12',
                'type': 'mark_scheme',
                'title': 'Economics 9708 May/June 2024 Paper 12 (Mark Scheme)'
            }
        ]

        # Mock successful downloads
        mock_download.return_value = True
        mock_signature.side_effect = ['sig_qp_12', 'sig_ms_12']  # Unique signatures
        mock_save.side_effect = [
            '/absolute/path/qp_12.pdf',
            '/absolute/path/ms_12.pdf'
        ]

        # Execute sync
        stats = sync_cambridge_resources(subject_code="9708", years_back=10)

        # Verify statistics
        assert stats['total_found'] == 2
        assert stats['new_downloaded'] == 2
        assert stats['skipped_duplicates'] == 0
        assert stats['mark_schemes_linked'] == 1  # MS linked to QP

        # Verify database records created
        qp_query = select(Resource).where(Resource.signature == 'sig_qp_12')
        qp = db_session.exec(qp_query).first()

        assert qp is not None
        assert qp.resource_type == ResourceType.PAST_PAPER
        assert qp.title == 'Economics 9708 May/June 2024 Paper 12'
        assert qp.visibility == Visibility.PUBLIC
        assert qp.admin_approved is True

        # Verify mark scheme linked
        assert qp.metadata is not None
        assert 'mark_scheme_id' in qp.metadata

        ms_query = select(Resource).where(Resource.signature == 'sig_ms_12')
        ms = db_session.exec(ms_query).first()

        assert ms is not None
        assert str(ms.id) == qp.metadata['mark_scheme_id']

    @patch('src.services.sync_service.scrape_cambridge_website')
    @patch('src.services.sync_service.download_past_paper')
    @patch('src.services.sync_service.calculate_signature')
    @patch('src.services.sync_service.save_file_to_local')
    def test_sync_skips_duplicates_via_signature(
        self,
        mock_save,
        mock_signature,
        mock_download,
        mock_scrape,
        db_session: Session
    ):
        """Should skip download if signature matches existing resource."""
        existing_signature = 'existing_sig_123'

        # Create existing resource
        existing = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title='Economics 9708 May/June 2024 Paper 12',
            file_path='/fake/path.pdf',
            signature=existing_signature,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            s3_sync_status=S3SyncStatus.SUCCESS
        )
        db_session.add(existing)
        db_session.commit()

        # Mock scraping returns same file
        mock_scrape.return_value = [
            {
                'url': 'https://example.com/9708_m24_qp_12.pdf',
                'filename': '9708_m24_qp_12.pdf',
                'year': '2024',
                'session': 'm',
                'paper': '12',
                'type': 'question_paper',
                'title': 'Economics 9708 May/June 2024 Paper 12'
            }
        ]

        mock_download.return_value = True
        mock_signature.return_value = existing_signature  # Same signature

        # Execute sync
        stats = sync_cambridge_resources(subject_code="9708", years_back=10)

        # Verify duplicate was skipped
        assert stats['total_found'] == 1
        assert stats['new_downloaded'] == 0
        assert stats['skipped_duplicates'] == 1

        # Verify existing resource updated_at was updated
        db_session.refresh(existing)
        assert existing.updated_at is not None

    @patch('src.services.sync_service.scrape_cambridge_website')
    @patch('src.services.sync_service.download_past_paper')
    def test_sync_handles_download_failures(
        self,
        mock_download,
        mock_scrape,
        db_session: Session
    ):
        """Should track failed downloads and continue with others."""
        mock_scrape.return_value = [
            {
                'url': 'https://example.com/9708_m24_qp_12.pdf',
                'year': '2024',
                'session': 'm',
                'paper': '12',
                'type': 'question_paper',
                'title': 'Economics 9708 May/June 2024 Paper 12'
            }
        ]

        # Mock download failure
        mock_download.return_value = False

        # Execute sync
        stats = sync_cambridge_resources(subject_code="9708", years_back=10)

        # Verify failure was tracked
        assert stats['total_found'] == 1
        assert stats['new_downloaded'] == 0
        assert stats['skipped_duplicates'] == 1  # Failed download counts as skipped

    @patch('src.services.sync_service.scrape_cambridge_website')
    @patch('src.services.sync_service.download_past_paper')
    @patch('src.services.sync_service.calculate_signature')
    @patch('src.services.sync_service.save_file_to_local')
    def test_sync_filters_by_year(
        self,
        mock_save,
        mock_signature,
        mock_download,
        mock_scrape,
        db_session: Session
    ):
        """Should only download past papers from specified years."""
        current_year = datetime.now().year

        # Mock papers from different years
        mock_scrape.return_value = [
            {
                'url': 'https://example.com/old_paper.pdf',
                'year': str(current_year - 15),  # Too old (beyond 10 years)
                'session': 'm',
                'paper': '12',
                'type': 'question_paper',
                'title': 'Old Paper'
            },
            {
                'url': 'https://example.com/recent_paper.pdf',
                'year': str(current_year - 2),  # Recent (within 10 years)
                'session': 'm',
                'paper': '12',
                'type': 'question_paper',
                'title': 'Recent Paper'
            }
        ]

        mock_download.return_value = True
        mock_signature.return_value = 'recent_sig'
        mock_save.return_value = '/absolute/path/recent.pdf'

        # Execute sync with 10 years back
        stats = sync_cambridge_resources(subject_code="9708", years_back=10)

        # Verify only recent paper was processed
        assert stats['total_found'] == 1  # Old paper filtered out
        assert stats['new_downloaded'] == 1


class TestSyncAPIEndpoints:
    """Test sync API endpoints."""

    @patch('src.routes.resource_sync.manual_sync_trigger.delay')
    def test_trigger_manual_sync_admin_only(self, mock_task, client, admin_student, regular_student):
        """Admin should be able to trigger manual sync, students should not."""
        # Admin can trigger
        response = client.post(
            "/api/sync/trigger?subject_code=9708&years_back=5",
            headers={"Authorization": f"Bearer {admin_student.id}"}
        )

        assert response.status_code == 202
        data = response.json()
        assert data['status'] == 'queued'
        assert 'task_id' in data
        mock_task.assert_called_once()

        # Student cannot trigger
        response = client.post(
            "/api/sync/trigger",
            headers={"Authorization": f"Bearer {regular_student.id}"}
        )

        assert response.status_code == 403
        assert "Only admins" in response.json()['detail']

    def test_get_sync_status(self, client, admin_student, db_session: Session):
        """Should return sync status and statistics."""
        # Create some test resources
        for i in range(5):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER,
                title=f"Test Paper {i}",
                file_path=f"/fake/path{i}.pdf",
                signature=f"sig_{i}",
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                s3_sync_status=S3SyncStatus.SUCCESS
            )
            db_session.add(resource)
        db_session.commit()

        response = client.get(
            "/api/sync/status",
            headers={"Authorization": f"Bearer {admin_student.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert 'total_resources' in data
        assert data['total_resources'] >= 5
        assert 'by_type' in data
        assert 's3_sync_health' in data
        assert 'sync_status' in data

    def test_get_s3_status(self, client, admin_student, db_session: Session):
        """Should return S3 upload statistics."""
        # Create resources with different S3 statuses
        statuses = [S3SyncStatus.PENDING, S3SyncStatus.SUCCESS, S3SyncStatus.FAILED]

        for i, status in enumerate(statuses):
            resource = Resource(
                id=uuid4(),
                resource_type=ResourceType.PAST_PAPER,
                title=f"Test Paper {i}",
                file_path=f"/fake/path{i}.pdf",
                signature=f"sig_s3_{i}",
                visibility=Visibility.PUBLIC,
                admin_approved=True,
                s3_sync_status=status
            )
            db_session.add(resource)
        db_session.commit()

        response = client.get(
            "/api/sync/s3-status",
            headers={"Authorization": f"Bearer {admin_student.id}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert 'pending_uploads' in data
        assert 'failed_uploads' in data
        assert 'synced_uploads' in data
        assert 's3_online' in data
        assert data['pending_uploads'] >= 1
        assert data['failed_uploads'] >= 1
        assert data['synced_uploads'] >= 1

    @patch('src.routes.resource_sync.retry_failed_syncs.delay')
    def test_retry_s3_admin_only(self, mock_task, client, admin_student, regular_student):
        """Admin should be able to retry failed S3 uploads, students should not."""
        # Admin can retry
        response = client.post(
            "/api/sync/retry-s3",
            headers={"Authorization": f"Bearer {admin_student.id}"}
        )

        assert response.status_code == 202
        data = response.json()
        assert data['status'] == 'queued'
        mock_task.assert_called_once()

        # Student cannot retry
        response = client.post(
            "/api/sync/retry-s3",
            headers={"Authorization": f"Bearer {regular_student.id}"}
        )

        assert response.status_code == 403
        assert "Only admins" in response.json()['detail']
