"""
PDF Text Extraction Service with OCR Fallback.

Feature: 007-resource-bank-files (User Story 3)
Created: 2025-12-27

Two-stage extraction strategy:
1. Native PDF extraction (PyPDF2) - fast, works for text-based PDFs
2. OCR fallback (pytesseract) - slow, for scanned/image-based PDFs

Threshold: If native extraction yields <100 characters, trigger OCR.

Constitutional Compliance:
- Principle I: Content integrity via accurate text extraction
- FR-034: Support both native and scanned PDFs
"""

import os
from pathlib import Path
from typing import Optional

import PyPDF2


def extract_pdf_text(file_path: str, ocr_threshold: int = 100) -> dict:
    """
    Extract text from PDF using PyPDF2 with OCR fallback.

    Two-stage approach:
    1. Try native PDF text extraction
    2. If text length < ocr_threshold, trigger OCR fallback

    Args:
        file_path: Absolute path to PDF file
        ocr_threshold: Minimum characters to consider native extraction successful (default: 100)

    Returns:
        Dictionary with:
        - text: Extracted text content
        - method: "native" or "ocr"
        - page_count: Number of pages in PDF
        - char_count: Character count of extracted text
        - ocr_triggered: Boolean indicating if OCR was used

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        PyPDF2.errors.PdfReadError: If PDF is corrupted/invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Stage 1: Native PDF extraction
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)

            # Extract text from all pages
            native_text = ''
            for page in reader.pages:
                native_text += page.extract_text()

        # Check if native extraction yielded sufficient text
        if len(native_text.strip()) >= ocr_threshold:
            return {
                'text': native_text,
                'method': 'native',
                'page_count': page_count,
                'char_count': len(native_text),
                'ocr_triggered': False
            }

        # Stage 2: OCR fallback for scanned PDFs
        print(f"INFO: Native extraction yielded {len(native_text)} chars (< {ocr_threshold}), triggering OCR")

        ocr_text = extract_pdf_text_with_ocr(file_path)

        return {
            'text': ocr_text,
            'method': 'ocr',
            'page_count': page_count,
            'char_count': len(ocr_text),
            'ocr_triggered': True
        }

    except PyPDF2.errors.PdfReadError as e:
        raise PyPDF2.errors.PdfReadError(f"Invalid or corrupted PDF: {str(e)}")


def extract_pdf_text_with_ocr(file_path: str) -> str:
    """
    Extract text from PDF using OCR (pytesseract).

    Used as fallback when native extraction yields insufficient text
    (typically for scanned/image-based PDFs).

    Args:
        file_path: Absolute path to PDF file

    Returns:
        Extracted text content

    Raises:
        ImportError: If pdf2image or pytesseract not installed
        Exception: If OCR processing fails
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract

        # Convert PDF pages to images
        images = convert_from_path(file_path)

        # OCR each page
        ocr_text = ''
        for i, image in enumerate(images):
            print(f"INFO: OCR processing page {i+1}/{len(images)}")
            page_text = pytesseract.image_to_string(image)
            ocr_text += page_text + '\n'

        return ocr_text

    except ImportError as e:
        raise ImportError(
            f"OCR dependencies not installed: {str(e)}. "
            "Install with: pip install pdf2image pytesseract"
        )
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")


def detect_scanned_pdf(file_path: str) -> bool:
    """
    Detect if PDF is scanned (image-based) vs native (text-based).

    Uses simple heuristic: extract text from first 3 pages, if <100 chars total,
    likely scanned.

    Args:
        file_path: Absolute path to PDF file

    Returns:
        True if likely scanned, False if likely native text PDF
    """
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Check first 3 pages (or fewer if PDF is short)
            sample_pages = min(3, len(reader.pages))

            sample_text = ''
            for i in range(sample_pages):
                sample_text += reader.pages[i].extract_text()

        # If minimal text extracted from sample, likely scanned
        return len(sample_text.strip()) < 100

    except Exception:
        # If detection fails, assume native PDF
        return False


def extract_text_from_page_range(file_path: str, start_page: int, end_page: int) -> str:
    """
    Extract text from specific page range (for textbook excerpts).

    Args:
        file_path: Absolute path to PDF file
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed, inclusive)

    Returns:
        Extracted text from specified page range

    Raises:
        ValueError: If page range is invalid
        FileNotFoundError: If PDF doesn't exist
    """
    if start_page < 1 or end_page < start_page:
        raise ValueError(f"Invalid page range: {start_page}-{end_page}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)

        if end_page > len(reader.pages):
            raise ValueError(
                f"Page range {start_page}-{end_page} exceeds PDF length ({len(reader.pages)} pages)"
            )

        # Extract text from page range (convert to 0-indexed)
        page_text = ''
        for i in range(start_page - 1, end_page):
            page_text += reader.pages[i].extract_text() + '\n'

    return page_text


def get_pdf_metadata(file_path: str) -> dict:
    """
    Extract PDF metadata (title, author, page count, creation date).

    Args:
        file_path: Absolute path to PDF file

    Returns:
        Dictionary with metadata:
        - title: PDF title (from metadata or filename)
        - author: Author name (if available)
        - page_count: Number of pages
        - creation_date: Creation date (if available)
        - file_size: File size in bytes
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)

        metadata = reader.metadata if reader.metadata else {}

        return {
            'title': metadata.get('/Title', Path(file_path).stem),
            'author': metadata.get('/Author', None),
            'page_count': len(reader.pages),
            'creation_date': metadata.get('/CreationDate', None),
            'file_size': os.path.getsize(file_path)
        }
