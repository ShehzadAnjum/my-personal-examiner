"""
Unit Tests: Cambridge Filename Parser

Tests for Phase II User Story 3 (US3) - Cambridge Filename Parsing.

Test Coverage:
- T022: Standard format (9708_s22_qp_31.pdf)
- T023: Mark scheme format (9708_w21_ms_32.pdf)
- T024: Variant format (9708_s22_qp_31_v2.pdf)
- T025: Different sessions (9706_m23_qp_42.pdf)
- T026: Invalid format (should raise InvalidFilenameFormatError)

Success Criteria:
- 100% parsing accuracy for Cambridge standard format (NFR-007)
- All tests must pass before Phase 3 checkpoint

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest

from src.question_extractors.cambridge_parser import (
    CambridgeFilenameParser,
    InvalidFilenameFormatError,
    PaperType,
    ParsedFilename,
    Session,
)


class TestCambridgeFilenameParser:
    """Test suite for Cambridge International filename parsing"""

    @pytest.fixture
    def parser(self) -> CambridgeFilenameParser:
        """Create parser instance for tests"""
        return CambridgeFilenameParser()

    # ========================================================================
    # T022: Test standard format (Economics Paper 3, Summer 2022)
    # ========================================================================

    def test_parse_standard_format(self, parser: CambridgeFilenameParser):
        """
        T022: Parse standard Cambridge filename format

        Given: Filename "9708_s22_qp_31.pdf"
        When: Parser extracts metadata
        Then: Returns correct subject, year, session, paper type, paper number
        """
        filename = "9708_s22_qp_31.pdf"

        result = parser.parse(filename)

        assert isinstance(result, ParsedFilename)
        assert result.subject_code == "9708"
        assert result.year == 2022
        assert result.session == Session.MAY_JUNE
        assert result.paper_type == PaperType.QUESTION_PAPER
        assert result.paper_number == 31
        assert result.variant is None
        assert result.original_filename == filename

    def test_source_paper_string_generation(self, parser: CambridgeFilenameParser):
        """
        T022 (additional): Verify source_paper string generation

        Given: Parsed filename
        When: to_source_paper_string() called
        Then: Returns filename without .pdf extension
        """
        filename = "9708_s22_qp_31.pdf"
        result = parser.parse(filename)

        source_paper = result.to_source_paper_string()

        assert source_paper == "9708_s22_qp_31"
        assert ".pdf" not in source_paper

    # ========================================================================
    # T023: Test mark scheme format (Economics Paper 3, Winter 2021)
    # ========================================================================

    def test_parse_mark_scheme_format(self, parser: CambridgeFilenameParser):
        """
        T023: Parse mark scheme filename

        Given: Filename "9708_w21_ms_32.pdf"
        When: Parser extracts metadata
        Then: Returns MARK_SCHEME paper type and OCT_NOV session
        """
        filename = "9708_w21_ms_32.pdf"

        result = parser.parse(filename)

        assert result.subject_code == "9708"
        assert result.year == 2021
        assert result.session == Session.OCT_NOV  # w = winter = OCT_NOV
        assert result.paper_type == PaperType.MARK_SCHEME  # ms = MARK_SCHEME
        assert result.paper_number == 32
        assert result.variant is None

    # ========================================================================
    # T024: Test variant format (Economics Paper 3 Variant 2)
    # ========================================================================

    def test_parse_variant_format(self, parser: CambridgeFilenameParser):
        """
        T024: Parse filename with variant suffix

        Given: Filename "9708_s22_qp_31_v2.pdf"
        When: Parser extracts metadata
        Then: Returns variant=2
        """
        filename = "9708_s22_qp_31_v2.pdf"

        result = parser.parse(filename)

        assert result.subject_code == "9708"
        assert result.year == 2022
        assert result.session == Session.MAY_JUNE
        assert result.paper_type == PaperType.QUESTION_PAPER
        assert result.paper_number == 31
        assert result.variant == 2  # v2 parsed correctly

    def test_parse_variant_3(self, parser: CambridgeFilenameParser):
        """
        T024 (additional): Parse variant 3 format

        Tests robustness with different variant numbers
        """
        filename = "9708_w21_qp_33_v3.pdf"

        result = parser.parse(filename)

        assert result.paper_number == 33
        assert result.variant == 3

    # ========================================================================
    # T025: Test different sessions (Accounting Paper 4, March 2023)
    # ========================================================================

    def test_parse_march_session(self, parser: CambridgeFilenameParser):
        """
        T025: Parse March (Feb/March) session format

        Given: Filename "9706_m23_qp_42.pdf"
        When: Parser extracts metadata
        Then: Returns FEB_MARCH session for 'm' code
        """
        filename = "9706_m23_qp_42.pdf"

        result = parser.parse(filename)

        assert result.subject_code == "9706"  # Accounting
        assert result.year == 2023
        assert result.session == Session.FEB_MARCH  # m = march = FEB_MARCH
        assert result.paper_type == PaperType.QUESTION_PAPER
        assert result.paper_number == 42
        assert result.variant is None

    def test_parse_all_sessions(self, parser: CambridgeFilenameParser):
        """
        T025 (additional): Verify all three session codes parse correctly

        Tests robustness across all valid session codes
        """
        test_cases = [
            ("9708_s22_qp_31.pdf", Session.MAY_JUNE),
            ("9708_m22_qp_31.pdf", Session.FEB_MARCH),
            ("9708_w22_qp_31.pdf", Session.OCT_NOV),
        ]

        for filename, expected_session in test_cases:
            result = parser.parse(filename)
            assert result.session == expected_session, f"Failed for {filename}"

    # ========================================================================
    # T026: Test invalid format (non-Cambridge filename)
    # ========================================================================

    def test_parse_invalid_format_raises_error(self, parser: CambridgeFilenameParser):
        """
        T026: Parse invalid filename raises InvalidFilenameFormatError

        Given: Filename "random_economics_questions.pdf"
        When: Parser attempts to extract metadata
        Then: Raises InvalidFilenameFormatError with helpful message
        """
        invalid_filename = "random_economics_questions.pdf"

        with pytest.raises(InvalidFilenameFormatError) as exc_info:
            parser.parse(invalid_filename)

        # Verify error message is helpful
        assert invalid_filename in str(exc_info.value)
        assert "Cambridge International format" in str(exc_info.value)

    def test_parse_invalid_formats_comprehensive(self, parser: CambridgeFilenameParser):
        """
        T026 (additional): Test various invalid formats

        Tests robustness with different types of invalid filenames
        """
        invalid_filenames = [
            "economics_paper_2022.pdf",  # Wrong format entirely
            "9708_s22.pdf",  # Missing components
            "9708_s22_qp.pdf",  # Missing paper number
            "708_s22_qp_31.pdf",  # Wrong subject code length
            "9708_x22_qp_31.pdf",  # Invalid session code
            "9708_s22_xx_31.pdf",  # Invalid paper type
            "9708_s22_qp_31.doc",  # Wrong extension
        ]

        for invalid_filename in invalid_filenames:
            with pytest.raises(
                InvalidFilenameFormatError, match="Cambridge International format"
            ):
                parser.parse(invalid_filename)

    # ========================================================================
    # Additional Tests: Edge Cases & Robustness
    # ========================================================================

    def test_parse_case_insensitive(self, parser: CambridgeFilenameParser):
        """
        Test parser handles uppercase/lowercase variations

        Cambridge filenames are typically lowercase but parser should be robust
        """
        filenames = [
            "9708_S22_QP_31.PDF",  # All uppercase
            "9708_S22_qp_31.pdf",  # Mixed case
            "9708_s22_QP_31.PDF",  # Mixed case extension
        ]

        for filename in filenames:
            result = parser.parse(filename)
            assert result.subject_code == "9708"
            assert result.year == 2022
            # Case-insensitive matching should work

    def test_parse_from_full_path(self, parser: CambridgeFilenameParser):
        """
        Test parser extracts filename from full path

        Users may provide full paths, parser should handle this
        """
        full_path = "/home/user/downloads/9708_s22_qp_31.pdf"

        result = parser.parse(full_path)

        assert result.subject_code == "9708"
        assert result.original_filename == "9708_s22_qp_31.pdf"  # Just filename

    def test_is_valid_filename_method(self, parser: CambridgeFilenameParser):
        """
        Test is_valid_filename() method (doesn't raise exceptions)

        Useful for validation without try/except
        """
        assert parser.is_valid_filename("9708_s22_qp_31.pdf") is True
        assert parser.is_valid_filename("random_file.pdf") is False

    def test_parse_examiner_report_format(self, parser: CambridgeFilenameParser):
        """
        Test parsing examiner report paper type

        Examiner reports use 'er' code
        """
        filename = "9708_s22_er_32.pdf"

        result = parser.parse(filename)

        assert result.paper_type == PaperType.EXAMINER_REPORT
        assert result.paper_number == 32

    def test_year_conversion_edge_cases(self, parser: CambridgeFilenameParser):
        """
        Test year conversion for different decades

        Verify 2-digit to 4-digit conversion works correctly
        """
        test_cases = [
            ("9708_s05_qp_31.pdf", 2005),  # Early 2000s
            ("9708_s18_qp_31.pdf", 2018),  # 2018
            ("9708_s99_qp_31.pdf", 2099),  # Far future (edge case)
        ]

        for filename, expected_year in test_cases:
            result = parser.parse(filename)
            assert result.year == expected_year, f"Failed for {filename}"

    def test_paper_number_range(self, parser: CambridgeFilenameParser):
        """
        Test various paper numbers parse correctly

        Cambridge papers range from 01 to 99 typically
        """
        test_cases = [
            ("9708_s22_qp_01.pdf", 1),
            ("9708_s22_qp_11.pdf", 11),
            ("9708_s22_qp_31.pdf", 31),
            ("9708_s22_qp_42.pdf", 42),
            ("9708_s22_qp_99.pdf", 99),
        ]

        for filename, expected_number in test_cases:
            result = parser.parse(filename)
            assert result.paper_number == expected_number


# ========================================================================
# Parametrized Tests for Comprehensive Coverage
# ========================================================================


@pytest.mark.parametrize(
    "filename,expected_code,expected_year,expected_session,expected_type,expected_paper",
    [
        # Economics 9708
        ("9708_s22_qp_31.pdf", "9708", 2022, Session.MAY_JUNE, PaperType.QUESTION_PAPER, 31),
        ("9708_w21_ms_32.pdf", "9708", 2021, Session.OCT_NOV, PaperType.MARK_SCHEME, 32),
        # Accounting 9706
        ("9706_m23_qp_42.pdf", "9706", 2023, Session.FEB_MARCH, PaperType.QUESTION_PAPER, 42),
        # Math 9709
        ("9709_s20_qp_11.pdf", "9709", 2020, Session.MAY_JUNE, PaperType.QUESTION_PAPER, 11),
        # English 8021
        ("8021_w19_ms_12.pdf", "8021", 2019, Session.OCT_NOV, PaperType.MARK_SCHEME, 12),
    ],
)
def test_parse_multiple_subjects_parametrized(
    filename, expected_code, expected_year, expected_session, expected_type, expected_paper
):
    """
    Parametrized test for multiple subjects

    Verifies parser works generically across all Cambridge subjects
    """
    parser = CambridgeFilenameParser()
    result = parser.parse(filename)

    assert result.subject_code == expected_code
    assert result.year == expected_year
    assert result.session == expected_session
    assert result.paper_type == expected_type
    assert result.paper_number == expected_paper
