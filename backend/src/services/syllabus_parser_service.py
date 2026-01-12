"""
Syllabus Parser Service for Cambridge International PDF Extraction.

Feature: Admin-First Topic Generation
Created: 2026-01-05

Parses Cambridge syllabus PDFs to extract topic codes, descriptions, and learning outcomes.
Uses hybrid approach: auto-extract with confidence scores for admin review.

Constitutional Compliance:
- Principle I: Extract ONLY from uploaded syllabus (no LLM invention)
- Principle III: Strict Cambridge format validation
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from src.services.pdf_extraction_service import extract_pdf_text, get_pdf_metadata


@dataclass
class ExtractedTopic:
    """
    Represents a topic extracted from Cambridge syllabus PDF.

    Attributes:
        code: Topic code (e.g., "1.1.1", "2.3")
        title: Topic title
        description: Full description from syllabus
        learning_outcomes: List of learning outcome bullet points
        assessment_info: Which papers, marks allocation
        confidence: 0-1 confidence score for admin review
        parent_section: Parent section code (e.g., "1.1" for topic "1.1.1")
        source_page: Page number where topic was found
    """
    code: str
    title: str
    description: str
    learning_outcomes: list[str] = field(default_factory=list)
    assessment_info: str = ""
    confidence: float = 1.0
    parent_section: Optional[str] = None
    source_page: Optional[int] = None


@dataclass
class SyllabusParseResult:
    """
    Result of syllabus PDF parsing.

    Attributes:
        success: Whether parsing succeeded
        topics: List of extracted topics
        metadata: PDF metadata (title, page count, etc.)
        subject_code: Detected subject code (e.g., "9708")
        subject_name: Detected subject name (e.g., "Economics")
        syllabus_year: Detected syllabus year range (e.g., "2023-2025")
        error_message: Error details if parsing failed
        warnings: List of warnings during parsing
    """
    success: bool
    topics: list[ExtractedTopic] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    subject_code: str = ""
    subject_name: str = ""
    syllabus_year: str = ""
    error_message: str = ""
    warnings: list[str] = field(default_factory=list)


# Cambridge syllabus section patterns
SECTION_PATTERNS = [
    # Pattern: "1.1 Topic Title" or "1.1.1 Topic Title"
    re.compile(r'^(\d+(?:\.\d+)+)\s+(.+)$', re.MULTILINE),
    # Pattern with leading bullet/dash
    re.compile(r'^[•\-]\s*(\d+(?:\.\d+)+)\s+(.+)$', re.MULTILINE),
]

# Learning outcome patterns (bullet points under sections)
LEARNING_OUTCOME_PATTERNS = [
    # Bullet patterns
    re.compile(r'^[•\-\*]\s*(.+)$', re.MULTILINE),
    # Numbered list
    re.compile(r'^\d+[.)\]]\s*(.+)$', re.MULTILINE),
    # Lettered list
    re.compile(r'^[a-z][.)\]]\s*(.+)$', re.MULTILINE),
]

# Subject code pattern (Cambridge format: 4 digits)
SUBJECT_CODE_PATTERN = re.compile(r'\b(\d{4})\b')

# Year pattern for syllabus version
YEAR_PATTERN = re.compile(r'(\d{4})[–\-](\d{4})')


def parse_syllabus_pdf(file_path: str) -> SyllabusParseResult:
    """
    Parse Cambridge syllabus PDF and extract topics.

    Uses two-stage approach:
    1. Extract text from PDF
    2. Parse text to identify sections, topics, learning outcomes

    Args:
        file_path: Absolute path to syllabus PDF

    Returns:
        SyllabusParseResult with extracted topics and metadata

    Example:
        >>> result = parse_syllabus_pdf("/path/to/9708_y25_sy.pdf")
        >>> if result.success:
        ...     for topic in result.topics:
        ...         print(f"{topic.code}: {topic.title} [{topic.confidence:.0%}]")
    """
    try:
        # Stage 1: Extract PDF text
        extraction_result = extract_pdf_text(file_path)
        text = extraction_result['text']

        # Get PDF metadata
        metadata = get_pdf_metadata(file_path)

        # Detect subject code and name
        subject_code = _detect_subject_code(text)
        subject_name = _detect_subject_name(text)
        syllabus_year = _detect_syllabus_year(text)

        # Stage 2: Parse text to extract topics
        topics = _extract_topics_from_text(text)

        # Calculate confidence scores
        topics = _calculate_confidence_scores(topics)

        # Validate topics
        warnings = _validate_topics(topics)

        return SyllabusParseResult(
            success=True,
            topics=topics,
            metadata=metadata,
            subject_code=subject_code,
            subject_name=subject_name,
            syllabus_year=syllabus_year,
            warnings=warnings,
        )

    except FileNotFoundError as e:
        return SyllabusParseResult(
            success=False,
            error_message=f"Syllabus PDF not found: {str(e)}",
        )
    except Exception as e:
        return SyllabusParseResult(
            success=False,
            error_message=f"Failed to parse syllabus: {str(e)}",
        )


def _detect_subject_code(text: str) -> str:
    """Detect Cambridge subject code from syllabus text."""
    # Look for 4-digit code near beginning of document
    first_pages = text[:5000]  # Check first ~5000 chars

    # Common patterns: "9708", "Cambridge International AS and A Level Economics (9708)"
    match = SUBJECT_CODE_PATTERN.search(first_pages)
    if match:
        return match.group(1)

    return ""


def _detect_subject_name(text: str) -> str:
    """Detect subject name from syllabus text."""
    first_pages = text[:3000]

    # Common Cambridge subjects
    subjects = [
        "Economics", "Accounting", "Business", "Mathematics",
        "Physics", "Chemistry", "Biology", "English", "History",
        "Geography", "Computer Science", "Psychology", "Sociology"
    ]

    for subject in subjects:
        if subject.lower() in first_pages.lower():
            return subject

    return ""


def _detect_syllabus_year(text: str) -> str:
    """Detect syllabus year range from text."""
    first_pages = text[:3000]

    match = YEAR_PATTERN.search(first_pages)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    return ""


def _extract_topics_from_text(text: str) -> list[ExtractedTopic]:
    """
    Extract topics from syllabus text.

    Identifies section headers (numbered like 1.1, 2.3.1) and
    extracts content under each section.
    """
    topics = []
    lines = text.split('\n')

    current_topic: Optional[ExtractedTopic] = None
    current_outcomes: list[str] = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check for section header
        section_match = None
        for pattern in SECTION_PATTERNS:
            section_match = pattern.match(line)
            if section_match:
                break

        if section_match:
            # Save previous topic
            if current_topic:
                current_topic.learning_outcomes = current_outcomes
                topics.append(current_topic)

            # Start new topic
            code = section_match.group(1)
            title = section_match.group(2).strip()

            # Determine parent section
            parts = code.split('.')
            parent = '.'.join(parts[:-1]) if len(parts) > 1 else None

            current_topic = ExtractedTopic(
                code=code,
                title=title,
                description=title,  # Will be expanded
                parent_section=parent,
                source_page=i // 50 + 1,  # Rough page estimate
            )
            current_outcomes = []

        elif current_topic:
            # Check for learning outcome bullet
            outcome_match = None
            for pattern in LEARNING_OUTCOME_PATTERNS:
                outcome_match = pattern.match(line)
                if outcome_match:
                    break

            if outcome_match:
                outcome = outcome_match.group(1).strip()
                if outcome and len(outcome) > 5:  # Filter noise
                    current_outcomes.append(outcome)
            elif len(line) > 20:
                # Likely a description line
                if current_topic.description == current_topic.title:
                    current_topic.description = line
                else:
                    current_topic.description += " " + line

    # Don't forget last topic
    if current_topic:
        current_topic.learning_outcomes = current_outcomes
        topics.append(current_topic)

    return topics


def _calculate_confidence_scores(topics: list[ExtractedTopic]) -> list[ExtractedTopic]:
    """
    Calculate confidence scores for extracted topics.

    Higher confidence when:
    - Code follows standard format (X.X.X)
    - Has meaningful title (>5 chars, not just numbers)
    - Has learning outcomes
    - Description differs from title
    """
    for topic in topics:
        score = 1.0

        # Code format check
        code_parts = topic.code.split('.')
        if len(code_parts) < 2:
            score -= 0.2
        if not all(part.isdigit() for part in code_parts):
            score -= 0.1

        # Title quality
        if len(topic.title) < 5:
            score -= 0.3
        if topic.title.replace(' ', '').isdigit():
            score -= 0.4

        # Learning outcomes
        if len(topic.learning_outcomes) == 0:
            score -= 0.15
        elif len(topic.learning_outcomes) > 5:
            score += 0.05

        # Description quality
        if topic.description == topic.title:
            score -= 0.1

        topic.confidence = max(0.0, min(1.0, score))

    return topics


def _validate_topics(topics: list[ExtractedTopic]) -> list[str]:
    """
    Validate extracted topics and return warnings.
    """
    warnings = []

    if len(topics) == 0:
        warnings.append("No topics found. PDF may not be a valid Cambridge syllabus.")
    elif len(topics) < 10:
        warnings.append(f"Only {len(topics)} topics found. Syllabus may be partially parsed.")

    # Check for low-confidence topics
    low_confidence = [t for t in topics if t.confidence < 0.7]
    if low_confidence:
        warnings.append(
            f"{len(low_confidence)} topics have low confidence (<70%). "
            "Admin review recommended."
        )

    # Check for duplicate codes
    codes = [t.code for t in topics]
    duplicates = set(c for c in codes if codes.count(c) > 1)
    if duplicates:
        warnings.append(f"Duplicate topic codes found: {', '.join(duplicates)}")

    return warnings


def validate_cambridge_format(topics: list[ExtractedTopic]) -> tuple[bool, list[str]]:
    """
    Validate that topics follow Cambridge syllabus format.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    for topic in topics:
        # Check code format
        if not topic.code:
            issues.append(f"Topic missing code: {topic.title[:30]}")
        elif not re.match(r'^\d+(\.\d+)*$', topic.code):
            issues.append(f"Invalid code format: {topic.code}")

        # Check title
        if not topic.title or len(topic.title) < 3:
            issues.append(f"Topic {topic.code} has invalid title")

    return len(issues) == 0, issues
