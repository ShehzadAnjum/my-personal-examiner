"""
StudentLLMConfig Model

Encrypted storage for student's own LLM API keys.

Feature: 006-resource-bank
Constitutional Requirements:
- API keys MUST be AES-256 encrypted at rest - Security
- Keys never logged or exposed in responses
- Multi-tenant isolation by student_id - Principle V
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel

from src.models.enums import LLMProvider


class StudentLLMConfig(SQLModel, table=True):
    """
    StudentLLMConfig entity

    Encrypted storage for student's own LLM API keys.
    Enables students to generate personalized content using their own API keys.

    Attributes:
        id: Unique identifier
        student_id: Owner of this config (multi-tenant key)
        provider: LLM provider (openai, anthropic, google)
        api_key_encrypted: AES-256-GCM encrypted API key
        is_active: Whether this key is currently active
        created_at: When key was added
        updated_at: Last update timestamp
        usage_this_month: Token count this billing period
        usage_reset_at: When usage counter resets

    Security Requirements:
        - api_key_encrypted: NEVER store plaintext, NEVER log
        - Responses show only last 4 characters as hint
        - One active key per provider per student

    Constitutional Compliance:
        - Principle V: Filter by student_id for multi-tenant isolation
        - Security: Encrypted storage with Fernet (AES-256)
    """

    __tablename__ = "student_llm_configs"
    __table_args__ = (
        # Unique constraint: one config per (student_id, provider)
        Index(
            "idx_llmconfig_student_provider",
            "student_id",
            "provider",
            unique=True,
        ),
        # Index for active keys per student
        Index(
            "idx_llmconfig_student_active",
            "student_id",
            postgresql_where="is_active = true",
        ),
        # Constraints
        CheckConstraint(
            "usage_this_month >= 0",
            name="ck_llmconfig_usage_positive",
        ),
    )

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    # Multi-Tenant Isolation Key (CRITICAL)
    student_id: UUID = Field(
        foreign_key="students.id",
        nullable=False,
        index=True,
        description="Owner of this config - ALL queries MUST filter by this",
    )

    # Provider
    provider: LLMProvider = Field(
        nullable=False,
        description="LLM provider (openai, anthropic, google)",
    )

    # Encrypted API Key (SECURITY CRITICAL)
    api_key_encrypted: str = Field(
        nullable=False,
        max_length=512,
        description="AES-256-GCM encrypted API key - NEVER log or expose",
    )

    # Status
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Whether this key is currently active",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When key was added",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )

    # Usage Tracking
    usage_this_month: int = Field(
        default=0,
        nullable=False,
        description="Token count this billing period",
    )

    usage_reset_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="When usage counter resets (start of next month)",
    )

    def add_usage(self, tokens: int) -> None:
        """
        Add token usage to this month's counter.

        Args:
            tokens: Number of tokens to add
        """
        if tokens > 0:
            self.usage_this_month += tokens
            self.updated_at = datetime.utcnow()

    def reset_usage(self) -> None:
        """Reset monthly usage counter."""
        self.usage_this_month = 0
        self.usage_reset_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate this API key."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate this API key."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def get_key_hint(self, decrypted_key: str) -> str:
        """
        Get masked key hint for display (last 4 characters only).

        Args:
            decrypted_key: The decrypted API key

        Returns:
            str: Masked key like "****...****1234"

        Note:
            This method requires the decrypted key to be passed in.
            The encryption/decryption is handled by llm_key_service.
        """
        if len(decrypted_key) <= 4:
            return "*" * len(decrypted_key)
        return f"****...****{decrypted_key[-4:]}"

    def __repr__(self) -> str:
        """String representation for debugging - NEVER include key"""
        return (
            f"<StudentLLMConfig(student_id={self.student_id}, "
            f"provider={self.provider}, is_active={self.is_active})>"
        )
