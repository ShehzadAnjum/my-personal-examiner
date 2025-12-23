"""
Question Extractors Package

Generic PDF question extraction framework for Phase II Question Bank.

Modules:
- cambridge_parser: Parse Cambridge International PDF filenames
- generic_extractor: Subject config-driven question extraction
- mark_scheme_extractor: Extract marking criteria from mark schemes (Phase II: minimal text extraction)
- extraction_patterns: Pattern matching utilities

Architecture Decision AD-002: Generic Extraction Framework
- Config-driven (not subject-specific)
- Reads extraction patterns from subject.extraction_patterns JSONB
- Economics 9708 serves as reference implementation

Architecture Decision AD-005: Minimal Mark Scheme Extraction
- Phase II: Store raw mark scheme text only
- Phase III: Parse detailed marking criteria (levels, points, rubrics)
"""

from src.question_extractors.cambridge_parser import (
    CambridgeFilenameParser,
    InvalidFilenameFormatError,
    ParsedFilename,
)
from src.question_extractors.generic_extractor import ExtractionError, GenericExtractor
from src.question_extractors.mark_scheme_extractor import MarkSchemeExtractor

__all__ = [
    "CambridgeFilenameParser",
    "InvalidFilenameFormatError",
    "ParsedFilename",
    "GenericExtractor",
    "ExtractionError",
    "MarkSchemeExtractor",
]
