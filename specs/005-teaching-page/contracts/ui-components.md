# UI Component Contracts: Teaching Page

**Feature**: 005-teaching-page (PhD-Level Concept Explanations)
**Date**: 2025-12-23
**Phase**: 1 (Design & Contracts)
**Purpose**: Define React component interfaces and props for teaching page UI

---

## Component Hierarchy

```
TeachingPage (app/(dashboard)/teaching/page.tsx)
├── TopicBrowser (hierarchical tree)
│   └── TopicCard (individual topic preview)
├── TopicSearch (search bar + results)
│   └── TopicCard (search result item)
└── [if loading] TopicSearchSkeleton

ExplanationPage (app/(dashboard)/teaching/[topicId]/page.tsx)
├── ExplanationView (full explanation display)
│   ├── ExplanationSection (collapsible section)
│   │   ├── Definition (always expanded)
│   │   ├── Key Terms (collapsible)
│   │   ├── Core Principles (always expanded)
│   │   ├── Examples (collapsible, 2-3 items)
│   │   ├── Visual Aids (collapsible, diagram descriptions)
│   │   ├── Worked Examples (collapsible)
│   │   ├── Misconceptions (collapsible)
│   │   ├── Practice Problems (collapsible)
│   │   └── Related Concepts (always expanded)
│   └── BookmarkButton (fixed position or header)
└── [if loading] ExplanationSkeleton

SavedPage (app/(dashboard)/teaching/saved/page.tsx)
└── SavedExplanationsList (list of bookmarked explanations)
    └── TopicCard (with "Remove" button)
```

---

## Component 1: TopicCard

**Purpose**: Display a single syllabus topic with code, description, and metadata

**File**: `frontend/components/teaching/TopicCard.tsx`

**Props Interface**:
```typescript
interface TopicCardProps {
  topic: SyllabusTopic;
  onClick: () => void;
  showRemoveButton?: boolean;
  onRemove?: () => void;
}
```

**Usage Example**:
```typescript
<TopicCard
  topic={{
    id: "550e8400-e29b-41d4-a716-446655440000",
    code: "3.1.2",
    description: "Price Elasticity of Demand (PED): Definition, calculation, determinants",
    level: "AS",
    paper_number: 2,
    section: "Microeconomics - Markets",
    // ... other fields
  }}
  onClick={() => navigate(`/teaching/${topic.id}`)}
  showRemoveButton={false}
/>
```

**Visual Design**:
- **Layout**: Card component (shadcn/ui) with padding, border, hover effect
- **Content**:
  - **Top**: Badge with topic code (e.g., "3.1.2") + level badge (e.g., "AS Paper 2")
  - **Middle**: Topic description (1-2 lines, truncated with "...")
  - **Bottom**: Section name (smaller, muted text)
- **Interaction**:
  - **Hover**: Subtle shadow, cursor pointer
  - **Click**: Navigate to explanation page
  - **Remove Button** (if showRemoveButton=true): X icon in top-right corner

**Accessibility**:
- **ARIA**: `role="button"`, `aria-label="View explanation for {topic.description}"`
- **Keyboard**: `tabIndex={0}`, Enter/Space to activate

**Responsive**:
- **Mobile (375px+)**: Stack badges vertically, truncate description to 1 line
- **Tablet (768px+)**: Badges horizontal, description 2 lines
- **Desktop (1024px+)**: Full content, wider cards

**Implementation Skeleton**:
```typescript
// frontend/components/teaching/TopicCard.tsx
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

export function TopicCard({ topic, onClick, showRemoveButton, onRemove }: TopicCardProps) {
  return (
    <Card
      onClick={onClick}
      className="cursor-pointer hover:shadow-md transition-shadow relative"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') onClick();
      }}
      aria-label={`View explanation for ${topic.description}`}
    >
      {showRemoveButton && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 h-6 w-6"
          onClick={(e) => {
            e.stopPropagation();
            onRemove?.();
          }}
          aria-label="Remove bookmark"
        >
          <X className="h-4 w-4" />
        </Button>
      )}

      <CardHeader>
        <div className="flex gap-2 mb-2">
          <Badge variant="secondary">{topic.code}</Badge>
          <Badge variant="outline">{`${topic.level} Paper ${topic.paper_number}`}</Badge>
        </div>
        <CardTitle className="text-lg line-clamp-2">{topic.description}</CardTitle>
      </CardHeader>

      <CardFooter>
        <CardDescription className="text-sm">{topic.section}</CardDescription>
      </CardFooter>
    </Card>
  );
}
```

