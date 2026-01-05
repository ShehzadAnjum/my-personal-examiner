---
name: topic-explanation-page-structure
description: |
  Topic explanation page 9-component PhD-level framework for /teaching/[topicId] route.
  MUST USE when: generating topic explanations, creating definition sections, writing core principles,
  formatting real-world examples, designing visual aids/diagrams, creating worked examples,
  documenting common misconceptions, building practice problems, listing related concepts,
  implementing version switchers, adding personalization buttons (Simpler/Detail/Examples/Exam Focus/Visual),
  building admin regenerate features, formatting collapsible sections, text selection menus.
  Covers: ExplanationView, ExplanationSection components, 9-component framework,
  definition formatting, key terms, misconception structure (3-part), practice problem difficulty badges,
  bookmark functionality, Resource Bank v1 badge, admin section regeneration.
triggers:
  - "/teaching/[topicId]"
  - "topic explanation"
  - "9-component framework"
  - "definition section"
  - "core principles"
  - "real-world examples"
  - "visual aids"
  - "worked examples"
  - "common misconceptions"
  - "practice problems"
  - "related concepts"
  - "explanation content"
  - "PhD-level explanation"
  - "ExplanationView"
  - "ExplanationSection"
  - "version switcher"
  - "personalization buttons"
  - "admin regenerate"
  - "Resource Bank explanation"
  - "misconception format"
  - "practice question format"
  - "collapsible sections"
---

# Topic Explanation Page Structure & 9-Component Framework

**Purpose**: Document the exact structure, organization, and formatting of the `/teaching/[topicId]` page for consistent PhD-level content generation.

**Location**: `frontend/app/(dashboard)/teaching/[topicId]/page.tsx`

**Framework**: Agent 06's 9-component PhD-level explanation framework

**Last Updated**: 2026-01-05

---

## Page Purpose

Display comprehensive, PhD-level explanations for Economics 9708 topics using the official 9-component framework with Resource Bank integration.

---

