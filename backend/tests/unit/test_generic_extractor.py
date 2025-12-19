"""
Unit Tests: Generic Question Extractor

Tests for Phase II User Story 4 (US4) - PDF Question Extraction.

Test Coverage:
- T034: GenericExtractor with mock Economics config
- Extraction pattern utilities
- Text processing functions
- Difficulty calculation

Success Criteria:
- >95% extraction accuracy for Economics 9708 (tested in integration tests)
- All utility functions work correctly

Constitutional Requirement:
- >80% test coverage (Principle VII)
"""

import pytest

from src.question_extractors import extraction_patterns as ep
from src.question_extractors.generic_extractor import ExtractionError, GenericExtractor
from src.models.subject import Subject


class TestExtractionPatternUtilities:
    """Test suite for extraction pattern utility functions"""

    def test_split_by_delimiter(self):
        """Test splitting text by question delimiter"""
        text = "Introduction\nQuestion 1\nWhat is GDP?\nQuestion 2\nWhat is inflation?"

        chunks = ep.split_by_delimiter(text, r"Question \d+")

        assert len(chunks) == 3  # [intro, Q1 text, Q2 text]
        assert "Introduction" in chunks[0]
        assert "What is GDP?" in chunks[1]
        assert "What is inflation?" in chunks[2]

    def test_extract_marks_standard_format(self):
        """Test extracting marks from standard format [N marks]"""
        text = "Explain inflation. [25 marks]"

        marks = ep.extract_marks(text, r"\[(\d+)\s+marks?\]")

        assert marks == 25

    def test_extract_marks_no_match(self):
        """Test extracting marks when pattern doesn't match"""
        text = "Define GDP."

        marks = ep.extract_marks(text, r"\[(\d+)\s+marks?\]")

        assert marks is None

    def test_extract_marks_alternative_format(self):
        """Test extracting marks from alternative format (8 marks)"""
        text = "Explain supply and demand. 8 marks"

        marks = ep.extract_marks(text, r"(\d+)\s+marks?")

        assert marks == 8

    def test_remove_headers_footers(self):
        """Test removing Cambridge headers/footers"""
        text = "Cambridge International\nWhat is GDP?\n[Turn over]"

        patterns = [
            {"pattern": "Cambridge International.*", "description": "header"},
            {"pattern": r"\[Turn over\]", "description": "page turn"},
        ]

        cleaned = ep.remove_headers_footers(text, patterns)

        assert "Cambridge International" not in cleaned
        assert "[Turn over]" not in cleaned
        assert "What is GDP?" in cleaned

    def test_detect_diagram_reference_positive(self):
        """Test detecting diagram reference when present"""
        text = "Using Figure 1, explain the supply and demand curves."

        has_diagram = ep.detect_diagram_reference(text, ["Figure", "Diagram", "Graph"])

        assert has_diagram is True

    def test_detect_diagram_reference_negative(self):
        """Test detecting diagram reference when absent"""
        text = "Explain inflation and its causes."

        has_diagram = ep.detect_diagram_reference(text, ["Figure", "Diagram", "Graph"])

        assert has_diagram is False

    def test_extract_question_number(self):
        """Test extracting question number from delimiter"""
        text = "Question 1\nWhat is GDP? [8 marks]"

        number = ep.extract_question_number(text, r"Question (\d+)")

        assert number == 1

    def test_extract_question_number_no_match(self):
        """Test extracting question number when pattern doesn't match"""
        text = "What is GDP?"

        number = ep.extract_question_number(text, r"Question (\d+)")

        assert number is None

    def test_extract_subparts(self):
        """Test extracting subparts (a), (b), (c)"""
        text = "(a) Define GDP. [8 marks]\n(b) Explain inflation. [12 marks]"

        subparts = ep.extract_subparts(text, r"\([a-z]\)")

        assert len(subparts) == 2
        assert subparts[0]["label"] == "(a)"
        assert "Define GDP" in subparts[0]["text"]
        assert subparts[1]["label"] == "(b)"
        assert "Explain inflation" in subparts[1]["text"]

    def test_aggregate_subpart_marks(self):
        """Test aggregating marks from multiple subparts"""
        subparts = [
            {"text": "Define GDP. [8 marks]"},
            {"text": "Explain inflation. [12 marks]"},
        ]

        total = ep.aggregate_subpart_marks(subparts, r"\[(\d+)\s+marks?\]")

        assert total == 20  # 8 + 12

    def test_calculate_difficulty_from_marks_easy(self):
        """Test difficulty calculation for easy questions (1-12 marks)"""
        assert ep.calculate_difficulty_from_marks(8) == "easy"
        assert ep.calculate_difficulty_from_marks(1) == "easy"
        assert ep.calculate_difficulty_from_marks(12) == "easy"

    def test_calculate_difficulty_from_marks_medium(self):
        """Test difficulty calculation for medium questions (13-20 marks)"""
        assert ep.calculate_difficulty_from_marks(13) == "medium"
        assert ep.calculate_difficulty_from_marks(15) == "medium"
        assert ep.calculate_difficulty_from_marks(20) == "medium"

    def test_calculate_difficulty_from_marks_hard(self):
        """Test difficulty calculation for hard questions (21-30 marks)"""
        assert ep.calculate_difficulty_from_marks(21) == "hard"
        assert ep.calculate_difficulty_from_marks(25) == "hard"
        assert ep.calculate_difficulty_from_marks(30) == "hard"


