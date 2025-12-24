/**
 * MermaidDiagram Component
 *
 * Renders Mermaid diagrams from code strings.
 * Used for visual aids in teaching explanations (supply/demand curves, flowcharts, etc.)
 *
 * Features:
 * - Auto-initializes Mermaid library
 * - Error handling with fallback UI
 * - Collapsible code view for developers
 * - Responsive container with overflow handling
 *
 * @example
 * ```tsx
 * <MermaidDiagram
 *   code="graph TD; A-->B; B-->C;"
 *   id="diagram-1"
 * />
 * ```
 */

'use client';

import { useState, useEffect } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  code: string;
  id: string;
}

export function MermaidDiagram({ code, id }: MermaidDiagramProps) {
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Detect dark mode on mount and when it changes
  useEffect(() => {
    const checkDarkMode = () => {
      const darkMode = document.documentElement.classList.contains('dark');
      setIsDarkMode(darkMode);
    };

    // Initial check
    checkDarkMode();

    // Watch for theme changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => observer.disconnect();
  }, []);

  // Render diagram when code, id, or theme changes
  useEffect(() => {
    async function renderDiagram() {
      if (!code || code.trim() === '') {
        setError('No diagram code provided');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        // Initialize Mermaid with current theme
        mermaid.initialize({
          startOnLoad: false,
          theme: isDarkMode ? 'dark' : 'default',
          securityLevel: 'loose',
        });

        // Clean the code - remove any leading/trailing whitespace
        const cleanCode = code.trim();

        // Generate unique ID to avoid conflicts
        const diagramId = `${id}-${Date.now()}`;

        const { svg } = await mermaid.render(diagramId, cleanCode);
        setSvg(svg);
        setError('');
      } catch (err) {
        console.error('Mermaid render error:', err);
        console.error('Failed diagram code:', code);
        setError(`Failed to render diagram: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        setIsLoading(false);
      }
    }

    renderDiagram();
  }, [code, id, isDarkMode]);

  if (isLoading) {
    return (
      <div className="bg-muted/50 border border-muted rounded-lg p-8 text-center">
        <div className="animate-pulse text-muted-foreground">Loading diagram...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/50 rounded-lg p-4">
        <div className="text-destructive text-sm font-semibold mb-2">⚠️ Diagram Rendering Error</div>
        <div className="text-destructive/80 text-xs mb-3">{error}</div>
        <details>
          <summary className="cursor-pointer text-xs text-muted-foreground hover:text-primary transition">
            Show diagram code
          </summary>
          <pre className="mt-2 bg-muted p-3 rounded text-xs overflow-x-auto font-mono">
            {code}
          </pre>
        </details>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="bg-muted/50 border border-muted rounded-lg p-4 text-center text-muted-foreground text-sm">
        No diagram to display
      </div>
    );
  }

  return (
    <div className="mermaid-container bg-background border rounded-lg p-4 overflow-x-auto min-h-[200px]">
      <div
        className="mermaid-diagram"
        dangerouslySetInnerHTML={{ __html: svg }}
        style={{ minHeight: '150px' }}
      />
      <details className="mt-3">
        <summary className="cursor-pointer text-sm text-muted-foreground hover:text-primary transition">
          Show diagram code
        </summary>
        <pre className="mt-2 bg-muted p-3 rounded text-xs overflow-x-auto font-mono">
          {code}
        </pre>
      </details>
    </div>
  );
}
