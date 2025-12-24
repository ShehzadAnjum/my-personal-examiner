/**
 * Markdown Component
 *
 * Renders markdown content with custom styling to match the app theme.
 * Uses react-markdown with GitHub Flavored Markdown (GFM) support.
 */

'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';

export interface MarkdownProps {
  children: string;
  className?: string;
}

export function Markdown({ children, className }: MarkdownProps) {
  return (
    <div
      className={cn(
        'prose prose-sm dark:prose-invert max-w-none',
        'prose-headings:font-semibold prose-headings:tracking-tight',
        'prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base',
        'prose-p:text-base prose-p:leading-relaxed',
        'prose-strong:text-foreground prose-strong:font-semibold',
        'prose-ul:list-disc prose-ul:pl-6',
        'prose-ol:list-decimal prose-ol:pl-6',
        'prose-li:text-base prose-li:leading-relaxed',
        'prose-code:text-sm prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded',
        'prose-pre:bg-muted prose-pre:p-4 prose-pre:rounded-lg',
        'prose-blockquote:border-l-primary prose-blockquote:text-muted-foreground',
        'prose-a:text-primary prose-a:no-underline hover:prose-a:underline',
        'break-words hyphens-auto',
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Custom rendering for specific elements
        p: ({ children }) => (
          <p
            className="text-base leading-relaxed break-words whitespace-normal mb-4 last:mb-0"
            style={{
              wordBreak: 'break-word',
              overflowWrap: 'anywhere',
            }}
          >
            {children}
          </p>
        ),
        strong: ({ children }) => (
          <strong className="font-semibold text-foreground">{children}</strong>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-6 space-y-1 mb-4">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-6 space-y-1 mb-4">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="text-base leading-relaxed">{children}</li>
        ),
        h1: ({ children }) => (
          <h1 className="text-2xl font-semibold tracking-tight mb-4">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-semibold tracking-tight mb-3">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold tracking-tight mb-2">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-base font-semibold tracking-tight mb-2">{children}</h4>
        ),
      }}
    >
      {children}
    </ReactMarkdown>
    </div>
  );
}
