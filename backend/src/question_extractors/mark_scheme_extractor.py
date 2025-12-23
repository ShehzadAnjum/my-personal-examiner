"""
Minimal Mark Scheme Extractor

Phase II Quick Win: Store raw mark scheme text for later parsing.

This minimal implementation:
- Extracts full text from mark scheme PDFs
- Matches mark schemes to question papers via filename
- Stores raw text in database for Phase III detailed parsing

Architecture Decision AD-005: Defer detailed mark scheme parsing to Phase III.
Phase II focuses on question bank; marking criteria parsing happens when building AI marker.

Usage:
    >>> extractor = MarkSchemeExtractor()
    >>> ms_text = extractor.extract_text("9708_s22_ms_22.pdf")
    >>> matched_qp = extractor.get_matching_question_paper("9708_s22_ms_22.pdf")
    >>> # Returns: "9708_s22_qp_22.pdf"
"""

from pathlib import Path

import pdfplumber
from pypdf import PdfReader

from src.question_extractors.cambridge_parser import (
    CambridgeFilenameParser,
    PaperType,
    Session,
)

# Reverse mappings: Enum → Code
SESSION_TO_CODE = {
    Session.MAY_JUNE: "s",
    Session.FEB_MARCH: "m",
    Session.OCT_NOV: "w",
}

PAPER_TYPE_TO_CODE = {
    PaperType.QUESTION_PAPER: "qp",
    PaperType.MARK_SCHEME: "ms",
    PaperType.EXAMINER_REPORT: "er",
}


class MarkSchemeExtractor:
    """
    Minimal mark scheme extractor for Phase II

    Extracts raw text from Cambridge mark scheme PDFs and matches them to
    corresponding question papers via filename parsing.

    Detailed parsing (extracting marking points, levels, criteria) is deferred
    to Phase III when building the AI marking engine.

    Attributes:
        filename_parser: CambridgeFilenameParser for metadata extraction
    """

    def __init__(self):
        """Initialize mark scheme extractor"""
        self.filename_parser = CambridgeFilenameParser()

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract full text from mark scheme PDF

        Uses pdfplumber (primary) with PyPDF2 fallback, same as GenericExtractor.

        Args:
            pdf_path: Path to mark scheme PDF

        Returns:
            str: Full extracted text from all pages

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If both pdfplumber and PyPDF2 fail

        Examples:
            >>> extractor = MarkSchemeExtractor()
            >>> text = extractor.extract_text("9708_s22_ms_22.pdf")
            >>> "Mark Scheme" in text
            True
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Mark scheme PDF not found: {pdf_path}")

        # Try pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                return text
        except Exception as e:
            # Fallback to PyPDF2
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                return text
            except Exception as e2:
                raise Exception(
                    f"Failed to extract text from {pdf_path}. "
                    f"pdfplumber error: {e}, PyPDF2 error: {e2}"
                )

    def get_matching_question_paper(self, mark_scheme_filename: str) -> str | None:
        """
        Get matching question paper filename for a mark scheme

        Converts mark scheme filename to corresponding question paper filename
        by replacing paper type 'ms' with 'qp'.

        Args:
            mark_scheme_filename: Mark scheme filename (e.g., "9708_s22_ms_22.pdf")

        Returns:
            str | None: Matching question paper filename (e.g., "9708_s22_qp_22.pdf")
                       or None if filename invalid

        Examples:
            >>> extractor = MarkSchemeExtractor()
            >>> extractor.get_matching_question_paper("9708_s22_ms_22.pdf")
            '9708_s22_qp_22.pdf'
            >>> extractor.get_matching_question_paper("9708_w21_ms_31.pdf")
            '9708_w21_qp_31.pdf'
        """
        try:
            # Parse mark scheme filename
            parsed = self.filename_parser.parse(mark_scheme_filename)

            # Convert enums back to codes
            session_code = SESSION_TO_CODE[parsed.session]
            year_2digit = str(parsed.year)[-2:]  # Extract last 2 digits (2022 → 22)

            # Build question paper filename (replace ms with qp)
            qp_filename = (
                f"{parsed.subject_code}_"
                f"{session_code}{year_2digit}_"
                f"qp_{parsed.paper_number:02d}"  # Ensure 2-digit format
            )

            # Add variant if present
            if parsed.variant:
                qp_filename += f"_v{parsed.variant}"

            qp_filename += ".pdf"

            return qp_filename

        except Exception:
            return None

    def get_matching_mark_scheme(self, question_paper_filename: str) -> str | None:
        """
        Get matching mark scheme filename for a question paper

        Converts question paper filename to corresponding mark scheme filename
        by replacing paper type 'qp' with 'ms'.

        Args:
            question_paper_filename: Question paper filename (e.g., "9708_s22_qp_22.pdf")

        Returns:
            str | None: Matching mark scheme filename (e.g., "9708_s22_ms_22.pdf")
                       or None if filename invalid

        Examples:
            >>> extractor = MarkSchemeExtractor()
            >>> extractor.get_matching_mark_scheme("9708_s22_qp_22.pdf")
            '9708_s22_ms_22.pdf'
            >>> extractor.get_matching_mark_scheme("9708_w21_qp_31.pdf")
            '9708_w21_ms_31.pdf'
        """
        try:
            # Parse question paper filename
            parsed = self.filename_parser.parse(question_paper_filename)

            # Convert enums back to codes
            session_code = SESSION_TO_CODE[parsed.session]
            year_2digit = str(parsed.year)[-2:]  # Extract last 2 digits (2022 → 22)

            # Build mark scheme filename (replace qp with ms)
            ms_filename = (
                f"{parsed.subject_code}_"
                f"{session_code}{year_2digit}_"
                f"ms_{parsed.paper_number:02d}"  # Ensure 2-digit format
            )

            # Add variant if present
            if parsed.variant:
                ms_filename += f"_v{parsed.variant}"

            ms_filename += ".pdf"

            return ms_filename

        except Exception:
            return None

    def extract_and_match(self, mark_scheme_path: str) -> dict[str, str]:
        """
        Extract mark scheme text and find matching question paper

        Convenience method that combines extraction and matching.

        Args:
            mark_scheme_path: Path to mark scheme PDF

        Returns:
            dict with keys:
                - 'mark_scheme_filename': Original mark scheme filename
                - 'question_paper_filename': Matching question paper filename
                - 'mark_scheme_text': Full extracted text
                - 'source_paper': Source paper identifier (for database)

        Examples:
            >>> extractor = MarkSchemeExtractor()
            >>> result = extractor.extract_and_match("9708_s22_ms_22.pdf")
            >>> result['question_paper_filename']
            '9708_s22_qp_22.pdf'
            >>> len(result['mark_scheme_text']) > 1000
            True
        """
        pdf_path = Path(mark_scheme_path)
        filename = pdf_path.name

        # Extract text
        text = self.extract_text(mark_scheme_path)

        # Find matching question paper
        qp_filename = self.get_matching_question_paper(filename)

        # Parse for source_paper identifier
        parsed = self.filename_parser.parse(filename)
        source_paper = parsed.to_source_paper_string()

        return {
            "mark_scheme_filename": filename,
            "question_paper_filename": qp_filename,
            "mark_scheme_text": text,
            "source_paper": source_paper,
        }
