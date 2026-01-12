"""
Unit tests for file storage service.

Feature: 007-resource-bank-files
Created: 2025-12-27
"""

import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.models.enums import ResourceType
from src.services.file_storage_service import (
    calculate_signature,
    get_file_extension,
    get_file_path_for_resource,
    save_file_to_local,
    scan_file_for_virus,
    validate_file_size,
)


class TestCalculateSignature:
    """Test SHA-256 signature calculation."""

    def test_calculate_signature_returns_64_char_hex(self):
        """Signature should be 64-character hexadecimal string."""
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(b"Test content for signature")
            temp_path = f.name

        try:
            signature = calculate_signature(temp_path)
            assert len(signature) == 64
            assert all(c in '0123456789abcdef' for c in signature)
        finally:
            os.remove(temp_path)

    def test_calculate_signature_is_deterministic(self):
        """Same content should produce same signature."""
        content = b"Deterministic test content"
        
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(content)
            temp_path1 = f.name

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(content)
            temp_path2 = f.name

        try:
            sig1 = calculate_signature(temp_path1)
            sig2 = calculate_signature(temp_path2)
            assert sig1 == sig2
        finally:
            os.remove(temp_path1)
            os.remove(temp_path2)

    def test_calculate_signature_differs_for_different_content(self):
        """Different content should produce different signatures."""
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(b"Content A")
            temp_path1 = f.name

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(b"Content B")
            temp_path2 = f.name

        try:
            sig1 = calculate_signature(temp_path1)
            sig2 = calculate_signature(temp_path2)
            assert sig1 != sig2
        finally:
            os.remove(temp_path1)
            os.remove(temp_path2)


class TestGetFilePathForResource:
    """Test file path generation for different resource types."""

    def test_syllabus_path_structure(self):
        """Syllabus files should be stored in syllabus/{subject_code}/."""
        path = get_file_path_for_resource(
            resource_type=ResourceType.SYLLABUS,
            filename="9708_syllabus_2025.pdf",
            subject_code="9708"
        )
        assert path == "backend/resources/syllabus/9708/9708_syllabus_2025.pdf"

    def test_past_paper_path_structure(self):
        """Past papers should be stored in past_papers/{subject_code}/."""
        path = get_file_path_for_resource(
            resource_type=ResourceType.PAST_PAPER,
            filename="2024_m_qp_22.pdf",
            subject_code="9708"
        )
        assert path == "backend/resources/past_papers/9708/2024_m_qp_22.pdf"

    def test_user_upload_requires_student_id(self):
        """User uploads should require student_id."""
        with pytest.raises(ValueError, match="student_id required"):
            get_file_path_for_resource(
                resource_type=ResourceType.USER_UPLOAD,
                filename="my_notes.pdf",
                student_id=None
            )

    def test_user_upload_path_includes_student_id(self):
        """User uploads should be scoped to student directory."""
        student_id = uuid4()
        path = get_file_path_for_resource(
            resource_type=ResourceType.USER_UPLOAD,
            filename="my_notes.pdf",
            student_id=student_id
        )
        assert path == f"backend/resources/user_uploads/{student_id}/my_notes.pdf"

    def test_video_metadata_path(self):
        """Videos should be stored in videos/metadata/."""
        path = get_file_path_for_resource(
            resource_type=ResourceType.VIDEO,
            filename="video_metadata.json"
        )
        assert path == "backend/resources/videos/metadata/video_metadata.json"


class TestSaveFileToLocal:
    """Test file saving to permanent storage."""

    def test_save_creates_parent_directories(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "source.txt"
            source_file.write_text("Test content")

            dest_path = Path(temp_dir) / "new_dir" / "subdir" / "dest.txt"
            
            result = save_file_to_local(str(source_file), str(dest_path))
            
            assert os.path.exists(result)
            assert Path(result).read_text() == "Test content"

    def test_save_preserves_file_content(self):
        """Should preserve file content during copy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_content = b"Binary content \x00\x01\x02"
            source_file = Path(temp_dir) / "source.bin"
            source_file.write_bytes(source_content)

            dest_path = Path(temp_dir) / "dest.bin"
            
            save_file_to_local(str(source_file), str(dest_path))
            
            assert dest_path.read_bytes() == source_content


class TestScanFileForVirus:
    """Test virus scanning with ClamAV."""

    @patch('src.services.file_storage_service.pyclamd.ClamdUnixSocket')
    def test_scan_returns_safe_when_no_virus(self, mock_clamd):
        """Should return safe=True when no virus detected."""
        mock_cd = MagicMock()
        mock_cd.scan_file.return_value = None  # No virus
        mock_clamd.return_value = mock_cd

        result = scan_file_for_virus("/fake/path.pdf")
        
        assert result["safe"] is True
        assert "virus" not in result

    @patch('src.services.file_storage_service.pyclamd.ClamdUnixSocket')
    def test_scan_detects_virus_and_deletes_file(self, mock_clamd):
        """Should detect virus, delete file, and return safe=False."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            mock_cd = MagicMock()
            mock_cd.scan_file.return_value = {
                temp_path: ('FOUND', 'Eicar-Test-Signature')
            }
            mock_clamd.return_value = mock_cd

            result = scan_file_for_virus(temp_path)
            
            assert result["safe"] is False
            assert result["virus"] == "Eicar-Test-Signature"
            assert not os.path.exists(temp_path)  # File should be deleted
        except FileNotFoundError:
            # Expected - file was deleted
            pass

    @patch('src.services.file_storage_service.pyclamd.ClamdUnixSocket')
    def test_scan_handles_clamav_unavailable(self, mock_clamd):
        """Should gracefully handle ClamAV daemon unavailable."""
        mock_clamd.side_effect = FileNotFoundError("Socket not found")

        result = scan_file_for_virus("/fake/path.pdf")
        
        assert result["safe"] is True  # Phase 1: allow with warning
        assert "warning" in result
        assert "ClamAV daemon unavailable" in result["warning"]


class TestValidateFileSize:
    """Test file size validation."""

    def test_validate_accepts_file_within_limit(self):
        """Should accept files within 50MB limit."""
        file_size_30mb = 30 * 1024 * 1024
        assert validate_file_size(file_size_30mb) is True

    def test_validate_accepts_file_at_exact_limit(self):
        """Should accept file at exactly 50MB."""
        file_size_50mb = 50 * 1024 * 1024
        assert validate_file_size(file_size_50mb) is True

    def test_validate_rejects_file_exceeding_limit(self):
        """Should reject files exceeding 50MB limit."""
        file_size_51mb = 51 * 1024 * 1024
        assert validate_file_size(file_size_51mb) is False

    def test_validate_respects_custom_limit(self):
        """Should respect custom size limit."""
        file_size_10mb = 10 * 1024 * 1024
        assert validate_file_size(file_size_10mb, max_size_mb=5) is False
        assert validate_file_size(file_size_10mb, max_size_mb=20) is True


class TestGetFileExtension:
    """Test file extension extraction."""

    def test_extracts_pdf_extension(self):
        """Should extract .pdf extension."""
        assert get_file_extension("document.pdf") == ".pdf"

    def test_extracts_extension_lowercase(self):
        """Should return extension in lowercase."""
        assert get_file_extension("Document.PDF") == ".pdf"

    def test_handles_multiple_dots(self):
        """Should extract last extension with multiple dots."""
        assert get_file_extension("archive.tar.gz") == ".gz"

    def test_handles_no_extension(self):
        """Should return empty string for no extension."""
        assert get_file_extension("filename") == ""
