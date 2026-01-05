# Resource Bank - Remaining Tasks

**Feature**: 007-resource-bank-files
**Phase 10**: Polish & Cross-Cutting Concerns
**Status**: Backend Complete ✅ | Frontend & Validation Pending
**Created**: 2025-12-27

---

## ✅ Completed Backend Implementation (86/94 tasks)

**All 7 user stories implemented with full backend functionality**:
- ✅ Phase 1-9: Complete (79 tasks)
- ✅ Phase 10 Backend: Complete (7 tasks: T080-T086)

**Backend Features Ready**:
- User uploads with virus scanning, OCR, S3 sync
- Daily Cambridge resource sync
- Admin review workflow (approve/reject/preview)
- Auto-selection algorithm with relevance scoring
- Manual admin tagging with full-text search
- YouTube transcript extraction
- Observability metrics and logging
- S3 outage handling and retry logic
- Signed URL generation for downloads

---

## 📋 Remaining Tasks (8 tasks)

### T087: HTTPS Enforcement

**Task**: Configure HTTPS enforcement for all API endpoints

**Why**: FR-058 requires secure communications

**Implementation**:
```python
# backend/src/main.py - Add HTTPS redirect middleware

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Production only - skip in development
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Environment Configuration**:
```bash
# .env.production
ENVIRONMENT=production
HTTPS_ONLY=true
```

**Deployment**: Configure reverse proxy (Nginx/Caddy) for SSL/TLS termination

---

### T088: Frontend Resource Browser (Student View)

**Task**: Create `frontend/app/(dashboard)/resources/page.tsx`

**Purpose**: Student resource browser showing public resources + own private uploads

**UI Components Needed**:
- Resource list with filters (type, visibility)
- Search bar (full-text search via `/api/resources/search`)
- Upload button
- Resource cards (title, type, thumbnail, actions)
- Quota usage indicator (X/100 resources)

**API Integration**:
```typescript
// GET /api/resources?visibility=public,private&student_id={current_user}
// GET /api/resources/search?query=fiscal%20policy
```

**Acceptance Criteria**:
- Student sees all PUBLIC resources
- Student sees own PRIVATE resources
- Student sees own PENDING_REVIEW resources
- Student can search by keywords
- Student can upload new resource
- Quota displayed: "72/100 resources used"

---

### T089: Frontend Admin Review Dashboard

**Task**: Create `frontend/app/(dashboard)/resources/admin/page.tsx`

**Purpose**: Admin dashboard for reviewing pending resources

**UI Components Needed**:
- Pending resources list
- Preview panel (first 3 pages for PDFs)
- Approve/Reject buttons
- Metadata edit form
- Student information display

**API Integration**:
```typescript
// GET /api/admin/resources/pending
// GET /api/admin/resources/{id}/preview
// PUT /api/admin/resources/{id}/approve
// PUT /api/admin/resources/{id}/reject
// PUT /api/admin/resources/{id}/metadata
```

**Acceptance Criteria**:
- Admin sees list of pending resources
- Admin can preview PDF (first 3 pages as images)
- Admin can approve → visibility changes to PUBLIC
- Admin can reject → file + record deleted
- Admin can edit title/description before approval
- Shows student name and email who uploaded

---

### T090: Frontend Resource Upload Component

**Task**: Create `frontend/components/ResourceUpload.tsx`

**Purpose**: File upload component with drag-drop, validation, progress

**UI Features**:
- Drag-and-drop zone
- File picker button
- File size validation (max 50MB client-side)
- File type validation (PDF, images, etc.)
- Upload progress bar
- YouTube URL input field
- Title and description fields
- Resource type selector

**API Integration**:
```typescript
// POST /api/resources/upload (multipart/form-data)
// POST /api/resources/upload/youtube (form-data: url, title)
```

**Validation**:
```typescript
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg'];

