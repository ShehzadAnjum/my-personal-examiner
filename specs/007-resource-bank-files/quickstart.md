# Quickstart Guide: Resource Bank Local Development

**Feature**: 007-resource-bank-files
**Date**: 2025-12-27
**Est. Setup Time**: 30-45 minutes

---

## Prerequisites

### Software Requirements
- Python 3.11+ (`python --version`)
- PostgreSQL 16 (`psql --version`)
- Redis 7+ (`redis-cli --version`)
- Tesseract OCR 5+ (`tesseract --version`)
- ClamAV 0.103+ (`clamscan --version`)
- UV 0.5+ (`uv --version`)
- AWS CLI (`aws --version`) - optional for S3 testing

### System Packages (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    clamav \
    clamav-daemon \
    redis-server \
    postgresql-16 \
    libpq-dev
```

### System Packages (macOS)
```bash
brew install tesseract redis clamav postgresql@16
brew services start redis
brew services start postgresql@16
brew services start clamav
```

---

## Environment Setup

### 1. Clone Repository & Install Dependencies
```bash
cd /home/anjum/dev/my_personal_examiner/backend
uv sync  # Installs all dependencies from pyproject.toml
```

### 2. Configure Environment Variables
Create `.env` file in `backend/`:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/my_personal_examiner

# AWS S3 (optional for local dev, required for production)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=resource-bank-dev

# YouTube API (optional, max 10 videos in Phase 1)
YOUTUBE_API_KEY=your_youtube_api_key

# Security
SIGNING_SECRET_KEY=generate_random_32_char_string_here

# Redis
REDIS_URL=redis://localhost:6379/0

# ClamAV
CLAMAV_SOCKET=/var/run/clamav/clamd.ctl  # or TCP: localhost:3310
```

### 3. Initialize Database
```bash
# Create database
createdb my_personal_examiner

# Run migrations
cd backend
alembic upgrade head  # Creates all tables including Resource Bank tables
```

### 4. Start ClamAV Daemon
```bash
# Update virus definitions
sudo freshclam

# Start daemon (Ubuntu/Debian)
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon

# Verify daemon running
clamdscan --version
```

---

## Running Services

### Terminal 1: FastAPI Server
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```
Access API at: http://localhost:8000/docs (Swagger UI)

### Terminal 2: Celery Worker
```bash
cd backend
celery -A src.tasks.celery_app worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduler)
```bash
cd backend
celery -A src.tasks.celery_app beat --loglevel=info
```
Daily sync job runs at 2:00 AM UTC

### Terminal 4: Flower (Celery Monitoring - Optional)
```bash
cd backend
celery -A src.tasks.celery_app flower --port=5555
```
Access Flower at: http://localhost:5555

---

## Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires running PostgreSQL + Redis)
pytest tests/integration/ -v

# Resource-specific tests
pytest tests/unit/test_resource_service.py -v
pytest tests/integration/test_resource_upload.py -v
```

### Manual Testing with Sample Data

#### Upload Sample Syllabus
```bash
curl -X POST http://localhost:8000/api/resources/upload \
  -F "file=@/path/to/9708_syllabus_2024.pdf" \
  -F "resource_type=syllabus" \
  -F "title=Economics 9708 Syllabus 2024"
```

#### Trigger Manual Sync
```bash
curl -X POST http://localhost:8000/api/sync/trigger
```

#### List Resources
```bash
curl http://localhost:8000/api/resources
```

---

## Local File Storage Structure

After first upload, verify directory structure:
```bash
ls -la backend/resources/

# Expected structure:
backend/resources/
├── syllabus/9708/
├── past_papers/9708/
├── textbooks/9708/
│   ├── Textbooks/
│   └── excerpts/
├── user_uploads/{student_id}/
├── videos/metadata/
└── downloads/  # Auto-cleaned after 24h
```

---

## Common Issues & Solutions

### Issue: "ClamAV daemon not running"
```bash
sudo systemctl status clamav-daemon
sudo systemctl restart clamav-daemon
```

### Issue: "Tesseract not found"
```bash
which tesseract
# If not found, install: sudo apt-get install tesseract-ocr
```

### Issue: "Redis connection refused"
```bash
redis-cli ping  # Should return PONG
sudo systemctl restart redis
```

### Issue: "S3 upload fails"
For local dev, S3 uploads are optional. Set in `.env`:
```bash
S3_ENABLED=false  # Disables S3 background uploads
```

### Issue: "Database migration fails"
```bash
# Check current revision
alembic current

# Reset to clean state (⚠️ DESTROYS DATA)
alembic downgrade base
alembic upgrade head
```

---

## Next Steps

1. ✅ **Setup Complete** - All services running
2. ⏳ **Run `/sp.tasks`** - Generate implementation tasks
3. ⏳ **Implement FR-001 to FR-073** - 73 functional requirements
4. ⏳ **Write Tests** - Target >80% coverage
5. ⏳ **Deploy to Staging** - Vercel + Neon PostgreSQL

---

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/resource-upload`
2. **Implement functional requirement** (e.g., FR-022: Auto-upload to S3)
3. **Write tests**: `tests/unit/test_s3_upload.py`
4. **Run tests**: `pytest tests/unit/test_s3_upload.py -v`
5. **Commit**: `git commit -m "feat: implement FR-022 auto S3 upload"`
6. **Repeat** for all 73 requirements

---

**Ready for Development** ✅

**Estimated Implementation Time**: 40-55 hours (per plan.md)
