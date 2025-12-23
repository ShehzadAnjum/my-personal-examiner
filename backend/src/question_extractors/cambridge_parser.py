"""
Cambridge International Filename Parser

Parses Cambridge International PDF filenames to extract metadata.

Standard Cambridge filename format:
    {subject_code}_{session}{year}_{paper_type}_{paper_number}[_v{variant}].pdf

Examples:
    9708_s22_qp_31.pdf → Economics, Summer 2022, Question Paper, Paper 31
    9708_w21_ms_32.pdf → Economics, Winter 2021, Mark Scheme, Paper 32
    9706_m23_qp_42_v2.pdf → Accounting, March 2023, Question Paper, Paper 42, Variant 2

Architecture Decision AD-002: Generic Extraction Framework
- Filename parsing is subject-agnostic (works for all Cambridge subjects)
- Metadata extracted here feeds into subject-specific extraction logic
- 100% accuracy required per NFR-007

Phase II Success Criterion SC-007:
- 100% of uploaded PDFs must have complete source_paper metadata
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Session(str, Enum):
    """Cambridge International examination sessions"""

    MAY_JUNE = "MAY_JUNE"
    FEB_MARCH = "FEB_MARCH"
    OCT_NOV = "OCT_NOV"


class PaperType(str, Enum):
    """Cambridge International paper types"""

    QUESTION_PAPER = "QUESTION_PAPER"
    MARK_SCHEME = "MARK_SCHEME"
    EXAMINER_REPORT = "EXAMINER_REPORT"


# Session code to Session enum mapping
SESSION_MAP: dict[str, Session] = {
    "s": Session.MAY_JUNE,
    "m": Session.FEB_MARCH,
    "w": Session.OCT_NOV,
}

# Paper type code to PaperType enum mapping
PAPER_TYPE_MAP: dict[str, PaperType] = {
    "qp": PaperType.QUESTION_PAPER,
    "ms": PaperType.MARK_SCHEME,
    "er": PaperType.EXAMINER_REPORT,
}


@dataclass(frozen=True)
class ParsedFilename:
    """
    Structured metadata extracted from Cambridge filename

    Attributes:
        subject_code: Cambridge subject code (e.g., "9708" for Economics)
        year: Full 4-digit year (e.g., 2022)
        session: Examination session (MAY_JUNE, FEB_MARCH, OCT_NOV)
        paper_type: Type of paper (QUESTION_PAPER, MARK_SCHEME, EXAMINER_REPORT)
        paper_number: Paper number (e.g., 31, 32, 42)
        variant: Optional variant number (e.g., 2 for v2)
        original_filename: Original filename string

    Examples:
        >>> parsed = ParsedFilename(
        ...     subject_code="9708",
        ...     year=2022,
        ...     session=Session.MAY_JUNE,
        ...     paper_type=PaperType.QUESTION_PAPER,
        ...     paper_number=31,
        ...     variant=None,
        ...     original_filename="9708_s22_qp_31.pdf"
        ... )
        >>> parsed.subject_code
        '9708'
        >>> parsed.year
        2022
    """

    subject_code: str
    year: int
    session: Session
    paper_type: PaperType
    paper_number: int
    variant: int | None
    original_filename: str

    def to_source_paper_string(self) -> str:
        """
        Generate source_paper string for database storage

        Format matches original filename without .pdf extension.
        Used as unique identifier for questions.

        Returns:
            str: Source paper identifier (e.g., "9708_s22_qp_31")

        Examples:
            >>> parsed.to_source_paper_string()
            '9708_s22_qp_31'
        """
        return self.original_filename.replace(".pdf", "")


class InvalidFilenameFormatError(ValueError):
    """
    Raised when filename does not match Cambridge International format

    This is a validation error indicating the PDF is not from Cambridge
    or does not follow the standard naming convention.

    Attributes:
        filename: The invalid filename that was attempted to parse
        message: Human-readable error message
    """

    def __init__(self, filename: str, message: str | None = None):
        self.filename = filename
        if message is None:
            message = (
                f"Filename '{filename}' does not match Cambridge International format. "
                f"Expected: NNNN_sYY_qp_NN.pdf (e.g., 9708_s22_qp_31.pdf)"
            )
        super().__init__(message)


class CambridgeFilenameParser:
    """
    Parser for Cambridge International PDF filenames

    Extracts structured metadata from Cambridge filename format using regex.

    Filename Format:
        {subject_code}_{session}{year}_{paper_type}_{paper_number}[_v{variant}].pdf

    Components:
        - subject_code: 4 digits (e.g., 9708)
        - session: s/m/w (summer/march/winter)
        - year: 2 digits (e.g., 22 for 2022)
        - paper_type: qp/ms/er (question paper/mark scheme/examiner report)
        - paper_number: 2 digits (e.g., 31)
        - variant: optional (e.g., v2)

    Usage:
        >>> parser = CambridgeFilenameParser()
        >>> parsed = parser.parse("9708_s22_qp_31.pdf")
        >>> parsed.subject_code
        '9708'
        >>> parsed.year
        2022
        >>> parsed.session
        <Session.MAY_JUNE: 'MAY_JUNE'>

    Architecture:
        - Generic (not subject-specific) - works for all Cambridge subjects
        - Uses named capture groups for readability
        - Case-insensitive matching for robustness
        - Validates format before extraction

    Performance:
        - Regex compiled once (class-level)
        - O(1) lookup for session/paper type mapping
        - <1ms parsing time per filename
    """

    # Compiled regex pattern (class-level for performance)
    # Named capture groups for clarity
    PATTERN = re.compile(
        r"(?P<code>\d{4})_"  # Subject code (4 digits)
        r"(?P<session>[smw])"  # Session (s/m/w)
        r"(?P<year>\d{2})_"  # Year (2 digits)
        r"(?P<type>qp|ms|er)_"  # Paper type
        r"(?P<paper>\d{2})"  # Paper number (2 digits)
        r"(?:_v(?P<variant>\d+))?"  # Optional variant
        r"\.pdf$",  # Extension
        re.IGNORECASE,  # Case-insensitive for robustness
    )

    def parse(self, filename: str) -> ParsedFilename:
        """
        Parse Cambridge International filename to extract metadata

        Args:
            filename: Cambridge PDF filename (e.g., "9708_s22_qp_31.pdf")

        Returns:
            ParsedFilename: Structured metadata

        Raises:
            InvalidFilenameFormatError: If filename doesn't match Cambridge format

        Examples:
            >>> parser = CambridgeFilenameParser()
            >>> parsed = parser.parse("9708_s22_qp_31.pdf")
            >>> parsed.subject_code
            '9708'
            >>> parsed.year
            2022

            >>> parser.parse("random_file.pdf")
            Traceback (most recent call last):
                ...
            InvalidFilenameFormatError: Filename 'random_file.pdf' does not match...
        """
        # Extract filename from path if full path provided
        filename = Path(filename).name

        # Match against pattern
        match = self.PATTERN.match(filename)

        if not match:
            raise InvalidFilenameFormatError(filename)

        # Extract components from named groups
        subject_code = match.group("code")
        year_str = match.group("year")
        session_code = match.group("session").lower()
        paper_type_code = match.group("type").lower()
        paper_number_str = match.group("paper")
        variant_str = match.group("variant")

        # Convert year: 2-digit to 4-digit (assume 2000+)
        # Cambridge A-Levels started using this format around 2005
        year = 2000 + int(year_str)

        # Map session code to Session enum
        if session_code not in SESSION_MAP:
            raise InvalidFilenameFormatError(
                filename, f"Unknown session code: '{session_code}' (expected s/m/w)"
            )
        session = SESSION_MAP[session_code]

        # Map paper type code to PaperType enum
        if paper_type_code not in PAPER_TYPE_MAP:
            raise InvalidFilenameFormatError(
                filename, f"Unknown paper type: '{paper_type_code}' (expected qp/ms/er)"
            )
        paper_type = PAPER_TYPE_MAP[paper_type_code]

        # Parse paper number
        paper_number = int(paper_number_str)

        # Parse optional variant
        variant = int(variant_str) if variant_str else None

        return ParsedFilename(
            subject_code=subject_code,
            year=year,
            session=session,
            paper_type=paper_type,
            paper_number=paper_number,
            variant=variant,
            original_filename=filename,
        )

    def is_valid_filename(self, filename: str) -> bool:
        """
        Check if filename matches Cambridge format (without raising exception)

        Args:
            filename: Filename to validate

        Returns:
            bool: True if valid Cambridge format, False otherwise

        Examples:
            >>> parser = CambridgeFilenameParser()
            >>> parser.is_valid_filename("9708_s22_qp_31.pdf")
            True
            >>> parser.is_valid_filename("random_file.pdf")
            False
        """
        try:
            self.parse(filename)
            return True
        except InvalidFilenameFormatError:
            return False
