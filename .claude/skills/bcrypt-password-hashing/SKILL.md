---
name: bcrypt-password-hashing
description: bcrypt password hashing and verification patterns for secure authentication. Use when implementing password authentication, user registration, or login systems.
---

# Skill: bcrypt Password Hashing

**Type**: Security Expertise
**Created**: 2025-12-18
**Domain**: Authentication Security
**Parent Agent**: 02-Backend-Service

## Overview
Secure password hashing and verification using bcrypt with passlib for My Personal Examiner project.

## Constitutional Requirement
**Principle II**: A* Standard - Passwords MUST be hashed with bcrypt work factor 12 (constitutional requirement).

## Critical Version Compatibility
⚠️ **MUST use bcrypt 4.x** (not 5.x) - passlib incompatible with bcrypt 5.0+
```toml
# pyproject.toml
bcrypt = ">=4.0.0,<5.0.0"  # Pin to 4.x
passlib = {extras = ["bcrypt"], version = ">=1.7.4"}
```

## Standard Pattern

### 1. Setup Password Context
```python
# backend/src/services/password_service.py
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor 12 (constitutional requirement)
)


def hash_password(plain_password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        plain_password: Plain text password

    Returns:
        Hashed password (bcrypt, work factor 12)

    Example:
        >>> hash_password("MySecurePass123")
        '$2b$12$...'  # 60-character bcrypt hash
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise

    Example:
        >>> verify_password("MySecurePass123", stored_hash)
        True
    """
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. Integration with Student Service
```python
# backend/src/services/student_service.py
from src.services.password_service import hash_password, verify_password


def create_student(session: Session, data: RegisterRequest) -> Student:
    """Create student with hashed password"""

    # Hash password before storing
    password_hash = hash_password(data.password)

    student = Student(
        email=data.email,
        password_hash=password_hash,  # Store hash, NEVER plain password
        full_name=data.full_name
    )

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


def authenticate_student(
    session: Session,
    credentials: LoginRequest
) -> Student:
    """Authenticate student with email/password"""

    # Get student by email
    statement = select(Student).where(Student.email == credentials.email)
    student = session.exec(statement).first()

    if not student:
        raise InvalidCredentialsError("Invalid email or password")

    # Verify password
    if not verify_password(credentials.password, student.password_hash):
        raise InvalidCredentialsError("Invalid email or password")

    return student
```

## Security Best Practices

### ✅ DO: Use Work Factor 12
```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12  # Constitutional requirement
)
```

### ❌ DON'T: Use Lower Work Factor
```python
# WRONG - Too weak
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=8)
```

---

### ✅ DO: Hash Before Storing
```python
def create_student(data):
    password_hash = hash_password(data.password)
    student = Student(password_hash=password_hash)  # Store hash
    return student
```

### ❌ DON'T: Store Plain Passwords
```python
# DANGEROUS - Never store plain passwords
student = Student(password=data.password)
```

---

### ✅ DO: Generic Error Messages
```python
if not verify_password(password, hash):
    raise InvalidCredentialsError("Invalid email or password")  # Generic
```

### ❌ DON'T: Reveal Which Field Failed
```python
# WRONG - Helps attackers enumerate emails
if not student:
    raise ValueError("Email not found")
if not verify_password(...):
    raise ValueError("Password incorrect")
```

---

### ✅ DO: Constant-Time Comparison
```python
# passlib.verify() uses constant-time comparison internally
return pwd_context.verify(plain_password, hashed_password)
```

### ❌ DON'T: Manual String Comparison
```python
# WRONG - Timing attack vulnerable
return plain_password == hashed_password
```

## Testing Password Hashing

```python
# tests/unit/test_password_service.py
import pytest
from src.services.password_service import hash_password, verify_password


def test_hash_password_generates_bcrypt_hash():
    """Test password is hashed with bcrypt"""
    plain = "TestPassword123"
    hashed = hash_password(plain)

    # bcrypt hashes start with $2b$ and are 60 chars
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60


def test_hash_password_different_each_time():
    """Test hashing same password twice produces different hashes (salt)"""
    plain = "TestPassword123"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)

    assert hash1 != hash2  # Different due to random salt


def test_verify_password_correct():
    """Test verify returns True for correct password"""
    plain = "TestPassword123"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_incorrect():
    """Test verify returns False for wrong password"""
    plain = "TestPassword123"
    wrong = "WrongPassword456"
    hashed = hash_password(plain)

    assert verify_password(wrong, hashed) is False


def test_hash_uses_work_factor_12():
    """Test bcrypt work factor is 12 (constitutional requirement)"""
    plain = "TestPassword123"
    hashed = hash_password(plain)

    # bcrypt format: $2b$12$... (12 is the work factor)
    assert "$2b$12$" in hashed
```

## Troubleshooting

### Error: "module 'bcrypt' has no attribute '__about__'"
**Cause**: passlib incompatible with bcrypt 5.0+
**Solution**: Downgrade to bcrypt 4.x
```bash
uv add 'bcrypt>=4.0.0,<5.0.0'
```

### Error: "password cannot be longer than 72 bytes"
**Cause**: bcrypt has 72-byte limit
**Solution**: Hash password if >72 bytes (or enforce max length in validation)
```python
# In Pydantic schema
password: str = Field(max_length=72)
```

### Performance Concerns
**Symptom**: Login/registration slow
**Expected**: bcrypt work factor 12 takes ~200-300ms (intentional - prevents brute force)
**Action**: This is correct behavior - do NOT lower work factor

## Migration from Plain Passwords

If upgrading from system with plain passwords:
```python
def upgrade_password_if_needed(student: Student, plain_password: str):
    """One-time upgrade from plain to hashed passwords"""

    # Check if password is plain (not bcrypt hash)
    if not student.password_hash.startswith("$2b$"):
        # Hash the plain password
        student.password_hash = hash_password(plain_password)
        session.add(student)
        session.commit()
```

## Constitutional Compliance

**Principle II**: A* Standard - Security Non-Negotiable
- ✅ bcrypt work factor 12 (not 8, not 10)
- ✅ Never store plain passwords
- ✅ Use passlib for industry-standard implementation
- ✅ Version pinned to bcrypt 4.x for compatibility

## Usage Frequency
**Used:** 1 time (student registration)
**Will Use:** 2-3 times (registration, login, password reset)
**Critical:** Core security pattern for all authentication

**Version**: 1.0.0 | **Last Updated**: 2025-12-18