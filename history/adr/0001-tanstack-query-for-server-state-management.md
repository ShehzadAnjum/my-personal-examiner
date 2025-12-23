# ADR-0001: TanStack Query for Server State Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-21
- **Feature:** 004-coaching-page (Interactive AI Tutoring)
- **Context:** Real-time chat interface with REST API backend

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - All frontend API integration patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - SWR, Redux Toolkit, custom hooks
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all components using server data
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Use TanStack Query v5.62+ for all server state management in the coaching page feature.**

This decision encompasses:
- **Data Fetching**: `useQuery` for GET requests (session data, messages, history)
- **Mutations**: `useMutation` for POST requests (start session, send message)
- **Polling**: Built-in `refetchInterval` for real-time updates (2-second polling)
- **Caching**: Query cache with configurable stale time and cache time
- **Optimistic Updates**: `onMutate` callbacks for instant UI feedback
- **Retry Logic**: Automatic retry with exponential backoff (3 attempts: 1s, 2s, 4s)
- **Network Awareness**: `networkMode` for offline-first queries and retry-on-reconnect mutations
- **Persistence**: Optional cache persistence to localStorage

## Consequences

### Positive

1. **Built-in Real-Time Support**: Polling with `refetchInterval` eliminates need for custom WebSocket or SSE infrastructure for REST API
2. **Optimistic Updates Out-of-Box**: `onMutate`, `onError`, `onSuccess` callbacks enable instant UI feedback before server response
3. **Automatic Retry with Backoff**: 3-attempt retry with exponential backoff (1s, 2s, 4s) handles transient network failures without custom logic
4. **Network-Aware**: `networkMode: 'offlineFirst'` for queries uses cache when offline; `networkMode: 'always'` for mutations retries when reconnected
5. **Caching & Performance**: Reduces redundant API calls, configurable stale/cache times, query deduplication
6. **Developer Experience**: React hooks-based API, TypeScript support, DevTools for debugging query state
7. **Battle-Tested**: Used in production by thousands of React apps, extensive documentation, active community
8. **Framework Agnostic**: Can migrate to other React frameworks (Remix, Vite) without rewriting state management

### Negative

1. **Bundle Size**: ~12KB gzipped (larger than custom hooks or SWR ~4KB)
2. **Learning Curve**: Team needs to understand query keys, cache invalidation, stale-while-revalidate patterns
3. **Vendor Dependency**: Tied to TanStack Query's API design and versioning (v5 has breaking changes from v4)
4. **Over-Engineering Risk**: May be overkill for simple CRUD operations (but coaching chat is real-time, not simple CRUD)
5. **Configuration Complexity**: Default options can be surprising (5-minute stale time, infinite cache time) - requires careful configuration
6. **Debugging Challenges**: Cache state can be non-obvious without DevTools, query key collisions can cause bugs

## Alternatives Considered

### Alternative 1: SWR (Stale-While-Revalidate by Vercel)

**Why Rejected**:
- Smaller bundle size (~4KB) but lacks built-in mutation support (need custom logic)
- No built-in retry with exponential backoff (must implement manually)
- Less TypeScript inference for mutation states
- Optimistic updates require more boilerplate
- Polling support exists but less flexible than TanStack Query
- **Verdict**: Good for read-heavy apps, insufficient for real-time chat with mutations

### Alternative 2: Redux Toolkit + RTK Query

**Why Rejected**:
- Requires Redux infrastructure (store, slices, reducers) - overkill for frontend-only state
- RTK Query is powerful but tightly couples to Redux ecosystem
- More boilerplate for simple queries (need to define endpoints, slices)
- Polling and retry require additional configuration
- **Verdict**: Better for apps already using Redux for global state; coaching page has no Redux dependency

### Alternative 3: Custom React Hooks (useEffect + useState)

**Why Rejected**:
- Must implement caching, retry, polling, optimistic updates, network detection manually
- High risk of bugs (race conditions, stale closures, memory leaks)
- No DevTools for debugging
- Reinvents the wheel (TanStack Query has 8+ years of optimization)
- **Verdict**: Possible for learning exercise, impractical for production

### Alternative 4: Apollo Client (GraphQL)

**Why Rejected**:
- Backend uses REST API, not GraphQL
- Requires GraphQL server or REST-to-GraphQL adapter
- Heavier bundle size (~30KB) for features we don't need
- **Verdict**: Wrong tool for REST API backend

## References

- Feature Spec: `specs/004-coaching-page/spec.md`
- Implementation Plan: `specs/004-coaching-page/plan.md`
- Research Notes: `specs/004-coaching-page/research.md` (Questions Q1-Q4 detail TanStack Query usage)
- Related ADRs: None (first frontend state management decision)
- Official Docs: https://tanstack.com/query/latest/docs/react/overview
- Evaluator Evidence: Research.md shows polling, retry, offline detection patterns validated against requirements FR-017 to FR-020
