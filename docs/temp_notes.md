● Here's where to find everything:

  📍 Documentation Locations

  | Document                   | Path                                                          | Purpose                                  |
  |----------------------------|---------------------------------------------------------------|------------------------------------------|
  | Quick Start Guide          | specs/008-academic-level-hierarchy/quickstart.md              | Setup walkthrough & API examples         |
  | Requirements Checklist     | specs/008-academic-level-hierarchy/checklists/requirements.md | Spec validation                          |
  | Tasks (with verifications) | specs/008-academic-level-hierarchy/tasks.md                   | All T001-T067 including acceptance tests |
  | Full Spec                  | specs/008-academic-level-hierarchy/spec.md                    | User stories & requirements              |
  | Data Model                 | specs/008-academic-level-hierarchy/data-model.md              | ER diagram & relationships               |

  ---
  🚀 Setup & Walkthrough Sequence

  Step 1: Start Backend & Frontend

  # Terminal 1 - Backend
  cd backend && uv run uvicorn src.main:app --reload

  # Terminal 2 - Frontend
  cd frontend && pnpm dev

  Step 2: Login as Admin

  Navigate to http://localhost:3000/login and sign in.

  Step 3: Admin Setup Wizard (3-Step Flow)

  Navigate to http://localhost:3000/admin/setup

  The wizard guides you through:

  | Step | URL                          | Action                                                     |
  |------|------------------------------|------------------------------------------------------------|
  | 1️⃣   | /admin/setup/academic-levels | Create "A-Level" (code: A, board: Cambridge International) |
  | 2️⃣   | /admin/setup/subjects        | Create "Economics" under A-Level                           |
  | 3️⃣   | /admin/setup/syllabus        | Upload syllabus PDF (code: 9708, years: 2023-2025)         |

  Step 4: Verify Student View

  Navigate to http://localhost:3000/teaching

  You should see:
  - Breadcrumb: A-Level > Economics > 9708
  - Header subtitle showing hierarchy
  - Topics loaded from syllabus

  ---
  ✅ Manual Verification Checklist

  From tasks.md, these are the acceptance verification tasks:

  US1 - Academic Levels (T025-T027)

  - Admin can create academic level via /admin/setup/academic-levels
  - List shows created levels with subject counts
  - Duplicate code returns 409 error

  US2 - Subjects (T036-T038)

  - Create subject under academic level
  - Subject appears in level detail view
  - Verify subject-level relationship persists

  US3 - Syllabi (T046-T047)

  - Upload syllabus for subject
  - Topics extracted and displayed

  US4 - Navigation (T053-T054)

  - Teaching page shows A-Level > Economics > 9708 breadcrumb
  - Header shows dynamic hierarchy subtitle

  US5 - Edit/Delete (T061-T063)

  - Edit academic level name → verify change persists
  - Delete blocked when level has subjects (400 error)
  - Delete works when level is empty

  ---
  🔗 Quick API Test

  # Get full hierarchy tree
  curl http://localhost:8000/api/hierarchy | jq

  # List academic levels
  curl http://localhost:8000/api/academic-levels | jq