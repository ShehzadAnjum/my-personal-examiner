# Feature Specification: Resource Bank File Storage & Multi-Source Content Management

**Feature Branch**: `007-resource-bank-files`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "Resource Bank - File Storage & Multi-Source Content Management: A centralized content repository that stores, syncs, and manages multiple learning resources (official syllabus, past papers, textbooks, user uploads, YouTube links) to support AI-powered topic generation and study plan creation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Initializes Official Resource Repository (Priority: P1)

Admin uploads the official Cambridge Economics 9708 syllabus and configures the Resource Bank to store and manage it locally with cloud backup.

**Why this priority**: Foundation for all other features. Without the official syllabus, no topic generation or study plans can be created. This is the critical first step.

**Independent Test**: Can be fully tested by uploading a syllabus PDF, verifying it's stored in correct directory structure (`backend/resources/syllabus/9708/`), confirming S3 background upload, and checking database record creation. Delivers value by establishing the authoritative Cambridge syllabus as the single source of truth.

**Acceptance Scenarios**:

1. **Given** admin has Cambridge syllabus PDF, **When** admin uploads it via admin UI, **Then** system stores file in `backend/resources/syllabus/9708/syllabus_2024.pdf`, creates database record with metadata (title, source, file_path, signature), and queues S3 background upload
2. **Given** syllabus is stored locally, **When** S3 upload completes, **Then** system updates database record with S3 URL and marks sync status as "synced"
3. **Given** syllabus exists in Resource Bank, **When** admin re-uploads same file, **Then** system detects duplicate via signature matching and rejects upload with message "Syllabus already exists"

---

### User Story 2 - System Auto-Syncs Cambridge Past Papers Daily (Priority: P1)

System automatically checks Cambridge website daily for new past papers, downloads them (question papers + mark schemes), and stores them with proper organization and metadata.

**Why this priority**: Past papers are essential for exam preparation and topic generation. Automatic sync ensures students always have access to the latest exam materials without manual admin work.

**Independent Test**: Can be tested by triggering daily sync job, mocking Cambridge website with test PDFs, verifying files are downloaded to `backend/resources/past_papers/9708/`, checking signature-based change detection prevents duplicate downloads, and confirming mark schemes are linked to question papers. Delivers value by automating resource maintenance.

**Acceptance Scenarios**:

1. **Given** daily sync job runs, **When** system checks Cambridge website, **Then** system downloads all Economics 9708 past papers from last 10 years, stores in `backend/resources/past_papers/9708/{year}_{session}_qp_{paper}.pdf` format, and creates database records with metadata
2. **Given** past paper already exists locally, **When** sync job runs, **Then** system compares file signature (SHA-256 hash), skips download if unchanged, and updates "last_checked" timestamp
3. **Given** new past paper is available, **When** sync job runs, **Then** system downloads new file, stores it, creates database record, uploads to S3 in background, and notifies admin via system log
4. **Given** mark scheme PDF is available, **When** system downloads past paper, **Then** system also downloads corresponding mark scheme, links them in database via `paper_id` relationship, and stores in same directory

---

### User Story 3 - Student Uploads Private Learning Resource (Priority: P2)

Student uploads their own study notes or textbook excerpts to use for personalized topic generation, with automatic background upload for admin review.

**Why this priority**: Enables personalized learning by allowing students to leverage their own materials. Requires P1 infrastructure but adds significant value for individual learners.