---

## Component 2: TopicBrowser

**Purpose**: Display hierarchical tree of topics organized by AS/A2, Papers, Sections

**File**: `frontend/components/teaching/TopicBrowser.tsx`

**Props Interface**:
```typescript
interface TopicBrowserProps {
  topics: SyllabusTopic[];
  onTopicSelect: (topicId: string) => void;
  isLoading?: boolean;
}
```

**Usage Example**:
```typescript
<TopicBrowser
  topics={topics}
  onTopicSelect={(id) => navigate(`/teaching/${id}`)}
  isLoading={isLoadingTopics}
/>
```

**Visual Design**:
- **Layout**: Collapsible tree structure with shadcn/ui Accordion
- **Hierarchy**:
  - **Level 1**: AS-Level vs A2-Level (always expanded)
  - **Level 2**: Paper 1, Paper 2, Paper 3, Paper 4 (collapsible)
  - **Level 3**: Sections (e.g., "Microeconomics - Markets") (collapsible)
  - **Level 4**: Individual topics (TopicCard components)
- **Interaction**:
  - **Expand/Collapse**: Click section headers to toggle
  - **Topic Selection**: Click TopicCard to view explanation

**Accessibility**:
- **ARIA**: Accordion component handles ARIA labels automatically
- **Keyboard**: Tab to navigate sections, Enter to expand/collapse, Shift+Tab to go back

**Responsive**:
- **Mobile**: Narrower indentation (8px per level)
- **Desktop**: Wider indentation (16px per level)

**Implementation Skeleton**:
```typescript
// frontend/components/teaching/TopicBrowser.tsx
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';
import { TopicCard } from './TopicCard';

export function TopicBrowser({ topics, onTopicSelect, isLoading }: TopicBrowserProps) {
  const grouped = useMemo(() => {
    // Group topics by: level → paper → section
    return topics.reduce((acc, topic) => {
      const key = `${topic.level}-P${topic.paper_number}-${topic.section}`;
      if (!acc[key]) acc[key] = [];
      acc[key].push(topic);
      return acc;
    }, {} as Record<string, SyllabusTopic[]>);
  }, [topics]);

  if (isLoading) return <TopicSearchSkeleton />;

  return (
    <Accordion type="multiple" className="w-full">
      {Object.entries(grouped).map(([key, sectionTopics]) => {
        const [level, paper, section] = key.split('-');
        return (
          <AccordionItem key={key} value={key}>
            <AccordionTrigger className="text-lg font-semibold">
              {level} {paper} - {section} ({sectionTopics.length} topics)
            </AccordionTrigger>
            <AccordionContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                {sectionTopics.map((topic) => (
                  <TopicCard
                    key={topic.id}
                    topic={topic}
                    onClick={() => onTopicSelect(topic.id)}
                  />
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        );
      })}
    </Accordion>
  );
}
```

---

## Component 3: TopicSearch

**Purpose**: Search bar with live results for filtering syllabus topics

**File**: `frontend/components/teaching/TopicSearch.tsx`

**Props Interface**:
```typescript
interface TopicSearchProps {
  topics: SyllabusTopic[];
  onTopicSelect: (topicId: string) => void;
  placeholder?: string;
}
```

**Usage Example**:
```typescript
<TopicSearch
  topics={topics}
  onTopicSelect={(id) => navigate(`/teaching/${id}`)}
  placeholder="Search topics (e.g., elasticity, demand, supply)..."
/>
```

