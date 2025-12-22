# Feature Specification: AI Teaching System - Student Interface

**Feature Branch**: `003-ai-teaching-frontend`
**Created**: 2025-12-21
**Status**: Draft
**Input**: User description: "Phase IV: Frontend UI for AI Teaching System - Build 6 web pages (Coaching, Exam, Results, Feedback, Planner, Dashboard, Auth) to make all 6 AI teaching roles visible and usable. Student workflow: learn → coach → exam → results → feedback → plan. Next.js 15 + Tailwind CSS + TypeScript. Backend APIs already functional."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Tutoring Session (Priority: P1)

A student struggling with a specific Economics concept (e.g., "I don't understand price elasticity") wants to get personalized tutoring with adaptive explanations and Socratic questioning until they understand the concept.

**Why this priority**: This is the most critical student-facing feature after topic learning (already built). When students don't understand from the teaching page, they need immediate help. This completes the learn → get-help workflow which is the core value proposition of personalized AI teaching.

**Independent Test**: Can be fully tested by starting a coaching session, sending messages, receiving adaptive responses, and viewing the full conversation history. Delivers value as a standalone feature that helps students overcome knowledge gaps.

**Acceptance Scenarios**:

1. **Given** a student viewing a concept they don't understand, **When** they initiate a coaching session with their struggle area (e.g., "I don't understand price elasticity"), **Then** the coach asks a Socratic question to diagnose their misconception
2. **Given** an active coaching session, **When** the student responds to the coach's question, **Then** the coach provides a targeted explanation with analogies and asks a follow-up question
3. **Given** a coaching session in progress, **When** the student sends 5+ messages, **Then** the full conversation history is visible with clear role labels (student vs coach) and timestamps
4. **Given** a resolved coaching session, **When** the session ends, **Then** the system provides a summary with outcome (resolved/needs_more_help/refer_to_teacher) and option to revisit the topic explanation
5. **Given** multiple concurrent students, **When** each starts a coaching session, **Then** conversations are isolated with no cross-student data leakage

---

### User Story 2 - Practice Exam Attempt (Priority: P1)

A student preparing for Cambridge A-Level Economics wants to take a timed practice exam that simulates real exam conditions, with the ability to save progress and submit when complete.

**Why this priority**: Exam practice is the second most critical workflow after learning concepts. Students need to apply knowledge under exam conditions to prepare for real exams. This enables the learn → practice workflow which validates understanding.

**Independent Test**: Can be fully tested by generating an exam, displaying questions, accepting answers, tracking time, and submitting the completed attempt. Delivers value as a standalone feature for exam preparation.

**Acceptance Scenarios**:

1. **Given** a student ready to practice, **When** they request a new practice exam, **Then** the system displays exam metadata (subject, total marks, time limit) and starts the timer
2. **Given** an active exam attempt, **When** the student views a question, **Then** the question text, marks, and input area are displayed with clear formatting
3. **Given** a question with multiple parts (e.g., Question 1(a), 1(b), 1(c)), **When** the student answers, **Then** each part has a separate input area with marks indicated
4. **Given** an exam in progress, **When** the student navigates between questions, **Then** previously entered answers are preserved and visible
5. **Given** a completed exam, **When** the student submits, **Then** the system confirms submission, stops the timer, and redirects to results (or results pending screen if marking is async)
6. **Given** an exam with a time limit (e.g., 90 minutes), **When** time expires, **Then** the system auto-submits the attempt and displays a timeout notification

---

### User Story 3 - View Marking Results & Feedback (Priority: P1)

After submitting a practice exam, a student wants to view their marks, see which questions they got right/wrong, read detailed feedback on errors, and understand why marks were deducted.

**Why this priority**: Viewing results completes the practice → feedback loop which is essential for learning. Without seeing mistakes and understanding errors, students cannot improve. This is the third step in the core workflow (learn → practice → get-marked).

**Independent Test**: Can be fully tested by displaying a marked attempt with scores, feedback, and error breakdowns. Delivers value as a standalone feature that shows students exactly where they went wrong.

**Acceptance Scenarios**:

