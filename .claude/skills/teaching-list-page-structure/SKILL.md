---
name: teaching-list-page-structure
description: |
  Teaching page list view structure and formatting for /teaching route.
  MUST USE when: creating topic browsers, building syllabus lists, formatting topic cards,
  designing accordion sections for topics, implementing topic search interfaces,
  creating section headers (Economics 9708 sections 1-6), styling topic code badges,
  adding "Explained" indicators, building quick stats footers, implementing cache badges.
  Covers: TopicBrowser, TopicCard, TopicSearch components, gradient headers, accordion layout.
triggers:
  - "/teaching page"
  - "topic browser"
  - "topic list"
  - "syllabus sections"
  - "topic cards"
  - "section accordion"
  - "topic search"
  - "Economics 9708 sections"
  - "teaching page layout"
  - "browse topics"
  - "learning outcomes preview"
---

# Teaching List Page Structure & Formatting

**Purpose**: Document the exact structure, organization, and formatting of the `/teaching` page for consistent content generation.

**Location**: `frontend/app/(dashboard)/teaching/page.tsx`

**Last Updated**: 2026-01-05

---

## Page Purpose

Browse and search Economics 9708 syllabus topics with PhD-level explanations.

---

## 1. Page Header Section

### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ [Gradient Background Card with Decorative Blobs]            │
│                                                              │
│ [📚 Icon]  Teaching                                          │
│            PhD-Level Economics Explanations                  │
│                                                              │
│ Browse Economics 9708 syllabus topics and request            │
│ comprehensive, PhD-level explanations                        │
│                                                              │
│ [Optional: ⚡ Loaded from cache (instant) badge]            │
└─────────────────────────────────────────────────────────────┘
```

### Exact Formatting Details

**Container**:
- Classes: `mb-8 relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-secondary/5 to-accent/10 p-8 border border-primary/20`
- Purpose: Create premium, gradient-enhanced header

**Decorative Elements** (absolute positioned):
- Top-right blob: `w-64 h-64 bg-primary/20 rounded-full blur-3xl -z-10`
- Bottom-left blob: `w-64 h-64 bg-accent/20 rounded-full blur-3xl -z-10`

**Icon Container**:
- Classes: `p-3 bg-primary/10 rounded-xl backdrop-blur-sm`
- Icon: `<BookOpen />` with `h-8 w-8 text-primary`

**Title**:
- Element: `<h1>`
- Classes: `text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent`
- Text: **"Teaching"**

**Subtitle**:
- Element: `<p>`
- Classes: `text-sm text-muted-foreground`
- Text: **"PhD-Level Economics Explanations"**

**Description**:
- Element: `<p>`
- Classes: `text-base text-foreground/80 max-w-2xl`
- Text: **"Browse Economics 9708 syllabus topics and request comprehensive, PhD-level explanations"**

**Cache Badge** (conditional, shown when loaded from cache):
- Container: `mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full`
- Emoji: ⚡
- Text: "Loaded from cache (instant)" with classes `text-sm font-medium text-green-600 dark:text-green-400`

---

## 2. Error State (If applicable)

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ [⚠️ Alert Icon] Failed to Load Topics                       │
│                                                              │
│ [Error message text]                           [Retry Button]│
└─────────────────────────────────────────────────────────────┘
```

### Exact Formatting
- Component: `<Alert variant="destructive">`
- Icon: `<AlertCircle className="h-4 w-4" />`
- Title: "Failed to Load Topics"
- Retry button: `<Button variant="outline" size="sm">Retry</Button>`

---

## 3. Browse/Search Tabs

### Tab Layout
```
┌───────────────────────────────┐
│  📚 Browse  |  🔍 Search       │
└───────────────────────────────┘
```

### Exact Formatting

**Container**:
- Component: `<Tabs>` with `value={activeTab}` (either 'browse' or 'search')

**Tab List**:
- Classes: `grid w-full max-w-md grid-cols-2 mb-6`
- Two triggers: "Browse" and "Search"
- Each with icon and gap: `className="gap-2"`

**Icons**:
- Browse: `<BookOpen className="h-4 w-4" />`
- Search: `<Search className="h-4 w-4" />`

---

## 4. Browse Tab Content (Default)

### Hierarchy Structure
```
Economics 9708 Syllabus (N topics)
│
├── Section 1: Basic Economic Ideas and Resource Allocation (X topics)
│   ├── Topic 1.1.1 - Scarcity, choice and opportunity cost
│   ├── Topic 1.1.2 - Economic assumptions
│   └── ...
│
├── Section 2: The Price System and the Microeconomy (X topics)
│   ├── Topic 2.1.1 - Demand
│   ├── Topic 2.1.2 - Supply
│   └── ...
│
└── ... (continues for all 6 sections)
```