**Visual Design**:
- **Layout**: Search input + results list
- **Input**: shadcn/ui Input with search icon (left), clear button (right if text exists)
- **Results**: Grid of TopicCard components (2-3 columns)
- **Empty State**: "No results found for '{query}'. Try refining your search."

**Interaction**:
- **Typing**: Debounced 300ms (avoid excessive re-renders)
- **Highlight**: Matching keywords in results (use `<mark>` tag with Tailwind)
- **Clear**: X button to reset search

**Accessibility**:
- **ARIA**: `role="searchbox"`, `aria-label="Search syllabus topics"`
- **Keyboard**: Type to search, Escape to clear, Tab to navigate results

**Responsive**:
- **Mobile**: 1 column results
- **Tablet**: 2 columns results
- **Desktop**: 3 columns results

**Implementation Skeleton**:
```typescript
// frontend/components/teaching/TopicSearch.tsx
import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TopicCard } from './TopicCard';
import { useDebounce } from '@/hooks/useDebounce';

export function TopicSearch({ topics, onTopicSelect, placeholder }: TopicSearchProps) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  const filteredTopics = useMemo(() => {
    if (!debouncedQuery) return [];

    const lowerQuery = debouncedQuery.toLowerCase();
    return topics.filter(topic =>
      topic.code.toLowerCase().includes(lowerQuery) ||
      topic.description.toLowerCase().includes(lowerQuery) ||
      topic.learning_outcomes?.toLowerCase().includes(lowerQuery)
    );
  }, [topics, debouncedQuery]);

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder || "Search topics..."}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10 pr-10"
          role="searchbox"
          aria-label="Search syllabus topics"
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6"
            onClick={() => setQuery('')}
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {debouncedQuery && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTopics.length > 0 ? (
            filteredTopics.map((topic) => (
              <TopicCard
                key={topic.id}
                topic={topic}
                onClick={() => onTopicSelect(topic.id)}
              />
            ))
          ) : (
            <p className="col-span-full text-center text-muted-foreground">
              No results found for '{debouncedQuery}'. Try refining your search.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Component 4: ExplanationView

**Purpose**: Display full PhD-level explanation with collapsible sections

**File**: `frontend/components/teaching/ExplanationView.tsx`

**Props Interface**:
```typescript
interface ExplanationViewProps {
  explanation: TopicExplanation;
  isBookmarked: boolean;
  onBookmarkToggle: () => void;
}
```

**Usage Example**:
```typescript
<ExplanationView
  explanation={explanationData}
  isBookmarked={isBookmarked}
  onBookmarkToggle={() => mutate()}
/>
```

**Visual Design**:
- **Layout**: Single-column content with collapsible sections
- **Header**:
  - Concept name (text-2xl font-bold)
  - Syllabus code badge (e.g., "3.1.2")
  - Bookmark button (top-right, sticky)
- **Sections** (in order):
  1. **Definition** (always expanded, quote block style)
  2. **Key Terms** (collapsible, Accordion)
  3. **Core Principles** (always expanded)
  4. **Examples** (collapsible, numbered list with cards)
  5. **Visual Aids** (collapsible, diagram descriptions)
  6. **Worked Examples** (collapsible, step-by-step with marks)
  7. **Common Misconceptions** (collapsible, warning icon)
  8. **Practice Problems** (collapsible, problem cards)
  9. **Related Concepts** (always expanded, topic links)

**Typography**:
- **Headings**: `text-2xl font-bold` (concept name), `text-xl font-semibold` (section titles)
- **Body**: `text-base leading-relaxed` (readable line height for long content)
- **Economic Terms**: `font-semibold` (bold inline)
- **Definitions**: `border-l-4 border-primary pl-4 italic` (quote block)
- **Code/Math**: `font-mono bg-muted px-1 rounded` (inline code style)

**Accessibility**:
- **ARIA**: Each section has `aria-label="..."` with section name
- **Keyboard**: Tab to navigate between sections, Enter to expand/collapse

**Responsive**:
- **Mobile**: Single column, narrower max-width (600px)
- **Tablet**: Single column, medium max-width (800px)
- **Desktop**: Single column, wide max-width (1000px)

**Implementation Skeleton**:
```typescript
// frontend/components/teaching/ExplanationView.tsx
import { ExplanationSection } from './ExplanationSection';
import { BookmarkButton } from './BookmarkButton';
import { Badge } from '@/components/ui/badge';

