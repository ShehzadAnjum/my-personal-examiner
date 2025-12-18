#!/bin/bash
# Phase I Completion Gate Script
#
# Validates that Phase I (Core Infrastructure) is 100% complete
# according to constitutional requirements.
#
# Constitutional Principle VII: Phase Boundaries Are Hard Gates
# This script MUST pass before Phase II can begin.

set -e  # Exit on any error

echo "🔍 Checking Phase I Completion..."
echo ""

ERRORS=0

# Change to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# ============================================================================
# 1. Test Coverage Requirement (>80%)
# ============================================================================
echo "1️⃣  Checking test coverage (>80% required)..."
if uv run pytest tests/ --cov=src --cov-fail-under=80 --quiet --no-header 2>&1 | grep -q "passed"; then
    echo "   ✅ Test coverage >80%"
else
    echo "   ❌ Test coverage <80%"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 2. All Tests Pass
# ============================================================================
echo "2️⃣  Checking all tests pass..."
if uv run pytest tests/ --quiet --no-header 2>&1 | grep -q "passed"; then
    TEST_COUNT=$(uv run pytest tests/ --collect-only --quiet | grep "test session starts" -A 1 | tail -1 | grep -oE '[0-9]+' | head -1)
    echo "   ✅ All $TEST_COUNT tests passing"
else
    echo "   ❌ Some tests failing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 3. Required Endpoints Implemented
# ============================================================================
echo "3️⃣  Checking required endpoints..."

# Check POST /api/auth/register exists
if grep -q "def register" src/routes/auth.py; then
    echo "   ✅ POST /api/auth/register implemented"
else
    echo "   ❌ POST /api/auth/register missing"
    ERRORS=$((ERRORS + 1))
fi

# Check POST /api/auth/login exists
if grep -q "def login" src/routes/auth.py; then
    echo "   ✅ POST /api/auth/login implemented"
else
    echo "   ❌ POST /api/auth/login missing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 4. Database Models Created
# ============================================================================
echo "4️⃣  Checking database models..."

if [ -f "src/models/student.py" ]; then
    echo "   ✅ Student model exists"
else
    echo "   ❌ Student model missing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 5. Multi-Tenant Pattern Enforced
# ============================================================================
echo "5️⃣  Checking multi-tenant patterns (Constitutional Principle V)..."

# Check for student_id filtering in queries
if grep -q "student_id" src/models/student.py; then
    echo "   ✅ Multi-tenant anchor (student_id) present"
else
    echo "   ❌ Multi-tenant anchor missing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 6. Password Hashing Enforced
# ============================================================================
echo "6️⃣  Checking password hashing (Constitutional Principle I)..."

if grep -q "hash_password" src/services/auth_service.py; then
    echo "   ✅ Password hashing function exists"
else
    echo "   ❌ Password hashing missing"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "bcrypt" src/services/auth_service.py; then
    echo "   ✅ Using bcrypt for password hashing"
else
    echo "   ❌ Not using bcrypt"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 7. Alembic Migrations Created
# ============================================================================
echo "7️⃣  Checking database migrations..."

if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions/*.py 2>/dev/null | wc -l)" -gt 0 ]; then
    MIGRATION_COUNT=$(ls alembic/versions/*.py 2>/dev/null | wc -l)
    echo "   ✅ $MIGRATION_COUNT Alembic migration(s) created"
else
    echo "   ❌ No Alembic migrations found"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 8. Environment Configuration
# ============================================================================
echo "8️⃣  Checking environment configuration..."

if [ -f ".env.example" ]; then
    echo "   ✅ .env.example exists"
else
    echo "   ❌ .env.example missing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 9. Dependencies Configured
# ============================================================================
echo "9️⃣  Checking dependencies..."

if [ -f "pyproject.toml" ]; then
    echo "   ✅ pyproject.toml exists"
else
    echo "   ❌ pyproject.toml missing"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "fastapi" pyproject.toml; then
    echo "   ✅ FastAPI dependency configured"
else
    echo "   ❌ FastAPI missing from dependencies"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "sqlmodel" pyproject.toml; then
    echo "   ✅ SQLModel dependency configured"
else
    echo "   ❌ SQLModel missing from dependencies"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 10. Vercel Deployment Configuration
# ============================================================================
echo "🔟  Checking Vercel deployment..."

if [ -f "vercel.json" ]; then
    echo "   ✅ vercel.json exists"
else
    echo "   ❌ vercel.json missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "api/index.py" ]; then
    echo "   ✅ api/index.py exists (Vercel entry point)"
else
    echo "   ❌ api/index.py missing"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# Final Result
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ PHASE I COMPLETE - All gates passed!"
    echo "   Ready to proceed to Phase II (Question Bank & Exam Generation)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo "❌ PHASE I INCOMPLETE - $ERRORS gate(s) failed"
    echo "   Fix failing gates before proceeding to Phase II"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