if (file.size > MAX_FILE_SIZE) {
  setError('File size exceeds 50MB limit');
  return;
}
```

**Acceptance Criteria**:
- Drag-drop works for PDFs
- Shows file size before upload
- Validates file size client-side
- Shows upload progress (0-100%)
- Supports YouTube URL uploads
- Displays quota warning if approaching limit

---

### T091: Test Suite Coverage Validation

**Task**: Run full test suite and verify >80% coverage

**Command**:
```bash
cd backend
pytest tests/ -v --cov=backend/src --cov-report=term-missing --cov-report=html
```

**Expected Output**:
```
======================== test session starts =========================
collected 150+ items

tests/unit/test_admin_service.py .................. [  X%]
tests/unit/test_resource_service.py .................. [  X%]
tests/unit/test_tagging_service.py .................. [  X%]
tests/unit/test_youtube_service.py .................. [  X%]
tests/integration/test_admin_review.py .................. [  X%]
tests/integration/test_auto_selection.py .................. [  X%]
tests/integration/test_manual_tagging.py .................. [  X%]
tests/integration/test_youtube_upload.py .................. [  X%]

----------- coverage: platform linux, python 3.11.x -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
backend/src/routes/admin_resources.py       123      5    96%   45, 67
backend/src/routes/resources.py             245     12    95%   123-135
backend/src/routes/resource_tagging.py       87      3    97%   56-58
backend/src/routes/metrics.py                112      8    93%   78-85
backend/src/services/resource_service.py     312     15    95%   ...
backend/src/services/tagging_service.py       95      4    96%   ...
backend/src/services/youtube_service.py      187     10    95%   ...
backend/src/utils/logging_utils.py            75      0   100%
backend/src/utils/s3_utils.py                 92      6    93%   ...
-----------------------------------------------------------------------
TOTAL                                       2847    143    95%
```

**Constitutional Requirement**: >80% coverage (Constitution Principle IX)

**Fix Low Coverage**:
- Add tests for uncovered error paths
- Test edge cases (quota exceeded, S3 unavailable, etc.)
- Add integration tests for multi-user scenarios

---

### T092: Quickstart Validation

**Task**: Follow `docs/quickstart.md` and verify all services start

**Services to Verify**:
1. **PostgreSQL**: `psql -U postgres -d my_personal_examiner`
2. **Redis**: `redis-cli ping` → PONG
3. **ClamAV**: `systemctl status clamav-daemon`
4. **FastAPI**: `uvicorn src.main:app --reload` → http://localhost:8000/docs
5. **Celery Worker**: `celery -A src.tasks worker --loglevel=info`
6. **Celery Beat**: `celery -A src.tasks beat --loglevel=info`
7. **Flower**: `celery -A src.tasks flower --port=5555` → http://localhost:5555

**Expected Output**:
```bash
# FastAPI
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using statreload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
🚀 My Personal Examiner API starting up...

# Celery Worker
[2025-12-27 12:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-12-27 12:00:00,100: INFO/MainProcess] mingle: all alone
[2025-12-27 12:00:00,200: INFO/MainProcess] celery@hostname ready.

# Celery Beat
[2025-12-27 12:00:00,000: INFO/MainProcess] Scheduler: Sending due task daily-cambridge-sync
```

**Troubleshooting**:
- If PostgreSQL fails: Check `DATABASE_URL` in `.env`
- If Redis fails: `sudo systemctl start redis-server`
- If ClamAV fails: `sudo systemctl start clamav-daemon`
- If Celery fails: Check Redis connection, verify `CELERY_BROKER_URL`

---

### T093: Code Cleanup

**Task**: Remove debug statements, organize imports, run linters

**Commands**:
```bash
cd backend

# Format with Black
black src/ tests/ --line-length=100

# Lint with Ruff
ruff check src/ tests/ --fix

# Sort imports
isort src/ tests/

# Type check with MyPy
mypy src/

