---
name: shadcn-ui-components
description: Use shadcn/ui React components (Accordion, Card, Button, Toast, Skeleton) with Tailwind CSS and accessibility built-in. Use when building collapsible sections, content cards, interactive buttons, notifications, or loading placeholders.
allowed-tools: Read, Write, Edit
version: 1.0.0
last-updated: 2025-12-24
parent-agent: frontend-web
constitutional-principles: [III, VI]
tags:
  - shadcn/ui
  - React components
  - Tailwind CSS
  - Accessibility
  - WCAG 2.1 AA
triggers:
  - "Accordion"
  - "collapsible section"
  - "Card component"
  - "Button"
  - "Toast notification"
  - "Skeleton loader"
  - "shadcn/ui"
---

# Skill: shadcn/ui Component Library Integration

**Domain**: Frontend UI Component Development
**Purpose**: Provide reusable patterns for shadcn/ui components with accessibility and Tailwind CSS integration

## Overview

shadcn/ui is a collection of accessible, customizable React components built with Radix UI and Tailwind CSS. Unlike traditional component libraries, shadcn/ui components are **copied into your project** (not installed as dependencies), giving you full control over styling and behavior.

**Installed Components** (in this project):
- ✅ Accordion - Collapsible sections with ARIA support
- ✅ Card - Content containers
- ✅ Button - Interactive elements
- ✅ Toast - Notifications
- ✅ Skeleton - Loading placeholders
- ✅ Input - Form fields

## When to Use This Skill

Invoke this skill when you need to:
- Create collapsible sections (Accordion)
- Display content in cards (Card)
- Add interactive buttons (Button)
- Show user notifications (Toast)
- Implement loading states (Skeleton)
- Build accessible forms (Input)

## Component Patterns

### 1. Accordion (Collapsible Sections)

**Use Case**: Display content in expandable/collapsible sections (e.g., FAQs, explanation sections, multi-step forms)

**Basic Pattern**:
```typescript
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '@/components/ui/accordion';

export function ExplanationSection({ title, children, defaultExpanded = false }) {
  return (
    <Accordion
      type="single"
      collapsible
      defaultValue={defaultExpanded ? 'item-1' : undefined}
    >
      <AccordionItem value="item-1">
        <AccordionTrigger className="text-xl font-semibold">
          {title}
        </AccordionTrigger>
        <AccordionContent className="text-base leading-relaxed">
          {children}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

**Multiple Sections**:
```typescript
<Accordion type="single" collapsible>
  <AccordionItem value="definition">
    <AccordionTrigger>Definition</AccordionTrigger>
    <AccordionContent>
      Price Elasticity of Demand measures...
    </AccordionContent>
  </AccordionItem>

  <AccordionItem value="examples">
    <AccordionTrigger>Examples</AccordionTrigger>
    <AccordionContent>
      1. Luxury goods have elastic demand...
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

**Always Expanded (Non-Collapsible)**:
```typescript
// For critical content that should always be visible
<div className="border rounded-lg p-4">
  <h3 className="text-xl font-semibold mb-2">{title}</h3>
  <div className="text-base leading-relaxed">{children}</div>
</div>
```

**Accessibility**:
- ✅ Keyboard: Enter to toggle, Tab to navigate, Escape to close
- ✅ Screen reader: "Examples, collapsed, button" → "Examples, expanded, button"
- ✅ ARIA: aria-expanded, aria-controls, aria-labelledby
- ✅ Focus indicators: Visible outline on keyboard focus

### 2. Card (Content Containers)

**Use Case**: Display topics, saved explanations, dashboard widgets

**Basic Pattern**:
```typescript
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

export function TopicCard({ topic, onClick }) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <CardHeader>
        <CardTitle>{topic.code}</CardTitle>
        <CardDescription>{topic.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          {topic.learning_outcomes}
        </p>
      </CardContent>
    </Card>
  );
}
```

**Card Grid Layout**:
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {topics.map(topic => (
    <TopicCard key={topic.id} topic={topic} onClick={() => navigate(topic.id)} />
  ))}
</div>
```

### 3. Button (Interactive Elements)

**Use Case**: Actions, form submissions, navigation

**Variants**:
```typescript
import { Button } from '@/components/ui/button';

// Primary action
<Button onClick={handleSave}>Save Explanation</Button>

// Secondary action
<Button variant="outline" onClick={handleCancel}>Cancel</Button>

// Destructive action
<Button variant="destructive" onClick={handleDelete}>Remove Bookmark</Button>

// Ghost button (minimal styling)
<Button variant="ghost" onClick={handleClose}>Close</Button>

// With loading state
<Button disabled={isPending}>
  {isPending ? 'Saving...' : 'Save'}
</Button>
```

**Icon Buttons**:
```typescript
import { BookmarkIcon } from 'lucide-react';

<Button size="icon" variant="outline" onClick={handleBookmark}>
  <BookmarkIcon className="h-4 w-4" />
