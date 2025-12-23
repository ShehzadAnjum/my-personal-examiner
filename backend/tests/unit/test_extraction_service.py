"""
Unit Tests: Extraction Service

Tests for Phase II US1 - Upload & Storage extraction service.

Test Coverage:
- Question paper extraction (integration with GenericExtractor)
- Mark scheme extraction (integration with MarkSchemeExtractor)
- PDF type detection
- Model instance creation

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest
from pathlib import Path
from uuid import uuid4

from src.services.extraction_service import ExtractionError, ExtractionService


class TestExtractionService:
    """Test suite for extraction service"""

    @pytest.fixture
    def service(self) -> ExtractionService:
        """Create extraction service instance"""
        return ExtractionService()

    @pytest.fixture
    def subject_id(self):
        """Mock subject UUID"""
        return uuid4()

    @pytest.fixture
    def economics_extraction_patterns(self):
        """Economics extraction patterns from YAML config"""
        return {
            "question_delimiter": {
                "primary": "(^[1-9]\\s+(?!Section)(?=[A-Z(]))",
                "alternatives": ["Question\\s+\\d+", "Q\\.?\\s*\\d+"],
            },
            "marks_pattern": {
                "primary": "\\[\\d+(?:\\s+marks?)?\\]",
                "number_extraction": "\\[(\\d+)(?:\\s+marks?)?\\]",
            },
            "subpart_pattern": {
                "primary": "^\\(([a-z])\\)",
                "alternatives": ["^\\(([ivx]+)\\)", "^([a-z])\\)"],
            },
        }

    # ========================================================================
    # PDF Type Detection Tests
    # ========================================================================

    def test_detect_question_paper_type(self, service: ExtractionService):
        """Test detecting question paper PDF type"""
        pdf_type = service.detect_pdf_type("9708_s22_qp_22.pdf")
        assert pdf_type == "question_paper"

    def test_detect_mark_scheme_type(self, service: ExtractionService):
        """Test detecting mark scheme PDF type"""
        pdf_type = service.detect_pdf_type("9708_s22_ms_22.pdf")
        assert pdf_type == "mark_scheme"

    def test_detect_unknown_type(self, service: ExtractionService):
        """Test detecting unknown PDF type"""
        pdf_type = service.detect_pdf_type("random_file.pdf")
        assert pdf_type == "unknown"

    def test_detect_examiner_report_type(self, service: ExtractionService):
        """Test detecting examiner report (unsupported)"""
        pdf_type = service.detect_pdf_type("9708_s22_er_22.pdf")
        assert pdf_type == "unknown"  # Not supported yet

    # ========================================================================
    # Question Paper Extraction Tests
    # ========================================================================

    def test_extract_question_paper_integration(
        self,
        service: ExtractionService,
        subject_id,
        economics_extraction_patterns,
    ):
        """
        Integration test: Extract questions from real Economics paper

        PREREQUISITES:
        - Question paper PDF downloaded to resources/subjects/9708/sample_papers/

        EXPECTED:
        - Question models created with correct metadata
        - All fields populated from parsed filename
        - Extraction patterns applied successfully
        """
        qp_path = Path("resources/subjects/9708/sample_papers/9708_s22_qp_22.pdf")

        if not qp_path.exists():
            pytest.skip(f"Question paper PDF not found: {qp_path}")

        questions = service.extract_question_paper(
            str(qp_path), subject_id, economics_extraction_patterns
        )

        # Verify questions extracted
        assert len(questions) > 0, "No questions extracted"

        # Verify first question structure
        first_q = questions[0]
        assert first_q.subject_id == subject_id
        assert first_q.source_paper == "9708_s22_qp_22"
        assert first_q.paper_number == 22
        assert first_q.year == 2022
        assert first_q.session == "MAY_JUNE"
        assert first_q.question_number >= 1
        assert first_q.max_marks > 0
        assert len(first_q.question_text) > 10

    def test_extract_question_paper_invalid_filename(
        self,
        service: ExtractionService,
        subject_id,
        economics_extraction_patterns,
    ):
        """Test extraction fails for invalid filename"""
        with pytest.raises(ExtractionError, match="Invalid Cambridge filename"):
            service.extract_question_paper(
                "invalid_file.pdf", subject_id, economics_extraction_patterns
            )

    def test_extract_question_paper_wrong_type(
        self,
        service: ExtractionService,
        subject_id,
        economics_extraction_patterns,
    ):
        """Test extraction fails for mark scheme (wrong type)"""
        ms_path = Path("resources/subjects/9708/sample_papers/9708_s22_ms_22.pdf")

        if not ms_path.exists():
            pytest.skip(f"Mark scheme PDF not found: {ms_path}")

        with pytest.raises(ExtractionError, match="Expected question paper"):
            service.extract_question_paper(
                str(ms_path), subject_id, economics_extraction_patterns
            )

    # ========================================================================
    # Mark Scheme Extraction Tests
    # ========================================================================

    def test_extract_mark_scheme_integration(
        self, service: ExtractionService, subject_id
    ):
        """
        Integration test: Extract mark scheme from real Economics PDF

        PREREQUISITES:
        - Mark scheme PDF downloaded to resources/subjects/9708/sample_papers/

        EXPECTED:
        - MarkScheme model created with raw text
        - Matching question paper filename identified
        - All metadata populated from parsed filename
        """
        ms_path = Path("resources/subjects/9708/sample_papers/9708_s22_ms_22.pdf")

        if not ms_path.exists():
            pytest.skip(f"Mark scheme PDF not found: {ms_path}")

        mark_scheme, qp_filename = service.extract_mark_scheme(str(ms_path), subject_id)

        # Verify mark scheme structure
        assert mark_scheme.subject_id == subject_id
        assert mark_scheme.source_paper == "9708_s22_ms_22"
        assert mark_scheme.paper_number == 22
        assert mark_scheme.year == 2022
        assert mark_scheme.session == "MAY_JUNE"
        assert len(mark_scheme.mark_scheme_text) > 1000
        assert mark_scheme.question_paper_filename == "9708_s22_qp_22.pdf"

        # Verify matching question paper filename
        assert qp_filename == "9708_s22_qp_22.pdf"

    def test_extract_mark_scheme_invalid_filename(
        self, service: ExtractionService, subject_id
    ):
        """Test extraction fails for invalid filename"""
        with pytest.raises(ExtractionError, match="Invalid Cambridge filename"):
            service.extract_mark_scheme("invalid_file.pdf", subject_id)

    def test_extract_mark_scheme_wrong_type(
        self, service: ExtractionService, subject_id
    ):
        """Test extraction fails for question paper (wrong type)"""
        qp_path = Path("resources/subjects/9708/sample_papers/9708_s22_qp_22.pdf")

        if not qp_path.exists():
            pytest.skip(f"Question paper PDF not found: {qp_path}")

        with pytest.raises(ExtractionError, match="Expected mark scheme"):
            service.extract_mark_scheme(str(qp_path), subject_id)

    # ========================================================================
    # Session Conversion Tests
    # ========================================================================

    def test_session_to_string_conversion(self, service: ExtractionService):
        """Test Session enum to string conversion"""
        from src.question_extractors.cambridge_parser import Session

        assert service._session_to_string(Session.MAY_JUNE) == "MAY_JUNE"
        assert service._session_to_string(Session.FEB_MARCH) == "FEB_MARCH"
        assert service._session_to_string(Session.OCT_NOV) == "OCT_NOV"
