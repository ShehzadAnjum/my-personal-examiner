"""
Unit tests for Cambridge sync service.

Feature: 007-resource-bank-files (User Story 2)
Created: 2025-12-27

Tests signature-based change detection, metadata parsing,
mark scheme linking, and download logic.
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlmodel import Session, select

from src.models.enums import ResourceType, S3SyncStatus, Visibility
from src.models.resource import Resource
from src.services.sync_service import (
    check_resource_exists,
    download_past_paper,
    link_mark_scheme,
    parse_cambridge_filename,
    scrape_cambridge_website,
    sync_past_paper_from_url,
)


class TestParseCambridgeFilename:
    """Test Cambridge filename parsing and metadata extraction."""

    def test_parse_question_paper_filename(self):
        """Should parse question paper filename correctly."""
        filename = "9708_m24_qp_12.pdf"
        metadata = parse_cambridge_filename(filename)

        assert metadata is not None
        assert metadata['year'] == "2024"
        assert metadata['session'] == "m"
        assert metadata['paper'] == "12"
        assert metadata['type'] == "question_paper"
        assert "May/June" in metadata['title']
        assert "2024" in metadata['title']
        assert "Paper 12" in metadata['title']

    def test_parse_mark_scheme_filename(self):
        """Should parse mark scheme filename correctly."""
        filename = "9708_s23_ms_22.pdf"
        metadata = parse_cambridge_filename(filename)

        assert metadata is not None
        assert metadata['year'] == "2023"
        assert metadata['session'] == "s"
        assert metadata['paper'] == "22"
        assert metadata['type'] == "mark_scheme"
        assert "Oct/Nov" in metadata['title']
        assert "Mark Scheme" in metadata['title']

    def test_parse_winter_session(self):
        """Should parse Feb/March (winter) session correctly."""
        filename = "9708_w22_qp_11.pdf"
        metadata = parse_cambridge_filename(filename)

        assert metadata is not None
        assert metadata['session'] == "w"
        assert "Feb/March" in metadata['title']

    def test_parse_invalid_filename(self):
        """Should return None for invalid filename."""
        invalid_filenames = [
            "invalid_file.pdf",
            "9708_2024_qp_12.pdf",  # Wrong format
            "9708_m24_12.pdf",  # Missing qp/ms
            "textbook.pdf"
        ]

        for filename in invalid_filenames:
            assert parse_cambridge_filename(filename) is None


class TestDownloadPastPaper:
    """Test PDF download from Cambridge website."""

    @patch('src.services.sync_service.requests.get')
    def test_download_success(self, mock_get):
        """Should download PDF and save to destination."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"PDF content chunk 1", b"PDF content chunk 2"]
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = os.path.join(temp_dir, "test.pdf")
            result = download_past_paper("https://example.com/paper.pdf", dest_path)

            assert result is True
            assert os.path.exists(dest_path)

            # Verify content
            with open(dest_path, 'rb') as f:
                content = f.read()
                assert content == b"PDF content chunk 1PDF content chunk 2"

    @patch('src.services.sync_service.requests.get')
    def test_download_creates_parent_directories(self, mock_get):
        """Should create parent directories if they don't exist."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"Test content"]
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = os.path.join(temp_dir, "subdir1", "subdir2", "test.pdf")
            result = download_past_paper("https://example.com/paper.pdf", dest_path)

            assert result is True
            assert os.path.exists(dest_path)

    @patch('src.services.sync_service.requests.get')
    def test_download_handles_network_error(self, mock_get):
        """Should return False and log error on network failure."""
        import requests.exceptions
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = os.path.join(temp_dir, "test.pdf")
            result = download_past_paper("https://example.com/paper.pdf", dest_path)

            assert result is False
            assert not os.path.exists(dest_path)

    @patch('src.services.sync_service.requests.get')
    def test_download_handles_404_error(self, mock_get):
        """Should return False on 404 Not Found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = os.path.join(temp_dir, "test.pdf")
            result = download_past_paper("https://example.com/paper.pdf", dest_path)

            assert result is False


class TestCheckResourceExists:
    """Test signature-based duplicate detection."""

    def test_returns_resource_when_signature_exists(self, db_session: Session):
        """Should return existing resource with matching signature."""
        signature = "abc123def456"

        # Create resource with signature
        resource = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Test Paper",
            file_path="/fake/path.pdf",
            signature=signature,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            s3_sync_status=S3SyncStatus.SUCCESS
        )
        db_session.add(resource)
        db_session.commit()

        # Check if exists
        result = check_resource_exists(signature, db_session)

        assert result is not None
        assert result.id == resource.id
        assert result.signature == signature

    def test_returns_none_when_signature_not_found(self, db_session: Session):
        """Should return None when signature doesn't exist."""
        result = check_resource_exists("nonexistent_signature", db_session)
        assert result is None