**Independent Test**: Can be tested by student uploading PDF via UI, verifying file stores in `backend/resources/user_uploads/{student_id}/`, checking visibility is "private", confirming admin sees it in "Pending Review" dashboard, and validating multi-tenant isolation (other students can't access). Delivers value by supporting personalized study materials.

**Acceptance Scenarios**:

1. **Given** authenticated student, **When** student uploads "My Economics Notes.pdf" via UI, **Then** system stores file in `backend/resources/user_uploads/{student_id}/{resource_id}.pdf`, creates database record with visibility="private", uploaded_by={student_id}, admin_approved=false, and queues background S3 upload
2. **Given** student uploaded resource, **When** student tags it to syllabus point 9708.5.1, **Then** system creates link record in `syllabus_point_resources` table with relevance_score=NULL (admin to set later)
3. **Given** student has private resource, **When** student generates topic explanation, **Then** system includes student's resource in available resource list for selection
4. **Given** student has private resource, **When** another student views resource list, **Then** private resource is NOT visible (multi-tenant isolation enforced)
5. **Given** uploaded file exceeds 50MB, **When** student attempts upload, **Then** system rejects with error "File too large. Maximum size: 50MB"

---

### User Story 4 - Admin Reviews and Approves User-Uploaded Resources (Priority: P2)

Admin reviews student-uploaded resources in dashboard, can preview content, edit metadata/excerpts, and approve for public sharing or silently reject.

**Why this priority**: Quality control for user-generated content. Prevents low-quality or copyrighted material from becoming publicly available while enabling valuable student contributions.

**Independent Test**: Can be tested by creating pending resource, admin viewing in review dashboard, previewing PDF content, editing title/description, approving, and verifying visibility changes to "public" and other students can now access. Delivers value by curating high-quality public resources.

**Acceptance Scenarios**:

1. **Given** student uploaded resource with status "Pending Review", **When** admin views review dashboard, **Then** system displays list of pending uploads with student name, resource title, upload date, and file size
2. **Given** admin viewing pending resource, **When** admin clicks "Preview", **Then** system displays PDF content inline with first 3 pages visible
3. **Given** admin reviewing resource, **When** admin clicks "Approve", **Then** system updates visibility="public", admin_approved=true, sets approval_date, and makes resource visible to all students in next sync
4. **Given** admin reviewing resource, **When** admin clicks "Reject", **Then** system deletes file from storage, removes database record, and does NOT notify student
5. **Given** admin reviewing resource, **When** admin edits title from "My Notes" to "Monetary Policy Summary Notes", clicks "Approve", **Then** system saves edited metadata and approves with new title
6. **Given** admin reviewing textbook excerpt, **When** admin extracts key paragraphs to "excerpt" field, **Then** system stores excerpt text in database for LLM prompts while keeping full PDF for reference

---

### User Story 5 - System Auto-Selects Best Resources for Topic Generation (Priority: P3)

When admin generates topic explanation, system automatically selects most relevant resources (syllabus, past papers, textbook excerpts) based on quality scores, with option to override selection.

**Why this priority**: Optimizes topic generation quality by using best available sources. Builds on P1/P2 infrastructure but is enhancement rather than core functionality.

**Independent Test**: Can be tested by generating topic for 9708.5.1, verifying system auto-selects syllabus (100% relevance), 3 most relevant past papers (scored by keyword matching), and textbook chapter 12 (if tagged), displaying quality scores in UI, and allowing manual override. Delivers value by improving explanation quality.

**Acceptance Scenarios**:

1. **Given** admin generating topic 9708.5.1 "Fiscal Policy", **When** system analyzes available resources, **Then** system auto-selects: official syllabus (relevance_score=1.0), 3 past papers with "fiscal policy" in questions (relevance_score=0.8-0.9), and textbook chapter if tagged
2. **Given** resources are auto-selected, **When** admin views resource selection UI, **Then** system displays selected resources with quality scores shown as "90% relevance", "85% relevance", etc., and allows admin to uncheck or add additional resources
3. **Given** admin generates topic with selected resources, **When** LLM prompt is constructed, **Then** prompt includes: syllabus learning outcomes, past paper question texts, textbook excerpt summaries, with clear attribution for each source
4. **Given** topic generation completes, **When** explanation is saved, **Then** system creates records in `explanation_resource_usage` table tracking which resources were used with contribution_weight values

---

### User Story 6 - Admin Tags Resources to Syllabus Points via Manual Interface (Priority: P3)

Admin uses manual tagging interface to link resources (textbooks, videos, articles) to specific syllabus points with relevance scores, improving resource discovery and auto-selection accuracy.

**Why this priority**: Improves resource organization and auto-selection algorithm. Optional enhancement that increases system intelligence over time.

**Independent Test**: Can be tested by admin opening tagging UI, searching for resource "Economics Textbook Chapter 12", selecting it, linking to syllabus point 9708.5.1, setting relevance score to 0.95, and verifying link appears in database and affects future auto-selections. Delivers value by creating structured knowledge base.

**Acceptance Scenarios**:

1. **Given** admin in tagging interface, **When** admin searches "fiscal policy", **Then** system displays matching resources (textbooks, videos, past papers) and matching syllabus points (9708.5.1, 9708.5.2)
2. **Given** admin selects resource and syllabus point, **When** admin sets relevance score slider to 95%, clicks "Link", **Then** system creates record in `syllabus_point_resources` with relevance_score=0.95
3. **Given** resource is linked to syllabus point, **When** admin generates topic for that point, **Then** auto-selection algorithm prioritizes linked resource based on relevance score
4. **Given** textbook PDF uploaded, **When** admin enters page range "245-267" for chapter, **Then** system stores page_range in metadata JSONB field for precise excerpt extraction

---

### User Story 7 - System Extracts YouTube Transcript for Topic Generation (Priority: P3)

Admin adds YouTube video link to Resource Bank, system automatically extracts transcript via YouTube API, identifies key timestamps, and makes content searchable for topic generation.

**Why this priority**: Enhances multi-source learning by incorporating video content. Nice-to-have feature that complements text-based resources.

**Independent Test**: Can be tested by admin pasting YouTube URL, system calling YouTube API to extract transcript, parsing it into searchable text, identifying topic-related timestamps (using keyword matching), storing in database, and including transcript excerpts in LLM prompts when relevant. Delivers value by diversifying learning resources.

**Acceptance Scenarios**:

1. **Given** admin adds YouTube video URL "https://youtube.com/watch?v=abc123", **When** system processes link, **Then** system calls YouTube API, extracts full transcript, stores in database metadata field, and saves video metadata (title, channel, duration, thumbnail)
2. **Given** video transcript exists, **When** system searches for "fiscal policy" keywords, **Then** system identifies matching timestamps (e.g., "2:30 - Definition of fiscal policy", "5:45 - Examples of fiscal policy") and stores as structured data
3. **Given** video is linked to syllabus point, **When** admin generates topic, **Then** system includes relevant transcript excerpts in LLM prompt with timestamp references
4. **Given** YouTube API rate limit is reached, **When** system attempts transcript extraction, **Then** system queues request for retry after rate limit reset, logs warning, and continues without blocking

---

### Edge Cases

- **What happens when syllabus file is corrupted or unreadable?**
  - System detects invalid PDF during upload, rejects with error message, and logs incident for admin review

- **How does system handle duplicate resources uploaded by different students?**
  - System compares file signatures (SHA-256 hash), detects duplicates, and allows upload but marks as "duplicate of resource #{original_id}" in metadata

- **What if Cambridge website is unreachable during daily sync?**
  - System logs failed sync attempt, retries after 4 hours (3 retries max per day), sends alert to admin if all retries fail

- **How does system handle scanned (image-based) PDFs?**
  - System detects scanned PDFs by checking for text content, triggers OCR process using pytesseract, extracts text, stores both original PDF and OCR text in database

- **What if student uploads copyrighted textbook?**
  - Admin review process catches this, admin rejects upload, and system provides guidance to student about acceptable materials (excerpts, summaries, own notes)

- **How does multi-tenant isolation work if admin approves user resource?**
  - Upon approval, visibility changes from "private" to "public", making it accessible to all students, but `uploaded_by` field preserves original uploader for attribution

- **What if S3 background upload fails?**
  - System retries upload 3 times with exponential backoff (1min, 5min, 15min), marks resource as "sync_failed" in database, sends alert to admin, resource remains accessible locally

- **What if S3 remains unavailable for extended period (24+ hours)?**
  - System continues operating with local-only storage, all uploads/downloads work normally, failed S3 uploads queued in database with status "pending_retry", admin dashboard shows "S3 offline - X resources pending sync", automatic batch retry when S3 connectivity restored

- **Can rejected resources be re-submitted or restored?**
  - No. Rejection permanently deletes file and database record (linear workflow). Student must re-upload if they want to submit revised version. This prevents database bloat and simplifies state machine for Phase 1.

---

## Clarifications

### Session 2025-12-27

- Q: What are the hard limits for resource storage per student and total system capacity? → A: 100 resources per student, 100K total system resources (moderate limits with growth room for Phase 1 MVP)
- Q: What happens if S3 remains unavailable for an extended period (24+ hours)? → A: System continues operating with local-only storage, queues failed uploads for batch retry when S3 recovers
- Q: What are the encryption requirements for resources and user data? → A: User data (auth, personal info, preferences) + private student uploads: HTTPS in transit + S3 SSE-S3 at rest. Public resources (syllabus, past papers, approved uploads): HTTPS in transit only, no encryption at rest required
- Q: What metrics and logging are required for operational monitoring? → A: Basic metrics (upload count, sync status, storage usage) + error logging + security event logging (failed auth, unauthorized access attempts)
- Q: What is the complete state machine for resource lifecycle transitions? → A: Linear workflow: uploaded → pending_review → approved/rejected (rejected deletes resource, no re-submission)

---

## Requirements *(mandatory)*

### Functional Requirements

**File Storage & Organization**

- **FR-001**: System MUST store resources in organized directory structure: `backend/resources/{resource_type}/{subject_code}/` where resource_type includes: syllabus, past_papers, textbooks, user_uploads, videos, downloads
- **FR-002**: System MUST separate textbooks into two subdirectories: `Textbooks/` for full PDFs (user/admin owned) and `excerpts/` for extracted sections
- **FR-003**: System MUST implement gitignore for `backend/resources/` directory to prevent accidental commit of large files
- **FR-004**: System MUST store user uploads in isolated subdirectories: `backend/resources/user_uploads/{student_id}/` for multi-tenant file separation
- **FR-005**: System MUST maintain temporary downloads folder at `backend/resources/downloads/` that auto-cleans files older than 24 hours

**Database Schema**

- **FR-006**: System MUST implement `resources` table with fields: id (UUID), resource_type (ENUM: syllabus, textbook, past_paper, video, article, user_upload), title (TEXT), source_url (TEXT), file_path (TEXT), uploaded_by_student_id (UUID nullable), admin_approved (BOOLEAN default false), visibility (ENUM: public, private, pending_review), metadata (JSONB), signature (TEXT for SHA-256), created_at, updated_at
- **FR-007**: System MUST implement `syllabus_point_resources` table linking resources to syllabus points with fields: syllabus_point_id (UUID), resource_id (UUID), relevance_score (FLOAT 0-1), added_by (ENUM: system, admin, student), PRIMARY KEY (syllabus_point_id, resource_id)
- **FR-008**: System MUST implement `explanation_resource_usage` table tracking resource usage with fields: explanation_id (UUID), resource_id (UUID), contribution_weight (FLOAT), created_at, PRIMARY KEY (explanation_id, resource_id)
- **FR-009**: System MUST implement `student_resource_preferences` table with fields: student_id (UUID), resource_id (UUID), enabled (BOOLEAN default true), priority (INT for ordering), PRIMARY KEY (student_id, resource_id)

**Resource Types & Ingestion**

- **FR-010**: System MUST support uploading official Cambridge syllabus PDFs and parse learning outcomes for database storage
- **FR-011**: System MUST support downloading past papers (question papers + mark schemes) and automatically link them via paper_id relationship
- **FR-012**: System MUST support textbook integration by storing chapter references, page ranges, and extracted excerpts (not full text unless user-uploaded)
- **FR-013**: System MUST support YouTube links by storing video metadata and extracting transcripts via youtube-transcript-api
- **FR-014**: System MUST support user uploads of PDFs with file size limit of 50MB and virus scanning before storage
- **FR-015**: System MUST perform OCR on scanned PDFs using pytesseract and store extracted text in metadata JSONB field

**Sync Strategy**

- **FR-016**: System MUST calculate SHA-256 signature for all files upon upload/download and store in database for change detection
- **FR-017**: System MUST run daily sync job (scheduled for 2:00 AM) that checks Cambridge website for new syllabus versions and past papers
- **FR-018**: System MUST implement differential sync by comparing file signatures - only download if signature changed or file doesn't exist locally
- **FR-019**: System MUST track sync status in database with fields: last_sync_date, sync_status (ENUM: success, failed, in_progress), last_checked_date
- **FR-020**: System MUST download ALL past papers for Economics 9708 (no user configuration for selective download)
- **FR-021**: System MUST implement first-time sync that downloads complete resource set: official syllabus, all past papers, one textbook metadata

**User Upload Workflow**

- **FR-022**: System MUST auto-upload student resources to `user_uploads/{student_id}/` in background without requiring explicit "Submit for Review" action
- **FR-023**: System MUST set uploaded resource visibility to "pending_review" and admin_approved to false by default
- **FR-024**: System MUST make pending resources visible only to admin and uploader (multi-tenant isolation)
- **FR-025**: System MUST queue S3 background upload for all user uploads using async task queue
- **FR-026**: System MUST allow admin to preview PDF content (first 3 pages inline) in review dashboard

**Admin Review Workflow**

- **FR-027**: System MUST provide admin dashboard listing all pending resources with columns: student name, resource title, upload date, file size
- **FR-028**: System MUST allow admin to Approve resource by clicking button, which updates visibility="public", admin_approved=true, sets approval_date
- **FR-029**: System MUST allow admin to Reject resource (silent - no student notification), which deletes file and database record
- **FR-030**: System MUST allow admin to Edit metadata (title, description, excerpts) before approving
- **FR-031**: System MUST allow admin to extract textbook excerpts and store in database for LLM prompt inclusion

**Resource Lifecycle State Machine**

- **FR-068**: System MUST implement linear state transitions for user uploads: uploaded → pending_review → approved OR rejected (terminal states)
- **FR-069**: System MUST set initial state to "pending_review" when student uploads resource
- **FR-070**: System MUST transition to "approved" state when admin clicks Approve (sets visibility="public", admin_approved=true)
- **FR-071**: System MUST transition to "rejected" state by deleting resource (file + database record) when admin clicks Reject - no restoration possible
- **FR-072**: System MUST prevent state transitions from approved back to pending_review (one-way approval)
- **FR-073**: System MUST allow student to re-upload deleted resource as new submission (creates new resource_id, resets to pending_review)

**Topic Generation Integration**

- **FR-032**: System MUST auto-select resources for topic generation based on relevance_score from `syllabus_point_resources` table, prioritizing highest scores
- **FR-033**: System MUST display quality scores in UI as percentages (e.g., "90% relevance") when showing selected resources
- **FR-034**: System MUST allow admin to manually override auto-selection by unchecking/adding resources in selection UI
- **FR-035**: System MUST construct LLM prompt including: syllabus learning outcomes, past paper question texts, textbook excerpts, with clear source attribution
- **FR-036**: System MUST track resource usage by creating `explanation_resource_usage` records after successful topic generation

**Multi-Tenant Isolation**

- **FR-037**: System MUST enforce visibility rules in ALL queries: public resources visible to all, private resources visible only to uploader + admin, pending resources visible to admin + uploader
- **FR-038**: System MUST filter user uploads by student_id in file storage and database queries to prevent unauthorized access
- **FR-039**: System MUST validate user permissions before serving file downloads via signed URLs or permission checks

**Data Encryption & Security**

- **FR-058**: System MUST enforce HTTPS for all API endpoints serving resources (in-transit encryption for all resource types)
- **FR-059**: System MUST enable S3 SSE-S3 encryption at rest for user data (authentication, personal info, student resource preferences)
- **FR-060**: System MUST enable S3 SSE-S3 encryption at rest for private student uploads (visibility="private" resources)
- **FR-061**: System MAY use S3 default encryption for public resources (syllabus, past papers, approved uploads) but not required
- **FR-062**: System MUST use signed URLs with expiration (1 hour) for private resource downloads to prevent unauthorized access

**Observability & Logging**

- **FR-063**: System MUST track basic metrics: total resource count, upload count per day, sync job success/failure rate, storage usage by type (syllabus/past_papers/user_uploads)
- **FR-064**: System MUST log all errors with severity levels (ERROR, WARNING, INFO) including: file upload failures, S3 sync failures, OCR failures, Cambridge website unreachable
- **FR-065**: System MUST log security events: failed authentication attempts, unauthorized resource access attempts, quota exceeded violations, admin approval/rejection actions
- **FR-066**: System MUST expose metrics endpoint for admin dashboard showing: total resources, resources by visibility (public/private/pending), S3 sync status, storage usage by student
- **FR-067**: System MUST retain error logs for 90 days and security event logs for 1 year for audit purposes

**S3 Background Upload**

- **FR-040**: System MUST queue S3 uploads to background task queue (Celery or similar) to avoid blocking API responses
- **FR-041**: System MUST retry failed S3 uploads 3 times with exponential backoff (1min, 5min, 15min)
- **FR-042**: System MUST update database sync_status field upon S3 upload completion or failure
- **FR-043**: System MUST send alert to admin if S3 upload fails after all retries
- **FR-054**: System MUST continue operating with local-only storage if S3 unavailable for extended period (24+ hours)
- **FR-055**: System MUST queue failed S3 uploads with status "pending_retry" in database for batch retry when S3 recovers
- **FR-056**: System MUST display S3 outage status in admin dashboard showing count of pending sync resources
- **FR-057**: System MUST automatically trigger batch S3 upload for queued resources when S3 connectivity restored

**Resource Tagging Interface**

- **FR-044**: System MUST provide manual tagging interface where admin can search resources and syllabus points by keyword
- **FR-045**: System MUST allow admin to create `syllabus_point_resources` links with adjustable relevance_score (slider 0-100%)
- **FR-046**: System MUST allow admin to specify page ranges for textbooks in metadata JSONB field (e.g., {"page_range": "245-267"})

**Full Text Search**

- **FR-047**: System MUST implement full-text search on PDF content using extracted text (OCR or native PDF text)
- **FR-048**: System MUST index past paper questions for keyword matching during auto-selection
- **FR-049**: System MUST index YouTube transcripts for searchability

**Resource Quotas & Limits**

- **FR-050**: System MUST enforce resource quota of 100 resources per student (user_uploads only, excluding public/official resources)
- **FR-051**: System MUST enforce total system capacity of 100K resources across all types (prevents unbounded growth)
- **FR-052**: System MUST reject new student uploads when quota reached with error "Resource limit reached (100/100). Delete unused resources to upload new ones."
- **FR-053**: System MUST display current quota usage in student dashboard (e.g., "72/100 resources used")

### Key Entities

- **Resource**: Represents any learning material (syllabus, past paper, textbook, video, user upload). Attributes: type, title, source_url, file_path, visibility, signature, metadata JSONB (flexible for type-specific fields like page_range, chapter, video_duration)

- **SyllabusPointResource**: Links resources to specific syllabus points with relevance scoring. Attributes: syllabus_point_id, resource_id, relevance_score (0-1 float), added_by (system/admin/student)

- **ExplanationResourceUsage**: Tracks which resources contributed to each generated explanation. Attributes: explanation_id, resource_id, contribution_weight (how much this resource influenced the explanation)

- **StudentResourcePreference**: User-specific resource preferences for personalized learning. Attributes: student_id, resource_id, enabled (bool), priority (int for ordering)

- **ResourceSyncStatus**: Tracks sync history and S3 upload status. Attributes: resource_id, last_sync_date, sync_status (success/failed/in_progress), s3_url, last_checked_date

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin can upload official Cambridge syllabus and 10 years of past papers, with all files stored locally and synced to S3, completing first-time setup in under 15 minutes
- **SC-002**: Daily sync job detects new Cambridge resources within 24 hours of publication and automatically downloads them with 99% success rate
- **SC-003**: Students can upload personal study materials under 50MB with files becoming available for private use immediately and queueing for admin review in under 5 seconds
- **SC-004**: Admin can review and approve 10 pending user uploads in under 10 minutes using preview and one-click approval workflow
- **SC-005**: Topic generation auto-selects most relevant resources (based on relevance scores) 90% of the time without admin override needed
- **SC-006**: System prevents duplicate resource downloads through signature matching, reducing storage usage by at least 30% compared to naive re-download approach
- **SC-007**: Multi-tenant isolation ensures 100% of queries correctly filter resources by visibility and student_id with zero unauthorized access incidents
- **SC-008**: Full-text search returns relevant resources within 2 seconds for keyword queries across 1000+ stored documents
- **SC-009**: S3 background uploads complete within 5 minutes for files under 50MB with 95% success rate on first attempt
- **SC-010**: OCR processing extracts searchable text from scanned PDFs with 85% accuracy for Economics-specific terminology

## Assumptions

- Cambridge website provides stable URLs for past paper downloads (documented pattern exists)
- Admin has AWS S3 credentials configured for background upload (credentials stored in environment variables)
- YouTube API quota is sufficient for expected video link volume (max 10 videos per day in Phase 1)
- Textbook excerpts fall under fair use for education (legal review not part of Phase 1)
- Single textbook in Phase 1 is sufficient for MVP validation (configurable for multiple in future)
- Daily sync at 2:00 AM is acceptable downtime window (low user activity period)
- 50MB file size limit is reasonable for student uploads (typical PDF notes are 1-10MB)
- OCR accuracy of 85% is acceptable for Economics terminology (manual correction available if needed)
- Virus scanning uses ClamAV or similar open-source solution (integration not specified but required)
- Signed URLs with 1-hour expiration handle private resource download authorization
- Resource quota of 100 per student balances personal usage needs with infrastructure costs for Phase 1 MVP
- System capacity of 100K total resources provides sufficient headroom for ~1000 students in Phase 1
- S3 SSE-S3 encryption provides adequate protection for user data and private uploads in Phase 1 (KMS not required for MVP)
- HTTPS enforcement is standard for all API endpoints (Let's Encrypt or similar for SSL certificates)
- Basic metrics and logging provide sufficient operational visibility for Phase 1 (comprehensive APM deferred to Phase 2)
- 90-day error log retention and 1-year security log retention meet audit requirements without excessive storage costs

## Constitutional Compliance

- **Principle I - Subject Accuracy**: Official Cambridge resources (syllabus, past papers) are authoritative sources verified through signature-based integrity checks
- **Principle V - Multi-Tenant Isolation**: All database queries filter by student_id and visibility, file storage isolates user uploads by student_id subdirectories
- **Principle IV - Spec-Driven Development**: This specification completed before implementation planning begins

## Dependencies

- **External Dependencies**:
  - Cambridge International website API/scraping access for past paper downloads
  - YouTube Data API v3 for video metadata and youtube-transcript-api for transcript extraction
  - AWS S3 or compatible object storage service with credentials
  - ClamAV or virus scanning service for upload safety

- **Internal Dependencies**:
  - Feature 006-resource-bank (generated explanations table and sync service foundation)
  - Existing multi-tenant authentication system (student_id from JWT tokens)
  - Background task queue (Celery recommended, or Python asyncio for Phase 1 MVP)

- **Technical Requirements**:
  - Python libraries: PyPDF2 (PDF parsing), pytesseract (OCR), youtube-transcript-api (transcripts), boto3 (S3 upload)
  - PostgreSQL JSONB support for flexible metadata storage
  - File system with sufficient storage (estimate 50GB for 10 years of past papers + user uploads)

## Out of Scope (Phase 1)

- **Embeddings-based search**: Phase 1 uses full-text keyword search only, embeddings planned for Phase 2
- **Multiple textbook support**: Phase 1 limited to 1 textbook integration, multiple textbooks in Phase 2
- **Collaborative resource editing**: Phase 1 admin-only editing, collaborative features (student annotations, comments) deferred
- **Mobile app file upload**: Phase 1 web UI only, mobile upload in Phase 3
- **Real-time sync notifications**: Phase 1 daily batch sync, real-time sync on mobile devices in Phase 3
- **Resource versioning**: Phase 1 replaces resources on signature change, full version history in Phase 2
- **Advanced quality scoring**: Phase 1 uses manual relevance scores, ML-based quality scoring in Phase 3
- **Resource recommendations**: Phase 1 auto-selection by relevance score only, collaborative filtering in Phase 3

## Phase 1 MVP Scope Summary

✅ **Included**:
- Official syllabus storage + daily sync
- Past paper storage (all years) + mark scheme linking
- 1 textbook integration (excerpts + metadata)
- User uploads (background auto-sync)
- Resource quality scoring (manual relevance scores)
- Auto-suggest resources + manual override
- Local storage + S3 background upload
- Manual tagging interface (resources → syllabus points)
- Signature-based differential sync
- Admin review workflow (Approve/Reject/Edit)
- Full-text search (keyword-based)
- OCR for scanned PDFs
- YouTube transcript extraction
- Multi-tenant isolation (public/private/pending visibility)

❌ **Deferred**:
- Embeddings-based semantic search
- Multiple textbook support
- Real-time sync
- Mobile app integration
- Resource versioning
- ML-based quality scoring
- Collaborative features
