/**
 * ExplanationSection Component
 *
 * Collapsible section for displaying parts of a topic explanation.
 *
 * Feature: 005-teaching-page (User Story 1: View Explanation)
 *
 * Uses shadcn/ui Accordion for:
 * - WCAG 2.1 AA accessibility (keyboard navigation, screen reader support)
 * - Smooth expand/collapse animations
 * - ARIA attributes (aria-expanded, aria-controls)
 *
 * Design Pattern (from research.md Decision 3):
 * - Always Expanded: Definition, Core Principles, Related Concepts (essential info)
 * - Collapsible: Examples, Misconceptions, Practice Problems, Visual Aids (supplementary)
 *
 * Constitutional Compliance:
 * - Principle III: PhD-level pedagogy (clear visual hierarchy, reduced cognitive load)
 * - Principle VI: Constructive feedback (collapsible sections help students focus)
 *
 * @example
 * // Always expanded section (critical content)
 * <ExplanationSection
 *   title="Definition"
 *   defaultExpanded={true}
 *   icon={<BookOpenIcon />}
 * >
 *   <p>Price Elasticity of Demand measures...</p>
 * </ExplanationSection>
 *
 * @example
 * // Collapsible section (supplementary content)
 * <ExplanationSection
 *   title="Examples"
 *   defaultExpanded={false}
 * >
 *   {examples.map(ex => <Example key={ex.id} {...ex} />)}
 * </ExplanationSection>
 */

'use client';

import { ReactNode } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

export interface ExplanationSectionProps {
  /** Section title (e.g., "Definition", "Examples", "Common Misconceptions") */
  title: string;

  /** Content to display inside the section */
  children: ReactNode;

  /** Whether section should be expanded by default (true for critical content) */
  defaultExpanded?: boolean;

  /** Optional icon to display before title */
  icon?: ReactNode;

  /** Optional action button (e.g., admin regenerate) - rendered outside trigger to avoid button nesting */
  action?: ReactNode;

  /** Optional CSS class for custom styling */
  className?: string;
}

/**
 * Collapsible section for explanation content
 *
 * Accessibility:
 * - Keyboard: Enter/Space to toggle, Tab to navigate, Escape to close
 * - Screen reader: "Examples, collapsed, button" → "Examples, expanded, button"
 * - Focus indicator: Visible outline on keyboard focus
 */
export function ExplanationSection({
  title,
  children,
  defaultExpanded = false,
  icon,
  action,
  className = '',
}: ExplanationSectionProps) {
  return (
    <Accordion
      type="single"
      collapsible
      defaultValue={defaultExpanded ? 'item-1' : undefined}
      className={className}
    >
      <AccordionItem value="item-1" className="border rounded-lg px-4">
        <div className="flex items-center justify-between">
          <AccordionTrigger className="text-xl font-semibold hover:no-underline flex-1">
            <div className="flex items-center gap-2">
              {icon && <span className="text-muted-foreground">{icon}</span>}
              <span>{title}</span>
            </div>
          </AccordionTrigger>
          {action && (
            <div className="flex-shrink-0 ml-2" onClick={(e) => e.stopPropagation()}>
              {action}
            </div>
          )}
        </div>
        <AccordionContent className="text-base leading-relaxed pb-4 pt-2">
          {children}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

/**
 * Non-collapsible section for always-visible critical content
 *
 * Use for: Definition, Core Principles, Related Concepts
 *
 * @example
 * <ExplanationSectionAlwaysExpanded
 *   title="Definition"
 *   icon={<BookOpenIcon />}
 * >
 *   <p>{explanation.definition}</p>
 * </ExplanationSectionAlwaysExpanded>
 */
export function ExplanationSectionAlwaysExpanded({
  title,
  children,
  icon,
  action,
  className = '',
}: Omit<ExplanationSectionProps, 'defaultExpanded'>) {
  return (
    <div className={`border rounded-lg p-6 w-full max-w-none min-w-0 overflow-visible ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold flex items-center gap-2 break-words">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <span className="break-words">{title}</span>
        </h3>
        {action && <div className="flex-shrink-0 ml-2">{action}</div>}
      </div>
      <div className="text-base leading-relaxed w-full max-w-none min-w-0 overflow-visible break-words">{children}</div>
    </div>
  );
}
