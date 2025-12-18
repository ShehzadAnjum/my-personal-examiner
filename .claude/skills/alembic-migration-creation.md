# Skill: Alembic Migration Creation

**Type**: Database Management
**Created**: 2025-12-18
**Domain**: Database Migrations
**Parent Agent**: 02-Backend-Service

## Overview
Create and apply database schema migrations using Alembic with SQLModel.

## Common Patterns

### Generate Migration (Auto-detect)
```bash
cd backend
uv run alembic revision --autogenerate -m "create students table"
```

### Manual Migration
```bash
uv run alembic revision -m "add student email index"
# Edit generated file in alembic/versions/
```

### Apply Migrations
```bash
uv run alembic upgrade head  # Apply all
uv run alembic upgrade +1    # Apply next one
```

### Rollback
```bash
uv run alembic downgrade -1  # Undo last migration
```

### Check Status
```bash
uv run alembic current  # Show current version
uv run alembic history  # Show all migrations
```

## Migration File Pattern
```python
def upgrade() -> None:
    """Create table"""
    op.create_table(
        'students',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
    )

def downgrade() -> None:
    """Drop table"""
    op.drop_table('students')
```

## Seed Data Pattern
```python
from uuid import uuid4

def upgrade() -> None:
    economics_id = str(uuid4())
    op.execute(f"""
        INSERT INTO subjects (id, code, name)
        VALUES ('{economics_id}', '9708', 'Economics')
    """)
```

**Usage:** 1 time (will use 20+ times)
**Version**: 1.0.0 | **Last Updated**: 2025-12-18
