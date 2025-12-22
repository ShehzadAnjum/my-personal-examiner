# Feature Specification: Coaching Page - Interactive AI Tutoring

**Feature Branch**: `004-coaching-page`
**Created**: 2025-12-21
**Status**: Draft
**Input**: User description: "Coaching Page - Interactive AI Tutoring: Students initiate coaching sessions by describing their struggle (e.g., 'I don't understand price elasticity'). System displays chat interface with student/coach message bubbles, timestamps, and real-time responses. Coach asks Socratic questions to diagnose misconceptions, provides targeted explanations with analogies, and adapts follow-up questions. Session ends with outcome (resolved/needs_more_help/refer_to_teacher). Backend APIs exist: POST /api/coaching/tutor-session (start), POST /api/coaching/session/{id}/respond (send message), GET /api/coaching/session/{id} (get transcript). Chat UI similar to ChatGPT/WhatsApp with conversation history, loading states, error handling."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start Coaching Session (Priority: P1)

A student struggling with a specific Economics concept wants to get immediate help by describing their confusion and receiving an initial diagnostic question from the AI coach.

**Why this priority**: This is the entry point for the entire coaching feature. Without the ability to start a session, no other coaching functionality works. This is the minimum viable product (MVP) that delivers immediate value by connecting confused students with AI help.

**Independent Test**: Can be fully tested by submitting a struggle description (e.g., "I don't understand price elasticity"), receiving a session ID, and seeing the coach's first Socratic question. Delivers value even without message history or session outcomes.

**Acceptance Scenarios**:

1. **Given** a logged-in student on the coaching page, **When** they enter their struggle area "I don't understand price elasticity" and click "Start Session", **Then** a new session is created and the coach responds with a diagnostic Socratic question
2. **Given** a student with no active session, **When** they submit an empty struggle description, **Then** the system displays an error "Please describe what you're struggling with"
3. **Given** a student starting a new session, **When** the backend API is slow (>3 seconds), **Then** a loading indicator is displayed with message "Coach is preparing your session..."
4. **Given** a student, **When** the backend API fails (500 error), **Then** an error message is displayed "Unable to start session. Please try again."
5. **Given** multiple students, **When** each starts a coaching session, **Then** sessions are isolated with unique session IDs and no cross-student data leakage

---

### User Story 2 - Chat Conversation (Priority: P1)

During an active coaching session, a student wants to send messages to the coach, receive adaptive responses, and see the full conversation history with clear visual distinction between student and coach messages.

**Why this priority**: This is the core interaction loop that makes coaching valuable. Without back-and-forth conversation, the coach cannot diagnose misconceptions or provide targeted help. This must work for coaching to have any impact.

**Independent Test**: Can be fully tested by sending multiple student messages and receiving coach responses within an active session. Conversation history is visible with role labels (student/coach) and timestamps. Delivers value as the primary teaching mechanism.

**Acceptance Scenarios**:

1. **Given** an active coaching session, **When** the student sends a message "I think elasticity is about how prices change", **Then** the message appears in the chat history as a student message and the coach responds with a follow-up question or clarification
2. **Given** an ongoing conversation, **When** the student views the chat, **Then** all messages are displayed with visual distinction (student messages aligned right, coach messages aligned left) and timestamps in human-readable format (e.g., "2 minutes ago")
3. **Given** a student sending a message, **When** the coach is processing (API call in progress), **Then** a typing indicator is shown (e.g., "Coach is thinking...")
4. **Given** a long conversation (15+ messages), **When** the student scrolls, **Then** the chat automatically scrolls to the latest message but allows manual scrolling to review history
5. **Given** a student entering a very long message (>2000 characters), **When** they attempt to send, **Then** the system displays an error "Message too long. Please keep it under 2000 characters."
6. **Given** a network disconnection, **When** the student sends a message, **Then** the system displays "Message failed to send. Retrying..." and automatically retries when connection is restored

---

### User Story 3 - Session Outcome & Conclusion (Priority: P2)

When the coach determines the session has reached a conclusion, the student wants to see the outcome (resolved/needs_more_help/refer_to_teacher) and have options for next steps.

**Why this priority**: While important for closure and guidance, this is P2 because the core value (P1) is the conversation itself. Students can still benefit from coaching even without a formal outcome. This enhances the experience but isn't blocking for core functionality.

