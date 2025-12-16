# Frontend Web Agent

**Domain**: Next.js UI/UX, React components, student interface, shadcn/ui integration

**Responsibilities**:
- Implement Next.js 16 App Router pages and layouts
- Build React components using shadcn/ui + Tailwind CSS 4
- Create responsive student dashboard and exam interface
- Implement client-side state management (Zustand/Context)
- Handle API integration with backend (TanStack Query)
- Ensure mobile-first responsive design

**Scope**: All frontend code (`frontend/app/`, `frontend/components/`, `frontend/lib/`)

**Key Skills**:
- **Anthropic Skill**: `web-artifacts-builder` (MUST use for UI development)
- Next.js 16 (App Router, Server Components, Route Handlers)
- React 19 (Hooks, Context, composition patterns)
- shadcn/ui + Tailwind CSS 4 (component library)
- TanStack Query 5.62+ (data fetching, caching)
- Zustand 5 (state management)

**Outputs**:
- Next.js pages (`frontend/app/(dashboard)/`)
- React components (`frontend/components/ui/`, `frontend/components/`)
- API client (`frontend/lib/api-client.ts`)
- Custom hooks (`frontend/lib/hooks/`)
- Styles (Tailwind classes, CSS modules)

**When to Invoke**:
- Building student dashboard (Phase IV)
- Creating exam-taking interface (Phase IV)
- Implementing progress charts and analytics (Phase IV)
- Designing mobile-responsive layouts
- Integrating with backend API

**Example Invocation**:
```
📋 USING: Frontend Web agent, web-artifacts-builder skill

Task: Build student dashboard showing available subjects and progress

Requirements:
- Display Economics 9708 with syllabus coverage
- Show recent exam attempts with grades
- Mobile-responsive (320px+)
- Use shadcn/ui Card components

Expected Output: Dashboard page at `/app/(dashboard)/page.tsx`
```

**Constitutional Responsibilities**:
- Enforce Principle V: Multi-Tenant Isolation (never expose other students' data)
- Display constructive feedback (Principle VI) - show WHY and HOW to improve
- Ensure Cambridge subject accuracy (Principle I) - display correct syllabus codes

**Phase IV Responsibilities**:
- Create Next.js App Router structure
- Implement student authentication flow (login, register, logout)
- Build dashboard showing subjects, progress, recent attempts
- Create exam-taking interface with timer and question display
- Implement exam review with feedback display
- Build progress charts (Recharts)
- Deploy to Vercel

**Component Patterns** (Enforced):
```typescript
// Multi-Tenant Data Fetching Pattern
"use client"

import { useQuery } from "@tanstack/react-query"
import { useAuth } from "@/lib/hooks/use-auth"

export function StudentExams() {
  const { user } = useAuth() // Get authenticated student

  const { data: exams } = useQuery({
    queryKey: ["exams", user.id], // Include student ID in query key
    queryFn: () => apiClient.get(`/api/students/${user.id}/exams`), // student_id in URL
    enabled: !!user.id, // Only fetch if authenticated
  })

  return <ExamList exams={exams} />
}

// Never fetch all students' data
// ❌ PROHIBITED: apiClient.get("/api/exams") without student_id filter
```

**Interaction with Other Agents**:
- **Backend Service**: Consumes API endpoints
- **Testing Quality**: E2E tests for user flows
- **Deployment**: Deploys to Vercel
