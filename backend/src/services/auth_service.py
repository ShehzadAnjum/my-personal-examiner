"""
Authentication Service

Handles password hashing, verification, and JWT token generation.

Constitutional Requirements:
- Passwords MUST be bcrypt-hashed (work factor 12) - Principle I
- JWT tokens expire after 24 hours - FR-003
- Passwords never stored in plain text - Principle I
"""

from passlib.context import CryptContext

# Password hashing context (bcrypt with work factor 12)
# Constitutional requirement: Work factor 12 balances security and performance
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Work factor 12 (constitutional requirement)
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt

    Uses bcrypt with work factor 12 (constitutional requirement).
    This function MUST be used for all password storage.

    Args:
        plain_password: Plain text password from user input

    Returns:
        str: Bcrypt-hashed password (suitable for database storage)

    Examples:
        >>> hashed = hash_password("SecurePass123")
        >>> hashed.startswith("$2b$12$")  # Bcrypt format with work factor 12
        True

    Constitutional Compliance:
        - Principle I: Password hashing mandatory (never store plain text)
        - FR-002: Minimum 8 characters enforced at schema level
        - Work factor 12: Balances security (resistant to brute force) and performance

    Security Notes:
        - Each call generates a unique salt (bcrypt automatic)
        - Same password produces different hashes (due to random salt)
        - Hashing is intentionally slow (~300ms) to prevent brute force
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash

    Used during login to check if provided password matches stored hash.
    Constant-time comparison prevents timing attacks.

    Args:
        plain_password: Plain text password from login attempt
        hashed_password: Bcrypt hash from database

    Returns:
        bool: True if password matches, False otherwise

    Examples:
        >>> hashed = hash_password("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False

    Security Notes:
        - Uses constant-time comparison (prevents timing attacks)
        - Intentionally slow (~300ms) to prevent brute force
        - Returns False for invalid hash format (graceful failure)
    """
    return pwd_context.verify(plain_password, hashed_password)
