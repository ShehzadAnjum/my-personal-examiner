"""
LLM Key Service

Handles encryption, decryption, and management of student LLM API keys.

Feature: 006-resource-bank
Security Requirements:
- API keys encrypted at rest using Fernet (AES-256)
- Keys NEVER logged or exposed in responses
- Only last 4 characters shown as hint
- ENCRYPTION_KEY must be set in environment
"""

import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.models.enums import LLMProvider
from src.models.student_llm_config import StudentLLMConfig


class EncryptionKeyNotSetError(Exception):
    """Raised when ENCRYPTION_KEY environment variable is not set"""

    pass


class InvalidEncryptionKeyError(Exception):
    """Raised when ENCRYPTION_KEY is invalid"""

    pass


class DecryptionError(Exception):
    """Raised when decryption fails (corrupted or wrong key)"""

    pass


class ConfigAlreadyExistsError(Exception):
    """Raised when trying to create duplicate config for student+provider"""

    pass


class ConfigNotFoundError(Exception):
    """Raised when config doesn't exist for student+provider"""

    pass


def _get_fernet() -> Fernet:
    """
    Get Fernet instance for encryption/decryption.

    Uses ENCRYPTION_KEY from environment.

    Returns:
        Fernet: Encryption instance

    Raises:
        EncryptionKeyNotSetError: If ENCRYPTION_KEY not set
        InvalidEncryptionKeyError: If ENCRYPTION_KEY is invalid format

    Security:
        - Key must be 32 url-safe base64-encoded bytes
        - Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    encryption_key = os.environ.get("ENCRYPTION_KEY")

    if not encryption_key:
        raise EncryptionKeyNotSetError(
            "ENCRYPTION_KEY environment variable not set. "
            "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    try:
        return Fernet(encryption_key.encode())
    except (ValueError, TypeError) as e:
        raise InvalidEncryptionKeyError(
            f"Invalid ENCRYPTION_KEY format: {e}. "
            "Key must be 32 url-safe base64-encoded bytes."
        ) from e


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage.

    Args:
        api_key: Plain text API key

    Returns:
        str: Encrypted key (url-safe base64)

    Raises:
        EncryptionKeyNotSetError: If ENCRYPTION_KEY not set
        InvalidEncryptionKeyError: If ENCRYPTION_KEY is invalid

    Security:
        - Uses Fernet (AES-256-CBC + HMAC-SHA256)
        - Includes timestamp for key rotation support
    """
    fernet = _get_fernet()
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key for use.

    Args:
        encrypted_key: Encrypted key from database

    Returns:
        str: Decrypted plain text API key

    Raises:
        EncryptionKeyNotSetError: If ENCRYPTION_KEY not set
        InvalidEncryptionKeyError: If ENCRYPTION_KEY is invalid
        DecryptionError: If decryption fails

    Security:
        - Decrypted key should NEVER be logged
        - Use only for LLM API calls, not for display
    """
    fernet = _get_fernet()
    try:
        return fernet.decrypt(encrypted_key.encode()).decode()
    except InvalidToken as e:
        raise DecryptionError(
            "Failed to decrypt API key. Key may be corrupted or encryption key changed."
        ) from e


def get_key_hint(api_key: str) -> str:
    """
    Get masked hint for API key display.

    Args:
        api_key: The plain text API key

    Returns:
        str: Masked key like "****...****abcd"

    Security:
        - Only shows last 4 characters
        - Safe to log and display in responses
    """
    if len(api_key) <= 4:
        return "*" * len(api_key)
    return f"****...****{api_key[-4:]}"


def save_api_key(
    session: Session,
    student_id: UUID,
    provider: LLMProvider,
    api_key: str,
) -> StudentLLMConfig:
    """
    Save or update an encrypted API key for a student.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)
        provider: LLM provider enum
        api_key: Plain text API key to encrypt

    Returns:
        StudentLLMConfig: Created or updated config

    Raises:
        EncryptionKeyNotSetError: If ENCRYPTION_KEY not set

    Multi-Tenant:
        - Config is scoped to student_id (Principle V)
    """
    # Encrypt the API key
    encrypted_key = encrypt_api_key(api_key)

    # Check if config already exists
    existing = get_config_by_provider(session, student_id, provider)

    if existing:
        # Update existing config
        existing.api_key_encrypted = encrypted_key
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.flush()
        return existing

    # Create new config
    config = StudentLLMConfig(
        student_id=student_id,
        provider=provider,
        api_key_encrypted=encrypted_key,
        is_active=True,
        usage_this_month=0,
    )

    session.add(config)
    session.flush()
    return config


def get_config_by_provider(
    session: Session,
    student_id: UUID,
    provider: LLMProvider,
) -> Optional[StudentLLMConfig]:
    """
    Get LLM config for a student and provider.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)
        provider: LLM provider enum

    Returns:
        StudentLLMConfig | None: Config if found

    Multi-Tenant:
        - ALWAYS filters by student_id (Principle V)
    """
    statement = select(StudentLLMConfig).where(
        StudentLLMConfig.student_id == student_id,
        StudentLLMConfig.provider == provider,
    )
    return session.exec(statement).first()


def get_all_configs(
    session: Session,
    student_id: UUID,
) -> list[StudentLLMConfig]:
    """
    Get all LLM configs for a student.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)

    Returns:
        list[StudentLLMConfig]: All configs for student

    Multi-Tenant:
        - ALWAYS filters by student_id (Principle V)
    """
    statement = select(StudentLLMConfig).where(
        StudentLLMConfig.student_id == student_id,
    )
    return list(session.exec(statement).all())


def get_active_config(
    session: Session,
    student_id: UUID,
    provider: LLMProvider,
) -> Optional[StudentLLMConfig]:
    """
    Get active LLM config for a student and provider.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)
        provider: LLM provider enum

    Returns:
        StudentLLMConfig | None: Active config if found

    Multi-Tenant:
        - ALWAYS filters by student_id (Principle V)
    """
    statement = select(StudentLLMConfig).where(
        StudentLLMConfig.student_id == student_id,
        StudentLLMConfig.provider == provider,
        StudentLLMConfig.is_active == True,  # noqa: E712
    )
    return session.exec(statement).first()


def delete_api_key(
    session: Session,
    student_id: UUID,
    provider: LLMProvider,
) -> bool:
    """
    Delete an API key for a student and provider.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)
        provider: LLM provider enum

    Returns:
        bool: True if deleted, False if not found

    Multi-Tenant:
        - ALWAYS filters by student_id (Principle V)
    """
    config = get_config_by_provider(session, student_id, provider)
    if config:
        session.delete(config)
        session.flush()
        return True
    return False


def get_api_key_status(
    session: Session,
    student_id: UUID,
) -> list[dict]:
    """
    Get status of all LLM providers for a student.

    Returns config status without exposing actual keys.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)

    Returns:
        list[dict]: Status for each provider with:
            - provider: Provider name
            - is_configured: Whether key exists
            - key_hint: Last 4 chars (if configured)
            - is_active: Whether key is active
            - usage_this_month: Token usage

    Security:
        - NEVER returns actual API keys
        - Only masked hints for verification
    """
    configs = get_all_configs(session, student_id)
    config_map = {c.provider: c for c in configs}

    result = []
    for provider in LLMProvider:
        config = config_map.get(provider)
        if config:
            # Get key hint (need to decrypt first)
            try:
                decrypted = decrypt_api_key(config.api_key_encrypted)
                hint = get_key_hint(decrypted)
            except DecryptionError:
                hint = "****...****ERROR"

            result.append(
                {
                    "provider": provider.value,
                    "is_configured": True,
                    "key_hint": hint,
                    "is_active": config.is_active,
                    "usage_this_month": config.usage_this_month,
                }
            )
        else:
            result.append(
                {
                    "provider": provider.value,
                    "is_configured": False,
                    "key_hint": None,
                    "is_active": False,
                    "usage_this_month": 0,
                }
            )

    return result


def add_usage(
    session: Session,
    student_id: UUID,
    provider: LLMProvider,
    tokens: int,
) -> None:
    """
    Add token usage to a student's config.

    Args:
        session: Database session
        student_id: Student UUID (multi-tenant key)
        provider: LLM provider enum
        tokens: Number of tokens to add

    Multi-Tenant:
        - ALWAYS filters by student_id (Principle V)
    """
    config = get_config_by_provider(session, student_id, provider)
    if config and tokens > 0:
        config.add_usage(tokens)
        session.add(config)
        session.flush()
