"""
Middleware Module

FastAPI dependencies for authentication and authorization.
"""

from src.middleware.admin_auth import get_admin_student, require_admin

__all__ = ["get_admin_student", "require_admin"]
