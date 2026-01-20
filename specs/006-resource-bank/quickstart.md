# Quickstart: Resource Bank Implementation

**Feature**: 006-resource-bank
**Date**: 2025-12-25
**Prerequisites**: Phase I complete (authentication, database, Student model)

## Development Environment Setup

### 1. Required Environment Variables

Add to `backend/.env`:

```bash
# Existing variables (should already be set)
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# NEW: Encryption key for student API keys (AES-256)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-generated-fernet-key-here

# NEW: Cache directory (optional, defaults to backend/cache)
RESOURCE_CACHE_DIR=./cache/resources
```

### 2. Install New Dependencies

```bash
cd backend
uv add cryptography
```

### 3. Create Cache Directory

```bash
mkdir -p backend/cache/resources/explanations
echo "*.json" > backend/cache/resources/.gitignore
echo "!index.json" >> backend/cache/resources/.gitignore
```

### 4. Database Migration

After creating models, generate and run migration:

```bash
cd backend
alembic revision --autogenerate -m "add_resource_bank_tables"
alembic upgrade head
```

## Implementation Order

Follow this order to satisfy dependencies:

### Phase 1: Models (No Dependencies)

1. **Create Enums** (`backend/src/models/enums.py`):
   ```python
   from enum import Enum

   class GeneratedByType(str, Enum):
       SYSTEM = "system"
       STUDENT = "student"

   class LLMProvider(str, Enum):
       OPENAI = "openai"
       ANTHROPIC = "anthropic"
       GOOGLE = "google"

   class MasteryLevel(str, Enum):
       NOT_STARTED = "not_started"
       LEARNING = "learning"
       FAMILIAR = "familiar"
       MASTERED = "mastered"
   ```

2. **GeneratedExplanation** (`backend/src/models/generated_explanation.py`)
3. **StudentLLMConfig** (`backend/src/models/student_llm_config.py`)
4. **StudentLearningPath** (`backend/src/models/student_learning_path.py`)

### Phase 2: Services (Depends on Models)

1. **llm_key_service.py** - Encryption/decryption (no DB dependency)
2. **cache_service.py** - File operations (no DB dependency)
3. **resource_service.py** - CRUD operations (depends on models)
4. **sync_service.py** - Sync logic (depends on cache + resource services)

### Phase 3: Routes (Depends on Services)

1. **resources.py** - Resource CRUD endpoints
2. **learning_path.py** - Learning progress endpoints

### Phase 4: Frontend (Depends on API)

1. **API clients** (`lib/api/resources.ts`, `lib/api/learning-path.ts`)
2. **Hooks** (`hooks/useResourceExplanation.tsx`, `hooks/useLearningPath.tsx`)
3. **Components** (VersionSwitcher, LLMConfigForm)
4. **Pages** (Settings LLM config section)

## Key Patterns

### Multi-Tenant Query Pattern

```python
# ALWAYS filter by student_id for per-student data
async def get_learning_path(student_id: UUID, session: AsyncSession):
    statement = select(StudentLearningPath).where(
        StudentLearningPath.student_id == student_id
    )
    return await session.exec(statement)
```

### Encryption Pattern

```python
from cryptography.fernet import Fernet
import os

def encrypt_api_key(api_key: str) -> str:
    fernet = Fernet(os.environ["ENCRYPTION_KEY"].encode())
    return fernet.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    fernet = Fernet(os.environ["ENCRYPTION_KEY"].encode())
    return fernet.decrypt(encrypted_key.encode()).decode()
```

### Signature Generation Pattern

```python
import hashlib
import json
from datetime import datetime

def generate_signature(content: dict, updated_at: datetime) -> str:
    data = f"{json.dumps(content, sort_keys=True)}:{updated_at.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()
```

### Cache-First Retrieval Pattern

```python
async def get_explanation(syllabus_point_id: UUID, version: int = 1):
    # 1. Check local cache
    cached = cache_service.get_cached(syllabus_point_id, version)
    if cached and cached.signature_matches():
        return cached.content, is_cached=True

    # 2. Fall back to database
    explanation = await resource_service.get_from_db(syllabus_point_id, version)
    if explanation:
        # 3. Update cache
        cache_service.save_to_cache(explanation)
        return explanation.content, is_cached=False

    return None
```

## Testing Strategy

### Unit Tests

```bash
# Run specific test file
cd backend
pytest tests/unit/test_llm_key_service.py -v

# Run all resource bank tests
pytest tests/unit/test_*service.py -v --tb=short
```

### Integration Tests

```bash
# Requires database connection
pytest tests/integration/test_resource_endpoints.py -v
```

### Test Fixtures

```python
# conftest.py additions
@pytest.fixture
def mock_encryption_key(monkeypatch):
    """Set test encryption key"""
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    return key

@pytest.fixture
def sample_explanation():
    """Sample explanation content"""
    return {
        "definition": "Test definition",
        "concept_explanation": "Test explanation",
        "summary": "Test summary"
    }
```

## Verification Checklist

Before marking each phase complete:

- [ ] All new models have corresponding tests
- [ ] Multi-tenant isolation verified (student_id filter present)
- [ ] API key encryption tested (never exposed in responses)
- [ ] Cache sync tested (signature comparison works)
- [ ] Integration tests pass
- [ ] No security warnings in logs

## Common Issues

### Issue: ENCRYPTION_KEY not set

```
Error: KeyError: 'ENCRYPTION_KEY'
Solution: Add ENCRYPTION_KEY to .env file (see setup above)
```

### Issue: Cache directory not writable

```
Error: PermissionError: [Errno 13]
Solution: mkdir -p backend/cache/resources && chmod 755 backend/cache
```

### Issue: Migration fails with FK constraint

```
Error: ForeignKeyViolation
Solution: Ensure SyllabusPoint and Student tables exist (Phase I)
```

## Next Steps

After completing all phases:

1. Run `/sp.tasks` to generate detailed task list
2. Implement tasks in order from tasks.md
3. Run phase gate validation script
4. Create PR using `/sp.git.commit_pr`
