/**
 * ExplanationView Component
 *
 * Displays a comprehensive PhD-level explanation using Agent 06's 9-component framework:
 * 1. Definition (always expanded)
 * 2. Key Terms (collapsible)
 * 3. Core Principles (always expanded) - from 'explanation' field
 * 4. Real-World Examples (collapsible)
 * 5. Visual Aids (collapsible)
 * 6. Worked Examples (collapsible)
 * 7. Common Misconceptions (collapsible)
 * 8. Practice Problems (collapsible)
 * 9. Related Concepts (always expanded)
 *
 * Features:
 * - Bookmark button integrated
 * - Semantic HTML for accessibility
 * - Responsive layout
 * - Clear visual hierarchy
 *
 * @example
 * ```tsx
 * <ExplanationView
 *   explanation={topicExplanation}
 *   isBookmarked={false}
 *   onBookmarkToggle={(isBookmarked) => console.log(isBookmarked)}
 * />
 * ```
 */

import {
  ExplanationSection,
  ExplanationSectionAlwaysExpanded,
} from './ExplanationSection';
import { BookmarkButton } from './BookmarkButton';
import { MermaidDiagram } from './MermaidDiagram';
import { Markdown } from '@/components/ui/markdown';
import type { TopicExplanation } from '@/lib/types/teaching';
import {
  BookOpenIcon,
  HashIcon,
  LightbulbIcon,
  TrendingUpIcon,
  ImageIcon,
  CalculatorIcon,
  AlertCircleIcon,
  PenToolIcon,
  LinkIcon,
} from 'lucide-react';

export interface ExplanationViewProps {
  explanation: TopicExplanation;
  isBookmarked: boolean;
  onBookmarkToggle: (isBookmarked: boolean) => void;
  isLoading?: boolean;
}

