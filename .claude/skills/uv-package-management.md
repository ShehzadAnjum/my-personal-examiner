# Skill: UV Package Management

**Type**: Development Tools
**Created**: 2025-12-18
**Domain**: Python Dependencies
**Parent Agent**: 02-Backend-Service

## Overview
UV is a Rust-based Python package manager (10-100x faster than pip) used for dependency management in My Personal Examiner.

## Common Commands

### Add Dependency
```bash
cd backend
uv add fastapi  # Latest version
uv add "fastapi>=0.115.0"  # Version constraint
uv add 'bcrypt>=4.0.0,<5.0.0'  # Pin to major version
```

### Add Dev Dependency
```bash
uv add --dev pytest
uv add --dev pytest-cov pytest-asyncio
```

### Generate requirements.txt
```bash
uv pip compile pyproject.toml -o requirements.txt
uv pip compile pyproject.toml -o api/requirements.txt  # For Vercel
```

### Run Commands
```bash
uv run python script.py
uv run pytest
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

### Update Dependencies
```bash
uv pip sync  # Sync with pyproject.toml
uv add --upgrade fastapi  # Upgrade specific package
```

## Lessons Learned
- Always use `uv run` instead of activating venv
- For Vercel: compile requirements.txt and copy to api/ directory
- Version constraints crucial: bcrypt 4.x not 5.x

**Version**: 1.0.0 | **Last Updated**: 2025-12-18
