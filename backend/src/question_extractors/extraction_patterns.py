"""
Extraction Pattern Utilities

Pattern matching and text processing utilities for PDF question extraction.

These utilities are used by GenericExtractor to:
- Split text by question delimiters
- Extract marks notation
- Filter headers/footers
- Detect diagrams/tables

Architecture Decision AD-002: Generic Extraction Framework
- Pattern-agnostic utilities (work with any regex patterns)
- Subject-specific patterns provided by subject.extraction_patterns JSONB
"""

import re
from typing import Any


def split_by_delimiter(text: str, delimiter_pattern: str, flags: int = re.MULTILINE) -> list[str]:
    """
    Split text by delimiter pattern (e.g., "Question 1", "Question 2")

    Args:
        text: Full PDF text to split
        delimiter_pattern: Regex pattern for question delimiter
        flags: Regex flags (default: re.MULTILINE)

    Returns:
        list[str]: Text chunks split by delimiter (first chunk may be header/intro)

    Examples:
        >>> text = "Introduction\\nQuestion 1\\nWhat is GDP?\\nQuestion 2\\nWhat is inflation?"
        >>> chunks = split_by_delimiter(text, r"Question \\d+")
        >>> len(chunks)
        3  # [intro, Q1 text, Q2 text]
    """
    split_result = re.split(delimiter_pattern, text, flags=flags)

    # If delimiter pattern has capturing group, re.split returns alternating chunks:
    # [header, delimiter1, text1, delimiter2, text2, ...]
    # We need to merge delimiter + text pairs
    if len(split_result) > 2 and all(len(chunk) < 10 for chunk in split_result[1::2]):
        # Looks like alternating pattern (delimiters are short chunks)
        merged = [split_result[0]]  # Keep header
        for i in range(1, len(split_result) - 1, 2):
            # Merge delimiter + text pairs
            merged.append(split_result[i] + split_result[i + 1])
        return merged

    return split_result


def extract_marks(text: str, marks_pattern: str) -> int | None:
    """
    Extract marks value from text using pattern

    Args:
        text: Question text containing marks notation
        marks_pattern: Regex pattern with capture group for number (e.g., "\\[(\\d+)\\s+marks?\\]")

    Returns:
        int | None: Marks value if found, None otherwise

    Examples:
        >>> extract_marks("Explain inflation. [25 marks]", r"\\[(\\d+)\\s+marks?\\]")
        25
        >>> extract_marks("Define GDP.", r"\\[(\\d+)\\s+marks?\\]")
        None
    """
    match = re.search(marks_pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def remove_headers_footers(text: str, patterns: list[dict[str, Any]]) -> str:
    """
    Remove headers, footers, and page metadata from text

    Args:
        text: Question text with headers/footers
        patterns: List of pattern dicts with 'pattern' and 'description' keys

    Returns:
        str: Cleaned text with headers/footers removed

    Examples:
        >>> text = "Cambridge International\\nWhat is GDP?\\n[Turn over]"
        >>> patterns = [
        ...     {"pattern": "Cambridge International.*", "description": "header"},
        ...     {"pattern": "\\[Turn over\\]", "description": "page turn"}
        ... ]
        >>> remove_headers_footers(text, patterns)
        'What is GDP?'
    """
    cleaned = text

    for pattern_dict in patterns:
        pattern = pattern_dict.get("pattern", "")
        if pattern:
            cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE | re.IGNORECASE)

    # Remove excessive whitespace
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)  # Collapse multiple blank lines
    cleaned = cleaned.strip()

    return cleaned


def detect_diagram_reference(text: str, indicators: list[str]) -> bool:
    """
    Detect if text contains diagram/figure references

    Args:
        text: Question text to check
        indicators: List of indicator strings (e.g., ["Figure", "Diagram", "Graph"])

    Returns:
        bool: True if diagram reference detected

    Examples:
        >>> detect_diagram_reference("Using Figure 1, explain...", ["Figure", "Diagram"])
        True
        >>> detect_diagram_reference("Explain inflation.", ["Figure", "Diagram"])
        False
    """
    for indicator in indicators:
        if re.search(indicator, text, re.IGNORECASE):
            return True
    return False


def extract_question_number(text: str, delimiter_pattern: str) -> int | None:
    """
    Extract question number from delimiter match

    Args:
        text: Text chunk starting with question delimiter
        delimiter_pattern: Regex pattern for question delimiter (e.g., "Question \\d+")

    Returns:
        int | None: Question number if found, None otherwise

    Examples:
        >>> extract_question_number("Question 1\\nWhat is GDP?", r"Question (\\d+)")
        1
        >>> extract_question_number("What is GDP?", r"Question (\\d+)")
        None
    """
    # Add capture group if not present
    if "(" not in delimiter_pattern:
        delimiter_pattern = delimiter_pattern.replace(r"\d+", r"(\d+)")

    match = re.search(delimiter_pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except (IndexError, ValueError):
            return None
    return None


def extract_subparts(text: str, subpart_pattern: str) -> list[dict[str, Any]]:
    """
    Extract subparts from question text (e.g., (a), (b), (c))

    Args:
        text: Question text with subparts
        subpart_pattern: Regex pattern for subparts (e.g., "\\([a-z]\\)")

    Returns:
        list[dict]: List of subpart dicts with 'label' and 'text' keys

    Examples:
        >>> text = "(a) Define GDP. [8 marks]\\n(b) Explain inflation. [12 marks]"
        >>> subparts = extract_subparts(text, r"\\([a-z]\\)")
        >>> len(subparts)
        2
        >>> subparts[0]['label']
        '(a)'
    """
    subparts = []
    matches = list(re.finditer(subpart_pattern, text, re.IGNORECASE))

    for i, match in enumerate(matches):
        label = match.group(0)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        subpart_text = text[start:end].strip()

        subparts.append({"label": label, "text": subpart_text, "start": start, "end": end})

    return subparts


def aggregate_subpart_marks(subparts: list[dict[str, Any]], marks_pattern: str) -> int:
    """
    Calculate total marks from subparts

    Args:
        subparts: List of subpart dicts (from extract_subparts)
        marks_pattern: Regex pattern for extracting marks

    Returns:
        int: Total marks across all subparts

    Examples:
        >>> subparts = [
        ...     {"text": "Define GDP. [8 marks]"},
        ...     {"text": "Explain inflation. [12 marks]"}
        ... ]
        >>> aggregate_subpart_marks(subparts, r"\\[(\\d+)\\s+marks?\\]")
        20
    """
    total = 0

    for subpart in subparts:
        subpart_text = subpart.get("text", "")
        marks = extract_marks(subpart_text, marks_pattern)
        if marks:
            total += marks

    return total


def calculate_difficulty_from_marks(marks: int) -> str:
    """
    Calculate question difficulty using marks-based heuristic

    Heuristic (from research.md):
    - 1-12 marks: easy
    - 13-20 marks: medium
    - 21-30 marks: hard

    This is Phase II approach. Phase III will use historical performance data.

    Args:
        marks: Maximum marks for question

    Returns:
        str: Difficulty level ("easy", "medium", "hard")

    Examples:
        >>> calculate_difficulty_from_marks(8)
        'easy'
        >>> calculate_difficulty_from_marks(15)
        'medium'
        >>> calculate_difficulty_from_marks(25)
        'hard'
    """
    if marks <= 12:
        return "easy"
    elif marks <= 20:
        return "medium"
    else:
        return "hard"
