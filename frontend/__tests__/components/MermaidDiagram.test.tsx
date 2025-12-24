/**
 * MermaidDiagram Component Tests
 *
 * Ensures Mermaid diagrams render correctly and prevent regression
 */

import { render, screen, waitFor } from '@testing-library/react';
import { MermaidDiagram } from '@/components/teaching/MermaidDiagram';

// Mock mermaid library
jest.mock('mermaid', () => ({
  initialize: jest.fn(),
  render: jest.fn().mockResolvedValue({
    svg: '<svg><text>Test SVG</text></svg>',
  }),
}));

describe('MermaidDiagram', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders mermaid diagram successfully', async () => {
    const testCode = `xychart-beta
    title "Supply and Demand"
    x-axis "Quantity" 0 --> 100
    y-axis "Price ($)" 0 --> 50
    line "Demand" [45, 40, 35, 30, 25, 20, 15, 10, 5]
    line "Supply" [5, 10, 15, 20, 25, 30, 35, 40, 45]`;

    render(<MermaidDiagram code={testCode} id="test-diagram" />);

    await waitFor(() => {
      // Check that the SVG was rendered
      const container = screen.getByText(/Test SVG/i).closest('.mermaid-container');
      expect(container).toBeInTheDocument();
    });
  });

  it('renders XY chart for supply and demand curves', async () => {
    const supplyDemandCode = `xychart-beta
    title "Supply and Demand"
    x-axis "Quantity" 0 --> 100
    y-axis "Price ($)" 0 --> 50
    line "Demand" [45, 40, 35, 30, 25, 20, 15, 10, 5]
    line "Supply" [5, 10, 15, 20, 25, 30, 35, 40, 45]`;

    render(<MermaidDiagram code={supplyDemandCode} id="supply-demand" />);

    await waitFor(() => {
      expect(screen.getByText(/Test SVG/i)).toBeInTheDocument();
    });
  });

  it('renders flowchart diagrams', async () => {
    const flowchartCode = `graph LR
    A[Perfect Competition] --> B{Many Firms?}
    B -->|Yes| C[Price Taker]
    B -->|No| D[Monopoly/Oligopoly]`;

    render(<MermaidDiagram code={flowchartCode} id="flowchart" />);

    await waitFor(() => {
      expect(screen.getByText(/Test SVG/i)).toBeInTheDocument();
    });
  });

  it('shows error message when rendering fails', async () => {
    const mermaid = require('mermaid');
    mermaid.render.mockRejectedValueOnce(new Error('Invalid syntax'));

    const invalidCode = 'invalid mermaid code';

    render(<MermaidDiagram code={invalidCode} id="error-test" />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to render diagram/i)).toBeInTheDocument();
    });
  });

  it('includes collapsible code view', async () => {
    const testCode = 'graph TD; A-->B;';

    render(<MermaidDiagram code={testCode} id="code-view-test" />);

    await waitFor(() => {
      expect(screen.getByText(/Show diagram code/i)).toBeInTheDocument();
    });
  });
});