export function ExplanationView({ explanation, isBookmarked, onBookmarkToggle }: ExplanationViewProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <div className="flex justify-between items-start sticky top-0 bg-background z-10 pb-4">
        <div>
          <Badge variant="secondary" className="mb-2">{explanation.syllabus_code}</Badge>
          <h1 className="text-3xl font-bold">{explanation.concept_name}</h1>
        </div>
        <BookmarkButton
          isBookmarked={isBookmarked}
          onClick={onBookmarkToggle}
        />
      </div>

      {/* Definition (always expanded) */}
      <div className="border-l-4 border-primary pl-4 py-2 italic bg-muted/30">
        <p className="text-base leading-relaxed">{explanation.definition}</p>
      </div>

      {/* Key Terms (collapsible) */}
      <ExplanationSection title="Key Terms" defaultExpanded={false}>
        <div className="space-y-3">
          {explanation.key_terms.map((kt, idx) => (
            <div key={idx}>
              <span className="font-semibold">{kt.term}:</span> {kt.definition}
            </div>
          ))}
        </div>
      </ExplanationSection>

      {/* Core Principles (always expanded) */}
      <div>
        <h2 className="text-xl font-semibold mb-3">Core Principles</h2>
        <p className="text-base leading-relaxed">{explanation.explanation}</p>
      </div>

      {/* Examples (collapsible) */}
      <ExplanationSection title="Examples" defaultExpanded={false}>
        <div className="space-y-4">
          {explanation.examples.map((ex, idx) => (
            <div key={idx} className="border-l-2 border-muted pl-4">
              <h4 className="font-semibold mb-1">{idx + 1}. {ex.title}</h4>
              <p className="mb-2">{ex.scenario}</p>
              <p className="text-sm text-muted-foreground">{ex.analysis}</p>
            </div>
          ))}
        </div>
      </ExplanationSection>

      {/* Visual Aids, Worked Examples, Misconceptions, Practice Problems - similar pattern */}

      {/* Related Concepts (always expanded) */}
      <div>
        <h2 className="text-xl font-semibold mb-3">Related Concepts</h2>
        <div className="flex flex-wrap gap-2">
          {explanation.related_concepts.map((concept, idx) => (
            <Badge key={idx} variant="outline">{concept}</Badge>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Component 5: ExplanationSection

**Purpose**: Reusable collapsible section component using shadcn/ui Accordion

**File**: `frontend/components/teaching/ExplanationSection.tsx`

**Props Interface**:
```typescript
interface ExplanationSectionProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  icon?: React.ReactNode;
}
```

**Usage Example**:
```typescript
<ExplanationSection
  title="Examples"
  defaultExpanded={false}
  icon={<BookOpen className="h-5 w-5" />}
>
  <p>Example content...</p>
</ExplanationSection>
```

**Visual Design**:
- **Layout**: shadcn/ui Accordion component
- **Trigger**: Title + optional icon + chevron (rotates on expand)
- **Content**: Padded container with children

**Accessibility**:
- **ARIA**: Handled automatically by shadcn/ui Accordion
- **Keyboard**: Enter toggles, Tab navigates

**Implementation**:
```typescript
// frontend/components/teaching/ExplanationSection.tsx
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export function ExplanationSection({ title, children, defaultExpanded, icon }: ExplanationSectionProps) {
  return (
    <Accordion type="single" collapsible defaultValue={defaultExpanded ? "item-1" : undefined}>
      <AccordionItem value="item-1">
        <AccordionTrigger className="text-xl font-semibold">
          {icon && <span className="mr-2">{icon}</span>}
          {title}
        </AccordionTrigger>
        <AccordionContent className="text-base leading-relaxed pt-4">
          {children}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

---

## Component 6: BookmarkButton

**Purpose**: Toggle bookmark state with visual feedback

**File**: `frontend/components/teaching/BookmarkButton.tsx`

**Props Interface**:
```typescript
interface BookmarkButtonProps {
  isBookmarked: boolean;
  onClick: () => void;
  isLoading?: boolean;
}
```

**Usage Example**:
```typescript
<BookmarkButton
  isBookmarked={isBookmarked}
  onClick={() => mutate()}
  isLoading={isBookmarking}
/>
```

**Visual Design**:
- **Layout**: Button with icon + text
- **Icon**: Bookmark outline (not bookmarked) vs Bookmark filled (bookmarked)
- **Text**: "Bookmark" (not bookmarked) vs "Bookmarked" (bookmarked)
- **Loading**: Spinner icon during mutation

**Interaction**:
- **Click**: Toggle bookmark state, show toast notification
- **Disabled**: During loading (isLoading=true)

**Accessibility**:
- **ARIA**: `aria-label="Bookmark this explanation"` or `aria-label="Remove bookmark"`
- **Keyboard**: Tab to focus, Enter/Space to activate

**Implementation**:
```typescript
// frontend/components/teaching/BookmarkButton.tsx
import { Button } from '@/components/ui/button';
import { Bookmark, BookmarkCheck, Loader2 } from 'lucide-react';

export function BookmarkButton({ isBookmarked, onClick, isLoading }: BookmarkButtonProps) {
  return (
    <Button
      variant={isBookmarked ? "default" : "outline"}
      size="sm"
      onClick={onClick}
      disabled={isLoading}
      aria-label={isBookmarked ? "Remove bookmark" : "Bookmark this explanation"}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin mr-2" />
      ) : isBookmarked ? (
        <BookmarkCheck className="h-4 w-4 mr-2" />
      ) : (
        <Bookmark className="h-4 w-4 mr-2" />
      )}
      {isBookmarked ? "Bookmarked" : "Bookmark"}
    </Button>
  );
}
```

---

## Component 7: SavedExplanationsList

**Purpose**: Display list of all bookmarked explanations

**File**: `frontend/components/teaching/SavedExplanationsList.tsx`

**Props Interface**:
```typescript
interface SavedExplanationsListProps {
  savedExplanations: SavedExplanation[];
  onTopicSelect: (topicId: string) => void;
  onRemove: (id: string) => void;
  isLoading?: boolean;
}
```

**Usage Example**:
```typescript
<SavedExplanationsList
  savedExplanations={savedData}
  onTopicSelect={(id) => navigate(`/teaching/${id}`)}
  onRemove={(id) => removeMutation.mutate(id)}
  isLoading={isLoadingSaved}
/>
```

**Visual Design**:
- **Layout**: Grid of TopicCard components with Remove buttons
- **Empty State**: "No saved explanations yet. Bookmark explanations to review them later."
- **Metadata**: Date saved displayed on each card

**Accessibility**:
- **ARIA**: List landmark with accessible card items

**Implementation**:
```typescript
// frontend/components/teaching/SavedExplanationsList.tsx
import { TopicCard } from './TopicCard';

export function SavedExplanationsList({ savedExplanations, onTopicSelect, onRemove, isLoading }: SavedExplanationsListProps) {
  if (isLoading) return <TopicSearchSkeleton />;

  if (savedExplanations.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          No saved explanations yet. Bookmark explanations to review them later.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {savedExplanations.map((saved) => (
        <TopicCard
          key={saved.id}
          topic={{
            id: saved.syllabus_point_id,
            code: saved.explanation_content.syllabus_code,
            description: saved.explanation_content.concept_name,
            // ... construct from explanation_content
          }}
          onClick={() => onTopicSelect(saved.syllabus_point_id)}
          showRemoveButton={true}
          onRemove={() => onRemove(saved.id)}
        />
      ))}
    </div>
  );
}
```

---

## Component 8: ExplanationSkeleton

**Purpose**: Loading state placeholder during AI explanation generation

**File**: `frontend/components/teaching/ExplanationSkeleton.tsx`

**Props**: None

**Visual Design**:
- **Layout**: Mimics ExplanationView structure with skeleton placeholders
- **Animated**: Pulse animation (Tailwind `animate-pulse`)
- **Duration**: 5-10 seconds (while AI generates explanation)

**Implementation**:
```typescript
// frontend/components/teaching/ExplanationSkeleton.tsx
import { Skeleton } from '@/components/ui/skeleton';

export function ExplanationSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <Skeleton className="h-10 w-3/4" />  {/* Title */}
      <Skeleton className="h-24 w-full" />  {/* Definition */}
      <Skeleton className="h-32 w-full" />  {/* Key Terms */}
      <Skeleton className="h-40 w-full" />  {/* Explanation */}
      <Skeleton className="h-48 w-full" />  {/* Examples */}
    </div>
  );
}
```

---

## Component 9: TopicSearchSkeleton

**Purpose**: Loading state placeholder during topic fetching

**File**: `frontend/components/teaching/TopicSearchSkeleton.tsx`

**Props**: None

**Visual Design**:
- **Layout**: Grid of skeleton cards (same layout as TopicBrowser)
- **Count**: 6-9 skeleton cards

**Implementation**:
```typescript
// frontend/components/teaching/TopicSearchSkeleton.tsx
import { Skeleton } from '@/components/ui/skeleton';

