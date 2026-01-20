# Phase 0: Technology Research & Best Practices

**Feature**: 007-resource-bank-files
**Date**: 2025-12-27
**Goal**: Resolve technology unknowns and establish implementation patterns

---

## 1. S3 Integration Patterns

### Decision
Use **boto3 SDK** with SSE-S3 server-side encryption, presigned URLs for downloads, and exponential backoff retry logic.

### Rationale
- boto3 is AWS's official Python SDK with mature S3 support
- SSE-S3 encryption enabled by default (no key management overhead for MVP)
- Presigned URLs provide time-limited access without exposing credentials
- Exponential backoff prevents overwhelming S3 during temporary outages

### Implementation Pattern
```python
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Configure boto3 client with retries
config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'  # Exponential backoff
    }
)
s3_client = boto3.client('s3', config=config)

# Upload with SSE-S3 encryption
def upload_to_s3(file_path, bucket, key):
    try:
        s3_client.upload_file(
            file_path,
            bucket,
            key,
            ExtraArgs={'ServerSideEncryption': 'AES256'}  # SSE-S3
        )
        return True
    except ClientError as e:
        # Log and retry via Celery
        return False

# Generate presigned URL (1-hour expiration)
def generate_download_url(bucket, key, expiration=3600):
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiration
    )
```

### Alternatives Considered
- **S3 SSE-KMS**: Rejected for Phase 1 (adds key management complexity, not required for MVP)
- **Multipart upload**: Deferred to Phase 2 (50MB file limit makes single-part upload acceptable)
- **S3 Transfer Manager**: Deferred (boto3 client sufficient for Phase 1 scale)

---

## 2. PDF Processing Strategy

### Decision
Use **PyPDF2** for native PDF text extraction with **pytesseract** OCR fallback for scanned PDFs.

### Rationale
- PyPDF2: Simple API, good for text-based PDFs (Cambridge past papers are mostly native PDFs)
- pytesseract: Python wrapper for Tesseract OCR (open-source, 85% accuracy acceptable for Phase 1)
- Two-stage approach: Try native extraction first, fall back to OCR if <100 characters extracted
- Low memory footprint for 50MB file limit

### Implementation Pattern
```python
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

def extract_pdf_text(file_path):
    # Stage 1: Try native PDF extraction
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

    # Stage 2: OCR fallback if minimal text
    if len(text.strip()) < 100:  # Likely scanned PDF
        images = convert_from_path(file_path)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image)

    return text
```

### Alternatives Considered
- **pdfplumber**: Rejected (heavier dependency, PyPDF2 sufficient for MVP)
- **PDFMiner**: Rejected (complex API, overkill for Phase 1)
- **Commercial OCR APIs (AWS Textract, Google Vision)**: Deferred to Phase 2 (cost consideration, 85% accuracy acceptable for MVP)

---

## 3. YouTube Transcript API

### Decision
Use **youtube-transcript-api** for transcript extraction with YouTube Data API v3 for video metadata.

### Rationale
- youtube-transcript-api: Unofficial but reliable, no API key required for transcripts
- YouTube Data API v3: Official API for video metadata (title, channel, duration, thumbnail)
- Quota management: 10 videos/day in Phase 1 MVP (well under 10,000 units/day free quota)
- Error handling: Graceful degradation if transcript unavailable (store video metadata only)

### Implementation Pattern
```python
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def extract_youtube_transcript(video_id):
    try:
        # Get transcript (no API key needed)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = ' '.join([entry['text'] for entry in transcript])

        # Get metadata via official API
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        response = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        ).execute()

        metadata = {
            'title': response['items'][0]['snippet']['title'],
            'channel': response['items'][0]['snippet']['channelTitle'],
            'duration': response['items'][0]['contentDetails']['duration'],
            'transcript': full_text,
            'timestamps': transcript  # Store for timestamp matching
        }
        return metadata
    except Exception as e:
        # Transcript unavailable, store metadata only
        return {'title': ..., 'transcript': None, 'error': str(e)}
```