**Independent Test**: Can be fully tested by completing a coaching session until the coach provides an outcome, displaying it clearly, and offering next action options. Delivers value by guiding students on what to do next.

**Acceptance Scenarios**:

1. **Given** a coaching session where the coach determines understanding is achieved, **When** the coach sends the final message, **Then** the system displays "Session Resolved ✓" with a summary and option to "Review Topic Explanation"
2. **Given** a session where the student still struggles, **When** the coach determines more help is needed, **Then** the system displays "Needs More Practice" with suggestions for practice problems
3. **Given** a complex topic beyond coaching scope, **When** the coach recommends deeper teaching, **Then** the system displays "Refer to Teacher" with a link to the full topic explanation page
4. **Given** a concluded session, **When** the student views the outcome, **Then** options are provided: "Start New Session", "Review This Session", or "Back to Dashboard"
5. **Given** an ended session, **When** the student tries to send a new message, **Then** the input is disabled and a message displays "Session ended. Please start a new session to continue."

---

### User Story 4 - View Past Session History (Priority: P3)

A student wants to review previous coaching sessions to revisit explanations and see how they overcame past misconceptions.

**Why this priority**: This is P3 because it's a nice-to-have feature that enhances learning but isn't required for the core coaching workflow (P1-P2). Students can still get help, have conversations, and see outcomes without accessing past sessions.

**Independent Test**: Can be fully tested by listing past sessions with dates/topics and allowing students to view full transcripts. Delivers value for review and reflection.

**Acceptance Scenarios**:

1. **Given** a student with 5+ past coaching sessions, **When** they navigate to session history, **Then** a list of sessions is displayed with topic, date, and outcome
2. **Given** a past session, **When** the student clicks to view it, **Then** the full conversation transcript is displayed in read-only mode
3. **Given** no past sessions, **When** the student views history, **Then** a message displays "No coaching sessions yet. Start your first session to get help!"

---

### Edge Cases