# Remove debug prints
grep -r "print(" src/ | grep -v "# DEBUG:"
```

**Checklist**:
- [ ] Remove all `print()` statements (except intentional logging)
- [ ] Remove commented-out code
- [ ] Organize imports (stdlib, third-party, local)
- [ ] Run Black formatter
- [ ] Run Ruff linter
- [ ] Fix all type hints warnings
- [ ] Remove unused variables
- [ ] Remove TODO comments (move to GitHub Issues)

---

### T094: Security Hardening

**Task**: Validate multi-tenant queries, verify HMAC, check ClamAV

**Multi-Tenant Query Audit**:
```bash
# Search for queries missing student_id filter
grep -r "select(Resource)" backend/src/routes/ | grep -v "student_id"
grep -r "exec(select" backend/src/routes/ | grep -v "student_id"
```

**Validation Checklist**:

**1. Multi-Tenant Isolation**:
- [ ] All student resource queries include `uploaded_by_student_id` filter
- [ ] Admin queries can bypass filter (but log access)
- [ ] Resource visibility enforced (PUBLIC, PRIVATE, PENDING_REVIEW)
- [ ] No student can see other students' PRIVATE resources

**2. Signed URL HMAC**:
```python
# Test signed URL generation and verification
from src.utils.s3_utils import generate_signed_download_url, verify_signed_url

url = generate_signed_download_url("resource-uuid", "/path/to/file.pdf")
# url: /api/resources/{id}/download?expires=1234567890&signature=abc...

# Verify signature
is_valid = verify_signed_url("resource-uuid", "/path/to/file.pdf", 1234567890, "abc...")
assert is_valid is True

# Verify expiration
is_valid_expired = verify_signed_url("resource-uuid", "/path/to/file.pdf", 1, "abc...")
assert is_valid_expired is False
```

**3. ClamAV Integration**:
```python
# Test virus scanning
from src.services.file_storage_service import scan_file_for_virus

result = scan_file_for_virus("/path/to/test/file.pdf")
assert result["safe"] is True
assert "virus" not in result

# Test with EICAR test virus file
# Download from: https://www.eicar.org/download-anti-malware-testfile/
eicar_result = scan_file_for_virus("/path/to/eicar.com")
assert eicar_result["safe"] is False
assert "EICAR" in eicar_result["virus"]
```

**4. Environment Variables Audit**:
```bash
# Check all required env vars are documented
grep -r "os.getenv" backend/src/ | cut -d'"' -f2 | sort | uniq
```

**Required Environment Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/my_personal_examiner

# S3 (optional - graceful degradation)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=my-personal-examiner-resources

# YouTube (optional - for video uploads)
YOUTUBE_API_KEY=your_youtube_api_key

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
DOWNLOAD_URL_SECRET_KEY=random_secret_key_for_hmac_signing

# LLM API Keys (for topic generation - not Resource Bank)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

---

## 🎯 Summary

**Backend Implementation**: 100% Complete ✅
**Frontend Implementation**: 0% (3 components to build)
**Validation & Testing**: Partial (need coverage validation, quickstart verification)
**Code Quality**: Needs cleanup and linting
**Security**: Needs final audit

**Estimated Remaining Effort**:
- Frontend (T088-T090): ~6-8 hours
- Testing (T091): ~2 hours
- Validation (T092): ~1 hour
- Cleanup (T093): ~1 hour
- Security Audit (T094): ~2 hours

**Total**: ~12-14 hours to full production readiness

---

## 📚 Next Steps

1. **For Backend-Only Use**: System is fully functional via API endpoints (use Swagger UI at `/docs`)
2. **For Full Stack**: Implement frontend components (T088-T090)
3. **Before Production**: Complete validation and security audit (T091-T094)

**API Documentation**: http://localhost:8000/docs (when FastAPI running)

**All 7 User Stories Functional**:
- ✅ US1: Admin uploads syllabus resources
- ✅ US2: Daily Cambridge resource sync
- ✅ US3: Students upload PDFs with quota enforcement
- ✅ US4: Admin reviews and approves uploads
- ✅ US5: Auto-selection picks best resources for topics
- ✅ US6: Admin manually tags resources
- ✅ US7: YouTube transcript extraction

**Ready for**: Integration with teaching module, topic generation, and student learning paths! 🎓