### Alternatives Considered
- **Whisper API for transcription**: Rejected (cost per video, unnecessary when YouTube provides transcripts)
- **Manual entry**: Rejected (doesn't scale, Phase 1 MVP needs automation)

---

## 4. Celery Background Tasks

### Decision
Use **Celery 5.3+** with **Redis broker** for background S3 uploads, daily sync jobs, and OCR processing.

### Rationale
- Celery: Industry-standard task queue for Python, mature retry logic, monitoring support
- Redis broker: Fast, reliable, simpler than RabbitMQ for MVP scale
- Task serialization: JSON (portable, debuggable)
- Retry strategy: Exponential backoff with max 3 attempts
- Monitoring: Flower dashboard for task tracking (optional Phase 1)

### Implementation Pattern
```python
# celery_app.py
from celery import Celery

app = Celery(
    'resource_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    task_acks_late=True,  # Re-queue if worker crashes
    task_reject_on_worker_lost=True
)

# S3 upload task with retry
@app.task(bind=True, max_retries=3)
def upload_to_s3_task(self, file_path, bucket, key):
    try:
        upload_to_s3(file_path, bucket, key)
    except Exception as exc:
        # Exponential backoff: 60s, 300s, 900s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# Daily sync scheduled task (Celery Beat)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-cambridge-sync': {
        'task': 'tasks.sync_task.sync_cambridge_resources',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
}
```

### Alternatives Considered
- **Python asyncio + apscheduler**: Rejected (less robust retry logic, no distributed task support)
- **AWS SQS + Lambda**: Deferred to Phase 2 (adds infrastructure complexity, local Celery sufficient for MVP)
- **RabbitMQ broker**: Rejected (Redis simpler for Phase 1 scale)

---

## 5. Virus Scanning Integration

### Decision
Use **ClamAV daemon** (clamd) with **pyclamd** Python client, scan after upload but before database record creation.

### Rationale
- ClamAV: Open-source, industry-standard antivirus for file scanning
- Daemon mode: Faster than CLI for repeated scans (no engine reload per file)
- Scan timing: After file write, before DB commit (prevents storing infected files)
- Quarantine: Delete infected file + log incident, return error to user
- Performance: <5 seconds for 50MB files (acceptable for upload flow)

### Implementation Pattern
```python
import pyclamd

# Initialize ClamAV daemon client
cd = pyclamd.ClamdUnixSocket()

def scan_file_for_virus(file_path):
    try:
        result = cd.scan_file(file_path)
        if result is None:
            return {'safe': True}
        else:
            # Infected file detected
            virus_name = result[file_path][1]
            os.remove(file_path)  # Delete immediately
            return {'safe': False, 'virus': virus_name}
    except Exception as e:
        # ClamAV daemon not running
        # Phase 1: Log warning and allow upload (manual review catches it)
        # Phase 2: Fail upload if daemon unavailable
        return {'safe': True, 'warning': 'Scan unavailable'}

# Usage in upload flow
@router.post('/upload')
def upload_resource(file: UploadFile):
    temp_path = save_temp_file(file)
    scan_result = scan_file_for_virus(temp_path)

    if not scan_result['safe']:
        raise HTTPException(400, f"Virus detected: {scan_result['virus']}")

    # Proceed with storage + DB record
    move_to_permanent_storage(temp_path)
    create_resource_record()
```

### Alternatives Considered
- **ClamAV CLI (clamscan)**: Rejected (slow engine reload per scan, daemon mode faster)
- **Commercial antivirus APIs**: Deferred to Phase 2 (cost consideration, ClamAV sufficient for MVP)
- **Skip virus scanning**: Rejected (security risk, admin review not sufficient alone)

---

## 6. Multi-Tenant File Storage

### Decision
Use **student_id-scoped directory structure** with **signed URLs** for private resource downloads.

### Rationale
- File isolation: `backend/resources/user_uploads/{student_id}/` prevents accidental cross-tenant access
- Signed URLs: Generate time-limited (1-hour) URLs with HMAC signature for private downloads
- Permission middleware: Check visibility + student_id before serving files
- Public resources: Serve directly (no signed URL needed for syllabus/past papers)

### Implementation Pattern
```python
import hmac
import hashlib
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SIGNING_SECRET_KEY')

def generate_signed_url(resource_id, student_id, expires_in=3600):
    expiry = datetime.utcnow() + timedelta(seconds=expires_in)
    expiry_ts = int(expiry.timestamp())

    # Create signature: HMAC(resource_id + student_id + expiry)
    message = f"{resource_id}:{student_id}:{expiry_ts}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"/api/resources/{resource_id}/download?sig={signature}&exp={expiry_ts}&student={student_id}"

def verify_signed_url(resource_id, signature, expiry_ts, student_id):
    # Check expiry
    if datetime.utcnow().timestamp() > expiry_ts:
        return False

    # Verify signature
    message = f"{resource_id}:{student_id}:{expiry_ts}"
    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)

# Middleware for download endpoint
@router.get('/resources/{id}/download')
def download_resource(id: str, sig: str, exp: int, student: str):
    if not verify_signed_url(id, sig, exp, student):
        raise HTTPException(403, "Invalid or expired signature")

    resource = get_resource(id)
    if resource.visibility == 'private' and resource.uploaded_by_student_id != student:
        raise HTTPException(403, "Unauthorized access")

    return FileResponse(resource.file_path)
```

### Alternatives Considered
- **S3 presigned URLs for all downloads**: Rejected (adds S3 dependency for local files, signed URLs sufficient)
- **JWT tokens for download auth**: Rejected (overkill for file downloads, simpler HMAC signature sufficient)
- **No permission checks (rely on obscurity)**: Rejected (violates multi-tenant isolation principle)

---

## 7. Full-Text Search

### Decision
Use **PostgreSQL full-text search** (tsvector + tsquery) with GIN indexes for Phase 1 MVP.

### Rationale
- PostgreSQL FTS: Built-in, no additional infrastructure (Elasticsearch adds complexity)
- tsvector: Tokenized, indexed text representation (supports stemming, ranking)
- GIN index: Fast full-text search across 1000+ documents (<2 seconds per SC-008)
- Search ranking: Uses ts_rank for relevance scoring
- Phase 1 sufficient: Deferred Elasticsearch to Phase 2 for advanced features (synonyms, facets)

### Implementation Pattern
```python
from sqlmodel import text

# Add tsvector column to Resource model
class Resource(SQLModel, table=True):
    # ... other fields
    search_vector: Optional[str] = Field(sa_column=Column(
        'search_vector',
        postgresql.TSVECTOR,
        Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, ''))")
    ))

# Create GIN index in migration
def upgrade():
    op.execute("""
        CREATE INDEX idx_resource_search_vector
        ON resources USING GIN (search_vector);
    """)

# Search query with ranking
def search_resources(query: str, limit: int = 20):
    session = get_session()
    results = session.exec(
        text("""
            SELECT id, title, ts_rank(search_vector, query) AS rank
            FROM resources, to_tsquery('english', :query) query
            WHERE search_vector @@ query
            ORDER BY rank DESC
            LIMIT :limit
        """),
        {"query": query, "limit": limit}
    ).all()
    return results
```

### Alternatives Considered
- **Elasticsearch**: Deferred to Phase 2 (adds infrastructure, PostgreSQL FTS sufficient for 1000 docs)
- **No search (browse only)**: Rejected (SC-008 requires 2-second search for 1000+ docs)
- **Simple LIKE queries**: Rejected (slow on large text fields, no ranking)

---

## 8. Daily Sync Job Scheduling

### Decision
Use **Celery Beat** for daily 2AM sync job with timezone-aware scheduling.

### Rationale
- Celery Beat: Distributed task scheduler built into Celery ecosystem
- Cron syntax: Familiar scheduling pattern (hour=2, minute=0)
- Timezone handling: Explicit UTC configuration prevents DST issues
- Retry logic: Celery task retry handles Cambridge website unavailability
- Monitoring: Celery Flower dashboard shows scheduled task history

### Implementation Pattern
```python
# celery_app.py (continued)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-cambridge-sync': {
        'task': 'tasks.sync_task.sync_cambridge_resources',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC daily
        'options': {'queue': 'sync'},  # Dedicated queue for long-running tasks
    },
}

# sync_task.py
@app.task(bind=True, max_retries=3)
def sync_cambridge_resources(self):
    try:
        # Download new past papers from Cambridge website
        new_resources = scrape_cambridge_website()

        for resource in new_resources:
            # Calculate signature, skip if exists
            if not resource_exists(resource.signature):
                download_and_store(resource)
                upload_to_s3_task.delay(resource.file_path)

        log_sync_success(len(new_resources))
    except Exception as exc:
        # Retry after 4 hours (3 retries max per day)
        raise self.retry(exc=exc, countdown=60 * 60 * 4)
```

### Alternatives Considered
- **System cron**: Rejected (requires root access, less portable than Celery Beat)
- **APScheduler**: Rejected (less integrated with Celery task queue)
- **AWS EventBridge**: Deferred to Phase 2 (adds AWS dependency, local Celery sufficient)

---

## Summary: Technology Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| S3 Integration | boto3 + SSE-S3 + presigned URLs | Official SDK, simple encryption, time-limited access |
| PDF Processing | PyPDF2 + pytesseract OCR | Native text extraction + OCR fallback, 85% accuracy acceptable |
| YouTube API | youtube-transcript-api + Data API v3 | Free transcripts, official metadata API |
| Background Tasks | Celery 5.3+ + Redis broker | Industry standard, robust retry logic |
| Virus Scanning | ClamAV daemon (clamd) + pyclamd | Open-source, fast daemon mode, <5s scans |
| File Storage | student_id-scoped directories + signed URLs | Multi-tenant isolation, HMAC-based auth |
| Full-Text Search | PostgreSQL FTS (tsvector + GIN) | Built-in, <2s search, no extra infrastructure |
| Sync Scheduling | Celery Beat (cron-style) | Integrated with task queue, timezone-aware |

**All unknowns resolved** ✅ - Ready for Phase 1 design (data model + contracts).

---

**Next**: Generate `data-model.md` with 4 SQLModel tables + relationships.
