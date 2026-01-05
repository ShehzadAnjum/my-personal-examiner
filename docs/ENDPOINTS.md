# My Personal Examiner - Available Endpoints

**Last Updated:** 2026-01-05

## 📚 Valid Frontend Routes

### Core Features (Phase I Complete ✅)

#### 1. Teaching Module
- **`/teaching`** - Teaching homepage (topic list)
- **`/teaching/[topicId]`** - Specific topic explanation
  - Example: `/teaching/1.1.1` (Economic Problem)
  - Example: `/teaching/1.2.1` (Demand)

#### 2. Coaching Module
- **`/coaching`** - Coaching homepage (start new session)
- **`/coaching/[sessionId]`** - Active coaching session
- **`/coaching/history`** - Past coaching sessions

#### 3. Resource Bank Module
- **`/resources`** - Student resource browser
  - Upload PDFs, videos, YouTube transcripts
  - Search and filter resources
  - View quota (X/100 resources)
- **`/resources/admin`** - Admin review dashboard (admin only)
  - Approve/reject pending uploads
  - Preview PDF resources

### Authentication
- **`/login`** - Login page (Email/Password or Google OAuth)
- **`/`** - Landing page (redirects to `/teaching` if authenticated)

### Coming Soon 🚧
- **`/planner`** - Study planner (Phase V)
- **`/examiner`** - Exam practice (Phase V)

---

## 🔧 Backend API Endpoints

**Base URL:** `http://localhost:8000`

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Login (returns student profile)
- `GET /api/auth/student-by-email?email={email}` - Find student by email

### Teaching
- `GET /api/teaching/topics/{topicId}/explanation?student_id={id}` - Get topic explanation
- `POST /api/teaching/topics/{topicId}/generate?student_id={id}` - Generate new explanation

### Coaching
- `POST /api/coaching/sessions?student_id={id}` - Start new coaching session
- `GET /api/coaching/sessions/{sessionId}?student_id={id}` - Get session details
- `POST /api/coaching/sessions/{sessionId}/messages?student_id={id}` - Send message
- `GET /api/coaching/sessions/history?student_id={id}` - Get session history

### Resource Bank
- `POST /api/resources/upload?student_id={id}` - Upload PDF/file
- `POST /api/resources/upload/youtube?student_id={id}` - Upload YouTube video
- `GET /api/resources?student_id={id}&visibility={public|private|pending_review}` - List resources
- `GET /api/resources/search?query={keywords}&student_id={id}` - Search resources
- `GET /api/resources/quota?student_id={id}` - Get quota status
- `GET /api/resources/{resourceId}?student_id={id}` - Get resource details
- `DELETE /api/resources/{resourceId}?student_id={id}` - Delete own resource

### Admin (Admin only)
- `GET /api/admin/resources/pending?student_id={id}` - List pending resources
- `POST /api/admin/resources/{resourceId}/approve?student_id={id}` - Approve resource
- `POST /api/admin/resources/{resourceId}/reject?student_id={id}` - Reject resource

---

## 🎯 Navigation Menu

**Desktop:** Visible in top bar (right side)
- Teaching | Coaching | Resources

**Mobile:** Hamburger menu (☰) in top right
- Full navigation drawer with descriptions

---

## ❌ Invalid Endpoints (404 Errors)

These endpoints **do not exist** and will return 404:

- ❌ `/teaching/resources` - Use `/resources` instead
- ❌ `/coaching/teaching` - Use `/teaching` instead
- ❌ `/resources/teaching` - Use `/teaching` instead

**Common Mistake:** Confusing page routes - each feature has its own root path.

---

## 🔑 Authentication Flow

### Google OAuth (Better Auth)
1. Click "Sign in with Google" on `/login`
2. Google redirects back with user info
3. Better Auth creates record in `user` table
4. Frontend calls `/api/student` which:
   - Checks if student exists in `students` table
   - Creates student record if missing
   - Returns `student_id` for API calls

### Email/Password
1. Register via `/login` signup form (creates records in both Better Auth and backend)
2. Login via `/login` (Better Auth validates)
3. Frontend gets `student_id` via `/api/student`

---

## 🐛 Troubleshooting

### "Content Not Available" Error
**Cause:** Trying to access invalid endpoint (e.g., `/teaching/resources`)

**Fix:** Use correct endpoints listed above

### "No pending resources to review"
**Cause:** All resources are already approved (admins auto-approve their uploads)

**Fix:** This is correct behavior - only student uploads show as pending

---

## 🔒 Security & Privacy Model

### Multi-Tenant Data Isolation

**Students can ONLY see:**
- ✅ All public resources (approved by admin)
- ✅ Their own private resources
- ✅ Their own pending resources
- ❌ **CANNOT** see other students' private resources
- ❌ **CANNOT** see other students' pending resources

**Admins can see:**
- ✅ All resources from all users (all statuses)
- ✅ Full visibility into system-wide resources
- ✅ Can approve/reject any pending upload

### Upload Workflow

**Student Upload:**
1. Student uploads PDF/video → Status: `pending_review`
2. Only visible to: Student (uploader) + Admins
3. Admin reviews and approves → Status: `public`
4. Now visible to: Everyone

**Admin Upload:**
1. Admin uploads PDF/video → Status: `public` (auto-approved)
2. Immediately visible to: Everyone
3. No review needed

### "Failed to load resource: 404"
**Cause:** Accessing non-existent page or API endpoint

**Fix:** Check browser console for exact failing URL, compare with valid endpoints above

---

## 📖 Usage Examples

### Upload a PDF
1. Go to `/resources`
2. Click "Upload" button
3. Drag-drop PDF or click to browse
4. Set title and type (textbook, past_paper, etc.)
5. Submit (auto-approved for admins, pending for students)

### Search Resources
1. Go to `/resources`
2. Type keywords in search box
3. Press Enter or click "Search"
4. Results show matching title/content

### Filter Resources (Role-Based)

**For Students:**
- **Public** - All approved public resources
- **My Private** - Only your private resources
- **My Pending** - Your uploads awaiting admin approval

**For Admins:**
- **All** - All resources from all users
- **Public** - All public resources
- **Private** - All private resources (from all users)
- **Pending Review (All)** - All pending uploads from all students

### Access Teaching
1. Go to `/teaching`
2. Click on any topic (e.g., "1.1.1 Economic Problem")
3. System generates explanation if not exists
4. Read explanation with diagrams and examples

---

**Questions?** Check the navigation menu or contact support.
