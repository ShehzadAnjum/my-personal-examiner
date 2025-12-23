"""
Generic Question Extractor

Subject config-driven PDF question extraction for Phase II Question Bank.

Architecture Decision AD-002: Generic Extraction Framework
- Reads extraction patterns from subject.extraction_patterns JSONB
- Not hard-coded per subject (Economics patterns in config, not code)
- Economics 9708 serves as reference implementation

Usage:
    >>> from src.models.subject import Subject
    >>> subject = session.exec(select(Subject).where(Subject.code == "9708")).first()
    >>> extractor = GenericExtractor(subject)
    >>> questions = extractor.extract_questions("path/to/9708_s22_qp_31.pdf")
    >>> len(questions)
    3  # Economics Paper 3 has 3 essay questions

Phase II Success Criteria:
- SC-002: >95% extraction accuracy for Economics 9708 standard format
- NFR-006: >95% accuracy (all questions extracted with correct marks)
"""

import re
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader

from src.models.subject import Subject
from src.question_extractors import extraction_patterns as ep
from src.question_extractors.cambridge_parser import CambridgeFilenameParser


class ExtractionError(Exception):
    """Raised when PDF extraction fails"""

    pass


class GenericExtractor:
    """
    Generic question extractor driven by subject configuration

    Extracts questions from PDFs using patterns from subject.extraction_patterns JSONB.
    Supports multi-page questions, subparts, diagrams, and header/footer filtering.

    Architecture:
    - Subject-agnostic (reads patterns from config, not hard-coded)
    - Uses pdfplumber (primary) with PyPDF2 fallback
    - Economics 9708 patterns demonstrate capabilities

    Attributes:
        subject: Subject instance with extraction_patterns JSONB populated
        config: Parsed extraction_patterns dictionary
        filename_parser: CambridgeFilenameParser for metadata extraction
    """

    def __init__(self, subject: Subject):
        """
        Initialize extractor with subject configuration

        Args:
            subject: Subject instance with extraction_patterns JSONB

        Raises:
            ValueError: If subject.extraction_patterns is None or invalid
        """
        if not subject.extraction_patterns:
            raise ValueError(
                f"Subject {subject.code} has no extraction_patterns config. "
                f"Run seed script: uv run python scripts/seed_economics_config.py"
            )

        self.subject = subject
        self.config: dict[str, Any] = subject.extraction_patterns
        self.filename_parser = CambridgeFilenameParser()

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber with PyPDF2 fallback

        Research Decision (research.md #1):
        - Primary: pdfplumber (better table/layout handling)
        - Fallback: PyPDF2 (faster for simple PDFs)

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text from all pages

        Raises:
            ExtractionError: If both pdfplumber and PyPDF2 fail

        Examples:
            >>> extractor = GenericExtractor(economics_subject)
            >>> text = extractor.extract_text("9708_s22_qp_31.pdf")
            >>> "Question 1" in text
            True
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise ExtractionError(f"PDF file not found: {pdf_path}")

        # Try pdfplumber first (better table handling)
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
                raise ExtractionError(
                    f"Failed to extract text from {pdf_path}. "
                    f"pdfplumber error: {e}, PyPDF2 error: {e2}"
                )

    def extract_questions(self, pdf_path: str) -> list[dict[str, Any]]:
        """
        Extract questions from PDF using subject-specific patterns

        Main extraction pipeline:
        1. Parse filename for metadata
        2. Extract text from PDF
        3. Filter headers/footers
        4. Split by question delimiter
        5. Parse each question (number, text, marks, difficulty)
        6. Handle subparts and multi-page questions

        Args:
            pdf_path: Path to PDF file

        Returns:
            list[dict]: List of extracted question dicts with keys:
                - question_number: int
                - question_text: str
                - max_marks: int
                - difficulty: str ("easy", "medium", "hard")
                - source_paper: str (from filename)
                - has_diagram: bool

        Raises:
            ExtractionError: If extraction fails or no questions found

        Examples:
            >>> extractor = GenericExtractor(economics_subject)
            >>> questions = extractor.extract_questions("9708_s22_qp_31.pdf")
            >>> questions[0]['question_number']
            1
            >>> questions[0]['max_marks']
            25
        """
        # Parse filename for metadata
        parsed_filename = self.filename_parser.parse(pdf_path)
        source_paper = parsed_filename.to_source_paper_string()

        # Extract text
        text = self.extract_text(pdf_path)

        # Filter headers/footers
        text = self._filter_headers_footers(text)

        # Split by question delimiter
        question_chunks = self._split_by_questions(text)

        # Parse each question
        questions = []
        for i, chunk in enumerate(question_chunks, start=1):
            try:
                question = self._parse_question(chunk, i, source_paper)
                if question:
                    questions.append(question)
            except Exception as e:
                # Log warning but continue with other questions
                print(f"Warning: Failed to parse question {i}: {e}")
                continue

        if not questions:
            raise ExtractionError(
                f"No questions found in {pdf_path}. "
                f"Check extraction patterns in subject config."
            )

        return questions

    def _split_by_questions(self, text: str) -> list[str]:
        """
        Split text by question delimiter pattern

        Uses question_delimiter from subject config.

        Args:
            text: Full PDF text

        Returns:
            list[str]: Text chunks (one per question)
        """
        delimiter_pattern = self.config.get("question_delimiter", {}).get("primary", r"Question\s+\d+")

        chunks = ep.split_by_delimiter(text, delimiter_pattern)

        # Remove first chunk if it's header/introduction
        if chunks and not re.search(r"^\d+", chunks[0].strip()):
            chunks = chunks[1:]

        return chunks

    def _filter_headers_footers(self, text: str) -> str:
        """
        Remove headers, footers, page numbers from text

        Uses headers_footers_to_remove patterns from subject config.

        Args:
            text: Raw PDF text

        Returns:
            str: Cleaned text
        """
        patterns = self.config.get("headers_footers_to_remove", [])
        return ep.remove_headers_footers(text, patterns)

    def _parse_question(
        self, text: str, fallback_number: int, source_paper: str
    ) -> dict[str, Any] | None:
        """
        Parse individual question from text chunk

        Extracts:
        - Question number
        - Question text (with subparts aggregated)
        - Maximum marks
        - Difficulty (heuristic-based)
        - Diagram detection

        Args:
            text: Question text chunk
            fallback_number: Sequential number if extraction fails
            source_paper: Source paper identifier

        Returns:
            dict | None: Question data or None if parsing fails
        """
        if not text.strip():
            return None

        # Extract question number
        delimiter_pattern = self.config.get("question_delimiter", {}).get("primary", r"Question\s+\d+")
        question_number = ep.extract_question_number(text, delimiter_pattern)
        if question_number is None:
            question_number = fallback_number

        # Check for subparts
        has_subparts = self.config.get("has_subparts", False)
        max_marks = 0
        question_text = text

        if has_subparts:
            subpart_pattern = self.config.get("subpart_patterns", {}).get(
                "lowercase_parentheses", {}
            ).get("pattern", r"\([a-z]\)")

            subparts = ep.extract_subparts(text, subpart_pattern)

            if subparts:
                # Aggregate marks from subparts
                marks_pattern = self._get_marks_pattern()
                max_marks = ep.aggregate_subpart_marks(subparts, marks_pattern)

                # Concatenate subpart text
                delimiter = self.config.get("subpart_aggregation", {}).get("text_delimiter", "\n\n")
                preserve_labels = self.config.get("subpart_aggregation", {}).get("preserve_labels", True)

                parts = []
                for subpart in subparts:
                    part_text = subpart["text"]
                    if preserve_labels:
                        part_text = f"{subpart['label']} {part_text}"
                    parts.append(part_text)

                question_text = delimiter.join(parts)

        # If no subparts or no marks from subparts, extract marks from full text
        if max_marks == 0:
            marks_pattern = self._get_marks_pattern()
            max_marks = ep.extract_marks(text, marks_pattern)

        if max_marks is None or max_marks == 0:
            # Skip questions without marks (might be instructions)
            return None

        # Calculate difficulty
        difficulty = self._calculate_difficulty(max_marks)

        # Detect diagram references
        diagram_indicators = self.config.get("diagram_detection", {}).get("indicators", [])
        has_diagram = ep.detect_diagram_reference(text, diagram_indicators)

        # Clean question text
        question_text = self._clean_question_text(question_text)

        return {
            "question_number": question_number,
            "question_text": question_text,
            "max_marks": max_marks,
            "difficulty": difficulty,
            "source_paper": source_paper,
            "has_diagram": has_diagram,
        }

    def _get_marks_pattern(self) -> str:
        """Get marks extraction pattern from config"""
        marks_config = self.config.get("marks_pattern", {})

        if isinstance(marks_config, dict):
            # Use number_extraction pattern if available (has capture group)
            pattern = marks_config.get("number_extraction")
            if pattern:
                return pattern

            # Otherwise use primary pattern
            pattern = marks_config.get("primary", r"\[(\d+)\s+marks?\]")
            return pattern
        else:
            # If marks_pattern is a string, use it directly
            return str(marks_config)

    def _calculate_difficulty(self, marks: int) -> str:
        """
        Calculate difficulty using marks-based heuristic

        Heuristic (from research.md):
        - 1-12 marks: easy
        - 13-20 marks: medium
        - 21-30 marks: hard

        Phase III will upgrade to historical performance-based difficulty.

        Args:
            marks: Maximum marks

        Returns:
            str: Difficulty level
        """
        return ep.calculate_difficulty_from_marks(marks)

    def _clean_question_text(self, text: str) -> str:
        """
        Clean question text (remove excessive whitespace, etc.)

        Args:
            text: Raw question text

        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = text.strip()

        return text
