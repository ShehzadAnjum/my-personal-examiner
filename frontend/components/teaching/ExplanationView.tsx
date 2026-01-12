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

import { useState } from 'react';
import {
  ExplanationSection,
  ExplanationSectionAlwaysExpanded,
} from './ExplanationSection';
import { BookmarkButton } from './BookmarkButton';
import { MermaidDiagram } from './MermaidDiagram';
import { Markdown } from '@/components/ui/markdown';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import type { TopicExplanation } from '@/lib/types/teaching';
import type { ExplanationSection as SectionName } from '@/lib/api/resources';
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
  RefreshCw,
  Loader2,
  Sparkles,
  FileText,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export interface ResourceForSelection {
  id: string;
  title: string;
  resource_type: string;
}

export interface ExplanationViewProps {
  explanation: TopicExplanation;
  isBookmarked: boolean;
  onBookmarkToggle: (isBookmarked: boolean) => void;
  isLoading?: boolean;
  /** Admin-related props for section regeneration */
  isAdmin?: boolean;
  onSectionRegenerate?: (sectionName: SectionName) => Promise<void>;
  regeneratingSection?: SectionName | null;
  /** Resource selection for v2+ generation */
  availableResources?: ResourceForSelection[];
  onGenerateWithResources?: (resourceIds: string[]) => Promise<void>;
  isGeneratingAlternative?: boolean;
  /** Current explanation version info */
  version?: number;
  hasV1?: boolean;
}

export function ExplanationView({
  explanation,
  isBookmarked,
  onBookmarkToggle,
  isLoading = false,
  isAdmin = false,
  onSectionRegenerate,
  regeneratingSection = null,
  availableResources = [],
  onGenerateWithResources,
  isGeneratingAlternative = false,
  version = 1,
  hasV1 = true,
}: ExplanationViewProps) {
  // State for resource selection panel
  const [showResourcePanel, setShowResourcePanel] = useState(false);
  const [selectedResources, setSelectedResources] = useState<Set<string>>(new Set());

  const handleResourceToggle = (resourceId: string) => {
    setSelectedResources((prev) => {
      const next = new Set(prev);
      if (next.has(resourceId)) {
        next.delete(resourceId);
      } else {
        next.add(resourceId);
      }
      return next;
    });
  };

  const handleGenerateAlternative = async () => {
    if (onGenerateWithResources) {
      await onGenerateWithResources(Array.from(selectedResources));
      setShowResourcePanel(false);
      setSelectedResources(new Set());
    }
  };

  // Admin section regenerate button component
  const AdminRegenButton = ({ section }: { section: SectionName }) => {
    if (!isAdmin || !onSectionRegenerate) return null;
    const isRegenerating = regeneratingSection === section;
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-6 px-2 text-xs text-amber-600 hover:text-amber-700 hover:bg-amber-50"
        onClick={() => onSectionRegenerate(section)}
        disabled={!!regeneratingSection}
        title={`Regenerate ${section} section`}
      >
        {isRegenerating ? (
          <Loader2 className="h-3 w-3 animate-spin" />
        ) : (
          <RefreshCw className="h-3 w-3" />
        )}
      </Button>
    );
  };
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

        {/* Version Badge and Bookmark Button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {version > 1 && (
              <Badge variant="secondary">
                v{version}
              </Badge>
            )}
            {version === 1 && hasV1 && (
              <Badge className="bg-blue-600">
                Official v1
              </Badge>
            )}
          </div>
          <BookmarkButton
            isBookmarked={isBookmarked}
            onClick={() => onBookmarkToggle(!isBookmarked)}
            isLoading={isLoading}
          />
        </div>

        {/* Generate Alternative Version Panel */}
        {hasV1 && onGenerateWithResources && (
          <div className="border rounded-lg p-4 bg-muted/30">
            <button
              onClick={() => setShowResourcePanel(!showResourcePanel)}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                <span className="font-medium">Generate Alternative Version</span>
              </div>
              {showResourcePanel ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>

            {showResourcePanel && (
              <div className="mt-4 space-y-4">
                <p className="text-sm text-muted-foreground">
                  Select resources to use as context for generating a personalized version
                  of this explanation.
                </p>

                {availableResources.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">
                    No resources available. Upload resources to enable this feature.
                  </p>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {availableResources.map((resource) => (
                      <div
                        key={resource.id}
                        className="flex items-center space-x-3 p-2 border rounded hover:bg-muted/50"
                      >
                        <Checkbox
                          id={`resource-${resource.id}`}
                          checked={selectedResources.has(resource.id)}
                          onCheckedChange={() => handleResourceToggle(resource.id)}
                        />
                        <label
                          htmlFor={`resource-${resource.id}`}
                          className="flex-1 cursor-pointer text-sm"
                        >
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <span>{resource.title}</span>
                            <Badge variant="outline" className="text-xs">
                              {resource.resource_type}
                            </Badge>
                          </div>
                        </label>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowResourcePanel(false);
                      setSelectedResources(new Set());
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleGenerateAlternative}
                    disabled={isGeneratingAlternative}
                  >
                    {isGeneratingAlternative ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Generate v{version + 1}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Section 1: Definition (Always Expanded) */}
      <ExplanationSectionAlwaysExpanded
        title="Definition"
        icon={<BookOpenIcon className="h-5 w-5" />}
        action={<AdminRegenButton section="definition" />}
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
        action={<AdminRegenButton section="concept_explanation" />}
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
          action={<AdminRegenButton section="real_world_examples" />}
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
          action={<AdminRegenButton section="diagrams" />}
        >
          <div className="space-y-4">
            {explanation.visual_aids.map((aid, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                {/* Header with type badge and title */}
                <div className="flex items-center gap-2">
                  {aid.type === 'suggested' ? (
                    <span className="inline-flex items-center rounded-md bg-amber-100 dark:bg-amber-900/30 px-2 py-1 text-xs font-medium text-amber-700 dark:text-amber-300">
                      Suggested
                    </span>
                  ) : (
                    <span className="inline-flex items-center rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                      {aid.type}
                    </span>
                  )}
                  <h4 className="font-semibold text-base">{aid.title}</h4>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {aid.description}
                </p>

                {/* Mermaid Diagram (if available) */}
                {aid.mermaid_code && (
                  <MermaidDiagram
                    code={aid.mermaid_code}
                    id={`mermaid-diagram-${index}`}
                  />
                )}

                {/* ASCII Art (if available) */}
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
            action={<AdminRegenButton section="common_misconceptions" />}
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
          action={<AdminRegenButton section="practice_questions" />}
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
          action={<AdminRegenButton section="related_topics" />}
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
          • Syllabus {explanation.syllabus_code.split('.')[0]}
        </p>
      </div>
    </div>
  );
}