1. **Given** a marked attempt, **When** the student views results, **Then** the overall score (e.g., "45/75"), percentage, and grade are prominently displayed
2. **Given** a marked attempt, **When** the student views question-level results, **Then** each question shows marks awarded vs max marks (e.g., "18/25") with color-coding (green for full marks, amber for partial, red for low/zero)
3. **Given** a question with errors, **When** the student expands feedback, **Then** the system displays categorized errors (factual, analytical, evaluative) with specific explanations of what was wrong
4. **Given** a question with partial marks, **When** the student views feedback, **Then** the system highlights which parts of the answer were good and which need improvement
5. **Given** an Economics essay question, **When** the student views marking breakdown, **Then** AO1/AO2/AO3 scores are shown separately with level descriptors (e.g., "Level 3: 11-15 marks - Good analysis...")
6. **Given** a low-confidence mark (needs review flag), **When** the student views results, **Then** the system displays a notice that the mark may be reviewed by a teacher

---

### User Story 4 - View Weakness Analysis & Improvement Plan (Priority: P2)

After receiving marks, a student wants to see a comprehensive analysis of their weaknesses across multiple attempts, understand patterns in their mistakes, and receive an actionable improvement plan.

**Why this priority**: Once students have taken exams and seen results (P1), they need guidance on how to improve. This is the next logical step in the workflow (practice → results → improve). However, it's P2 because students can still benefit from P1 features without this.

**Independent Test**: Can be fully tested by displaying weakness analysis from multiple attempts and showing an improvement plan. Delivers value as a standalone feature that identifies patterns and provides actionable next steps.

**Acceptance Scenarios**:

1. **Given** 3+ marked attempts, **When** the student requests weakness analysis, **Then** the system displays categorized weaknesses (e.g., "Microeconomics: weak on elasticity calculations", "Macroeconomics: struggles with evaluation")
2. **Given** a weakness analysis, **When** the student views it, **Then** each weakness shows evidence (question IDs where errors occurred) and severity (critical/moderate/minor)
3. **Given** an improvement plan, **When** the student views it, **Then** specific action items are listed (e.g., "Review price elasticity concept", "Practice 5 elasticity calculation questions", "Watch video on PED vs YED")
4. **Given** multiple improvement plans over time, **When** the student compares progress, **Then** the system shows which weaknesses were resolved and which remain
5. **Given** a weakness in a specific topic, **When** the student clicks it, **Then** the system links directly to the teaching explanation for that topic

---

### User Story 5 - View & Follow Study Schedule (Priority: P2)

A student wants to view their personalized study plan, see which topics to study each day, mark sessions as complete, and track progress toward their exam date.

**Why this priority**: Study planning helps students organize their learning over time. However, it's P2 because students can still learn, practice, and improve (P1 features) without a formal schedule. This enhances the experience but isn't blocking for core value.

**Independent Test**: Can be fully tested by displaying a study schedule, showing daily topics, and allowing students to mark sessions complete. Delivers value as a standalone feature for time management.

**Acceptance Scenarios**:

1. **Given** a generated study plan, **When** the student views their schedule, **Then** the system displays a calendar view with topics assigned to each day
2. **Given** a study schedule, **When** the student views a specific day, **Then** the system shows topics to study, estimated time, and activities (study/practice/review)
3. **Given** a scheduled study session, **When** the student completes it, **Then** they can mark it complete and the system updates progress tracking
4. **Given** a study plan with spaced repetition, **When** the student views the schedule, **Then** topics appear multiple times at increasing intervals (e.g., Day 1, Day 4, Day 11)
5. **Given** a multi-topic study day, **When** the student views it, **Then** topics are interleaved (e.g., Topic A → Topic B → Topic A → Topic C) with explanations of why
6. **Given** missed study sessions, **When** the student views their plan, **Then** overdue sessions are highlighted with options to reschedule

---

### User Story 6 - Dashboard Overview (Priority: P2)

A student wants to see an at-a-glance overview of their progress, including recent activity, upcoming study sessions, exam scores over time, and current weaknesses.

**Why this priority**: The dashboard provides a summary view of all features, but students can navigate directly to coaching, exams, results, etc. (P1) without needing this overview. It's P2 because it enhances navigation and motivation but isn't required for core functionality.

**Independent Test**: Can be fully tested by displaying summary statistics and recent activity. Delivers value as a standalone feature for progress monitoring.

**Acceptance Scenarios**:

1. **Given** a logged-in student, **When** they view the dashboard, **Then** recent activity is displayed (e.g., "Last exam: 62/75", "Last coaching session: Price Elasticity")
2. **Given** multiple exam attempts, **When** the student views the dashboard, **Then** a progress chart shows score trends over time
3. **Given** active weaknesses, **When** the student views the dashboard, **Then** top 3 weaknesses are highlighted with quick links to improvement plans
4. **Given** a study schedule, **When** the student views the dashboard, **Then** today's study topics are shown with a "Start Studying" button
5. **Given** no recent activity, **When** the student views the dashboard, **Then** suggested next actions are displayed (e.g., "Start learning a new topic", "Take a practice exam")