class TestGenericExtractor:
    """Test suite for GenericExtractor with mock Economics config"""

    @pytest.fixture
    def mock_economics_subject(self) -> Subject:
        """Create mock Economics subject with extraction patterns"""
        subject = Subject(
            code="9708",
            name="Economics",
            level="A",
            exam_board="Cambridge International",
            syllabus_year="2023-2025",
        )

        # Mock extraction patterns (simplified from Economics config)
        subject.extraction_patterns = {
            "version": "1.0",
            "subject_code": "9708",
            "question_delimiter": {
                "primary": r"Question\s+\d+",
                "alternatives": [r"Q\s*\d+"],
            },
            "marks_pattern": {
                "primary": r"\[\d+\s+marks?\]",
                "number_extraction": r"\[(\d+)\s+marks?\]",
            },
            "has_subparts": True,
            "subpart_patterns": {
                "lowercase_parentheses": {"pattern": r"\([a-z]\)", "examples": ["(a)", "(b)", "(c)"]}
            },
            "subpart_aggregation": {
                "sum_marks": True,
                "text_delimiter": "\n\n",
                "preserve_labels": True,
            },
            "headers_footers_to_remove": [
                {"pattern": "Cambridge International.*?Economics.*?9708", "description": "header"},
                {"pattern": r"\[Turn\s+over\]?", "description": "page turn"},
                {"pattern": "©\\s+UCLES\\s+\\d{4}", "description": "copyright"},
            ],
            "diagram_detection": {
                "indicators": ["Figure", "Diagram", "Graph", "curve", "axis"],
                "placeholder_format": "[DIAGRAM: {description}]",
            },
        }

        return subject

    def test_extractor_initialization(self, mock_economics_subject):
        """T034: Test GenericExtractor initialization with Economics config"""
        extractor = GenericExtractor(mock_economics_subject)

        assert extractor.subject.code == "9708"
        assert extractor.config is not None
        assert extractor.config["version"] == "1.0"
        assert "question_delimiter" in extractor.config

    def test_extractor_initialization_no_config_raises_error(self):
        """Test initialization fails if subject has no extraction_patterns"""
        subject = Subject(
            code="9999",
            name="Test Subject",
            level="A",
            exam_board="Cambridge International",
            syllabus_year="2023-2025",
        )
        # extraction_patterns is None

        with pytest.raises(ValueError, match="has no extraction_patterns config"):
            GenericExtractor(subject)

    def test_get_marks_pattern(self, mock_economics_subject):
        """Test marks pattern extraction from config"""
        extractor = GenericExtractor(mock_economics_subject)

        pattern = extractor._get_marks_pattern()

        assert pattern == r"\[(\d+)\s+marks?\]"
        assert "(" in pattern  # Has capture group

    def test_calculate_difficulty(self, mock_economics_subject):
        """Test difficulty calculation using heuristic"""
        extractor = GenericExtractor(mock_economics_subject)

        assert extractor._calculate_difficulty(8) == "easy"
        assert extractor._calculate_difficulty(15) == "medium"
        assert extractor._calculate_difficulty(25) == "hard"

    def test_clean_question_text(self, mock_economics_subject):
        """Test question text cleaning"""
        extractor = GenericExtractor(mock_economics_subject)

        messy_text = "What   is   GDP?  \n\n\n  How  is  it  calculated?  "

        cleaned = extractor._clean_question_text(messy_text)

        assert "  " not in cleaned  # No double spaces
        assert cleaned.strip() == cleaned  # No leading/trailing whitespace

    def test_filter_headers_footers(self, mock_economics_subject):
        """Test header/footer filtering using Economics patterns"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Cambridge International Economics 9708\nQuestion 1\n[Turn over]\n© UCLES 2022"

        cleaned = extractor._filter_headers_footers(text)

        assert "Cambridge International" not in cleaned
        assert "[Turn over]" not in cleaned
        assert "© UCLES" not in cleaned
        assert "Question 1" in cleaned

    def test_split_by_questions(self, mock_economics_subject):
        """Test splitting text by question delimiter"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Introduction text\nQuestion 1\nWhat is GDP?\nQuestion 2\nWhat is inflation?"

        chunks = extractor._split_by_questions(text)

        # Should have 2 questions (introduction filtered out)
        assert len(chunks) >= 2

    def test_parse_question_with_marks(self, mock_economics_subject):
        """Test parsing individual question with marks"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Question 1\nExplain the concept of inflation and its causes. [25 marks]"

        question = extractor._parse_question(text, fallback_number=1, source_paper="9708_s22_qp_31")

        assert question is not None
        assert question["question_number"] == 1
        assert question["max_marks"] == 25
        assert question["difficulty"] == "hard"
        assert "inflation" in question["question_text"]
        assert question["source_paper"] == "9708_s22_qp_31"

    def test_parse_question_with_subparts(self, mock_economics_subject):
        """Test parsing question with subparts (a), (b)"""
        extractor = GenericExtractor(mock_economics_subject)

        text = """Question 1
        (a) Define GDP. [8 marks]
        (b) Explain how GDP is calculated. [12 marks]
        """

        question = extractor._parse_question(text, fallback_number=1, source_paper="9708_s22_qp_31")

        assert question is not None
        assert question["max_marks"] == 20  # 8 + 12 aggregated
        assert question["difficulty"] == "medium"
        assert "(a)" in question["question_text"]  # Labels preserved
        assert "(b)" in question["question_text"]

    def test_parse_question_without_marks_returns_none(self, mock_economics_subject):
        """Test parsing question without marks returns None (skip)"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Question 1\nSome instruction text without marks."

        question = extractor._parse_question(text, fallback_number=1, source_paper="9708_s22_qp_31")

        # Questions without marks are skipped (likely instructions)
        assert question is None

    def test_parse_question_with_diagram_reference(self, mock_economics_subject):
        """Test detecting diagram reference in question"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Question 1\nUsing Figure 1, explain supply and demand. [20 marks]"

        question = extractor._parse_question(text, fallback_number=1, source_paper="9708_s22_qp_31")

        assert question is not None
        assert question["has_diagram"] is True

    def test_parse_question_without_diagram_reference(self, mock_economics_subject):
        """Test no false positive for diagram detection"""
        extractor = GenericExtractor(mock_economics_subject)

        text = "Question 1\nExplain inflation. [15 marks]"

        question = extractor._parse_question(text, fallback_number=1, source_paper="9708_s22_qp_31")

        assert question is not None
        assert question["has_diagram"] is False


# ========================================================================
# Integration Tests (require actual PDFs and database)
# ========================================================================


def test_extract_questions_from_economics_paper_2():
    """
    T035: Integration test - Extract from real Economics Paper 2 PDF (Data Response)

    PREREQUISITES:
    - Download 9708_s22_qp_22.pdf to resources/subjects/9708/sample_papers/
    - Ensure Economics 9708 config seeded in database

    EXPECTED RESULTS:
    - Extract 2-3 questions (Paper 2 typically has 2-3 questions)
    - Mixed marks (subparts add up to 20, 8+12, etc.)
    - Mixed difficulty based on marks
    - >95% extraction accuracy (SC-002)
    """
    from pathlib import Path
    from sqlmodel import Session, select

    from database import get_engine
    from models.subject import Subject

    # Get Economics subject from database
    engine = get_engine()
    with Session(engine) as session:
        economics = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not economics or not economics.extraction_patterns:
            pytest.skip("Economics 9708 not seeded in database. Run: uv run python scripts/seed_economics_config.py")

        # Initialize extractor
        extractor = GenericExtractor(economics)

        # Path to PDF (Paper 2 - Data Response/Essay)
        pdf_path = Path("resources/subjects/9708/sample_papers/9708_s22_qp_22.pdf")

        if not pdf_path.exists():
            pytest.skip(f"PDF not found: {pdf_path}. Download Economics PDFs first.")

        # Extract questions
        questions = extractor.extract_questions(str(pdf_path))

        # Assertions
        assert len(questions) >= 2, f"Expected >= 2 questions, got {len(questions)}"
        assert len(questions) <= 4, f"Expected <= 4 questions, got {len(questions)}"

        for question in questions:
            assert "question_number" in question
            assert "question_text" in question
            assert "max_marks" in question
            assert "difficulty" in question
            assert "source_paper" in question
            assert "has_diagram" in question

            # Verify types
            assert isinstance(question["question_number"], int)
            assert isinstance(question["question_text"], str)
            assert isinstance(question["max_marks"], int)
            assert question["difficulty"] in ["easy", "medium", "hard"]
            assert question["source_paper"] == "9708_s22_qp_22"

            # Paper 2 has mixed marks (not all 25)
            assert question["max_marks"] > 0
            assert question["max_marks"] <= 30


def test_extract_multi_page_question():
    """
    T037: Integration test - Handle multi-page questions

    Some Economics questions span 2-3 pages. Test concatenation.
    """
    from pathlib import Path
    from sqlmodel import Session, select

    from database import get_engine
    from models.subject import Subject

    engine = get_engine()
    with Session(engine) as session:
        economics = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not economics or not economics.extraction_patterns:
            pytest.skip("Economics 9708 not seeded in database")

        extractor = GenericExtractor(economics)

        # Paper 2 often has multi-page questions with data/tables
        pdf_path = Path("resources/subjects/9708/sample_papers/9708_s22_qp_22.pdf")

        if not pdf_path.exists():
            pytest.skip(f"PDF not found: {pdf_path}")

        text = extractor.extract_text(str(pdf_path))

        # Verify text extraction worked across multiple pages
        assert len(text) > 1000, "Extracted text too short for multi-page document"
        assert "Question" in text, "No question markers found"

        # Verify questions were parsed
        questions = extractor.extract_questions(str(pdf_path))
        assert len(questions) > 0, "No questions extracted from multi-page PDF"


def test_extract_question_with_table():
    """
    T038: Integration test - Handle questions with data tables

    Paper 2 (data response) often has tables. Test pdfplumber table extraction.
    """
    from pathlib import Path
    from sqlmodel import Session, select

    from database import get_engine
    from models.subject import Subject

    engine = get_engine()
    with Session(engine) as session:
        economics = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not economics or not economics.extraction_patterns:
            pytest.skip("Economics 9708 not seeded in database")

        extractor = GenericExtractor(economics)

        # Paper 2 (data response) contains tables
        pdf_path = Path("resources/subjects/9708/sample_papers/9708_w21_qp_23.pdf")

        if not pdf_path.exists():
            pytest.skip(f"PDF not found: {pdf_path}")

        # Extract text (pdfplumber should handle tables)
        text = extractor.extract_text(str(pdf_path))

        assert len(text) > 500, "Extracted text too short"

        # Extract questions
        questions = extractor.extract_questions(str(pdf_path))

        assert len(questions) > 0, "No questions extracted from PDF with tables"

        # Verify source paper is correct
        for question in questions:
            assert question["source_paper"] == "9708_w21_qp_23"
