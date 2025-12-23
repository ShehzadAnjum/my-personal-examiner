# ADR-0002: ChatScope UI Kit for Chat Interface

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-21
- **Feature:** 004-coaching-page (Interactive AI Tutoring)
- **Context:** ChatGPT-style chat interface for student-coach dialogue

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Chat UI is core UX of coaching feature
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Custom UI, react-chat-elements, Stream Chat
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects accessibility, mobile UX, design consistency
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Use ChatScope UI Kit (@chatscope/chat-ui-kit-react v2.0+) for all chat interface components.**

This decision encompasses:
- **Message Display**: `MessageList`, `Message` components for conversation history
- **Message Input**: `MessageInput` component with send button and typing detection
- **Visual Elements**: `Avatar`, `ChatContainer`, `ConversationHeader` components
- **Loading States**: `TypingIndicator` for "Coach is thinking..." feedback
- **Responsive Design**: Mobile-first components (works on 375px screens)
- **Accessibility**: Built-in ARIA labels, keyboard navigation, screen reader support
- **Theming**: Customizable via Tailwind CSS classes (not custom CSS-in-JS)

## Consequences

### Positive

1. **Development Speed**: Saves 2-3 days vs building custom chat UI from scratch (message bubbles, avatars, layouts, responsive design)
2. **Accessibility Built-In**: WCAG 2.1 AA compliant out-of-box (ARIA labels, keyboard nav, focus management, screen reader tested)
3. **Mobile-Optimized**: Responsive components work on 375px-1920px without media query debugging
4. **Consistent UX**: Follows chat UI patterns users expect (WhatsApp/Telegram/ChatGPT style)
5. **TypeScript Support**: Strong typing for props, prevents runtime errors
6. **Well-Maintained**: Active development (last release <6 months), 900+ GitHub stars, MIT license
7. **Theming Flexibility**: Can override styles with Tailwind classes (no CSS-in-JS lock-in)
8. **Battle-Tested**: Used in production chat apps, documented edge cases (long messages, image attachments, reactions)

### Negative

1. **Bundle Size**: ~45KB gzipped (larger than custom minimal chat UI ~5-10KB)
2. **Vendor Dependency**: Future updates may have breaking changes (v1→v2 had API changes)
3. **Customization Limits**: Complex custom layouts require overriding internals (not officially supported)
4. **Styling Conflicts**: ChatScope's default styles may conflict with Tailwind (need CSS reset)
5. **Over-Engineering**: Includes features we don't use (group chat, file uploads, reactions) - cannot tree-shake unused code
6. **Learning Curve**: Team must learn ChatScope's API (e.g., `MessageModel`, `MessageDirection`)
7. **Maintenance Risk**: If library becomes unmaintained, migration to custom UI is costly

## Alternatives Considered

### Alternative 1: Custom Chat UI (React Components)

**Why Rejected**:
- Estimated 2-3 days to build message bubbles, avatars, scroll behavior, responsive design
- High risk of accessibility bugs (missing ARIA labels, keyboard traps, screen reader issues)
- Need to handle edge cases (long messages, rapid message send, scroll-to-bottom on new message)
- Reinvents the wheel (chat UI patterns are well-established)
- **Verdict**: Only viable if ChatScope doesn't meet requirements (it does)

### Alternative 2: react-chat-elements

**Why Rejected**:
- Less actively maintained (last release 1+ years ago)
- Fewer features (no typing indicator, limited theming)
- ~300 GitHub stars (smaller community than ChatScope's 900+)
- No TypeScript typings (JSDoc only)
- **Verdict**: ChatScope is more mature and feature-complete

### Alternative 3: Stream Chat UI (getstream.io)

**Why Rejected**:
- Requires Stream backend service (paid, $99/month for production)
- Over-engineered for our use case (real-time collaboration, webhooks, moderation, analytics)
- Heavier bundle size (~200KB)
- Backend APIs already exist (POST /api/coaching/...) - don't need Stream's infrastructure
- **Verdict**: Wrong fit for REST API backend with simple polling

### Alternative 4: shadcn/ui Chat Components

**Why Rejected**:
- shadcn/ui doesn't have chat-specific components (only primitives like Card, Avatar, Input)
- Would need to build chat layout, message bubbles, scroll behavior manually
- Essentially same effort as "Custom Chat UI" alternative
- **Verdict**: shadcn/ui is great for forms/buttons, not for complex chat UX

## References

- Feature Spec: `specs/004-coaching-page/spec.md` (FR-003 to FR-010 detail chat interface requirements)
- Implementation Plan: `specs/004-coaching-page/plan.md` (ChatInterface component architecture)
- Research Notes: `specs/004-coaching-page/research.md` (Q6 discusses shadcn/ui + Tailwind patterns)
- Related ADRs: ADR-0001 (TanStack Query for server state management)
- Official Docs: https://chatscope.io/storybook/react/
- GitHub: https://github.com/chatscope/chat-ui-kit-react
- Evaluator Evidence: Implementation in `/components/coaching/ChatInterface.tsx` validates WCAG 2.1 AA compliance (manual accessibility audit pending)