### Exact Formatting

**Header**:
- Container: `flex items-center justify-between`
- Icon: `<BookOpen className="h-5 w-5 text-primary" />`
- Title: `<h2 className="text-lg font-semibold">Economics 9708 Syllabus ({count} topics)</h2>`

**Accordion Container**:
- Component: `<Accordion type="multiple">` (allows multiple sections open)
- Default: All sections expanded
- Spacing: `space-y-4`

**Each Section (AccordionItem)**:
- Border: `className="border rounded-lg px-4"`
- Value: Section number (e.g., "1", "2", "3")

**Section Trigger**:
- Container: `flex items-center justify-between w-full pr-4`
- Number badge:
  - Classes: `w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-sm`
  - Content: Section number (1-6)
- Title:
  - Element: `<h3 className="font-semibold text-base">`
  - Text: Section name (e.g., "Basic Economic Ideas and Resource Allocation")
- Count:
  - Element: `<p className="text-xs text-muted-foreground">`
  - Text: "{count} topic(s)"

**Section Content (Topics Grid)**:
- Container: `pt-4 pb-6`
- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- Each topic: `<TopicCard />` component

---

## 5. Topic Card Component

### Card Layout
```
┌─────────────────────────────────────────────────────┐
│ 📚 [9708.1.1.1]                    [✓ Explained] >  │
│                                                      │
│ Scarcity, choice and opportunity cost                │
│                                                      │
│ LEARNING OUTCOMES                                    │
│ • Understand the fundamental economic problem        │
│ • Explain the concept of opportunity cost            │
│                                                      │
│ + 2 more outcomes                                    │
└─────────────────────────────────────────────────────┘
```

### Exact Formatting

**Card Container**:
- Component: `<Card>`
- Classes: `group relative cursor-pointer transition-all hover:shadow-md hover:border-primary/50 focus-within:ring-2`
- Accessibility: `tabIndex={0}` `role="button"`

**Header Section**:
- BookOpen icon: `className="h-4 w-4 text-primary"`
- Code badge:
  - Classes: `rounded-md bg-primary/10 px-2.5 py-1 text-sm font-semibold text-primary font-mono`
  - Text: Topic code (e.g., "9708.1.1.1")

**"Explained" Badge** (if cached):
- Container: `px-2 py-1 rounded-md bg-green-500/10 border border-green-500/20`
- Icon: `<CheckCircle2 className="h-3.5 w-3.5 text-green-600" />`
- Text: "Explained" with `text-xs font-medium text-green-600`

**Arrow Icon** (right side):
- Icon: `<ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary" />`

**Description**:
- Element: `<h3 className="text-base font-semibold leading-tight mt-2 group-hover:text-primary">`
- Text: Topic description

**Learning Outcomes**:
- Label: `<p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">LEARNING OUTCOMES</p>`
- List: `<ul className="space-y-1 text-sm text-muted-foreground">`
- Each outcome:
  - Bullet: `<span className="text-primary mt-1.5 block h-1 w-1 rounded-full bg-primary" />`
  - Text: Outcome text

**"More Outcomes" Indicator** (if > 2 outcomes):
- Element: `<p className="text-xs text-muted-foreground italic mt-2">`
- Text: "+ {count} more outcome(s)"

---

## 6. Search Tab Content

### Layout
Shows a search input with instant filtering of topics.

### Exact Formatting
- Search input with autocomplete
- Filtered topic cards displayed below
- Real-time search (debounced)

---

## 7. Quick Stats Footer

### Layout
```
┌─────────────┬─────────────┬─────────────┐
│     N       │    9708     │  PhD-Level  │
│ Topics      │ Economics   │ Explanation │
│ Available   │   A-Level   │   Quality   │
└─────────────┴─────────────┴─────────────┘
```

### Exact Formatting

**Grid Container**:
- Classes: `grid grid-cols-1 md:grid-cols-3 gap-6`
- Margin: `mt-12 pt-6`

**Each Card**:
- Container: `relative group overflow-hidden rounded-2xl p-6 border`
- Gradient backgrounds (different for each):
  - Topics: `bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20`
  - Subject: `bg-gradient-to-br from-secondary/10 to-secondary/5 border-secondary/20`
  - Quality: `bg-gradient-to-br from-accent/10 to-accent/5 border-accent/20`

**Decorative Blob** (each card):
- Classes: `absolute top-0 right-0 w-32 h-32 rounded-full blur-2xl -z-10 group-hover:scale-150 transition-transform duration-500`
- Color matches card gradient

