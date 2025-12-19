"""
Unit Tests: Mark Scheme Extractor

Tests for Phase II - Minimal Mark Scheme Extraction (Quick Win).

Test Coverage:
- Filename matching (qp ↔ ms)
- Text extraction from mark scheme PDFs
- Integration with real Economics mark schemes

Constitutional Requirement:
- >80% test coverage (Principle VII)

Architecture Decision AD-005:
- Phase II: Store raw text only (minimal implementation)
- Phase III: Parse detailed marking criteria
"""

import pytest
from pathlib import Path

from src.question_extractors.mark_scheme_extractor import MarkSchemeExtractor


class TestMarkSchemeExtractor:
    """Test suite for minimal mark scheme extraction"""

    @pytest.fixture
    def extractor(self) -> MarkSchemeExtractor:
        """Create extractor instance for tests"""
        return MarkSchemeExtractor()

    # ========================================================================
    # Filename Matching Tests
    # ========================================================================

    def test_get_matching_question_paper_standard_format(self, extractor: MarkSchemeExtractor):
        """Test converting mark scheme filename to question paper filename"""
        ms_filename = "9708_s22_ms_22.pdf"

        qp_filename = extractor.get_matching_question_paper(ms_filename)

        assert qp_filename == "9708_s22_qp_22.pdf"

    def test_get_matching_question_paper_with_variant(self, extractor: MarkSchemeExtractor):
        """Test filename matching with variant suffix"""
        ms_filename = "9708_s22_ms_31_v2.pdf"

        qp_filename = extractor.get_matching_question_paper(ms_filename)

        assert qp_filename == "9708_s22_qp_31_v2.pdf"

    def test_get_matching_question_paper_different_sessions(self, extractor: MarkSchemeExtractor):
        """Test filename matching across different sessions"""
        test_cases = [
            ("9708_s22_ms_22.pdf", "9708_s22_qp_22.pdf"),  # Summer
            ("9708_w21_ms_32.pdf", "9708_w21_qp_32.pdf"),  # Winter
            ("9706_m23_ms_42.pdf", "9706_m23_qp_42.pdf"),  # March
        ]

        for ms_filename, expected_qp in test_cases:
            qp_filename = extractor.get_matching_question_paper(ms_filename)
            assert qp_filename == expected_qp, f"Failed for {ms_filename}"

    def test_get_matching_mark_scheme_standard_format(self, extractor: MarkSchemeExtractor):
        """Test converting question paper filename to mark scheme filename"""
        qp_filename = "9708_s22_qp_22.pdf"

        ms_filename = extractor.get_matching_mark_scheme(qp_filename)

        assert ms_filename == "9708_s22_ms_22.pdf"

    def test_get_matching_mark_scheme_with_variant(self, extractor: MarkSchemeExtractor):
        """Test reverse matching with variant"""
        qp_filename = "9708_w21_qp_32_v3.pdf"

        ms_filename = extractor.get_matching_mark_scheme(qp_filename)

        assert ms_filename == "9708_w21_ms_32_v3.pdf"

    def test_get_matching_question_paper_invalid_filename(self, extractor: MarkSchemeExtractor):
        """Test invalid filename returns None"""
        invalid_filename = "random_economics_markscheme.pdf"

        result = extractor.get_matching_question_paper(invalid_filename)

        assert result is None

    def test_get_matching_mark_scheme_invalid_filename(self, extractor: MarkSchemeExtractor):
        """Test reverse matching with invalid filename returns None"""
        invalid_filename = "random_paper.pdf"

        result = extractor.get_matching_mark_scheme(invalid_filename)

        assert result is None

    # ========================================================================
    # Text Extraction Tests
    # ========================================================================

    def test_extract_text_from_mark_scheme_pdf(self, extractor: MarkSchemeExtractor):
        """
        Integration test: Extract text from real Economics mark scheme

        PREREQUISITES:
        - Mark scheme PDF downloaded to resources/subjects/9708/sample_papers/

        EXPECTED:
        - Text extraction succeeds
        - Contains "Mark Scheme" or "MARK SCHEME"
        - Contains question identifiers
        """
        ms_path = Path("resources/subjects/9708/sample_papers/9708_s22_ms_22.pdf")

        if not ms_path.exists():
            pytest.skip(f"Mark scheme PDF not found: {ms_path}")

        text = extractor.extract_text(str(ms_path))

        # Verify extraction worked
        assert len(text) > 1000, "Extracted text too short"
        assert (
            "Mark Scheme" in text or "MARK SCHEME" in text
        ), "Mark scheme identifier not found"

        # Verify contains question references
        # Economics mark schemes have "Question Answer Marks" table
        assert "Question" in text or "Answer" in text, "Question column not found"

    def test_extract_text_file_not_found(self, extractor: MarkSchemeExtractor):
        """Test extraction fails gracefully for non-existent file"""
        non_existent_path = "resources/subjects/9708/sample_papers/nonexistent.pdf"

        with pytest.raises(FileNotFoundError):
            extractor.extract_text(non_existent_path)

    # ========================================================================
    # Combined Extraction and Matching Tests
    # ========================================================================

    def test_extract_and_match_integration(self, extractor: MarkSchemeExtractor):
        """
        Integration test: Extract mark scheme and match to question paper

        PREREQUISITES:
        - Mark scheme PDF downloaded

        EXPECTED:
        - Extraction succeeds
        - Matching question paper filename identified
        - Source paper metadata extracted
        """
        ms_path = Path("resources/subjects/9708/sample_papers/9708_s22_ms_22.pdf")

        if not ms_path.exists():
            pytest.skip(f"Mark scheme PDF not found: {ms_path}")

        result = extractor.extract_and_match(str(ms_path))

        # Verify result structure
        assert "mark_scheme_filename" in result
        assert "question_paper_filename" in result
        assert "mark_scheme_text" in result
        assert "source_paper" in result

        # Verify values
        assert result["mark_scheme_filename"] == "9708_s22_ms_22.pdf"
        assert result["question_paper_filename"] == "9708_s22_qp_22.pdf"
        assert result["source_paper"] == "9708_s22_ms_22"
        assert len(result["mark_scheme_text"]) > 1000

    def test_extract_and_match_with_variant(self, extractor: MarkSchemeExtractor):
        """Test combined extraction with variant suffix"""
        ms_path = Path("resources/subjects/9708/sample_papers/9708_w21_ms_32.pdf")

        if not ms_path.exists():
            pytest.skip(f"Mark scheme PDF not found: {ms_path}")

        result = extractor.extract_and_match(str(ms_path))

        # Verify matching
        assert result["mark_scheme_filename"] == "9708_w21_ms_32.pdf"
        assert result["question_paper_filename"] == "9708_w21_qp_32.pdf"
        assert result["source_paper"] == "9708_w21_ms_32"


# ========================================================================
# Integration Test Placeholders (Optional - Phase III)
# ========================================================================


@pytest.mark.skip(reason="Phase III: Detailed mark scheme parsing not implemented yet")
def test_parse_marking_criteria_from_mark_scheme():
    """
    Phase III: Parse detailed marking criteria (levels, points, rubrics)

    DEFERRED: Phase II stores raw text only
    FUTURE: Implement detailed parsing when building AI marking engine

    EXPECTED (Phase III):
    - Extract question-by-question marking criteria
    - Parse level descriptors (L1, L2, L3, L4)
    - Extract marks allocation per level
    - Parse guidance notes
    """
    pass


@pytest.mark.skip(reason="Phase III: Marking criteria matching not implemented yet")
def test_match_marking_criteria_to_questions():
    """
    Phase III: Match extracted marking criteria to question objects

    DEFERRED: Phase II focuses on question bank, not marking engine
    FUTURE: Link marking criteria to questions for AI marker

    EXPECTED (Phase III):
    - For each question, find corresponding marking criteria
    - Store structured marking data in question.marking_scheme JSONB
    - Enable AI marker to reference official Cambridge criteria
    """
    pass