export function ExplanationView({
  explanation,
  isBookmarked,
  onBookmarkToggle,
  isLoading = false,
}: ExplanationViewProps) {
  return (
    <div className="space-y-6 w-full max-w-none overflow-visible">
      {/* Header Section */}
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {explanation.concept_name}
          </h1>
          <p className="text-muted-foreground mt-1">
            Syllabus Code: <span className="font-mono">{explanation.syllabus_code}</span>
          </p>
        </div>

        {/* Bookmark Button */}
        <div className="flex justify-end">
          <BookmarkButton
            isBookmarked={isBookmarked}
            onClick={() => onBookmarkToggle(!isBookmarked)}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Section 1: Definition (Always Expanded) */}
      <ExplanationSectionAlwaysExpanded
        title="Definition"
        icon={<BookOpenIcon className="h-5 w-5" />}
      >
        <div className="w-full max-w-none overflow-visible">
          <p
            className="text-base leading-relaxed break-words hyphens-auto whitespace-normal"
            style={{
              wordBreak: 'break-word',
              overflowWrap: 'anywhere',
              maxWidth: '100%',
              width: '100%'
            }}
          >
            {explanation.definition}
          </p>
        </div>
      </ExplanationSectionAlwaysExpanded>

      {/* Section 2: Key Terms (Collapsible) */}
      {explanation.key_terms && explanation.key_terms.length > 0 && (
        <ExplanationSection
          title="Key Terms"
          icon={<HashIcon className="h-5 w-5" />}
          defaultExpanded={false}
        >
          <div className="space-y-3">
            {explanation.key_terms.map((term, index) => (
              <div key={index} className="border-l-2 border-primary/30 pl-4">
                <p className="font-semibold text-base">{term.term}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {term.definition}
                </p>
              </div>
            ))}
          </div>
        </ExplanationSection>
      )}

      {/* Section 3: Core Principles (Always Expanded) */}
      <ExplanationSectionAlwaysExpanded
        title="Core Principles"
        icon={<LightbulbIcon className="h-5 w-5" />}
      >
        <div className="w-full max-w-none overflow-visible">
          <Markdown className="text-base">
            {explanation.explanation}
          </Markdown>
        </div>
      </ExplanationSectionAlwaysExpanded>

      {/* Section 4: Real-World Examples (Collapsible) */}
      {explanation.examples && explanation.examples.length > 0 && (
        <ExplanationSection
          title="Real-World Examples"
          icon={<TrendingUpIcon className="h-5 w-5" />}
          defaultExpanded={false}
        >
          <div className="space-y-4">
            {explanation.examples.map((example, index) => (
              <div key={index} className="bg-muted/50 p-4 rounded-lg space-y-2">
                <h4 className="font-semibold text-base">{example.title}</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="font-medium text-muted-foreground">Scenario:</p>
                    <p className="whitespace-pre-wrap">{example.scenario}</p>
                  </div>
                  <div>
                    <p className="font-medium text-muted-foreground">Analysis:</p>
                    <p className="whitespace-pre-wrap">{example.analysis}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ExplanationSection>
      )}

      {/* Section 5: Visual Aids (Collapsible) */}
      {explanation.visual_aids && explanation.visual_aids.length > 0 && (
        <ExplanationSection
          title="Visual Aids"
          icon={<ImageIcon className="h-5 w-5" />}
          defaultExpanded={false}
        >
          <div className="space-y-4">
            {explanation.visual_aids.map((aid, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                    {aid.type}
                  </span>
                  <h4 className="font-semibold text-base">{aid.title}</h4>
                </div>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {aid.description}
                </p>

                {/* Mermaid Diagram */}
                {aid.mermaid_code && (
                  <MermaidDiagram
                    code={aid.mermaid_code}
                    id={`mermaid-diagram-${index}`}
                  />
                )}

                {/* ASCII Art */}
                {aid.ascii_art && (
                  <pre className="bg-slate-900 text-green-400 p-4 rounded overflow-x-auto text-xs font-mono">
                    {aid.ascii_art}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </ExplanationSection>
      )}

      {/* Section 6: Worked Examples (Collapsible) */}
      {explanation.worked_examples && explanation.worked_examples.length > 0 && (
        <ExplanationSection
          title="Worked Examples"
          icon={<CalculatorIcon className="h-5 w-5" />}
          defaultExpanded={false}
        >
          <div className="space-y-4">
            {explanation.worked_examples.map((example, index) => (
              <div key={index} className="bg-muted/50 p-4 rounded-lg space-y-3">
                <div>
                  <p className="font-semibold text-base mb-2">Problem:</p>
                  <p className="text-sm whitespace-pre-wrap">{example.problem}</p>
                </div>
                <div>
                  <p className="font-semibold text-base mb-2">Step-by-Step Solution:</p>
                  <div className="text-sm whitespace-pre-wrap font-mono bg-background p-3 rounded border">
                    {example.step_by_step_solution}
                  </div>
                </div>
                <div>
                  <p className="font-semibold text-base mb-2">Marks Breakdown:</p>
                  <p className="text-sm whitespace-pre-wrap text-muted-foreground">
                    {example.marks_breakdown}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </ExplanationSection>
      )}

      {/* Section 7: Common Misconceptions (Collapsible) */}
      {explanation.common_misconceptions &&
        explanation.common_misconceptions.length > 0 && (
          <ExplanationSection
            title="Common Misconceptions"
            icon={<AlertCircleIcon className="h-5 w-5" />}
            defaultExpanded={false}
          >
            <div className="space-y-3">
              {explanation.common_misconceptions.map((item, index) => (
                <div
                  key={index}
                  className="bg-destructive/10 border-l-4 border-destructive p-4 rounded space-y-2"
                >
                  <div>
                    <p className="font-semibold text-sm flex items-start gap-2">
                      <span className="text-destructive">❌</span>
                      <span>Misconception:</span>
                    </p>
                    <p className="text-sm pl-6 mt-1">{item.misconception}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm flex items-start gap-2">
                      <span className="text-orange-600 dark:text-orange-400">💡</span>
                      <span>Why it's wrong:</span>
                    </p>
                    <p className="text-sm pl-6 mt-1">{item.why_wrong}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm flex items-start gap-2">
                      <span className="text-green-600 dark:text-green-400">✅</span>
                      <span>Correct understanding:</span>
                    </p>
                    <p className="text-sm pl-6 mt-1">{item.correct_understanding}</p>
                  </div>
                </div>
              ))}
            </div>
          </ExplanationSection>
        )}

      {/* Section 8: Practice Problems (Collapsible) */}
      {explanation.practice_problems && explanation.practice_problems.length > 0 && (
        <ExplanationSection
          title="Practice Problems"
          icon={<PenToolIcon className="h-5 w-5" />}
          defaultExpanded={false}
        >
          <div className="space-y-4">
            {explanation.practice_problems.map((problem, index) => (
              <div key={index} className="bg-muted/50 p-4 rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-base">Problem {index + 1}</p>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                        problem.difficulty === 'easy'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : problem.difficulty === 'medium'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                          : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                      }`}
                    >
                      {problem.difficulty}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {problem.marks} marks
                    </span>
                  </div>
                </div>
                <p className="text-sm whitespace-pre-wrap">{problem.question}</p>
                <details className="text-sm">
                  <summary className="cursor-pointer hover:text-primary font-medium">
                    Show answer outline
                  </summary>
                  <div className="mt-2 pl-4 border-l-2 border-primary/30">
                    <p className="text-muted-foreground whitespace-pre-wrap">
                      {problem.answer_outline}
                    </p>
                  </div>
                </details>
              </div>
            ))}
          </div>
        </ExplanationSection>
      )}

      {/* Section 9: Related Concepts (Always Expanded) */}
      {explanation.related_concepts && explanation.related_concepts.length > 0 && (
        <ExplanationSectionAlwaysExpanded
          title="Related Concepts"
          icon={<LinkIcon className="h-5 w-5" />}
        >
          <div className="flex flex-wrap gap-2">
            {explanation.related_concepts.map((concept, index) => (
              <span
                key={index}
                className="inline-flex items-center rounded-md bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary/20 transition-colors cursor-pointer"
              >
                {concept}
              </span>
            ))}
          </div>
        </ExplanationSectionAlwaysExpanded>
      )}

      {/* Footer: Generated By */}
      <div className="pt-6 border-t">
        <p className="text-xs text-muted-foreground text-center">
          Generated by{' '}
          <span className="font-medium capitalize">{explanation.generated_by}</span> AI
          • Economics 9708 A-Level
        </p>
      </div>
    </div>
  );
}