class TestLinkMarkScheme:
    """Test linking mark schemes to question papers."""

    def test_link_mark_scheme_updates_metadata(self, db_session: Session):
        """Should update question paper metadata with mark_scheme_id."""
        # Create question paper
        qp = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Question Paper",
            file_path="/fake/qp.pdf",
            signature="qp_sig",
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            s3_sync_status=S3SyncStatus.SUCCESS
        )
        db_session.add(qp)

        # Create mark scheme
        ms = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Mark Scheme",
            file_path="/fake/ms.pdf",
            signature="ms_sig",
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            s3_sync_status=S3SyncStatus.SUCCESS
        )
        db_session.add(ms)
        db_session.commit()

        # Link mark scheme
        link_mark_scheme(qp.id, ms.id, db_session)

        # Verify link
        db_session.refresh(qp)
        assert qp.metadata is not None
        assert 'mark_scheme_id' in qp.metadata
        assert qp.metadata['mark_scheme_id'] == str(ms.id)

    def test_link_mark_scheme_raises_error_for_invalid_qp(self, db_session: Session):
        """Should raise ValueError if question paper doesn't exist."""
        fake_qp_id = uuid4()
        fake_ms_id = uuid4()

        with pytest.raises(ValueError, match="not found"):
            link_mark_scheme(fake_qp_id, fake_ms_id, db_session)


class TestScrapeCambridgeWebsite:
    """Test Cambridge website scraping."""

    def test_scrape_returns_list(self):
        """Should return list of resource metadata (Phase 1: empty mock)."""
        resources = scrape_cambridge_website(subject_code="9708")

        assert isinstance(resources, list)
        # Phase 1: Mock implementation returns empty list
        # Phase 2: Will test actual scraping with mocked HTML response


class TestSyncPastPaperFromURL:
    """Test complete sync workflow for single past paper."""

    @patch('src.services.sync_service.download_past_paper')
    @patch('src.services.sync_service.calculate_signature')
    def test_sync_creates_new_resource(self, mock_signature, mock_download, db_session: Session):
        """Should download, calculate signature, and create resource."""
        mock_download.return_value = True
        mock_signature.return_value = "new_signature_abc123"

        metadata = {
            'year': '2024',
            'session': 'm',
            'paper': '12',
            'type': 'question_paper',
            'title': 'Economics 9708 May/June 2024 Paper 12'
        }

        with patch('src.services.sync_service.save_file_to_local') as mock_save:
            mock_save.return_value = "/absolute/path/to/file.pdf"

            resource = sync_past_paper_from_url(
                url="https://example.com/paper.pdf",
                metadata=metadata,
                session=db_session,
                subject_code="9708"
            )

            assert resource is not None
            assert resource.title == metadata['title']
            assert resource.signature == "new_signature_abc123"
            assert resource.resource_type == ResourceType.PAST_PAPER
            assert resource.visibility == Visibility.PUBLIC
            assert resource.admin_approved is True

    @patch('src.services.sync_service.download_past_paper')
    @patch('src.services.sync_service.calculate_signature')
    def test_sync_skips_duplicate_signature(self, mock_signature, mock_download, db_session: Session):
        """Should skip download if signature already exists."""
        duplicate_signature = "duplicate_sig_123"
        mock_download.return_value = True
        mock_signature.return_value = duplicate_signature

        # Create existing resource with same signature
        existing = Resource(
            id=uuid4(),
            resource_type=ResourceType.PAST_PAPER,
            title="Existing Paper",
            file_path="/fake/path.pdf",
            signature=duplicate_signature,
            visibility=Visibility.PUBLIC,
            admin_approved=True,
            s3_sync_status=S3SyncStatus.SUCCESS
        )
        db_session.add(existing)
        db_session.commit()

        metadata = {
            'year': '2024',
            'session': 'm',
            'paper': '12',
            'type': 'question_paper',
            'title': 'Economics 9708 May/June 2024 Paper 12'
        }

        with patch('src.services.sync_service.save_file_to_local'):
            resource = sync_past_paper_from_url(
                url="https://example.com/paper.pdf",
                metadata=metadata,
                session=db_session,
                subject_code="9708"
            )

            # Should return None (skipped duplicate)
            assert resource is None

            # Verify existing resource updated_at timestamp was updated
            db_session.refresh(existing)
            assert existing.updated_at is not None

    @patch('src.services.sync_service.download_past_paper')
    def test_sync_returns_none_on_download_failure(self, mock_download, db_session: Session):
        """Should return None if download fails."""
        mock_download.return_value = False  # Download failed

        metadata = {
            'year': '2024',
            'session': 'm',
            'paper': '12',
            'type': 'question_paper',
            'title': 'Economics 9708 May/June 2024 Paper 12'
        }

        resource = sync_past_paper_from_url(
            url="https://example.com/paper.pdf",
            metadata=metadata,
            session=db_session,
            subject_code="9708"
        )

        assert resource is None