---

### User Story 7 - User Authentication (Priority: P3)

A student wants to create an account, log in securely, and access their personalized learning data across sessions without other students seeing their information.

**Why this priority**: Authentication is infrastructure required for multi-tenant isolation, but the core AI teaching features (P1-P2) can be demonstrated with a demo account. This is P3 because it's essential for production but not blocking for feature development and testing.

**Independent Test**: Can be fully tested by registering, logging in, and verifying session persistence. Delivers value as a standalone feature for security and personalization.

**Acceptance Scenarios**:

1. **Given** a new user, **When** they register with email and password, **Then** an account is created and they are logged in automatically
2. **Given** a registered user, **When** they log in with correct credentials, **Then** they access their dashboard with personalized data
3. **Given** a logged-in user, **When** they close the browser and return, **Then** they remain logged in (session persistence)
4. **Given** a logged-in user, **When** they log out, **Then** their session is cleared and they are redirected to the login page
5. **Given** an incorrect password, **When** a user attempts to log in, **Then** an error message is displayed without revealing whether the email exists
6. **Given** multiple students logged in, **When** each accesses their data, **Then** no cross-student information is visible (multi-tenant isolation)

---

### Edge Cases

- What happens when a student loses internet connection during an exam attempt? (Answer persistence, auto-save, resume capability)
- How does the system handle concurrent coaching sessions from the same student? (Allow or prevent)
- What happens if the backend API is unavailable when a student tries to view results? (Error handling, offline mode, cached data)
- How does the system handle extremely long answers (>10,000 characters)? (Character limits, validation)
- What happens when a student navigates away from an active exam without submitting? (Auto-save, warning dialogs)
- How does the system handle slow API responses (>5 seconds)? (Loading states, timeout handling)
- What happens if a student tries to access another student's results via URL manipulation? (Authorization checks)
- How does the system display questions with diagrams or tables? (Image rendering, responsive design)

---

## Requirements *(mandatory)*

### Functional Requirements

#### Coaching Page
- **FR-001**: System MUST allow students to initiate coaching sessions with a struggle area description
- **FR-002**: System MUST display conversation history with clear role labels (student/coach) and timestamps
- **FR-003**: System MUST allow students to send messages and receive adaptive responses from the coach
- **FR-004**: System MUST preserve conversation history across page refreshes
- **FR-005**: System MUST display session outcome (resolved/needs_more_help/refer_to_teacher) when coach determines session is complete

#### Exam Page
- **FR-006**: System MUST display exam metadata (subject, total marks, time limit) before starting
- **FR-007**: System MUST show a timer counting down from the time limit (if specified)
- **FR-008**: System MUST provide input areas for each question/sub-part with marks indicated
- **FR-009**: System MUST preserve answers when navigating between questions
- **FR-010**: System MUST allow students to submit the exam attempt manually
- **FR-011**: System MUST auto-submit when time expires (if time limit exists)
- **FR-012**: System MUST prevent editing after submission

#### Results Page
- **FR-013**: System MUST display overall score (marks awarded/total marks) and percentage
- **FR-014**: System MUST show question-level scores with color-coding (green/amber/red)
- **FR-015**: System MUST display categorized errors (factual/analytical/evaluative) with explanations
- **FR-016**: System MUST show AO1/AO2/AO3 breakdown for Economics questions
- **FR-017**: System MUST highlight low-confidence marks with a "needs review" notice
- **FR-018**: System MUST link to model answers or improvement suggestions

#### Feedback Page
- **FR-019**: System MUST display categorized weaknesses with evidence (question IDs)
- **FR-020**: System MUST show severity levels (critical/moderate/minor) for each weakness
- **FR-021**: System MUST provide actionable improvement plan with specific tasks
- **FR-022**: System MUST link weaknesses to relevant teaching topics
- **FR-023**: System MUST allow students to compare progress across multiple improvement plans

#### Planner Page
- **FR-024**: System MUST display study schedule in calendar view with topics assigned to days
- **FR-025**: System MUST show daily topics, estimated time, and activities (study/practice/review)
- **FR-026**: System MUST allow students to mark study sessions as complete
- **FR-027**: System MUST highlight overdue sessions with reschedule options
- **FR-028**: System MUST explain spaced repetition intervals (why topics repeat)

#### Dashboard
- **FR-029**: System MUST display recent activity (last exam, last coaching session)
- **FR-030**: System MUST show progress chart with exam scores over time
- **FR-031**: System MUST highlight top 3 current weaknesses with quick links
- **FR-032**: System MUST show today's study topics (if study plan exists)
- **FR-033**: System MUST provide suggested next actions when no recent activity