export function TopicSearchSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 9 }).map((_, i) => (
        <Skeleton key={i} className="h-32 w-full" />
      ))}
    </div>
  );
}
```

---

## TanStack Query Hooks

**Purpose**: Data fetching hooks for teaching page (wraps teachingApi client)

**File**: `frontend/lib/hooks/useTopics.tsx`

```typescript
import { useQuery } from '@tanstack/react-query';
import { teachingApi } from '@/lib/api/teaching';

export const useTopics = (filters?: { search?: string; level?: 'AS' | 'A2'; paper?: number }) => {
  return useQuery({
    queryKey: ['topics', filters],
    queryFn: () => teachingApi.getTopics(filters).then(data => data.topics),
    staleTime: 60 * 60 * 1000,  // 1 hour
    cacheTime: 2 * 60 * 60 * 1000,  // 2 hours
  });
};
```

**File**: `frontend/lib/hooks/useExplanation.tsx`

```typescript
export const useExplanation = (topicId: string) => {
  return useQuery({
    queryKey: ['explanation', topicId],
    queryFn: () => teachingApi.explainConcept(topicId).then(data => data.explanation),
    staleTime: 5 * 60 * 1000,  // 5 minutes
    cacheTime: 10 * 60 * 1000,  // 10 minutes
    enabled: !!topicId,
  });
};
```

**File**: `frontend/lib/hooks/useSavedExplanations.tsx`

```typescript
export const useSavedExplanations = () => {
  return useQuery({
    queryKey: ['savedExplanations'],
    queryFn: () => teachingApi.getSavedExplanations().then(data => data.saved_explanations),
    staleTime: 1 * 60 * 1000,  // 1 minute
    cacheTime: 5 * 60 * 1000,  // 5 minutes
  });
};
```

**File**: `frontend/lib/hooks/useBookmark.tsx`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { teachingApi } from '@/lib/api/teaching';
import { useToast } from '@/hooks/useToast';

export const useBookmark = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ syllabusPointId, explanation }: { syllabusPointId: string; explanation: TopicExplanation }) =>
      teachingApi.saveExplanation(syllabusPointId, explanation),
    onSuccess: () => {
      queryClient.invalidateQueries(['savedExplanations']);
      toast({
        title: "Explanation saved",
        description: "You can review this later in Saved Explanations.",
      });
    },
    onError: (error) => {
      toast({
        title: "Failed to save",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};
```

---

## UI Component Contracts Complete

All component interfaces, props, and implementation skeletons documented.

**Next**: Create quickstart.md with user flow examples