**Number Display**:
- Classes: `text-5xl font-black` + color (text-primary/secondary/accent)
- Content:
  - Card 1: Topic count (e.g., "127")
  - Card 2: "9708"
  - Card 3: "PhD-Level"

**Label**:
- Classes: `text-sm font-medium text-muted-foreground`
- Content:
  - Card 1: "Topics Available"
  - Card 2: "Economics A-Level"
  - Card 3: "Explanation Quality"

---

## 8. Section Names (Economics 9708 Specific)

### Official Section Structure

1. **Section 1**: "Basic Economic Ideas and Resource Allocation"
2. **Section 2**: "The Price System and the Microeconomy"
3. **Section 3**: "Government Microeconomic Intervention"
4. **Section 4**: "The Macroeconomy"
5. **Section 5**: "Government Macroeconomic Intervention"
6. **Section 6**: "International Economic Issues"

### Topic Code Format
- Pattern: `9708.{section}.{subsection}.{topic}`
- Example: `9708.1.1.1` = Section 1, Subsection 1, Topic 1

---

## 9. Loading State

### Skeleton Layout
Shows 5-6 animated skeleton cards while topics load.

### Exact Formatting
- Component: `<TopicSearchSkeleton count={6} />`
- Each skeleton: Pulsing gray card with shimmer effect

---

## 10. Empty State

### Layout
```
┌─────────────────────────────────────────────────────┐
│                   📚                                 │
│               No Topics Found                        │
│                                                      │
│  No syllabus topics available. This could mean...   │
└─────────────────────────────────────────────────────┘
```

### Exact Formatting
- Container: `flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg`
- Icon: `<BookOpen className="h-12 w-12 text-muted-foreground mb-4" />`
- Title: `<h3 className="text-lg font-semibold mb-2">No Topics Found</h3>`
- Description: Helpful message explaining why

---

## 11. Color Scheme & Theme

### Primary Colors
- **Primary**: Used for main accents, topic codes, icons
- **Secondary**: Used for subtitle gradients
- **Accent**: Used for decorative elements
- **Muted**: Used for secondary text (counts, labels)

### Hover States
- Cards: `hover:shadow-md hover:border-primary/50`
- Text: `group-hover:text-primary`
- Icons: Transition color to primary on hover

---

## 12. Responsive Behavior

### Breakpoints
- **Mobile (< 768px)**: Single column grid
- **Tablet (768px - 1024px)**: 2-column grid for topics
- **Desktop (> 1024px)**: 3-column grid for topics

### Navigation
- Stats footer: Stacks vertically on mobile
- Accordion sections: Full width at all sizes

---

## 13. Accessibility Features

### Keyboard Navigation
- Tab: Navigate between sections and cards
- Enter/Space: Activate card
- Arrow keys: Navigate within accordion

### Screen Reader
- All icons have `aria-hidden="true"`
- Cards have `aria-label` with full description
- Proper heading hierarchy (h1 → h2 → h3)

---

## 14. Performance Optimizations

### Caching Strategy
- **localStorage**: Syllabus topics cached for 24 hours
- **Key**: `syllabus_topics_9708`
- **Timestamp**: Stored separately for cache validation
- **Version**: Cache version for invalidation

### Loading Strategy
1. Check localStorage first (instant load)
2. Display cached data immediately
3. Validate cache age
4. Background sync if stale (>24h)
5. Show "Loaded from cache" badge if applicable

---

## 15. Content Guidelines

### When Creating Topic Lists
- **Always**: Use exact section names listed above
- **Always**: Follow topic code format (9708.X.X.X)
- **Always**: Include 2 learning outcomes preview
- **Always**: Show topic count for each section
- **Quality**: PhD-level descriptions, academically precise

### Topic Descriptions
- **Length**: 5-15 words
- **Tone**: Academic but accessible
- **Format**: Start with verb or noun phrase
- **Examples**:
  - ✅ "Scarcity, choice and opportunity cost"
  - ✅ "Elasticity of demand and supply"
  - ❌ "Learn about scarcity" (too casual)
  - ❌ "This section covers..." (too verbose)

---

## Summary: Key Visual Elements

1. **Gradient header** with decorative blobs - Premium feel
2. **Collapsible sections** - Organized hierarchy
3. **Grid layout** - Modern, scannable design
4. **Badge indicators** - Visual status cues
5. **Hover effects** - Interactive feedback
6. **Stats cards** - Quick overview
7. **Cache badge** - Performance transparency

**Constitutional Alignment**:
- ✅ Principle I: Subject accuracy (Cambridge 9708 syllabus)
- ✅ Principle III: PhD-level pedagogy (structured, hierarchical)
- ✅ Avoid over-engineering: Simple localStorage cache

**Status**: ✅ Production-ready formatting standard
