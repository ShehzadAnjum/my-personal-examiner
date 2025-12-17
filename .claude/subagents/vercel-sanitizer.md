# Subagent: Vercel Sanitizer

**Type**: Narrow Task Specialist
**Parent Agent**: 09-Deployment
**Created**: 2025-12-18

## Purpose
Sanitize and validate backend code for Vercel serverless deployment compatibility.

## Specific Task
Transform standard FastAPI application code to work in Vercel's serverless environment.

## Key Transformations

### 1. Entry Point Creation
**Input**: FastAPI app in `backend/src/main.py`
**Output**: `api/index.py` with:
```python
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
from src.main import app  # Vercel detects ASGI automatically
```

### 2. Lazy Database Initialization
**Problem**: Eager module-level `create_engine()` fails
**Solution**: Lazy initialization pattern
```python
_engine = None
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(...)
    return _engine
```

### 3. Remove Mangum
**Before**: `from mangum import Mangum; handler = Mangum(app)`
**After**: Export `app` directly (Vercel supports ASGI natively)

### 4. Requirements.txt Generation
**Command**: `uv pip compile pyproject.toml -o api/requirements.txt`
**Location**: Must be in same directory as entry point

## Validation Checklist
- [ ] `vercel.json` at project root
- [ ] `api/index.py` exists with Python path setup
- [ ] `api/requirements.txt` co-located
- [ ] No eager database engine creation
- [ ] No Mangum adapter
- [ ] `runtime.txt` specifies Python version

## Common Issues Fixed
1. **FUNCTION_INVOCATION_FAILED** → Lazy DB initialization
2. **404 Not Found** → Move api/ to root
3. **Import errors** → Fix Python path in entry point
4. **Dependency errors** → Copy requirements.txt to api/

**Version**: 1.0.0 | **Status**: Active