#### Authentication
- **FR-034**: System MUST allow new users to register with email and password
- **FR-035**: System MUST allow registered users to log in with credentials
- **FR-036**: System MUST persist login sessions across browser closures
- **FR-037**: System MUST allow users to log out and clear sessions
- **FR-038**: System MUST enforce multi-tenant isolation (no cross-student data access)
- **FR-039**: System MUST validate credentials securely without revealing email existence on failure

### Key Entities

- **Student**: User account with email, password, progress data, and learning history
- **Coaching Session**: Conversation between student and coach with messages, timestamps, and outcome
- **Exam Attempt**: Student's attempt at a practice exam with start time, end time, and answers
- **Question Answer**: Student's answer to a single question within an attempt
- **Marking Result**: Marks awarded, feedback, errors, and confidence score for a question or attempt
- **Weakness Analysis**: Categorized weaknesses with evidence and severity across multiple attempts
- **Improvement Plan**: Actionable tasks to address weaknesses with progress tracking
- **Study Schedule**: Calendar of study sessions with topics, activities, and completion status

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can initiate and complete a coaching session in under 5 minutes without errors
- **SC-002**: Students can navigate through a 3-question exam, submit answers, and view results in under 10 minutes
- **SC-003**: 90% of students successfully view their weakness analysis and improvement plan on first attempt without confusion
- **SC-004**: Students can view their study schedule and mark a session complete in under 2 minutes
- **SC-005**: Dashboard loads and displays all summary data in under 3 seconds
- **SC-006**: Students can register, log in, and access personalized data in under 2 minutes
- **SC-007**: System handles 100 concurrent students accessing different pages without performance degradation
- **SC-008**: Zero data leakage incidents (students cannot access other students' data)
- **SC-009**: Exam answers are auto-saved every 30 seconds to prevent data loss on disconnect
- **SC-010**: All pages are responsive and usable on desktop, tablet, and mobile devices

### User Satisfaction Metrics

- **SC-011**: 85%+ of students report that coaching sessions helped them understand difficult concepts
- **SC-012**: 90%+ of students find marking feedback clear and actionable
- **SC-013**: 80%+ of students follow their study schedule for at least 2 weeks
- **SC-014**: 95%+ of students can navigate between all pages without assistance

---

## Assumptions

- Backend APIs are fully functional and tested (coaching, exam, marking, feedback, planning services)
- Database contains Economics 9708 syllabus points and seeded data
- Authentication backend endpoints (/api/auth/register, /api/auth/login) exist
- All API responses follow consistent error handling patterns
- Students have modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Students have stable internet connection (occasional disconnects handled gracefully)
- Exam questions are text-based (diagrams handled as images or descriptions)
- Study schedules are pre-generated by backend (frontend displays only)

---

## Dependencies

- **Backend APIs**: All 6 AI teaching role APIs must be functional and deployed
- **Database**: Economics 9708 syllabus, questions, and mark schemes seeded
- **Authentication**: JWT token-based auth implemented in backend
- **File Storage**: If diagrams or images exist, they must be accessible via URLs

---

## Out of Scope (Phase IV)

- Mobile native apps (iOS/Android) - web-only for now
- Video/audio explanations - text-based teaching only
- Handwritten answer input - typed answers only
- Real-time collaboration (multiple students studying together)
- Teacher admin panel (separate feature)
- Multi-language support (English only)
- Accessibility features (WCAG compliance deferred to Phase V)
- Dark mode (light mode only)
- Offline mode (requires internet connection)

---

## Non-Functional Requirements

### Performance
- Page load time: <3 seconds on average
- API response time: <2 seconds for data fetching
- Auto-save exam answers: Every 30 seconds

### Security
- All API calls must use authentication tokens
- No sensitive data (passwords) stored in browser localStorage
- HTTPS required in production
- Multi-tenant isolation strictly enforced

### Usability
- Intuitive navigation (students can find features without training)
- Clear error messages (no technical jargon)
- Loading states for all async operations
- Consistent UI patterns across all pages

### Compatibility
- Modern browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Screen sizes: Desktop (1920x1080), Tablet (1024x768), Mobile (375x667)

---

## Open Questions

None at this time. Feature is well-defined based on existing backend APIs and user workflow.

---

**Status**: ✅ Specification Complete
**Next Steps**: Run `/sp.clarify` if needed, then `/sp.plan` to create implementation plan