</Button>
```

### 4. Toast (Notifications)

**Use Case**: User feedback for actions (save, delete, error)

**Basic Pattern**:
```typescript
import { useToast } from '@/components/ui/use-toast';

export function BookmarkButton() {
  const { toast } = useToast();

  const handleSave = () => {
    // ... save logic
    toast({
      title: 'Explanation saved',
      description: 'You can find it in your saved explanations',
    });
  };

  const handleError = (error) => {
    toast({
      variant: 'destructive',
      title: 'Failed to save',
      description: error.message,
    });
  };

  return <Button onClick={handleSave}>Save</Button>;
}
```

**Toast with Action**:
```typescript
toast({
  title: 'Bookmark removed',
  description: 'The explanation has been removed from your saved list',
  action: (
    <Button variant="outline" size="sm" onClick={handleUndo}>
      Undo
    </Button>
  ),
});
```

### 5. Skeleton (Loading States)

**Use Case**: Show loading placeholders while fetching data

**Basic Pattern**:
```typescript
import { Skeleton } from '@/components/ui/skeleton';

export function TopicCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-24 mb-2" /> {/* Topic code */}
        <Skeleton className="h-4 w-full" />    {/* Description */}
      </CardHeader>
      <CardContent>
        <Skeleton className="h-4 w-3/4" />     {/* Learning outcomes */}
      </CardContent>
    </Card>
  );
}
```

**Grid Skeleton**:
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {Array.from({ length: 6 }).map((_, i) => (
    <TopicCardSkeleton key={i} />
  ))}
</div>
```

**Explanation Page Skeleton**:
```typescript
export function ExplanationSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-64" />  {/* Title */}
      <Skeleton className="h-24 w-full" /> {/* Definition */}
      <Skeleton className="h-64 w-full" /> {/* Examples */}
    </div>
  );
}
```

## Styling Patterns

**Tailwind CSS Classes**:
- `className` prop accepts Tailwind utility classes
- Use `cn()` utility from `lib/utils.ts` to merge classes conditionally

```typescript
import { cn } from '@/lib/utils';

<Button
  className={cn(
    'w-full',
    isBookmarked && 'bg-primary text-primary-foreground'
  )}
>
  {isBookmarked ? 'Saved' : 'Save'}
</Button>
```

**Responsive Design**:
```typescript
<Card className="
  p-4              /* Mobile: 1rem padding */
  md:p-6           /* Tablet: 1.5rem padding */
  lg:p-8           /* Desktop: 2rem padding */
">
  {content}
</Card>
```

## Accessibility Best Practices

1. **Keyboard Navigation**: All interactive elements (buttons, accordions) are keyboard-accessible
2. **Screen Readers**: ARIA labels and announcements built-in
3. **Focus Indicators**: Visible outline on keyboard focus (via Tailwind `focus-visible:` utilities)
4. **Color Contrast**: WCAG 2.1 AA compliant (4.5:1 minimum)
5. **Touch Targets**: Minimum 44px for mobile (via shadcn/ui defaults)

## Constitutional Compliance

**Principle III: PhD-Level Pedagogy**
- Clear visual hierarchy (headings, spacing, typography)
- Loading states (skeletons) set expectations during AI generation
- Collapsible sections reduce cognitive load (students focus on relevant content)

**Principle VI: Constructive Feedback**
- Toast notifications explain success/failure with actionable messages
- Error states provide clear guidance (not just "Error occurred")
- Button states (loading, disabled) prevent user confusion

## Common Patterns in This Project

### Teaching Page: Collapsible Explanation Sections
```typescript
// Always expanded (critical content)
<div className="border rounded-lg p-4 mb-4">
  <h3 className="text-xl font-semibold mb-2">Definition</h3>
  <p>{explanation.definition}</p>
</div>

// Collapsible (supplementary content)
<ExplanationSection title="Examples" defaultExpanded={false}>
  {explanation.examples.map(ex => <Example key={ex.id} {...ex} />)}
</ExplanationSection>
```

### Topic Browser: Card Grid
```typescript
{isLoading ? (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {Array.from({ length: 6 }).map((_, i) => <TopicCardSkeleton key={i} />)}
  </div>
) : (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {topics.map(topic => <TopicCard key={topic.id} topic={topic} />)}
  </div>
)}
```

### Bookmark Button: Toast Feedback
```typescript
const { mutate: saveBookmark } = useSaveBookmark();
const { toast } = useToast();

const handleBookmark = () => {
  saveBookmark(
    { syllabusPointId, explanation },
    {
      onSuccess: () => toast({ title: 'Explanation saved' }),
      onError: (error) => toast({
        variant: 'destructive',
        title: 'Failed to save',
        description: error.message,
      }),
    }
  );
};
```

## Version History

- **1.0.0** (2025-12-24): Initial skill creation with Accordion, Card, Button, Toast, Skeleton patterns

**Status**: Active | **Next Update**: After Phase 3-5 completion (add more patterns as discovered)
