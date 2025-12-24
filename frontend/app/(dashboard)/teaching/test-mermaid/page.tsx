/**
 * Mermaid Diagram Test Page
 *
 * Tests that Mermaid XY charts render correctly for economic diagrams
 */

'use client';

import { MermaidDiagram } from '@/components/teaching/MermaidDiagram';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function TestMermaidPage() {
  const supplyDemandCode = `xychart-beta
    title "Supply and Demand"
    x-axis "Quantity" 0 --> 100
    y-axis "Price ($)" 0 --> 50
    line "Demand" [45, 40, 35, 30, 25, 20, 15, 10, 5]
    line "Supply" [5, 10, 15, 20, 25, 30, 35, 40, 45]`;

  const ppfCode = `xychart-beta
    title "Production Possibility Frontier"
    x-axis "Goods A" 0 --> 100
    y-axis "Goods B" 0 --> 100
    line "PPF" [100, 90, 75, 55, 30, 0]`;

  const flowchartCode = `graph LR
    A[Perfect Competition] --> B{Many Firms?}
    B -->|Yes| C[Price Taker]
    B -->|No| D[Monopoly/Oligopoly]
    C --> E[Allocative Efficiency]`;

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      <h1 className="text-3xl font-bold">Mermaid Diagram Tests</h1>

      <Card>
        <CardHeader>
          <CardTitle>Test 1: Supply and Demand Curve</CardTitle>
        </CardHeader>
        <CardContent>
          <MermaidDiagram code={supplyDemandCode} id="test-supply-demand" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Test 2: Production Possibility Frontier</CardTitle>
        </CardHeader>
        <CardContent>
          <MermaidDiagram code={ppfCode} id="test-ppf" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Test 3: Flowchart (Market Structures)</CardTitle>
        </CardHeader>
        <CardContent>
          <MermaidDiagram code={flowchartCode} id="test-flowchart" />
        </CardContent>
      </Card>
    </div>
  );
}
