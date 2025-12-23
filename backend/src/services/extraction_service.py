"""
Extraction Service

Orchestrates PDF extraction for question papers and mark schemes.
Combines GenericExtractor and MarkSchemeExtractor.

Phase II User Story 1: Upload & Storage
- Extracts questions from question paper PDFs
- Extracts raw text from mark scheme PDFs
- Links mark schemes to question papers via filename matching
"""

from pathlib import Path
from typing import Any
from uuid import UUID

from src.models.mark_scheme import MarkScheme
from src.models.question import Question
from src.question_extractors.cambridge_parser import (
    CambridgeFilenameParser,
    InvalidFilenameFormatError,
    PaperType,
    Session,
)
from src.question_extractors.generic_extractor import GenericExtractor
from src.question_extractors.mark_scheme_extractor import MarkSchemeExtractor


class ExtractionError(Exception):
    """Raised when PDF extraction fails"""

    pass


class ExtractionService:
    """
    Service for extracting questions and mark schemes from PDFs

    Orchestrates GenericExtractor and MarkSchemeExtractor to process
    Cambridge International past paper PDFs.

    Attributes:
        filename_parser: Parser for Cambridge filenames
        generic_extractor: Extractor for question papers
        mark_scheme_extractor: Extractor for mark schemes
    """

    def __init__(self):
        """Initialize extraction service"""
        self.filename_parser = CambridgeFilenameParser()
        self.mark_scheme_extractor = MarkSchemeExtractor()

    def extract_question_paper(
        self, pdf_path: str, subject_id: UUID, extraction_patterns: dict[str, Any]
    ) -> list[Question]:
        """
        Extract questions from question paper PDF

        Args:
            pdf_path: Path to question paper PDF
            subject_id: Subject UUID
            extraction_patterns: Extraction patterns from subject config (JSONB)

        Returns:
            list[Question]: Extracted Question model instances

        Raises:
            ExtractionError: If extraction fails
            InvalidFilenameFormatError: If filename is invalid

        Examples:
            >>> service = ExtractionService()
            >>> questions = service.extract_question_paper(
            ...     "9708_s22_qp_22.pdf",
            ...     economics_subject_id,
            ...     {"question_delimiter": {"primary": "..."}, ...}
            ... )
            >>> len(questions)
            4
        """
        pdf_path = Path(pdf_path)

        # Parse filename to extract metadata
        try:
            parsed = self.filename_parser.parse(pdf_path.name)
        except InvalidFilenameFormatError as e:
            raise ExtractionError(f"Invalid Cambridge filename: {pdf_path.name}") from e

        # Verify this is a question paper
        if parsed.paper_type != PaperType.QUESTION_PAPER:
            raise ExtractionError(
                f"Expected question paper (qp), got {parsed.paper_type.value}"
            )

        # Create temporary Subject instance with extraction patterns
        # GenericExtractor requires a Subject instance, so we create a minimal one
        from src.models.subject import Subject

        temp_subject = Subject(
            code="temp",
            name="Temporary",
            level="A",
            syllabus_year="2023-2025",
            extraction_patterns=extraction_patterns,
        )

        # Extract questions using GenericExtractor
        try:
            generic_extractor = GenericExtractor(temp_subject)
            extracted_questions = generic_extractor.extract_questions(str(pdf_path))
        except Exception as e:
            raise ExtractionError(f"Failed to extract questions: {e}") from e

        # Convert to Question model instances
        questions = []
        for q_data in extracted_questions:
            question = Question(
                subject_id=subject_id,
                question_text=q_data["question_text"],
                max_marks=q_data["max_marks"],
                difficulty=q_data.get("difficulty", "medium"),
                source_paper=parsed.to_source_paper_string(),
                paper_number=parsed.paper_number,
                question_number=q_data["question_number"],
                year=parsed.year,
                session=self._session_to_string(parsed.session),
                file_path=str(pdf_path),
            )
            questions.append(question)

        return questions

    def extract_mark_scheme(
        self, pdf_path: str, subject_id: UUID
    ) -> tuple[MarkScheme, str]:
        """
        Extract raw text from mark scheme PDF

        Args:
            pdf_path: Path to mark scheme PDF
            subject_id: Subject UUID

        Returns:
            tuple[MarkScheme, str]: (MarkScheme model instance, matching QP filename)

        Raises:
            ExtractionError: If extraction fails
            InvalidFilenameFormatError: If filename is invalid

        Examples:
            >>> service = ExtractionService()
            >>> mark_scheme, qp_filename = service.extract_mark_scheme(
            ...     "9708_s22_ms_22.pdf",
            ...     economics_subject_id
            ... )
            >>> mark_scheme.source_paper
            '9708_s22_ms_22'
            >>> qp_filename
            '9708_s22_qp_22.pdf'
        """
        pdf_path = Path(pdf_path)

        # Parse filename to extract metadata
        try:
            parsed = self.filename_parser.parse(pdf_path.name)
        except InvalidFilenameFormatError as e:
            raise ExtractionError(f"Invalid Cambridge filename: {pdf_path.name}") from e

        # Verify this is a mark scheme
        if parsed.paper_type != PaperType.MARK_SCHEME:
            raise ExtractionError(
                f"Expected mark scheme (ms), got {parsed.paper_type.value}"
            )

        # Extract mark scheme using MarkSchemeExtractor
        try:
            result = self.mark_scheme_extractor.extract_and_match(str(pdf_path))
        except Exception as e:
            raise ExtractionError(f"Failed to extract mark scheme: {e}") from e

        # Convert to MarkScheme model instance
        mark_scheme = MarkScheme(
            subject_id=subject_id,
            source_paper=result["source_paper"],
            mark_scheme_text=result["mark_scheme_text"],
            question_paper_filename=result["question_paper_filename"],
            paper_number=parsed.paper_number,
            year=parsed.year,
            session=self._session_to_string(parsed.session),
            file_path=str(pdf_path),
        )

        return mark_scheme, result["question_paper_filename"]

    def detect_pdf_type(self, pdf_path: str) -> str:
        """
        Detect PDF type from filename (question paper or mark scheme)

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: "question_paper", "mark_scheme", or "unknown"

        Examples:
            >>> service = ExtractionService()
            >>> service.detect_pdf_type("9708_s22_qp_22.pdf")
            'question_paper'
            >>> service.detect_pdf_type("9708_s22_ms_22.pdf")
            'mark_scheme'
        """
        try:
            parsed = self.filename_parser.parse(Path(pdf_path).name)
            if parsed.paper_type == PaperType.QUESTION_PAPER:
                return "question_paper"
            elif parsed.paper_type == PaperType.MARK_SCHEME:
                return "mark_scheme"
            else:
                return "unknown"
        except InvalidFilenameFormatError:
            return "unknown"

    def _session_to_string(self, session: Session) -> str:
        """
        Convert Session enum to string

        Args:
            session: Session enum value

        Returns:
            str: Session string (MAY_JUNE, FEB_MARCH, OCT_NOV)
        """
        return session.value
