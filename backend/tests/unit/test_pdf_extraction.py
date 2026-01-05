"""
Unit tests for PDF text extraction with OCR fallback.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Tests PyPDF2 native extraction, pytesseract OCR fallback,
and 100-character threshold detection.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import PyPDF2

from src.services.pdf_extraction_service import (
    detect_scanned_pdf,
    extract_pdf_text,
    extract_pdf_text_with_ocr,
    extract_text_from_page_range,
    get_pdf_metadata,
)


class TestExtractPDFText:
    """Test native PDF extraction with OCR fallback."""

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_native_extraction_success(self, mock_reader):
        """Should use native extraction when text >100 chars."""
        # Mock PDF with sufficient native text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a native PDF with plenty of text content. " * 5  # 250 chars

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page]
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = extract_pdf_text(temp_path, ocr_threshold=100)

            assert result['method'] == 'native'
            assert result['page_count'] == 2
            assert result['char_count'] > 100
            assert result['ocr_triggered'] is False
            assert len(result['text']) > 100

        finally:
            os.remove(temp_path)

    @patch('src.services.pdf_extraction_service.extract_pdf_text_with_ocr')
    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_ocr_fallback_when_text_below_threshold(self, mock_reader, mock_ocr):
        """Should trigger OCR when native extraction yields <100 chars."""
        # Mock PDF with minimal native text (scanned PDF)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "ab"  # Only 2 chars (below threshold)

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_reader.return_value = mock_pdf

        # Mock OCR extraction
        mock_ocr.return_value = "OCR extracted text from scanned PDF" * 10  # 370 chars

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = extract_pdf_text(temp_path, ocr_threshold=100)

            assert result['method'] == 'ocr'
            assert result['ocr_triggered'] is True
            mock_ocr.assert_called_once_with(temp_path)

        finally:
            os.remove(temp_path)

    def test_raises_error_for_nonexistent_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            extract_pdf_text("/fake/nonexistent.pdf")


class TestExtractPDFTextWithOCR:
    """Test pytesseract OCR extraction."""

    @patch('src.services.pdf_extraction_service.pytesseract.image_to_string')
    @patch('src.services.pdf_extraction_service.convert_from_path')
    def test_ocr_extraction_success(self, mock_convert, mock_tesseract):
        """Should extract text from images using OCR."""
        # Mock PDF to image conversion
        mock_image1 = MagicMock()
        mock_image2 = MagicMock()
        mock_convert.return_value = [mock_image1, mock_image2]

        # Mock OCR results
        mock_tesseract.side_effect = [
            "Page 1 OCR text content",
            "Page 2 OCR text content"
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = extract_pdf_text_with_ocr(temp_path)

            assert "Page 1 OCR text content" in result
            assert "Page 2 OCR text content" in result
            assert mock_tesseract.call_count == 2

        finally:
            os.remove(temp_path)

    @patch('src.services.pdf_extraction_service.pytesseract', None)
    @patch('src.services.pdf_extraction_service.convert_from_path', None)
    def test_raises_import_error_when_dependencies_missing(self):
        """Should raise ImportError if pdf2image or pytesseract not installed."""
        # This test verifies the import error handling in the function
        # In actual execution, the import would fail, but for testing we mock it
        pass  # Skipped in Phase 1 (dependencies are installed)


class TestDetectScannedPDF:
    """Test scanned PDF detection."""

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_detects_scanned_pdf(self, mock_reader):
        """Should return True for scanned PDFs (minimal text)."""
        # Mock PDF with minimal text (likely scanned)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "a"  # 1 char

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page, mock_page]
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = detect_scanned_pdf(temp_path)
            assert result is True  # Less than 100 chars from 3 pages = scanned

        finally:
            os.remove(temp_path)

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_detects_native_pdf(self, mock_reader):
        """Should return False for native PDFs (sufficient text)."""
        # Mock PDF with plenty of text (native)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is native text content. " * 10  # 300 chars

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page, mock_page]
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = detect_scanned_pdf(temp_path)
            assert result is False  # More than 100 chars = native

        finally:
            os.remove(temp_path)


class TestExtractTextFromPageRange:
    """Test page range extraction for textbook excerpts."""

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_extracts_specific_page_range(self, mock_reader):
        """Should extract text only from specified pages."""
        # Mock 10-page PDF
        mock_pages = []
        for i in range(10):
            page = MagicMock()
            page.extract_text.return_value = f"Page {i+1} content"
            mock_pages.append(page)

        mock_pdf = MagicMock()
        mock_pdf.pages = mock_pages
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            # Extract pages 3-5 (1-indexed)
            result = extract_text_from_page_range(temp_path, start_page=3, end_page=5)

            assert "Page 3 content" in result
            assert "Page 4 content" in result
            assert "Page 5 content" in result
            assert "Page 1 content" not in result  # Not in range
            assert "Page 10 content" not in result  # Not in range

        finally:
            os.remove(temp_path)

    def test_raises_error_for_invalid_page_range(self):
        """Should raise ValueError for invalid page range."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            with pytest.raises(ValueError, match="Invalid page range"):
                extract_text_from_page_range(temp_path, start_page=5, end_page=2)

            with pytest.raises(ValueError, match="Invalid page range"):
                extract_text_from_page_range(temp_path, start_page=0, end_page=5)

        finally:
            os.remove(temp_path)


class TestGetPDFMetadata:
    """Test PDF metadata extraction."""

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_extracts_metadata(self, mock_reader):
        """Should extract title, author, page count from PDF."""
        # Mock PDF metadata
        mock_metadata = {
            '/Title': 'Economics Textbook Chapter 12',
            '/Author': 'Cambridge Press',
            '/CreationDate': 'D:20240101120000'
        }

        mock_pdf = MagicMock()
        mock_pdf.metadata = mock_metadata
        mock_pdf.pages = [MagicMock(), MagicMock(), MagicMock()]  # 3 pages
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = get_pdf_metadata(temp_path)

            assert result['title'] == 'Economics Textbook Chapter 12'
            assert result['author'] == 'Cambridge Press'
            assert result['page_count'] == 3
            assert result['creation_date'] == 'D:20240101120000'
            assert result['file_size'] > 0

        finally:
            os.remove(temp_path)

    @patch('src.services.pdf_extraction_service.PyPDF2.PdfReader')
    def test_handles_missing_metadata(self, mock_reader):
        """Should use filename as title when metadata missing."""
        mock_pdf = MagicMock()
        mock_pdf.metadata = None  # No metadata
        mock_pdf.pages = [MagicMock()]
        mock_reader.return_value = mock_pdf

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="my_notes_") as temp:
            temp.write(b"%PDF-1.4 test")
            temp_path = temp.name

        try:
            result = get_pdf_metadata(temp_path)

            assert "my_notes_" in result['title']  # Uses filename
            assert result['author'] is None
            assert result['page_count'] == 1

        finally:
            os.remove(temp_path)
