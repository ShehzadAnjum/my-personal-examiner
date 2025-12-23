"""
MarkScheme Model

Represents mark schemes extracted from Cambridge past papers.
Global entity (not scoped to students) - all students see the same mark schemes.

Phase II: Stores raw text only (minimal extraction)
Phase III: Detailed parsing (levels, points, criteria)

Architecture Decision AD-005: Minimal Mark Scheme Extraction
- Phase II stores raw text for later parsing
- Phase III implements detailed marking criteria extraction
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class MarkScheme(SQLModel, table=True):
    """
    MarkScheme entity

    Represents a mark scheme extracted from Cambridge past papers.
    This is a global entity - not scoped to individual students.

    Attributes:
        id: Unique mark scheme identifier (UUID primary key)
        subject_id: Foreign key to parent subject
        source_paper: Source paper identifier (e.g., "9708_s22_ms_22")
        mark_scheme_text: Raw text extracted from PDF (Phase II minimal)
        question_paper_filename: Matching question paper filename
        paper_number: Paper number (e.g., 22, 31, 42)
        year: Exam year (e.g., 2022)
        session: Exam session (e.g., "MAY_JUNE", "FEB_MARCH", "OCT_NOV")
        file_path: Path to original mark scheme PDF
        created_at: Timestamp when mark scheme was extracted
        updated_at: Timestamp of last update

    Examples:
        >>> mark_scheme = MarkScheme(
        ...     subject_id=economics_subject_id,
        ...     source_paper="9708_s22_ms_22",
        ...     mark_scheme_text="<full extracted text>",
        ...     question_paper_filename="9708_s22_qp_22.pdf",
        ...     paper_number=22,
        ...     year=2022,
        ...     session="MAY_JUNE"
        ... )

    Constitutional Compliance:
        - Principle VIII: Every question needs verified mark scheme
        - AD-005: Phase II stores raw text, Phase III parses criteria
        - NFR-005: Question bank must include marking criteria
    """

    __tablename__ = "mark_schemes"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Foreign Key to Subject
    subject_id: UUID = Field(
        foreign_key="subjects.id",
        nullable=False,
        index=True,
        description="Parent subject ID",
    )

    # Source Metadata
    source_paper: str = Field(
        nullable=False,
        unique=True,
        index=True,
        max_length=50,
        description="Source paper identifier (e.g., '9708_s22_ms_22')",
    )

    # Phase II: Raw Text Storage (Minimal Extraction)
    mark_scheme_text: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Raw text extracted from mark scheme PDF",
    )

    # Matching Question Paper
    question_paper_filename: str = Field(
        nullable=False,
        max_length=100,
        description="Matching question paper filename (e.g., '9708_s22_qp_22.pdf')",
    )

    # Exam Metadata
    paper_number: int = Field(
        nullable=False,
        index=True,
        description="Paper number (e.g., 22, 31, 42)",
    )

    year: int = Field(
        nullable=False,
        index=True,
        ge=2000,
        description="Exam year (e.g., 2022)",
    )

    session: str = Field(
        nullable=False,
        index=True,
        max_length=20,
        description="Exam session: 'MAY_JUNE', 'FEB_MARCH', 'OCT_NOV'",
    )

    # File Storage
    file_path: str | None = Field(
        default=None,
        max_length=500,
        description="Path to original mark scheme PDF",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when mark scheme was extracted",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp of last update",
    )

    # Validation methods
    def is_valid_session(self) -> bool:
        """
        Validate session

        Returns:
            bool: True if session is valid Cambridge session
        """
        return self.session in ("MAY_JUNE", "FEB_MARCH", "OCT_NOV")

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<MarkScheme(source={self.source_paper}, year={self.year})>"