- What happens when a student loses internet connection mid-conversation? (Auto-retry, queue messages, show connection status)
- What happens if a student starts a new session while one is already active? (Allow or warn about existing session)
- What happens when the coach API takes >10 seconds to respond? (Timeout, allow retry, don't freeze UI)
- What happens if a student refreshes the page during an active session? (Resume session, preserve conversation)
- What happens when a student sends messages too quickly (spam)? (Rate limiting, show "Please wait" message)
- What happens if the session transcript is very long (50+ messages)? (Pagination, virtual scrolling, performance optimization)
- What happens if a student tries to view another student's session via URL manipulation? (Authorization check, 403 error)
- What happens when special characters or emojis are used in messages? (Proper escaping, rendering)

---

## Requirements *(mandatory)*

### Functional Requirements

#### Session Initiation
- **FR-001**: System MUST allow students to initiate a coaching session by entering their struggle area (minimum 10 characters)
- **FR-002**: System MUST create a unique session ID when a session starts
- **FR-003**: System MUST display the coach's first diagnostic question within 5 seconds of session creation
- **FR-004**: System MUST show a loading indicator while the session is being created
- **FR-005**: System MUST validate that the struggle description is not empty before allowing submission

#### Chat Interface
- **FR-006**: System MUST display conversation history with visual distinction between student and coach messages
- **FR-007**: System MUST show timestamps for each message in human-readable format (e.g., "2 minutes ago", "10:45 AM")
- **FR-008**: System MUST align student messages to the right and coach messages to the left (or use other clear visual distinction)
- **FR-009**: System MUST allow students to send messages with minimum 1 character and maximum 2000 characters
- **FR-010**: System MUST display a typing indicator when the coach is generating a response
- **FR-011**: System MUST auto-scroll to the latest message when a new message is added
- **FR-012**: System MUST allow manual scrolling to review message history without auto-scroll interference

#### Session Management
- **FR-013**: System MUST preserve conversation history across page refreshes
- **FR-014**: System MUST detect when a coach response includes a session outcome (resolved/needs_more_help/refer_to_teacher)
- **FR-015**: System MUST display the session outcome prominently when session ends
- **FR-016**: System MUST disable message input when session has ended
- **FR-017**: System MUST provide next action options when session concludes

#### Error Handling
- **FR-018**: System MUST display user-friendly error messages when API calls fail
- **FR-019**: System MUST automatically retry failed message sends (up to 3 attempts)
- **FR-020**: System MUST show connection status when network disconnection is detected
- **FR-021**: System MUST prevent message submission while a previous message is being sent

#### Multi-Tenant Security
- **FR-022**: System MUST enforce session access controls (students can only access their own sessions)
- **FR-023**: System MUST validate session ownership before displaying conversation history
- **FR-024**: System MUST not allow cross-student session access via URL manipulation

### Key Entities

- **Coaching Session**: A conversation between a student and AI coach with unique ID, topic, messages, and outcome
- **Message**: A single chat message with role (student/coach), content, timestamp, and optional metadata
- **Session Outcome**: The conclusion status (resolved/needs_more_help/refer_to_teacher) with summary and next actions
- **Student**: User account accessing the coaching feature with session history

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can initiate a coaching session and receive the first coach question in under 5 seconds
- **SC-002**: Students can send a message and receive a coach response in under 10 seconds (95th percentile)
- **SC-003**: 90% of students successfully complete at least one full coaching conversation (3+ message exchanges)
- **SC-004**: Zero data leakage incidents (students cannot access other students' sessions)
- **SC-005**: Chat interface handles 50+ message conversations without performance degradation
- **SC-006**: Message send failures auto-retry successfully 95% of the time within 30 seconds
- **SC-007**: Students can resume an active session after page refresh without data loss
- **SC-008**: All messages display with correct role labels (student/coach) and readable timestamps

### User Satisfaction Metrics

- **SC-009**: 85%+ of students report that the chat interface is intuitive and easy to use
- **SC-010**: 80%+ of students report that coaching sessions helped them understand their confusion
- **SC-011**: 90%+ of students can distinguish between their messages and coach messages without confusion
- **SC-012**: 75%+ of students complete sessions to outcome (don't abandon mid-conversation)

---

## Assumptions

- Backend coaching APIs are fully functional and tested (POST /api/coaching/tutor-session, POST /api/coaching/session/{id}/respond, GET /api/coaching/session/{id})
- Authentication is implemented and provides student_id for session isolation
- Backend returns properly formatted JSON responses with message content, role, and timestamps
- Coach responses are generated within 10 seconds (backend performance assumption)
- Students have modern browsers with JavaScript enabled
- Students have stable internet connection (occasional disconnects handled gracefully)
- Session transcripts are stored in database (not just in-memory)
- Backend enforces session ownership (students can only access their own sessions)

---

## Dependencies

- **Authentication System**: Must provide logged-in student_id
- **Backend Coaching API**: All 3 endpoints functional (start session, send message, get transcript)
- **Database**: Stores coaching sessions and message history
- **Network**: Real-time communication requires stable connection

---

## Out of Scope

- Voice/audio coaching (text-only chat)
- Real-time collaboration (multiple students in one session)
- Coach avatars or profile pictures
- Message editing after sending
- Message deletion
- File/image attachments in messages
- Session scheduling (sessions are on-demand, not scheduled)
- Teacher/admin oversight of sessions (student-only feature)
- Session analytics dashboard (separate feature)
- Export/download session transcripts

---

## Non-Functional Requirements

### Performance
- Session creation: <3 seconds
- Message send: <2 seconds
- Coach response: <10 seconds (95th percentile)
- Chat scroll: 60 FPS smooth scrolling
- Handles 50+ messages without lag

### Security
- All API calls use authentication tokens
- Session IDs are non-guessable (UUIDs)
- No sensitive data in localStorage
- HTTPS required in production

### Usability
- Clear visual distinction between student and coach messages
- Intuitive message input (Enter to send, Shift+Enter for new line)
- Clear loading states for all async operations
- Error messages are user-friendly (no technical jargon)

### Compatibility
- Modern browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Responsive design: Desktop (1920x1080), Tablet (1024x768), Mobile (375x667)

---

## Open Questions

None at this time. Feature is well-defined based on existing backend API and chat interface patterns (ChatGPT/WhatsApp).

---

**Status**: ✅ Specification Complete
**Next Steps**: Run `/sp.plan` to create implementation plan