## Page Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│ [Back to Topics Button]                                 │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [Version Switcher + Regenerate Buttons Card]       │ │
│ │ [Official v1 Badge] Version: [v1] [v2] [v3]        │ │
│ │ [Simpler] [More Detail] [More Examples] ...        │ │
│ │ [Admin: Regen v1] (if admin)                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [Topic Name]                                             │
│ Syllabus Code: 9708.X.X.X                   [Bookmark]  │
│                                                          │
│ ═════════════════════════════════════════════════════   │
│ 1. DEFINITION (Always Expanded)                         │
│ ═════════════════════════════════════════════════════   │
│ [Definition text...]                                     │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 2. KEY TERMS (Collapsible)                     [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ═════════════════════════════════════════════════════   │
│ 3. CORE PRINCIPLES (Always Expanded)                    │
│ ═════════════════════════════════════════════════════   │
│ [Detailed explanation with markdown...]                 │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 4. REAL-WORLD EXAMPLES (Collapsible)           [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 5. VISUAL AIDS (Collapsible)                   [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 6. WORKED EXAMPLES (Collapsible)               [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 7. COMMON MISCONCEPTIONS (Collapsible)         [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ─────────────────────────────────────────────────────   │
│ 8. PRACTICE PROBLEMS (Collapsible)             [▼]      │
│ ─────────────────────────────────────────────────────   │
│                                                          │
│ ═════════════════════════════════════════════════════   │
│ 9. RELATED CONCEPTS (Always Expanded)                   │
│ ═════════════════════════════════════════════════════   │
│ [Concept badges...]                                      │
│                                                          │
│ [Generated by {provider} AI • Economics 9708 A-Level]   │
│                                                          │
│ [Back to Topics]              [View Saved Explanations →]│
└─────────────────────────────────────────────────────────┘
```

---

## Top Navigation

### Back Button
- Component: `<Link href="/teaching">`
- Button: `<Button variant="ghost" size="sm">`
- Icon: `<ArrowLeft className="mr-2 h-4 w-4" />`
- Text: "Back to Topics"
- Margin: `mb-6`

---

## Version Control Card

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ [✅ Official v1]  Version: [v1] [v2] [v3] (Simpler)     │
│ [Simpler] [More Detail] [More Examples] [Exam Focus]    │
│ [More Visuals] [Admin: Regen v1]                        │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Container**:
- Component: `<Card className="p-4 mb-6">`
- Spacing: `space-y-4`

**Row 1: Version Switcher**

Official Badge (if from Resource Bank):
- Component: `<Badge variant="secondary">`
- Classes: `gap-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100`
- Icon: `<BadgeCheck className="h-3 w-3" />`
- Text: "Official v{version}"

Version Label:
- Icon: `<Sparkles className="h-4 w-4" />`
- Text: "Version:" with `text-sm font-semibold text-muted-foreground`

Version Buttons:
- Container: `flex gap-1`
- Each button:
  - Component: `<Button>`
  - Size: `size="sm"`
  - Classes: `h-8 px-3 text-xs`
  - Variant: `default` if active, `outline` if not
  - Text: "v{number}"

Current Version Label:
- Classes: `text-xs text-muted-foreground`
- Format: "({label})" e.g., "(Simpler)", "(Official)"

**Row 2: Personalization Buttons** (5 official styles per FR-006a)

Button Layout:
- Container: `flex gap-2 flex-wrap`
- All buttons: `variant="outline" size="sm" className="h-8 text-xs"`

Five Buttons:
1. **Simpler**: "Reduced complexity, basic vocabulary"
2. **More Detail**: "Deeper explanations, additional context"
3. **More Examples**: "3x more real-world examples"
4. **Exam Focus**: "Mark scheme alignment, examiner tips"
5. **More Visuals**: "Additional diagrams, visual representations"

**Admin Regenerate v1 Button** (if admin + official exists):
- Variant: `outline`
- Classes: `h-8 text-xs gap-1 border-amber-500 text-amber-600 hover:bg-amber-50`
- Icon: `<RefreshCw className="h-3 w-3" />`
- Text: "Regen v1"
- Disabled: During loading

**Admin Generate Section** (if admin + NO official):
- Container: `mt-4 pt-4 border-t border-amber-200 dark:border-amber-800`
- Layout: `flex items-center justify-between gap-4`
- Admin Icon: `<ShieldCheck className="h-4 w-4" />`
- Label: "Admin: No official explanation exists for this topic"
- Button:
  - Classes: `h-8 text-xs gap-1 bg-amber-600 hover:bg-amber-700 text-white`
  - Icon: `<ShieldCheck className="h-3 w-3" />`
  - Text: "Generate Official v1"
  - Loading state: `<Loader2>` spinner

---

## Page Header

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ Price Elasticity of Demand                              │
│ Syllabus Code: 9708.2.1.3                   [📌 Save]   │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Title**:
- Element: `<h1 className="text-3xl font-bold tracking-tight">`
- Text: Topic name (from `explanation.concept_name`)

**Metadata**:
- Element: `<p className="text-muted-foreground mt-1">`
- Format: "Syllabus Code: " + `<span className="font-mono">{code}</span>`

**Bookmark Button**:
- Container: `flex justify-end`
- Component: `<BookmarkButton>`
- States:
  - Not bookmarked: Outline style
  - Bookmarked: Filled style
- Loading: Disabled with spinner

---

## 9-Component Framework

### Design Pattern

**Always Expanded** (3 sections):
- Section 1: Definition
- Section 3: Core Principles
- Section 9: Related Concepts

**Collapsible** (6 sections):
- Section 2: Key Terms
- Section 4: Real-World Examples
- Section 5: Visual Aids
- Section 6: Worked Examples
- Section 7: Common Misconceptions
- Section 8: Practice Problems

---

## Section 1: Definition (Always Expanded)

### Component
`<ExplanationSectionAlwaysExpanded>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 📖 Definition                    [Admin: ⟳ Regen]       │
│                                                          │
│ [Full definition text as single paragraph]              │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Container**:
- Classes: `border rounded-lg p-6 w-full max-w-none min-w-0 overflow-visible`

**Header**:
- Title: `<h3 className="text-xl font-semibold">`
- Icon: `<BookOpenIcon className="h-5 w-5" />` with `text-muted-foreground`
- Layout: `flex items-center gap-2`

**Admin Regen Button** (if admin):
- Position: Right side of header
- Size: `size="sm"`
- Classes: `h-6 px-2 text-xs text-amber-600 hover:bg-amber-50`
- Icon: `<RefreshCw className="h-3 w-3" />` or `<Loader2>` if regenerating

**Content**:
- Element: `<p>`
- Classes: `text-base leading-relaxed break-words hyphens-auto whitespace-normal`
- Style: Full-width, word-break enabled
- Text: Direct from `explanation.definition`

**Content Guidelines**:
- **Length**: 2-4 sentences
- **Tone**: Formal, academic
- **Structure**: Start with formal definition, then expand with context
- **Example**: "Price Elasticity of Demand (PED) measures the responsiveness of quantity demanded to a change in price. It is calculated as the percentage change in quantity demanded divided by the percentage change in price. Understanding PED is crucial for businesses making pricing decisions and governments setting tax policy."

---

## Section 2: Key Terms (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ # Key Terms                                         [▼] │
├─────────────────────────────────────────────────────────┤
│ │ Elasticity                                            │
│ │ The responsiveness of one variable to changes in...  │
│ │                                                       │
│ │ Inelastic Demand                                      │
│ │ When percentage change in quantity demanded is...    │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<HashIcon className="h-5 w-5" />`

**Term Container**:
- Spacing: `space-y-3`
- Each term: `border-l-2 border-primary/30 pl-4`

**Term Title**:
- Element: `<p className="font-semibold text-base">`
- Text: Term name

**Term Definition**:
- Element: `<p className="text-sm text-muted-foreground mt-1">`
- Text: Definition

**Content Guidelines**:
- **Count**: 3-8 key terms
- **Selection**: Only truly essential vocabulary
- **Definitions**: 1-2 sentences each
- **Order**: Most important first

---

## Section 3: Core Principles (Always Expanded)

### Component
`<ExplanationSectionAlwaysExpanded>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 💡 Core Principles              [Admin: ⟳ Regen]       │
│                                                          │
│ [Rich markdown content with:]                            │
│ • Bullet points                                          │
│ • **Bold** emphasis                                      │
│ • Numbered lists                                         │
│ • Code blocks                                            │
│ • Mathematical notation                                  │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<LightbulbIcon className="h-5 w-5" />`

**Content**:
- Component: `<Markdown className="text-base">`
- Source: `explanation.explanation`
- Supports: Full markdown syntax

**Admin Regen Button**:
- Section name: "concept_explanation"

**Content Guidelines**:
- **Length**: 300-800 words
- **Structure**:
  1. Overview paragraph
  2. Detailed explanation with subsections
  3. Mathematical formulas (if applicable)
  4. Key relationships and patterns
- **Markdown usage**:
  - Headings: Use `###` for subsections
  - Lists: Use `-` or numbered `1.`
  - Emphasis: `**bold**` for key concepts
  - Formulas: Use inline math or code blocks
- **Example**:
```markdown
### The Determinants of Price Elasticity

Price elasticity depends on several factors:

1. **Availability of substitutes**: The more substitutes available, the more elastic demand becomes
2. **Proportion of income**: Goods that take up a large proportion of income tend to be more elastic
3. **Necessity vs luxury**: Necessities tend to be inelastic, luxuries more elastic
4. **Time period**: Demand becomes more elastic over longer time periods

The formula for PED is:

PED = (% Change in Quantity Demanded) / (% Change in Price)

A value greater than 1 indicates elastic demand, while less than 1 indicates inelastic.
```

---

## Section 4: Real-World Examples (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 📈 Real-World Examples       [Admin: ⟳ Regen]      [▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Example 1: Coffee Price Increase                   │ │
│ │                                                     │ │
│ │ Scenario:                                           │ │
│ │ A major coffee company increases prices by 20%...  │ │
│ │                                                     │ │
│ │ Analysis:                                           │ │
│ │ This demonstrates relatively inelastic demand...    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<TrendingUpIcon className="h-5 w-5" />`

**Admin Regen Button**:
- Section name: "real_world_examples"

**Container**:
- Spacing: `space-y-4`

**Each Example Card**:
- Container: `bg-muted/50 p-4 rounded-lg space-y-2`

**Example Title**:
- Element: `<h4 className="font-semibold text-base">`
- Format: "Example {number}: {title}"

**Scenario Section**:
- Label: `<p className="font-medium text-muted-foreground">Scenario:</p>`
- Content: `<p className="whitespace-pre-wrap">`

**Analysis Section**:
- Label: `<p className="font-medium text-muted-foreground">Analysis:</p>`
- Content: `<p className="whitespace-pre-wrap">`

**Content Guidelines**:
- **Count**: 2-4 examples
- **Length**: Each scenario 50-100 words, analysis 100-150 words
- **Structure**:
  - Title: Specific, concrete (not "Example 1")
  - Scenario: Real-world situation with numbers/data
  - Analysis: Connect to theory, explain economic principles at work
- **Industries**: Vary across different sectors
- **Example Titles**:
  - ✅ "Coffee Price Increase"
  - ✅ "Netflix Subscription Changes"
  - ✅ "Petrol Tax Policy"
  - ❌ "Example of Elasticity"

---

## Section 5: Visual Aids (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 🖼️ Visual Aids                  [Admin: ⟳ Regen]   [▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [Suggested] Supply and Demand Diagram               │ │
│ │                                                     │ │
│ │ Shows the relationship between price and quantity   │ │
│ │ with supply and demand curves intersecting...       │ │
│ │                                                     │ │
│ │ [Mermaid Diagram Rendered Here]                     │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<ImageIcon className="h-5 w-5" />`

**Admin Regen Button**:
- Section name: "diagrams"

**Container**:
- Spacing: `space-y-4`

**Each Visual Aid Card**:
- Container: `border rounded-lg p-4 space-y-3`

**Type Badge + Title**:
- Container: `flex items-center gap-2`
- Badge:
  - "Suggested": `bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300`
  - Other types: `bg-primary/10 text-primary`
  - Size: `text-xs font-medium px-2 py-1 rounded-md`
- Title: `<h4 className="font-semibold text-base">`

**Description**:
- Element: `<p className="text-sm text-muted-foreground whitespace-pre-wrap">`

**Mermaid Diagram** (if available):
- Component: `<MermaidDiagram code={aid.mermaid_code} id={unique_id} />`
- Renders interactive diagram

**ASCII Art** (if available):
- Element: `<pre className="bg-slate-900 text-green-400 p-4 rounded overflow-x-auto text-xs font-mono">`

**Content Guidelines**:
- **Count**: 2-4 visual aids
- **Types**:
  - "suggested": Recommended diagrams (most common)
  - "graph": Mathematical graphs
  - "flowchart": Process diagrams
  - "table": Data tables
- **Mermaid Syntax**: Use mermaid.js format for diagrams
- **Description**: 2-3 sentences explaining what diagram shows
- **Example Diagram Types**:
  - Supply and demand curves
  - Production possibilities frontier
  - Cost curves
  - Market equilibrium
  - Flow diagrams

---

## Section 6: Worked Examples (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 🧮 Worked Examples                                  [▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Problem:                                            │ │
│ │ Calculate PED when price increases from $10 to...   │ │
│ │                                                     │ │
│ │ Step-by-Step Solution:                              │ │
│ │ [Monospace code block with steps]                   │ │
│ │                                                     │ │
│ │ Marks Breakdown:                                    │ │
│ │ • Correct formula: 1 mark                           │ │
│ │ • Calculation: 2 marks                              │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<CalculatorIcon className="h-5 w-5" />`

**Container**:
- Spacing: `space-y-4`

**Each Example Card**:
- Container: `bg-muted/50 p-4 rounded-lg space-y-3`

**Problem Section**:
- Label: `<p className="font-semibold text-base mb-2">Problem:</p>`
- Content: `<p className="text-sm whitespace-pre-wrap">`

**Solution Section**:
- Label: `<p className="font-semibold text-base mb-2">Step-by-Step Solution:</p>`
- Content: `<div className="text-sm whitespace-pre-wrap font-mono bg-background p-3 rounded border">`

**Marks Breakdown**:
- Label: `<p className="font-semibold text-base mb-2">Marks Breakdown:</p>`
- Content: `<p className="text-sm whitespace-pre-wrap text-muted-foreground">`

**Content Guidelines**:
- **Count**: 1-3 worked examples
- **Complexity**: Progressive (easy → medium → hard)
- **Structure**:
  1. Problem statement with specific numbers
  2. Step-by-step solution (numbered steps)
  3. Marks breakdown (Cambridge exam style)
- **Solution Format**:
```
Step 1: Identify the formula
PED = (% Change in QD) / (% Change in Price)

Step 2: Calculate percentage changes
% Change in QD = ((120 - 100) / 100) × 100 = 20%
% Change in Price = ((12 - 10) / 10) × 100 = 20%

Step 3: Substitute into formula
PED = 20% / 20% = 1.0

Conclusion: Unit elastic demand (PED = 1)
```
- **Marks**: Show Cambridge mark scheme allocation

---

## Section 7: Common Misconceptions (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Common Misconceptions     [Admin: ⟳ Regen]      [▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ❌ Misconception:                                   │ │
│ │ Higher price always means lower demand              │ │
│ │                                                     │ │
│ │ 💡 Why it's wrong:                                  │ │
│ │ This confuses demand with quantity demanded...      │ │
│ │                                                     │ │
│ │ ✅ Correct understanding:                           │ │
│ │ A higher price leads to lower quantity demanded... │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<AlertCircleIcon className="h-5 w-5" />`

**Admin Regen Button**:
- Section name: "common_misconceptions"

**Container**:
- Spacing: `space-y-3`

**Each Misconception Card**:
- Container: `bg-destructive/10 border-l-4 border-destructive p-4 rounded space-y-2`

**Misconception Section**:
- Emoji: ❌ (red X)
- Label: `<p className="font-semibold text-sm">Misconception:</p>`
- Content: Text

**Why Wrong Section**:
- Emoji: 💡 (lightbulb, orange)
- Label: `<p className="font-semibold text-sm">Why it's wrong:</p>`
- Content: Explanation

**Correct Understanding Section**:
- Emoji: ✅ (green check)
- Label: `<p className="font-semibold text-sm">Correct understanding:</p>`
- Content: Proper explanation

**Content Guidelines**:
- **Count**: 3-5 misconceptions
- **Selection**: Address the MOST common student errors
- **Structure**:
  - Misconception: State incorrect belief (1 sentence)
  - Why wrong: Explain the error (2-3 sentences)
  - Correct: State proper understanding (2-3 sentences)
- **Examples**:
  - Confusing demand vs quantity demanded
  - Misunderstanding ceteris paribus
  - Incorrect formula application
  - Confusing elastic vs inelastic
- **Tone**: Constructive, not condescending

---

## Section 8: Practice Problems (Collapsible)

### Component
`<ExplanationSection defaultExpanded={false}>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ ✏️ Practice Problems         [Admin: ⟳ Regen]      [▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Problem 1               [easy]          4 marks     │ │
│ │                                                     │ │
│ │ Calculate the PED when price falls from...          │ │
│ │                                                     │ │
│ │ ▶ Show answer outline                               │ │
│ │   [Collapsed answer with mark scheme]               │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<PenToolIcon className="h-5 w-5" />`

**Admin Regen Button**:
- Section name: "practice_questions"

**Container**:
- Spacing: `space-y-4`

**Each Problem Card**:
- Container: `bg-muted/50 p-4 rounded-lg space-y-2`

**Problem Header**:
- Container: `flex items-center justify-between`
- Title: `<p className="font-semibold text-base">Problem {number}</p>`
- Difficulty Badge:
  - Easy: `bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300`
  - Medium: `bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300`
  - Hard: `bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300`
  - Size: `text-xs font-medium px-2 py-1 rounded-md`
- Marks: `<span className="text-xs text-muted-foreground">{marks} marks</span>`

**Question**:
- Element: `<p className="text-sm whitespace-pre-wrap">`

**Answer Outline** (Collapsible):
- Component: `<details className="text-sm">`
- Summary: `<summary className="cursor-pointer hover:text-primary font-medium">Show answer outline</summary>`
- Content: `<div className="mt-2 pl-4 border-l-2 border-primary/30">`

**Content Guidelines**:
- **Count**: 4-6 practice problems
- **Difficulty Distribution**:
  - 2 easy (2-4 marks each)
  - 2-3 medium (4-8 marks each)
  - 1-2 hard (8-12 marks each)
- **Question Types**:
  - Calculations
  - Diagram drawing
  - Short explanations
  - Analysis questions
- **Answer Outlines**: Include mark scheme points
- **Cambridge Style**: Match A-Level exam format

---

## Section 9: Related Concepts (Always Expanded)

### Component
`<ExplanationSectionAlwaysExpanded>`

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ 🔗 Related Concepts             [Admin: ⟳ Regen]       │
│                                                          │
│ [Supply Elasticity] [Cross-Price Elasticity]             │
│ [Income Elasticity] [Consumer Surplus]                   │
│ [Market Equilibrium]                                     │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Icon**: `<LinkIcon className="h-5 w-5" />`

**Admin Regen Button**:
- Section name: "related_topics"

**Container**:
- Layout: `flex flex-wrap gap-2`

**Each Concept Badge**:
- Element: `<span>`
- Classes: `inline-flex items-center rounded-md bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary/20 transition-colors cursor-pointer`
- Interactive: Hover effect, clickable

**Content Guidelines**:
- **Count**: 4-8 related concepts
- **Selection**: Direct conceptual links only
- **Order**: Most related first
- **Format**: Concept names, not topic codes
- **Examples**:
  - For "Price Elasticity of Demand":
    - ✅ "Supply Elasticity"
    - ✅ "Cross-Price Elasticity"
    - ✅ "Total Revenue Test"
    - ❌ "Market Failure" (too distant)

---

## Footer

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ Generated by OpenAI AI • Economics 9708 A-Level         │
└─────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Container**:
- Margin: `pt-6 border-t`

**Text**:
- Element: `<p className="text-xs text-muted-foreground text-center">`
- Format: "Generated by {provider} AI • Economics 9708 A-Level"
- Provider: Capitalize (e.g., "OpenAI", "Anthropic")

---

## Bottom Navigation

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ [← Back to Topics]           [View Saved Explanations →] │
└──────────────────────────────────────────────────────────┘
```

### Exact Formatting

**Container**:
- Classes: `mt-8 pt-6 border-t flex justify-between items-center`

**Back Button**:
- Component: `<Link href="/teaching">`
- Button: `<Button variant="outline" size="sm">`
- Icon: `<ArrowLeft className="mr-2 h-4 w-4" />`
- Text: "Back to Topics"

**Saved Link**:
- Component: `<Link href="/teaching/saved">`
- Button: `<Button variant="ghost" size="sm">`
- Text: "View Saved Explanations →"

---

## Text Selection Menu (Floating)

### Layout (appears on text selection)
```
┌─────────────────────────────────┐
│ 💡 Help Options                 │
├─────────────────────────────────┤
│ 💬 Ask AI Coach                 │
├─────────────────────────────────┤
│ 🟢 Simpler Language             │
│ 🔍 More Detail                  │
│ 📚 More Examples                │
├─────────────────────────────────┤
│ Selected: "economic surplus..." │
└─────────────────────────────────┘
```

### Exact Formatting

**Trigger**: User selects text > 10 characters

**Position**: Fixed, follows selection
- Style: `position: fixed, z-index: 50`
- Location: Below selected text (`top: selection.bottom + 10px`)

**Container**:
- Classes: `bg-card rounded-lg shadow-2xl border-2 border-primary p-2 min-w-[260px]`

**Header**:
- Classes: `text-xs font-semibold text-muted-foreground px-3 py-2 border-b`
- Text: "💡 Help Options"

**Primary Action**:
- Icon: 💬
- Text: "Ask AI Coach"
- Classes: `w-full text-left px-3 py-2 text-sm hover:bg-accent font-medium text-primary`

**Alternative Actions**:
- 🟢 Simpler Language
- 🔍 More Detail
- 📚 More Examples

**Selected Text Preview**:
- Classes: `text-xs text-muted-foreground px-3 py-2 border-t`
- Format: "Selected: "{text.slice(0, 50)}...""

---

## Loading States

### Initial Load
```
┌─────────────────────────────────────────────────────────┐
│ [Back to Topics]                                         │
│                                                          │
│ [Skeleton animation - title]                             │
│ [Skeleton animation - definition]                        │
│ [Skeleton animation - sections]                          │
└─────────────────────────────────────────────────────────┘
```

### Regeneration
- Same content remains visible
- Blur effect: Optional
- Loading indicator at top

---

## Error States

### No Official Explanation (Admin View)
```
┌─────────────────────────────────────────────────────────┐
│ 🛡️ No Official Explanation Yet                          │
│                                                          │
│ This topic doesn't have an official (v1) explanation    │
│ in the Resource Bank. As an admin, you can generate...  │
│                                                          │
│ [🛡️ Generate Official v1] [Back to Topics]             │
└─────────────────────────────────────────────────────────┘
```

### No Official Explanation (Student View)
```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Content Not Available                                │
│                                                          │
│ This topic has not been officially explained yet.        │
│ Please check back later or contact your administrator.  │
│                                                          │
│ [🔄 Retry] [Browse Topics]                              │
└─────────────────────────────────────────────────────────┘
```

---

## Accessibility Features

### Keyboard Navigation
- Tab through sections
- Enter to expand/collapse
- Escape to close text menu

### Screen Reader
- Semantic HTML (`<h1>`, `<h2>`, `<h3>`)
- ARIA labels on all interactive elements
- Section collapse states announced

---

## Content Quality Standards

### PhD-Level Requirements
- **Accuracy**: 100% Cambridge syllabus aligned
- **Depth**: Beyond A-Level, approaching undergraduate
- **Citations**: Use academic terminology
- **Examples**: Real-world, current, varied industries
- **Diagrams**: Professionally described
- **Practice**: Exam-standard questions

### Tone & Style
- Formal academic tone
- Clear, precise language
- Avoid colloquialisms
- Use proper economic terminology
- Maintain consistency across sections

---

## Summary: 9-Component Checklist

When generating content, ensure ALL components are present:

- [x] 1. Definition (always expanded, 2-4 sentences)
- [x] 2. Key Terms (3-8 terms with definitions)
- [x] 3. Core Principles (300-800 words, markdown)
- [x] 4. Real-World Examples (2-4 examples, scenario + analysis)
- [x] 5. Visual Aids (2-4 diagrams with descriptions)
- [x] 6. Worked Examples (1-3 step-by-step solutions)
- [x] 7. Common Misconceptions (3-5 misconception sets)
- [x] 8. Practice Problems (4-6 problems, varied difficulty)
- [x] 9. Related Concepts (4-8 concept badges)

**Constitutional Alignment**:
- ✅ Principle I: Subject Accuracy (Cambridge aligned)
- ✅ Principle II: A* Standard (PhD-level content)
- ✅ Principle VI: Constructive Feedback (misconceptions section)

**Status**: ✅ Production-ready formatting standard
