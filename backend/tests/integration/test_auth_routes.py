"""
Integration Tests for Authentication Routes

Tests POST /api/auth/register and POST /api/auth/login endpoints with full HTTP layer.

Constitutional Requirements:
- Email uniqueness enforced (409 on duplicate) - FR-001
- Password minimum 8 characters - FR-002
- Password never exposed in response - Principle I
"""

import pytest
from fastapi.testclient import TestClient


class TestRegisterEndpoint:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client: TestClient, sample_student_data: dict):
        """Test successful registration with valid data"""
        response = client.post("/api/auth/register", json=sample_student_data)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "created_at" in data

        # Check values
        assert data["email"] == sample_student_data["email"]
        assert data["full_name"] == sample_student_data["full_name"]

        # Check password NOT in response (security)
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(
        self, client: TestClient, sample_student_data: dict
    ):
        """Test that duplicate email returns 409 Conflict"""
        # Register first student
        client.post("/api/auth/register", json=sample_student_data)

        # Try to register again with same email
        response = client.post("/api/auth/register", json=sample_student_data)

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test that invalid email format returns 422 Validation Error"""
        invalid_data = {
            "email": "not-an-email",  # Invalid format
            "password": "ValidPass123",
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client: TestClient):
        """Test that password <8 chars returns 422 Validation Error"""
        invalid_data = {
            "email": "test@example.com",
            "password": "Short1",  # Only 6 characters (minimum is 8)
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error
        detail = response.json()["detail"]
        # Check error mentions password
        assert any("password" in str(error).lower() for error in detail)

    def test_register_missing_email(self, client: TestClient):
        """Test that missing email returns 422 Validation Error"""
        invalid_data = {
            # "email" missing
            "password": "ValidPass123",
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422

    def test_register_missing_password(self, client: TestClient):
        """Test that missing password returns 422 Validation Error"""
        invalid_data = {
            "email": "test@example.com",
            # "password" missing
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422

    def test_register_missing_full_name(self, client: TestClient):
        """Test that missing full_name returns 422 Validation Error"""
        invalid_data = {
            "email": "test@example.com",
            "password": "ValidPass123",
            # "full_name" missing
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422

    def test_register_empty_full_name(self, client: TestClient):
        """Test that empty full_name returns 422 Validation Error"""
        invalid_data = {
            "email": "test@example.com",
            "password": "ValidPass123",
            "full_name": "",  # Empty string (min_length=1)
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422

    def test_register_target_grades_optional(self, client: TestClient):
        """Test that target_grades is not required for registration"""
        data = {
            "email": "optional@example.com",
            "password": "ValidPass123",
            "full_name": "Optional Grades",
            # target_grades not provided (should default to None)
        }

        response = client.post("/api/auth/register", json=data)

        assert response.status_code == 201
        assert response.json()["target_grades"] is None

    def test_register_multiple_students(
        self, client: TestClient, sample_student_data: dict, sample_student_data_2: dict
    ):
        """Test registering multiple students with different emails"""
        # Register first student
        response1 = client.post("/api/auth/register", json=sample_student_data)
        assert response1.status_code == 201

        # Register second student
        response2 = client.post("/api/auth/register", json=sample_student_data_2)
        assert response2.status_code == 201

        # Check they have different IDs
        assert response1.json()["id"] != response2.json()["id"]

    def test_register_response_schema(
        self, client: TestClient, sample_student_data: dict
    ):
        """Test that registration response matches StudentResponse schema"""
        response = client.post("/api/auth/register", json=sample_student_data)

        assert response.status_code == 201
        data = response.json()

        # Required fields
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "created_at" in data

        # Optional field
        assert "target_grades" in data  # Can be None

        # Sensitive fields should NOT be present
        assert "password" not in data
        assert "password_hash" not in data
        assert "updated_at" not in data  # Internal field

    def test_register_email_case_preservation(self, client: TestClient):
        """Test that email local part case is preserved, domain is lowercased (RFC 5321)"""
        data = {
            "email": "Test.User@Example.COM",
            "password": "ValidPass123",
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=data)

        assert response.status_code == 201
        # Pydantic EmailStr normalizes domain to lowercase (RFC 5321 compliant)
        assert response.json()["email"] == "Test.User@example.com"

    def test_register_special_characters_in_name(self, client: TestClient):
        """Test registration with special characters in full_name"""
        data = {
            "email": "special@example.com",
            "password": "ValidPass123",
            "full_name": "Ñoño O'Brien-Smith",  # Special chars
        }

        response = client.post("/api/auth/register", json=data)

        assert response.status_code == 201
        assert response.json()["full_name"] == "Ñoño O'Brien-Smith"


class TestLoginEndpoint:
    """Tests for POST /api/auth/login (to be implemented)"""

    def test_login_success(self, client: TestClient, sample_student_data: dict):
        """Test successful login with valid credentials"""
        # Register first
        client.post("/api/auth/register", json=sample_student_data)

        # Login with same credentials
        login_data = {
            "email": sample_student_data["email"],
            "password": sample_student_data["password"],
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Should return student profile
        assert "id" in data
        assert "email" in data
        assert data["email"] == sample_student_data["email"]

        # Should NOT return password
        assert "password" not in data
        assert "password_hash" not in data

    def test_login_wrong_password(
        self, client: TestClient, sample_student_data: dict
    ):
        """Test login with wrong password returns 401 Unauthorized"""
        # Register first
        client.post("/api/auth/register", json=sample_student_data)

        # Login with wrong password
        login_data = {
            "email": sample_student_data["email"],
            "password": "WrongPassword123",
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_email(self, client: TestClient):
        """Test login with email that doesn't exist returns 401 Unauthorized"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123",
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        # Don't reveal whether email exists (security)
        assert "invalid" in response.json()["detail"].lower()

    def test_login_missing_email(self, client: TestClient):
        """Test login without email returns 422 Validation Error"""
        login_data = {
            # "email" missing
            "password": "SomePassword123",
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """Test login without password returns 422 Validation Error"""
        login_data = {
            "email": "test@example.com",
            # "password" missing
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_case_sensitive_password(
        self, client: TestClient, sample_student_data: dict
    ):
        """Test that password is case-sensitive"""
        # Register
        client.post("/api/auth/register", json=sample_student_data)

        # Try login with wrong case
        login_data = {
            "email": sample_student_data["email"],
            "password": sample_student_data["password"].upper(),  # Wrong case
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
