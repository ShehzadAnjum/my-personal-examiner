# Skill: Vercel FastAPI Deployment

**Type**: Deployment Expertise
**Created**: 2025-12-18
**Domain**: Infrastructure

## Overview
Deploy FastAPI backend applications to Vercel serverless platform with Neon PostgreSQL database.

## Prerequisites
- Vercel account and project created
- Neon PostgreSQL database provisioned
- GitHub repository connected to Vercel

## Step-by-Step Procedure

### 1. Project Structure Setup
```
my-project/
├── api/
│   ├── index.py           # Entry point
│   └── requirements.txt   # Dependencies
├── backend/
│   └── src/
│       └── main.py        # FastAPI app
├── vercel.json            # Deployment config
└── runtime.txt            # Python version
```

### 2. Create vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### 3. Create api/index.py
```python
import sys
from pathlib import Path

# Add backend to Python path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from src.main import app
# Vercel detects ASGI automatically - just export app
```

### 4. Generate api/requirements.txt
```bash
cd backend
uv pip compile pyproject.toml -o ../api/requirements.txt
```

### 5. Create runtime.txt
```
python-3.12
```

### 6. Configure Environment Variables
In Vercel dashboard, add:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `ALGORITHM` - HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES` - 1440
- `ENVIRONMENT` - production
- `DEBUG` - false

### 7. Implement Lazy Database Initialization
```python
# backend/src/database.py
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url_str, ...)
    return _engine

def get_session():
    with Session(get_engine()) as session:
        yield session
```

### 8. Deploy
```bash
git add .
git commit -m "feat: Configure Vercel deployment"
git push origin main
# Vercel auto-deploys on push
```

### 9. Verify Deployment
```bash
curl https://your-project.vercel.app/health
# Expected: {"status":"healthy"}
```

## Common Pitfalls

### ❌ Mangum Adapter
**Wrong**: `handler = Mangum(app)`
**Right**: Export `app` directly (Vercel supports ASGI natively)

### ❌ Eager Database Initialization
**Wrong**: Module-level `engine = create_engine(...)`
**Right**: Lazy `get_engine()` function

### ❌ api/ in backend/
**Wrong**: `backend/api/index.py`
**Right**: `api/index.py` (at root level)

### ❌ Missing requirements.txt
**Wrong**: Only `backend/requirements.txt`
**Right**: Copy to `api/requirements.txt` (co-located with entry point)

### ❌ Hardcoded secrets
**Wrong**: `.env` file with secrets in git
**Right**: Vercel environment variables (dashboard)

## Debugging

### Check Build Logs
1. Go to Vercel dashboard
2. Click deployment
3. Check "Build" tab for errors

### Check Function Logs
1. Go to Vercel dashboard
2. Click deployment
3. Check "Functions" tab for runtime errors

### Common Error Messages
- `FUNCTION_INVOCATION_FAILED` → Check function logs (usually import or DB error)
- `404 Not Found` → Check `vercel.json` routing
- `Module not found` → Check Python path setup in `api/index.py`
- `Database connection failed` → Check DATABASE_URL environment variable

## Performance Optimization

### Cold Start Reduction
- Keep lambda size small (<50MB)
- Minimize imports in entry point
- Use lazy loading for heavy dependencies

### Database Connection Pooling
```python
# Production: Use connection pooling
engine = create_engine(
    url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## Success Criteria
- ✅ Health check returns 200 OK
- ✅ API endpoints functional
- ✅ Database queries working
- ✅ No errors in Vercel logs
- ✅ Cold start <10s, warm response <500ms

**Version**: 1.0.0 | **Last Updated**: 2025-12-18
