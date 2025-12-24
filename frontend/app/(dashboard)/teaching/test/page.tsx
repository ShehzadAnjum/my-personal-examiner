/**
 * Teaching Components Test Page
 *
 * Purpose: Visual validation of teaching UI components before integration
 *
 * Navigate to: http://localhost:3000/teaching/test
 *
 * Components Tested:
 * - ExplanationSection (collapsible with Accordion)
 * - ExplanationSectionAlwaysExpanded (non-collapsible)
 * - BookmarkButton (interactive bookmark with states)
 * - ExplanationSkeleton (loading state with pulse animation)
 * - ExplanationView (complete 9-component PhD-level explanation)
 *
 * Instructions:
 * 1. Start dev server: cd frontend && npm run dev
 * 2. Navigate to http://localhost:3000/teaching/test
 * 3. Test interactions:
 *    - Click section headers to expand/collapse
 *    - Click bookmark buttons to toggle states
 *    - Use Tab key to navigate between components
 *    - Use Enter/Space to activate buttons
 *    - Verify smooth animations
 *    - Check visual hierarchy and typography
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ExplanationSection,
  ExplanationSectionAlwaysExpanded,
} from '@/components/teaching/ExplanationSection';
import {
  BookmarkButton,
  BookmarkIconButton,
  BookmarkButtonWithCount,
} from '@/components/teaching/BookmarkButton';
import {
  ExplanationSkeleton,
  ExplanationSkeletonCompact,
} from '@/components/teaching/ExplanationSkeleton';
import { ExplanationView } from '@/components/teaching/ExplanationView';
import { TopicCard, TopicCardCompact } from '@/components/teaching/TopicCard';
import { TopicBrowser, TopicBrowserCompact } from '@/components/teaching/TopicBrowser';
import { TopicSearch } from '@/components/teaching/TopicSearch';
import {
  TopicSearchSkeleton,
  TopicSearchSkeletonCompact,
  TopicSearchSkeletonGrid,
} from '@/components/teaching/TopicSearchSkeleton';
import type { TopicExplanation, SyllabusTopic } from '@/lib/types/teaching';
import {
  BookOpen,
  BookOpenIcon,
  LightbulbIcon,
  AlertCircleIcon,
  AlertCircle,
  CheckCircle2Icon,
  LinkIcon,
  ArrowRight,
} from 'lucide-react';

export default function TeachingTestPage() {
  // State for interactive bookmark button demo
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isBookmarked2, setIsBookmarked2] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [bookmarkCount, setBookmarkCount] = useState(42);

  // State for ExplanationView demo
  const [explanationBookmarked, setExplanationBookmarked] = useState(false);

  // Mock SyllabusTopic data (for TopicCard/TopicBrowser demo - T020/T021)
  const mockTopics: SyllabusTopic[] = [
    // Section 2: The Price System and the Microeconomy
    {
      id: '550e8400-e29b-41d4-a716-446655440000',
      code: '9708.2.1.1',
      description: 'The Law of Demand',
      learning_outcomes:
        'State the law of demand\nExplain why demand curves slope downward\nIdentify exceptions to the law of demand (Giffen goods, Veblen goods)',
      topics: 'Demand theory, Consumer behavior',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440001',
      code: '9708.2.1.2',
      description: 'Individual and Market Demand',
      learning_outcomes:
        'Distinguish between individual and market demand\nDerive market demand from individual demand curves\nAnalyze factors affecting demand',
      topics: 'Demand curves, Market analysis',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440002',
      code: '9708.2.2.1',
      description: 'The Law of Supply',
      learning_outcomes:
        'State the law of supply\nExplain why supply curves slope upward\nAnalyze factors affecting supply',
      topics: 'Supply theory, Producer behavior',
      subject_id: '9708',
    },

    // Section 3: Government Microeconomic Intervention
    {
      id: '550e8400-e29b-41d4-a716-446655440003',
      code: '9708.3.1.1',
      description: 'Price Elasticity of Demand (PED) - Introduction',
      learning_outcomes:
        'Define price elasticity of demand\nUnderstand the concept of responsiveness',
      topics: 'Elasticity basics',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440004',
      code: '9708.3.1.2',
      description: 'Price Elasticity of Demand (PED) - Calculation',
      learning_outcomes:
        'Calculate PED using the percentage change formula\nInterpret PED values (elastic, inelastic, unit elastic)\nAnalyze the relationship between PED and total revenue',
      topics: 'Elasticity, Demand theory, Market equilibrium',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440005',
      code: '9708.3.1.3',
      description: 'Income Elasticity of Demand (YED)',
      learning_outcomes:
        'Define income elasticity of demand (YED)\nDistinguish between normal and inferior goods using YED\nCalculate YED from given data',
      topics: 'Elasticity, Consumer behavior',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440006',
      code: '9708.3.1.4',
      description: 'Cross Elasticity of Demand (XED)',
      learning_outcomes:
        'Define cross elasticity of demand\nDistinguish between substitutes and complements using XED\nAnalyze market relationships',
      topics: 'Elasticity, Market relationships',
      subject_id: '9708',
    },

    // Section 4: The Macroeconomy
    {
      id: '550e8400-e29b-41d4-a716-446655440007',
      code: '9708.4.1.1',
      description: 'National Income Accounting',
      learning_outcomes:
        'Define GDP, GNP, and GNI\nCalculate national income using different methods\nUnderstand the circular flow of income',
      topics: 'Macroeconomics, National income',
      subject_id: '9708',
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440008',
      code: '9708.4.2.1',
      description: 'Aggregate Demand and Supply',
      learning_outcomes:
        'Define aggregate demand and aggregate supply\nAnalyze shifts in AD and AS curves\nUnderstand equilibrium in the macroeconomy',
      topics: 'Macroeconomics, AD-AS model',
      subject_id: '9708',
    },
  ];

  // Mock TopicExplanation data (from Agent 06's 9-component framework)
  const mockExplanation: TopicExplanation = {
    syllabus_code: '9708.3.1.2',
    concept_name: 'Price Elasticity of Demand (PED)',
    definition:
      'Price Elasticity of Demand (PED) measures the responsiveness of quantity demanded to a change in price, calculated as the percentage change in quantity demanded divided by the percentage change in price.\n\nFormula: PED = (% change in quantity demanded) / (% change in price)',
    key_terms: [
      {
        term: 'Elastic Demand',
        definition: 'When PED > 1, meaning quantity demanded changes by a larger percentage than price. Demand is responsive to price changes.',
      },
      {
        term: 'Inelastic Demand',
        definition: 'When PED < 1, meaning quantity demanded changes by a smaller percentage than price. Demand is unresponsive to price changes.',
      },
      {
        term: 'Unit Elastic Demand',
        definition: 'When PED = 1, meaning quantity demanded changes by the same percentage as price.',
      },
    ],
    explanation:
      'Key principles of PED:\n\n1. If PED > 1: Demand is ELASTIC (quantity changes more than price)\n   - Example: Luxury goods, non-essential items\n   - Price increase → large drop in quantity demanded\n\n2. If PED < 1: Demand is INELASTIC (quantity changes less than price)\n   - Example: Necessities (bread, fuel, insulin)\n   - Price increase → small drop in quantity demanded\n\n3. If PED = 1: Demand is UNIT ELASTIC (equal percentage changes)\n\n4. Determinants of PED:\n   - Availability of substitutes (more substitutes = more elastic)\n   - Necessity vs luxury (necessities = more inelastic)\n   - Proportion of income (larger proportion = more elastic)\n   - Time period (longer time = more elastic)\n   - Addiction/habit (addictive goods = more inelastic)',
    examples: [
      {
        title: 'Insulin (Inelastic Demand)',
        scenario:
          'A pharmaceutical company increases insulin price from $100 to $120 (20% increase). Quantity demanded falls from 1000 units to 950 units (5% decrease).',
        analysis:
          'PED = -5% / 20% = -0.25 (inelastic)\n\nWhy inelastic? Insulin is a life-saving necessity with no close substitutes. Diabetic patients cannot reduce consumption significantly even when price rises. This gives pharmaceutical companies pricing power, which is why governments often regulate insulin prices.',
      },
      {
        title: 'Designer Handbags (Elastic Demand)',
        scenario:
          'A luxury brand increases handbag price from $500 to $600 (20% increase). Quantity demanded falls from 10,000 units to 7,000 units (30% decrease).',
        analysis:
          'PED = -30% / 20% = -1.5 (elastic)\n\nWhy elastic? Designer handbags are luxury items with many substitute brands. Consumers can easily switch to cheaper alternatives or delay purchases. The large drop in quantity shows demand is responsive to price changes.',
      },
    ],
    visual_aids: [
      {
        type: 'diagram',
        title: 'Elastic vs Inelastic Demand Curves',
        description:
          'Elastic demand curve: Flatter slope (horizontal)\n- Small price change → large quantity change\n- PED > 1\n\nInelastic demand curve: Steeper slope (vertical)\n- Large price change → small quantity change\n- PED < 1\n\nVisualization:\nPrice ↑\n│\n│   ╱  (Elastic - flatter)\n│  ╱\n│ ╱\n│╱_________ Quantity →\n│|\n│ | (Inelastic - steeper)\n│ |\n│ |',
      },
    ],
    worked_examples: [
      {
        problem:
          'A coffee shop increases price from $3 to $4 per cup. Daily sales fall from 100 cups to 80 cups. Calculate PED and advise whether the shop should reverse the price increase.',
        step_by_step_solution:
          'Step 1: Calculate % change in quantity\nΔQ = (80 - 100) / 100 × 100 = -20%\n\nStep 2: Calculate % change in price\nΔP = (4 - 3) / 3 × 100 = +33.33%\n\nStep 3: Calculate PED\nPED = -20% / +33.33% = -0.6\n|PED| = 0.6 < 1 → Inelastic demand\n\nStep 4: Calculate revenue before and after\nRevenue before: $3 × 100 = $300\nRevenue after: $4 × 80 = $320\nRevenue increased by $20\n\nStep 5: Recommendation\nDo NOT reverse the price increase. Despite losing 20 cups in sales, total revenue increased by $20. With inelastic demand, price increases raise revenue.',
        marks_breakdown:
          '% change in quantity: 2 marks\n% change in price: 2 marks\nPED calculation: 2 marks\nRevenue analysis: 2 marks\nRecommendation with justification: 2 marks\nTotal: 10 marks',
      },
    ],
    common_misconceptions: [
      {
        misconception: 'Elastic demand means demand is high',
        why_wrong:
          'Elasticity measures RESPONSIVENESS to price changes, not the LEVEL of demand. You can have high demand that is inelastic (e.g., insulin) or low demand that is elastic (e.g., luxury yachts).',
        correct_understanding:
          'Elastic demand means quantity demanded is SENSITIVE to price changes. If price rises 10%, quantity might fall 20% (PED = -2). This is about responsiveness, not volume.',
      },
      {
        misconception: 'PED is always negative',
        why_wrong:
          'While PED is typically negative due to the law of demand (inverse price-quantity relationship), economists often report the ABSOLUTE VALUE to avoid confusion with signs.',
        correct_understanding:
          'PED formula gives negative values (e.g., -0.5, -2.3), but we interpret using absolute value: |PED| = 0.5 (inelastic), |PED| = 2.3 (elastic). Focus on the magnitude, not the sign.',
      },
    ],
    practice_problems: [
      {
        question:
          'The price of petrol increases from $1.50 to $1.80 per litre. Quantity demanded falls from 1,000,000 litres to 950,000 litres per day. Calculate PED.',
        difficulty: 'easy',
        answer_outline:
          '% change in quantity = (950,000 - 1,000,000) / 1,000,000 × 100 = -5%\n% change in price = (1.80 - 1.50) / 1.50 × 100 = +20%\nPED = -5% / +20% = -0.25 (inelastic)\n\nInterpretation: Petrol demand is inelastic because it is a necessity with few short-term substitutes.',
        marks: 6,
      },
      {
        question:
          'A firm sells 500 units at $20 each. After reducing price to $18, sales increase to 600 units. (a) Calculate PED. (b) Explain whether the firm should keep the new price or revert to the old price.',
        difficulty: 'medium',
        answer_outline:
          '(a) % change in quantity = (600 - 500) / 500 × 100 = +20%\n% change in price = (18 - 20) / 20 × 100 = -10%\nPED = +20% / -10% = -2 (elastic)\n\n(b) Revenue before: $20 × 500 = $10,000\nRevenue after: $18 × 600 = $10,800\nRevenue increased by $800.\n\nRecommendation: Keep the new price ($18). With elastic demand (|PED| > 1), a price decrease increases total revenue. The firm gains more from extra sales (100 units) than it loses from lower price ($2 per unit).',
        marks: 10,
      },
    ],
    related_concepts: [
      'Income Elasticity of Demand (YED)',
      'Cross Elasticity of Demand (XED)',
      'Price Elasticity of Supply (PES)',
      'Total Revenue and Elasticity',
    ],
    generated_by: 'anthropic',
  };

  // Simulate async bookmark action
  const handleBookmarkToggle = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsBookmarked(!isBookmarked);
      setIsLoading(false);
    }, 1500); // 1.5s simulated API call
  };

  const handleBookmarkToggle2 = () => {
    setIsBookmarked2(!isBookmarked2);
  };

  const handleBookmarkWithCount = () => {
    if (!isBookmarked) {
      setBookmarkCount(bookmarkCount + 1);
    } else {
      setBookmarkCount(bookmarkCount - 1);
    }
    setIsBookmarked(!isBookmarked);
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">
          Teaching Components Test Page
        </h1>
        <p className="text-muted-foreground">
          Visual validation of teaching UI components • Feature
          005-teaching-page
        </p>
      </div>

      <div className="space-y-6">
        {/* BookmarkButton Component Demo */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            BookmarkButton Component (NEW - T014)
          </h2>

          <div className="space-y-6">
            {/* Interactive States */}
            <div className="p-6 border rounded-lg bg-card">
              <h3 className="font-semibold mb-4">Interactive Button States</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <BookmarkButton
                    isBookmarked={isBookmarked}
                    isLoading={isLoading}
                    onClick={handleBookmarkToggle}
                  />
                  <span className="text-sm text-muted-foreground">
                    Click to toggle (simulates 1.5s API call)
                  </span>
                </div>
                <div className="text-xs text-muted-foreground bg-muted p-3 rounded">
                  <strong>Current state:</strong> {isBookmarked ? 'Bookmarked' : 'Not bookmarked'} •{' '}
                  {isLoading ? 'Loading...' : 'Ready'}
                </div>
              </div>
            </div>

            {/* All Button Variants */}
            <div className="p-6 border rounded-lg bg-card">
              <h3 className="font-semibold mb-4">Button Variants</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Default (Not Bookmarked) */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Default (Not Bookmarked)</p>
                  <BookmarkButton
                    isBookmarked={false}
                    onClick={() => alert('Save clicked!')}
                  />
                  <p className="text-xs text-muted-foreground">
                    Outline style, empty star icon
                  </p>
                </div>

                {/* Bookmarked */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Bookmarked</p>
                  <BookmarkButton
                    isBookmarked={true}
                    onClick={() => alert('Remove clicked!')}
                  />
                  <p className="text-xs text-muted-foreground">
                    Primary color, filled star icon
                  </p>
                </div>

                {/* Loading (Saving) */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Loading (Saving)</p>
                  <BookmarkButton
                    isBookmarked={false}
                    isLoading={true}
                    onClick={() => {}}
                  />
                  <p className="text-xs text-muted-foreground">
                    Spinner icon, "Saving..." text, disabled
                  </p>
                </div>

                {/* Loading (Removing) */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Loading (Removing)</p>
                  <BookmarkButton
                    isBookmarked={true}
                    isLoading={true}
                    onClick={() => {}}
                  />
                  <p className="text-xs text-muted-foreground">
                    Spinner icon, "Removing..." text, disabled
                  </p>
                </div>

                {/* Disabled */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Disabled</p>
                  <BookmarkButton
                    isBookmarked={false}
                    disabled={true}
                    onClick={() => {}}
                  />
                  <p className="text-xs text-muted-foreground">
                    Greyed out, not clickable
                  </p>
                </div>

                {/* Icon Only */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Icon Only</p>
                  <BookmarkIconButton
                    isBookmarked={isBookmarked2}
                    onClick={handleBookmarkToggle2}
                  />
                  <p className="text-xs text-muted-foreground">
                    Compact version for cards/headers
                  </p>
                </div>

                {/* With Count */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">With Count (Social Proof)</p>
                  <BookmarkButtonWithCount
                    isBookmarked={isBookmarked}
                    count={bookmarkCount}
                    onClick={handleBookmarkWithCount}
                  />
                  <p className="text-xs text-muted-foreground">
                    Shows how many students saved this
                  </p>
                </div>

                {/* Different Sizes */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Size Variants</p>
                  <div className="flex items-center gap-2">
                    <BookmarkButton
                      isBookmarked={false}
                      onClick={() => {}}
                      size="sm"
                    />
                    <BookmarkButton
                      isBookmarked={false}
                      onClick={() => {}}
                      size="default"
                    />
                    <BookmarkButton
                      isBookmarked={false}
                      onClick={() => {}}
                      size="lg"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Small, Default, Large
                  </p>
                </div>
              </div>
            </div>

            {/* Accessibility Info */}
            <div className="p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
              <h4 className="font-semibold text-sm mb-2 text-blue-900 dark:text-blue-100">
                ♿ Accessibility Features
              </h4>
              <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                <li>✅ Keyboard: Tab to focus, Enter/Space to activate</li>
                <li>✅ Screen reader: "Save explanation, button" or "Remove bookmark, button"</li>
                <li>✅ Loading state announced: "Saving explanation"</li>
                <li>✅ aria-label describes action, aria-pressed indicates state</li>
                <li>✅ Focus indicator visible on keyboard navigation</li>
                <li>✅ Touch target meets 44px minimum (WCAG 2.1 AA)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* TopicCard Component (NEW - T020) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            TopicCard Component (NEW - T020)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Displays syllabus topics in the topic browser. Shows topic code, description, and learning outcomes preview.
            Used in TopicBrowser (T021) and TopicSearch (T022) components.
          </p>

          <div className="space-y-6">
            {/* Regular TopicCard */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Regular TopicCard</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Full card with learning outcomes preview and topics field. Click to navigate to explanation page.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mockTopics.map((topic) => (
                  <TopicCard
                    key={topic.id}
                    topic={topic}
                    onClick={() => alert(`Navigate to: /teaching/${topic.id}\n\nTopic: ${topic.code} - ${topic.description}`)}
                  />
                ))}
              </div>
            </div>

            {/* TopicCard with Remove Button */}
            <div>
              <h3 className="text-lg font-semibold mb-3">TopicCard with Remove Button</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Used in saved topics list. Hover to see remove button (X icon in top-right corner).
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <TopicCard
                  topic={mockTopics[0]}
                  onClick={() => alert('View explanation')}
                  showRemoveButton
                  onRemove={() => alert('Remove topic from saved list')}
                />
              </div>
            </div>

            {/* Compact TopicCard */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Compact TopicCard</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Dense variant for search results or lists with many items. Shows only code and description.
              </p>

              <div className="space-y-2">
                {mockTopics.map((topic) => (
                  <TopicCardCompact
                    key={topic.id}
                    topic={topic}
                    onClick={() => alert(`Navigate to: /teaching/${topic.id}`)}
                  />
                ))}
              </div>
            </div>

            {/* Responsive Grid Demo */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Responsive Grid Layout</h3>
              <p className="text-sm text-muted-foreground mb-4">
                How TopicCards will appear in the TopicBrowser. Resize browser to see responsive behavior.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockTopics.concat(mockTopics).map((topic, index) => (
                  <TopicCard
                    key={`${topic.id}-${index}`}
                    topic={topic}
                    onClick={() => alert(`Navigate to: /teaching/${topic.id}`)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Testing Checklist */}
          <div className="mt-6 p-4 bg-primary/5 border-l-4 border-primary rounded">
            <h4 className="font-semibold text-sm mb-2 text-primary">TopicCard Testing Checklist (T020)</h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Verify topic code badge displays correctly (e.g., "9708.3.1.2")</li>
              <li>✅ Verify description is clear and readable</li>
              <li>✅ Verify learning outcomes preview shows first 2 outcomes</li>
              <li>✅ Verify "+ N more outcomes" indicator displays when &gt;2 outcomes exist</li>
              <li>✅ Verify topics field displays when present (bottom section)</li>
              <li>✅ Click card - should trigger onClick alert with topic details</li>
              <li>✅ Hover over card - should show shadow and border highlight</li>
              <li>✅ Hover over card with remove button - X icon should appear in top-right</li>
              <li>✅ Click remove button - should trigger onRemove alert (not card onClick)</li>
              <li>✅ Tab through cards - focus indicator should be visible (keyboard navigation)</li>
              <li>✅ Press Enter/Space on focused card - should trigger onClick</li>
              <li>✅ Verify compact variant shows only code + description (no outcomes)</li>
              <li>✅ Verify responsive grid (1 column mobile, 2 tablet, 3 desktop)</li>
              <li>✅ Test on mobile (375px width) - cards should be readable and tappable</li>
              <li>✅ Verify chevron icon changes color on hover</li>
              <li>✅ Verify BookOpen icon displays in topic code badge</li>
            </ul>
          </div>
        </div>

        {/* TopicBrowser Component (NEW - T021) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            TopicBrowser Component (NEW - T021)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Hierarchical tree view of syllabus topics organized by section. Parses syllabus codes
            (e.g., "9708.3.1.2") to group topics into collapsible sections with counts.
            Integrates with TopicCard component from T020.
          </p>

          <div className="space-y-6">
            {/* Regular TopicBrowser */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Regular TopicBrowser</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Full browser with all sections expanded by default. Click topics to view explanations.
                Click section headers to collapse/expand.
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicBrowser
                  topics={mockTopics}
                  onTopicClick={(topicId) =>
                    alert(`Navigate to: /teaching/${topicId}\n\nWould open explanation page`)
                  }
                />
              </div>
            </div>

            {/* Compact TopicBrowser */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Compact TopicBrowser</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Dense variant for sidebars or embedded views. Shows first section expanded,
                limits to 5 topics per section.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 bg-background">
                  <TopicBrowserCompact
                    topics={mockTopics}
                    onTopicClick={(topicId) => alert(`View topic: ${topicId}`)}
                  />
                </div>

                <div className="space-y-3 text-sm">
                  <div>
                    <p className="font-semibold mb-1">Use Cases:</p>
                    <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                      <li>Sidebar navigation in dashboard</li>
                      <li>Quick topic selector in modal dialogs</li>
                      <li>Related topics widget in explanation pages</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold mb-1">Features:</p>
                    <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                      <li>First section auto-expanded</li>
                      <li>Max 5 topics per section shown</li>
                      <li>"+ N more" indicator for truncated lists</li>
                      <li>Smaller text and tighter spacing</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Loading State */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Loading State</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Shown while topics are being fetched from API.
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicBrowser topics={[]} isLoading={true} />
              </div>
            </div>

            {/* Empty State */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Empty State</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Shown when no topics match the current filters or database is empty.
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicBrowser topics={[]} isLoading={false} />
              </div>
            </div>
          </div>

          {/* Testing Checklist */}
          <div className="mt-6 p-4 bg-primary/5 border-l-4 border-primary rounded">
            <h4 className="font-semibold text-sm mb-2 text-primary">
              TopicBrowser Testing Checklist (T021)
            </h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Verify topics are grouped by section (Section 2, 3, 4)</li>
              <li>✅ Verify section names display correctly (e.g., "Government Microeconomic Intervention")</li>
              <li>✅ Verify topic counts show in section headers (e.g., "4 topics")</li>
              <li>✅ Click section header - should collapse/expand section</li>
              <li>✅ Verify all sections expanded by default in regular browser</li>
              <li>✅ Verify topics within sections are sorted by code (9708.3.1.1 → 9708.3.1.2 → 9708.3.1.3)</li>
              <li>✅ Click topic card - should trigger onClick alert with topic ID</li>
              <li>✅ Verify footer stats show total topics and section count</li>
              <li>✅ Verify responsive grid (1 column mobile, 2 tablet, 3 desktop) within each section</li>
              <li>✅ Test compact variant - first section expanded, others collapsed</li>
              <li>✅ Verify compact variant shows max 5 topics per section</li>
              <li>✅ Verify "+ N more" indicator in compact variant</li>
              <li>✅ Verify loading state shows animated icon and text</li>
              <li>✅ Verify empty state shows BookOpen icon and helpful message</li>
              <li>✅ Tab through sections - keyboard navigation should work</li>
              <li>✅ Test on mobile (375px width) - sections should be readable and tappable</li>
            </ul>
          </div>
        </div>

        {/* TopicSearch Component (NEW - T022) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            TopicSearch Component (NEW - T022)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Client-side search for syllabus topics with 300ms debouncing and keyword highlighting.
            Searches across code, description, and learning outcomes. Instant results (&lt;1ms for 200 topics).
          </p>

          <div className="space-y-6">
            {/* Interactive Search Demo */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Interactive Search Demo</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Try searching for: "elasticity", "demand", "3.1", "PED", "macroeconomics", etc.
                Keywords will be highlighted in yellow.
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicSearch
                  topics={mockTopics}
                  onSelectTopic={(topicId) =>
                    alert(`Navigate to: /teaching/${topicId}\n\nWould open explanation page`)
                  }
                />
              </div>

              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded">
                <p className="text-xs text-blue-900 dark:text-blue-100 mb-2">
                  <strong>Search Features:</strong>
                </p>
                <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                  <li>300ms debounce - Type "elasticity" and watch it wait before searching</li>
                  <li>Keyword highlighting - Matching text highlighted in yellow</li>
                  <li>Multi-field search - Searches code, description, learning outcomes, topics</li>
                  <li>Result count - Shows "Found N results" or "Showing all topics"</li>
                  <li>Clear button - Click X to clear search instantly</li>
                  <li>No results state - Helpful suggestions when nothing matches</li>
                  <li>Learning outcome matches - Shows matching outcomes in italics</li>
                </ul>
              </div>
            </div>

            {/* Search Performance Test */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Performance Test</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Current dataset: {mockTopics.length} topics. Search should filter &lt;1ms.
                Open DevTools Console and type to see debounce delay logs.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 bg-background">
                  <p className="text-xs font-semibold mb-2 text-muted-foreground">
                    Search Query Examples:
                  </p>
                  <ul className="text-xs space-y-1">
                    <li><code className="px-1 py-0.5 bg-muted rounded">elasticity</code> → 4 results</li>
                    <li><code className="px-1 py-0.5 bg-muted rounded">demand</code> → 5 results</li>
                    <li><code className="px-1 py-0.5 bg-muted rounded">3.1</code> → 4 results (section 3.1)</li>
                    <li><code className="px-1 py-0.5 bg-muted rounded">macro</code> → 2 results</li>
                    <li><code className="px-1 py-0.5 bg-muted rounded">xyz</code> → 0 results (no match)</li>
                  </ul>
                </div>

                <div className="border rounded-lg p-4 bg-background">
                  <p className="text-xs font-semibold mb-2 text-muted-foreground">
                    Expected Behavior:
                  </p>
                  <ul className="text-xs space-y-1 list-disc list-inside">
                    <li>Typing → 300ms wait → Filter updates</li>
                    <li>Matching keywords highlighted in yellow</li>
                    <li>Result count updates dynamically</li>
                    <li>TopicCardCompact used for results</li>
                    <li>Click topic → Alert with topic ID</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Testing Checklist */}
          <div className="mt-6 p-4 bg-primary/5 border-l-4 border-primary rounded">
            <h4 className="font-semibold text-sm mb-2 text-primary">
              TopicSearch Testing Checklist (T022)
            </h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Type in search box - input should update immediately</li>
              <li>✅ Wait 300ms after typing - results should filter after debounce</li>
              <li>✅ Search "elasticity" - should find 4 topics and highlight keyword in yellow</li>
              <li>✅ Search "3.1" - should find 4 topics (section 3.1.x codes)</li>
              <li>✅ Search "xyz" - should show "No topics found" with suggestions</li>
              <li>✅ Verify result count displays correctly (e.g., "Found 4 results for 'elasticity'")</li>
              <li>✅ Verify "Showing all N topics" when search is empty</li>
              <li>✅ Click clear button (X) - should clear search and show all topics</li>
              <li>✅ Click topic card in results - should trigger onClick alert</li>
              <li>✅ Verify learning outcome matches show in italics below description</li>
              <li>✅ Test case-insensitive search ("DEMAND" = "demand")</li>
              <li>✅ Test multi-word search ("price elasticity")</li>
              <li>✅ Verify no results state shows helpful suggestions</li>
              <li>✅ Verify search across all fields (code, description, learning_outcomes, topics)</li>
              <li>✅ Test on mobile (375px width) - search input and results should be usable</li>
            </ul>
          </div>
        </div>

        {/* TopicSearchSkeleton Component (NEW - T023) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            TopicSearchSkeleton Component (NEW - T023)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Loading skeleton for TopicSearch component with pulse animation.
            Mimics search bar + topic results structure.
          </p>

          <div className="space-y-6">
            {/* Regular TopicSearchSkeleton */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Regular TopicSearchSkeleton</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Full skeleton with search bar and 5 topic card placeholders.
                Used while topics are being fetched from API.
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicSearchSkeleton count={5} />
              </div>
            </div>

            {/* Compact TopicSearchSkeleton */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Compact TopicSearchSkeleton</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Smaller skeleton for embedded search components (sidebars, modals).
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 bg-background">
                  <TopicSearchSkeletonCompact count={3} />
                </div>

                <div className="space-y-2 text-sm">
                  <p className="font-semibold">Features:</p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-1">
                    <li>Smaller input (h-9 vs h-10)</li>
                    <li>Tighter spacing (space-y-1.5)</li>
                    <li>Fewer skeletons (default 3 vs 5)</li>
                    <li>Compact card layout</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Grid TopicSearchSkeleton */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Grid TopicSearchSkeleton</h3>
              <p className="text-sm text-muted-foreground mb-4">
                For search results displayed in grid layout instead of list.
                Shows full TopicCard skeletons (not compact).
              </p>

              <div className="border rounded-lg p-6 bg-background">
                <TopicSearchSkeletonGrid count={6} columns={2} />
              </div>
            </div>

            {/* Before/After Comparison */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Before/After Comparison</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Left: Loading skeleton | Right: Actual search (type "elasticity")
              </p>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="border rounded-lg p-4 bg-muted/20">
                  <p className="text-sm font-medium mb-3 text-muted-foreground">Loading State...</p>
                  <TopicSearchSkeleton count={3} />
                </div>

                <div className="border rounded-lg p-4 bg-background">
                  <p className="text-sm font-medium mb-3 text-primary">Loaded Content</p>
                  <TopicSearch
                    topics={mockTopics.slice(0, 3)}
                    onSelectTopic={(id) => alert(id)}
                    placeholder="Search (pre-filtered to 3 topics)..."
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Testing Checklist */}
          <div className="mt-6 p-4 bg-primary/5 border-l-4 border-primary rounded">
            <h4 className="font-semibold text-sm mb-2 text-primary">
              TopicSearchSkeleton Testing Checklist (T023)
            </h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Verify pulse animation is smooth and continuous</li>
              <li>✅ Verify search icon animates with pulse</li>
              <li>✅ Verify skeleton structure matches TopicSearch layout</li>
              <li>✅ Verify regular skeleton shows 5 topic cards by default</li>
              <li>✅ Verify compact skeleton shows 3 topic cards by default</li>
              <li>✅ Verify compact skeleton has smaller input (h-9)</li>
              <li>✅ Verify grid skeleton shows cards in 2-column grid</li>
              <li>✅ Verify grid skeleton has full TopicCard structure (header, description, outcomes)</li>
              <li>✅ Verify fade-in animation on mount (500ms duration for regular)</li>
              <li>✅ Verify occasional learning outcome skeleton (every 3rd item)</li>
              <li>✅ Compare skeleton with actual TopicSearch - visual alignment should match</li>
              <li>✅ Test on mobile (375px width) - skeleton should be responsive</li>
            </ul>
          </div>
        </div>

        {/* Main Teaching Page Route (NEW - T024) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Main Teaching Page Route (NEW - T024)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            The main /teaching page that integrates TopicBrowser and TopicSearch.
            Uses useTopics hook to fetch topics from API, handles loading/error states,
            and provides Browse/Search tabs for different UX preferences.
          </p>

          <div className="space-y-6">
            {/* Live Page Link */}
            <div className="border-2 border-primary/30 rounded-lg p-6 bg-primary/5">
              <h3 className="text-lg font-semibold mb-3">🎯 Live Teaching Page</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The actual teaching page is now live! Click the link below to test the full integration.
              </p>

              <Link
                href="/teaching"
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium shadow-md hover:shadow-lg"
              >
                <BookOpen className="h-5 w-5" />
                Open Teaching Page
                <ArrowRight className="h-5 w-5" />
              </Link>

              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded">
                <p className="text-xs text-blue-900 dark:text-blue-100 mb-2">
                  <strong>What to Test:</strong>
                </p>
                <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                  <li>Browse tab: Hierarchical topic browser with collapsible sections</li>
                  <li>Search tab: Live search with debouncing and keyword highlighting</li>
                  <li>Loading state: Skeleton shows while topics are fetching from API</li>
                  <li>Error handling: Alert shows if API call fails (with retry button)</li>
                  <li>Click any topic: Navigate to /teaching/[topicId] explanation page</li>
                  <li>Quick stats footer: Shows topic count, subject code, quality level</li>
                </ul>
              </div>
            </div>

            {/* Page Architecture */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Page Architecture</h3>
              <div className="border rounded-lg p-4 bg-muted/20">
                <pre className="text-xs font-mono whitespace-pre-wrap">
{`/teaching (main page - T024)
├── Header (title + description)
├── Error Alert (if topics fail to load)
├── Tabs (Browse | Search)
│   ├── Browse Tab
│   │   └── TopicBrowser (T021)
│   │       └── TopicCard (T020) x N topics
│   └── Search Tab
│       └── TopicSearch (T022)
│           └── TopicCardCompact x N results
├── Loading State: TopicSearchSkeleton (T023)
└── Quick Stats Footer`}
                </pre>
              </div>
            </div>

            {/* Integration Points */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Integration Points</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <p className="font-semibold text-sm mb-2">Data Fetching:</p>
                  <ul className="text-xs space-y-1 text-muted-foreground list-disc list-inside">
                    <li>useTopics hook (TanStack Query)</li>
                    <li>1 hour staleTime (topics rarely change)</li>
                    <li>2 hour cache (fast re-access)</li>
                    <li>Exponential backoff retry</li>
                    <li>GET /api/syllabus?subject_code=9708</li>
                  </ul>
                </div>

                <div className="border rounded-lg p-4">
                  <p className="font-semibold text-sm mb-2">State Management:</p>
                  <ul className="text-xs space-y-1 text-muted-foreground list-disc list-inside">
                    <li>activeTab: 'browse' | 'search'</li>
                    <li>isLoading → TopicSearchSkeleton</li>
                    <li>isError → Alert + toast</li>
                    <li>topics[] → TopicBrowser/TopicSearch</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Prerequisites Warning */}
            <div className="border border-amber-200 dark:border-amber-800 rounded-lg p-4 bg-amber-50 dark:bg-amber-950">
              <p className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-2">
                ⚠️ Backend Requirements
              </p>
              <p className="text-xs text-amber-800 dark:text-amber-200 mb-2">
                For the teaching page to work properly, ensure:
              </p>
              <ul className="text-xs text-amber-700 dark:text-amber-300 space-y-1 list-disc list-inside">
                <li>Backend server running on http://localhost:8000</li>
                <li>GET /api/syllabus endpoint implemented</li>
                <li>Database seeded with Economics 9708 syllabus topics</li>
                <li>At least 1 topic exists in database</li>
              </ul>
              <p className="text-xs text-amber-700 dark:text-amber-300 mt-2">
                <strong>If backend is not ready:</strong> The page will show loading skeleton indefinitely,
                then error alert with retry button. This is expected behavior - the error handling is working correctly.
              </p>
            </div>
          </div>

          {/* Testing Checklist */}
          <div className="mt-6 p-4 bg-primary/5 border-l-4 border-primary rounded">
            <h4 className="font-semibold text-sm mb-2 text-primary">
              Main Teaching Page Testing Checklist (T024)
            </h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Navigate to /teaching - page should load</li>
              <li>✅ Verify page header displays (BookOpen icon + "Teaching" title)</li>
              <li>✅ Verify description text below header</li>
              <li>✅ Verify Browse/Search tabs display correctly</li>
              <li>✅ Click Browse tab - should show TopicBrowser with hierarchical sections</li>
              <li>✅ Click Search tab - should show TopicSearch with search input</li>
              <li>✅ Verify loading state shows TopicSearchSkeleton (if API is slow)</li>
              <li>✅ Verify error alert shows if backend is not running (red alert with retry button)</li>
              <li>✅ Click retry button in error alert - should attempt to refetch topics</li>
              <li>✅ Verify toast notification appears on error (top-right corner)</li>
              <li>✅ In Browse tab: Click any section header - should expand/collapse</li>
              <li>✅ In Browse tab: Click any topic card - should navigate to /teaching/[topicId]</li>
              <li>✅ In Search tab: Type "elasticity" - should filter and highlight results</li>
              <li>✅ In Search tab: Click any result - should navigate to /teaching/[topicId]</li>
              <li>✅ Verify Quick Stats footer shows topic count, subject code, quality level</li>
              <li>✅ Test on mobile (375px width) - tabs, browser, search should all work</li>
              <li>✅ Verify tab switching preserves scroll position</li>
              <li>✅ Verify topics load from cache on second visit (instant, no skeleton)</li>
            </ul>
          </div>
        </div>

        {/* Always Expanded Section (Critical Content) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Always Expanded (Critical Content)
          </h2>

          <div className="space-y-4">
            <ExplanationSectionAlwaysExpanded
              title="Definition"
              icon={<BookOpenIcon className="h-5 w-5" />}
            >
              <p className="mb-3">
                <strong>Price Elasticity of Demand (PED)</strong> measures the
                responsiveness of quantity demanded to a change in price,
                calculated as the percentage change in quantity demanded divided
                by the percentage change in price.
              </p>
              <p className="text-muted-foreground text-sm">
                This section is always visible because the definition is
                essential for understanding the concept.
              </p>
            </ExplanationSectionAlwaysExpanded>

            <ExplanationSectionAlwaysExpanded
              title="Core Principles"
              icon={<LightbulbIcon className="h-5 w-5" />}
            >
              <ul className="space-y-2 list-disc list-inside">
                <li>
                  If PED &gt; 1: Demand is <strong>elastic</strong> (quantity
                  changes more than price)
                </li>
                <li>
                  If PED &lt; 1: Demand is <strong>inelastic</strong> (quantity
                  changes less than price)
                </li>
                <li>
                  If PED = 1: Demand is <strong>unit elastic</strong> (equal
                  percentage changes)
                </li>
              </ul>
            </ExplanationSectionAlwaysExpanded>
          </div>
        </div>

        {/* Collapsible Sections (Supplementary Content) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Collapsible (Supplementary Content)
          </h2>

          <div className="space-y-4">
            <ExplanationSection
              title="Real-World Examples"
              defaultExpanded={false}
              icon={<CheckCircle2Icon className="h-5 w-5" />}
            >
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-1">
                    Example 1: Luxury Goods (Elastic Demand)
                  </h4>
                  <p className="text-sm">
                    A 10% increase in the price of designer handbags leads to a
                    25% decrease in quantity demanded. PED = 2.5 (elastic).
                    Consumers easily substitute with cheaper alternatives.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold mb-1">
                    Example 2: Necessities (Inelastic Demand)
                  </h4>
                  <p className="text-sm">
                    A 10% increase in the price of insulin leads to only a 2%
                    decrease in quantity demanded. PED = 0.2 (inelastic).
                    Diabetic patients have few alternatives.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold mb-1">
                    Example 3: Gasoline (Short-term Inelastic, Long-term
                    Elastic)
                  </h4>
                  <p className="text-sm">
                    Short-term: PED = 0.3 (people still need to drive).
                    Long-term: PED = 1.5 (consumers buy fuel-efficient cars,
                    carpool, use public transit).
                  </p>
                </div>
              </div>
            </ExplanationSection>

            <ExplanationSection
              title="Common Misconceptions"
              defaultExpanded={false}
              icon={<AlertCircleIcon className="h-5 w-5" />}
            >
              <div className="space-y-3">
                <div className="bg-destructive/10 border-l-4 border-destructive p-3 rounded">
                  <p className="font-semibold text-sm mb-1">
                    ❌ Misconception: "Elastic means demand is high"
                  </p>
                  <p className="text-sm">
                    ✅ Correction: Elasticity measures{' '}
                    <em>responsiveness to price changes</em>, not the level of
                    demand. High demand doesn't mean elastic demand.
                  </p>
                </div>

                <div className="bg-destructive/10 border-l-4 border-destructive p-3 rounded">
                  <p className="font-semibold text-sm mb-1">
                    ❌ Misconception: "PED is always negative"
                  </p>
                  <p className="text-sm">
                    ✅ Correction: While PED is typically negative (inverse
                    relationship between price and quantity), economists often
                    report the <strong>absolute value</strong> to avoid
                    confusion. PED = |-0.5| = 0.5 (inelastic).
                  </p>
                </div>
              </div>
            </ExplanationSection>

            <ExplanationSection
              title="Practice Problems"
              defaultExpanded={false}
            >
              <div className="space-y-4">
                <div className="bg-muted p-4 rounded-lg">
                  <p className="font-semibold mb-2">Problem 1:</p>
                  <p className="text-sm mb-2">
                    The price of coffee increases from $3 to $4 per cup. Quantity
                    demanded falls from 100 cups to 80 cups per day. Calculate
                    PED.
                  </p>
                  <details className="text-sm text-muted-foreground">
                    <summary className="cursor-pointer hover:text-foreground">
                      Show answer outline
                    </summary>
                    <div className="mt-2 pl-4">
                      <p>
                        % change in quantity = (80-100)/100 × 100 = -20%
                      </p>
                      <p>
                        % change in price = (4-3)/3 × 100 = +33.33%
                      </p>
                      <p>PED = -20% / +33.33% = -0.6 (inelastic)</p>
                    </div>
                  </details>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <p className="font-semibold mb-2">Problem 2:</p>
                  <p className="text-sm mb-2">
                    A firm lowers its product price from $50 to $40. Quantity
                    demanded rises from 200 to 280 units. Calculate PED and
                    determine if demand is elastic or inelastic.
                  </p>
                  <details className="text-sm text-muted-foreground">
                    <summary className="cursor-pointer hover:text-foreground">
                      Show answer outline
                    </summary>
                    <div className="mt-2 pl-4">
                      <p>
                        % change in quantity = (280-200)/200 × 100 = +40%
                      </p>
                      <p>
                        % change in price = (40-50)/50 × 100 = -20%
                      </p>
                      <p>PED = +40% / -20% = -2 (elastic, |PED| &gt; 1)</p>
                    </div>
                  </details>
                </div>
              </div>
            </ExplanationSection>

            <ExplanationSection
              title="Related Concepts"
              defaultExpanded={false}
              icon={<LinkIcon className="h-5 w-5" />}
            >
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-mono text-sm">9708.3.1.2</span>
                  <span className="text-sm">
                    Income Elasticity of Demand (YED) - Responsiveness to income
                    changes
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-mono text-sm">9708.3.1.3</span>
                  <span className="text-sm">
                    Cross Elasticity of Demand (XED) - Responsiveness to changes
                    in related goods
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-mono text-sm">9708.3.2.1</span>
                  <span className="text-sm">
                    Price Elasticity of Supply (PES) - Responsiveness of quantity
                    supplied
                  </span>
                </li>
              </ul>
            </ExplanationSection>
          </div>
        </div>

        {/* Loading States (Skeleton Components) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Loading States (NEW - T015)
          </h2>

          <div className="space-y-6">
            {/* Full Skeleton */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Full Explanation Skeleton</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Shows while AI generates explanation (~5-10 seconds). Mimics complete explanation structure with 9 sections.
              </p>
              <div className="border rounded-lg p-6 bg-muted/20">
                <ExplanationSkeleton />
              </div>
            </div>

            {/* Compact Skeleton */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Compact Skeleton (Preview)</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Used in lists or cards when showing multiple explanations loading.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 bg-muted/20">
                  <ExplanationSkeletonCompact />
                </div>
                <div className="border rounded-lg p-4 bg-muted/20">
                  <ExplanationSkeletonCompact />
                </div>
              </div>
            </div>

            {/* Side-by-Side Comparison */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Before/After Comparison</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Left: Loading skeleton | Right: Actual content (from above)
              </p>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="border rounded-lg p-4 bg-muted/20">
                  <p className="text-sm font-medium mb-3 text-muted-foreground">Loading State...</p>
                  <ExplanationSkeleton />
                </div>
                <div className="border rounded-lg p-4">
                  <p className="text-sm font-medium mb-3 text-primary">Loaded Content</p>
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold">Price Elasticity of Demand</h3>
                      <p className="text-sm text-muted-foreground">9708.3.1.2</p>
                    </div>
                    <ExplanationSectionAlwaysExpanded
                      title="Definition"
                      icon={<BookOpenIcon className="h-5 w-5" />}
                    >
                      <p>
                        <strong>Price Elasticity of Demand (PED)</strong> measures the
                        responsiveness of quantity demanded to a change in price.
                      </p>
                    </ExplanationSectionAlwaysExpanded>
                    <ExplanationSection title="Key Terms" defaultExpanded={false}>
                      <p>Elastic demand, Inelastic demand, Unit elastic...</p>
                    </ExplanationSection>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Complete Explanation View (All 9 Components) */}
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Complete Explanation View (NEW - T016)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Full implementation of Agent 06's 9-component PhD-level explanation framework.
            This is what students see when requesting an explanation for a syllabus topic.
          </p>

          <div className="border rounded-lg p-6 bg-background">
            <ExplanationView
              explanation={mockExplanation}
              isBookmarked={explanationBookmarked}
              onBookmarkToggle={setExplanationBookmarked}
            />
          </div>

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h4 className="font-semibold text-sm mb-2 text-blue-900 dark:text-blue-100">
              📘 9-Component Framework (Agent 06)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-blue-800 dark:text-blue-200">
              <div>
                <p className="font-medium">Always Expanded (Critical):</p>
                <ul className="list-disc list-inside pl-2">
                  <li>1. Definition</li>
                  <li>3. Core Principles</li>
                  <li>9. Related Concepts</li>
                </ul>
              </div>
              <div>
                <p className="font-medium">Collapsible (Supplementary):</p>
                <ul className="list-disc list-inside pl-2">
                  <li>2. Key Terms</li>
                  <li>4. Real-World Examples</li>
                  <li>5. Visual Aids</li>
                  <li>6. Worked Examples</li>
                  <li>7. Common Misconceptions</li>
                  <li>8. Practice Problems</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* End-to-End Testing (NEW - T017/T019) */}
        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            End-to-End Testing (NEW - T017/T019)
          </h2>

          <p className="text-sm text-muted-foreground mb-6">
            Test the complete explanation display flow: route → API → loading → display.
            This simulates what students will experience when selecting a topic.
          </p>

          <div className="space-y-4">
            {/* Test Links */}
            <div className="border rounded-lg p-6 bg-background">
              <h3 className="font-semibold mb-4">Test Dynamic Route</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Click the links below to test the /teaching/[topicId] dynamic route.
                These simulate topic selection from the topic browser (which will be built in User Story 2).
              </p>

              <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded">
                <p className="text-xs text-amber-900 dark:text-amber-100">
                  <strong>Expected Behavior:</strong> Since the topic IDs below are placeholders (not real UUIDs from the database),
                  clicking these links will likely show the error boundary. This is the correct behavior - it demonstrates
                  error handling works. To test successful explanation loading, you'll need to:
                </p>
                <ol className="text-xs text-amber-800 dark:text-amber-200 mt-2 ml-4 space-y-1 list-decimal">
                  <li>Start the backend server</li>
                  <li>Query the database for a real syllabus topic UUID</li>
                  <li>Replace the topic IDs below with real UUIDs</li>
                  <li>OR wait for User Story 2 (Topic Browser) which will provide clickable real topics</li>
                </ol>
              </div>

              <div className="space-y-3">
                <Link
                  href="/teaching/test-ped-topic-id"
                  className="block p-4 border border-primary/30 rounded-lg hover:bg-primary/5 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">Test Topic: Price Elasticity of Demand</p>
                      <p className="text-sm text-muted-foreground">
                        Route: /teaching/test-ped-topic-id
                      </p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-primary" />
                  </div>
                </Link>

                <Link
                  href="/teaching/test-invalid-topic"
                  className="block p-4 border border-destructive/30 rounded-lg hover:bg-destructive/5 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-destructive">Test Error: Invalid Topic ID</p>
                      <p className="text-sm text-muted-foreground">
                        Route: /teaching/test-invalid-topic (should trigger error boundary)
                      </p>
                    </div>
                    <AlertCircle className="h-5 w-5 text-destructive" />
                  </div>
                </Link>
              </div>
            </div>

            {/* T019 Checklist */}
            <div className="border rounded-lg p-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
              <h3 className="font-semibold mb-4 text-blue-900 dark:text-blue-100">
                📋 T019 End-to-End Test Checklist
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-200 mb-4">
                Complete this checklist to validate User Story 1 is fully functional.
              </p>

              <ul className="space-y-2 text-sm text-blue-900 dark:text-blue-100">
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-1" />
                  <label htmlFor="test-1">
                    <strong>Route Navigation:</strong> Click "Test Topic: Price Elasticity of Demand" link above - should navigate to /teaching/test-ped-topic-id
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-2" />
                  <label htmlFor="test-2">
                    <strong>Loading State:</strong> Verify ExplanationSkeleton displays while explanation is being fetched (should show pulsing placeholders)
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-3" />
                  <label htmlFor="test-3">
                    <strong>API Response Time:</strong> Explanation should load within 10 seconds (per T019 requirement) - check browser DevTools Network tab
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-4" />
                  <label htmlFor="test-4">
                    <strong>9 Components Present:</strong> Verify all 9 sections display: Definition, Key Terms, Core Principles, Examples, Visual Aids, Worked Examples, Misconceptions, Practice, Related
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-5" />
                  <label htmlFor="test-5">
                    <strong>Collapsible Sections:</strong> Click each collapsible section header (6 sections) - should smoothly expand/collapse with animation
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-6" />
                  <label htmlFor="test-6">
                    <strong>Typography:</strong> Verify text is clear and readable - headings should be larger/bolder than body text, code/math should use monospace font
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-7" />
                  <label htmlFor="test-7">
                    <strong>Bookmark Functionality:</strong> Click bookmark button - should toggle saved/unsaved state with optimistic update
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-8" />
                  <label htmlFor="test-8">
                    <strong>Navigation:</strong> Click "Back to Topics" button - should navigate to /teaching (may show 404 until User Story 2 is complete)
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-9" />
                  <label htmlFor="test-9">
                    <strong>Error Boundary:</strong> Click "Test Error: Invalid Topic ID" link - should display error boundary with retry option
                  </label>
                </li>
                <li className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1" id="test-10" />
                  <label htmlFor="test-10">
                    <strong>Mobile Responsive:</strong> Resize browser to 375px width - explanation should remain readable and functional on mobile
                  </label>
                </li>
              </ul>

              <div className="mt-4 p-3 bg-white dark:bg-blue-900 rounded border border-blue-300 dark:border-blue-700">
                <p className="text-xs text-blue-800 dark:text-blue-200">
                  <strong>Note:</strong> The topic browser (/teaching page) will be built in User Story 2 (T020-T025).
                  For now, test the dynamic route directly using the links above. Once User Story 2 is complete,
                  you'll be able to select topics from the browser UI instead of using direct links.
                </p>
              </div>
            </div>

            {/* Manual Testing Instructions */}
            <div className="border rounded-lg p-6 bg-background">
              <h3 className="font-semibold mb-4">Manual Testing Instructions</h3>

              {/* Prerequisites Warning */}
              <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded">
                <p className="text-sm font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                  ⚠️ Prerequisites for End-to-End Testing
                </p>
                <ul className="text-xs text-yellow-800 dark:text-yellow-200 space-y-1 list-disc list-inside">
                  <li><strong>Backend Server:</strong> Must be running on <code className="px-1 py-0.5 bg-yellow-100 dark:bg-yellow-900 rounded">http://localhost:8000</code></li>
                  <li><strong>Database:</strong> Must have Economics 9708 syllabus topics seeded</li>
                  <li><strong>Valid Topic IDs:</strong> Test links below use placeholder IDs - replace with real UUIDs from database</li>
                  <li><strong>API Endpoint:</strong> <code className="px-1 py-0.5 bg-yellow-100 dark:bg-yellow-900 rounded">POST /api/teaching/explain-concept</code> must be implemented</li>
                </ul>
                <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-2">
                  <strong>Note:</strong> If backend is not running, clicking test links will trigger the error boundary with "Expected JSON response from API" or "Empty response from API" error.
                </p>
              </div>

              <ol className="space-y-3 text-sm">
                <li>
                  <strong>1. Start Backend Server:</strong>
                  <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono">cd backend && uv run uvicorn src.main:app --reload</pre>
                </li>
                <li>
                  <strong>2. Start Frontend Development Server:</strong>
                  <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono">cd frontend && npm run dev</pre>
                </li>
                <li>
                  <strong>3. Open Test Page:</strong>
                  <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono">http://localhost:3000/teaching/test</pre>
                </li>
                <li>
                  <strong>3. Scroll to "End-to-End Testing" section (this section)</strong>
                </li>
                <li>
                  <strong>4. Click "Test Topic: Price Elasticity of Demand" link</strong>
                </li>
                <li>
                  <strong>5. Observe Loading Sequence:</strong>
                  <ul className="mt-1 ml-6 space-y-1 text-xs text-muted-foreground list-disc">
                    <li>ExplanationSkeleton appears with pulsing animation</li>
                    <li>API request sent to backend (check DevTools Network tab)</li>
                    <li>After response: Skeleton replaced with ExplanationView</li>
                  </ul>
                </li>
                <li>
                  <strong>6. Validate Display:</strong>
                  <ul className="mt-1 ml-6 space-y-1 text-xs text-muted-foreground list-disc">
                    <li>Scroll through entire explanation - verify all 9 sections present</li>
                    <li>Click collapsible headers - verify smooth expand/collapse</li>
                    <li>Click bookmark button - verify state toggle</li>
                    <li>Check typography - headings clear, code monospace, spacing consistent</li>
                  </ul>
                </li>
                <li>
                  <strong>7. Test Error Handling:</strong>
                  <ul className="mt-1 ml-6 space-y-1 text-xs text-muted-foreground list-disc">
                    <li>Click "Test Error: Invalid Topic ID" link</li>
                    <li>Verify error boundary displays with user-friendly message</li>
                    <li>Click "Try Again" - should retry API request</li>
                    <li>Click "Browse Topics" - should navigate to /teaching</li>
                  </ul>
                </li>
                <li>
                  <strong>8. Test Mobile:</strong>
                  <ul className="mt-1 ml-6 space-y-1 text-xs text-muted-foreground list-disc">
                    <li>Open DevTools (F12) → Toggle device toolbar (Ctrl+Shift+M)</li>
                    <li>Resize to 375px width (iPhone SE)</li>
                    <li>Verify explanation is readable and buttons are tappable</li>
                    <li>Scroll through all sections - no horizontal overflow</li>
                  </ul>
                </li>
              </ol>
            </div>
          </div>
        </div>

        {/* Test Instructions */}
        <div className="mt-12 p-6 bg-primary/5 border-l-4 border-primary rounded">
          <h3 className="font-semibold mb-2">Component Testing Checklist:</h3>

          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2 text-primary">ExplanationView (NEW - T016)</h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Verify all 9 sections display correctly (scroll through entire explanation)</li>
              <li>✅ Check 3 always-expanded sections (Definition, Core Principles, Related Concepts)</li>
              <li>✅ Click each collapsible section to expand/collapse (6 sections)</li>
              <li>✅ Verify bookmark button works (click to toggle bookmarked state)</li>
              <li>✅ Check Key Terms section displays term + definition pairs</li>
              <li>✅ Verify Real-World Examples show scenario + analysis</li>
              <li>✅ Check Visual Aids display type badge + description</li>
              <li>✅ Verify Worked Examples show step-by-step solution in monospace font</li>
              <li>✅ Check Common Misconceptions use ❌/💡/✅ icons correctly</li>
              <li>✅ Verify Practice Problems show difficulty badge (easy/medium/hard colors)</li>
              <li>✅ Click "Show answer outline" in practice problems - should expand</li>
              <li>✅ Verify Related Concepts display as clickable tags</li>
              <li>✅ Check footer shows "Generated by anthropic AI"</li>
              <li>✅ Test typography hierarchy (headings, body text, spacing)</li>
              <li>✅ Test on mobile (resize to 375px width) - should be responsive</li>
              <li>✅ Verify whitespace-pre-wrap preserves formatting in multiline text</li>
            </ul>
          </div>

          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2 text-primary">ExplanationSkeleton (T015)</h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Verify pulse animation is smooth and continuous</li>
              <li>✅ Confirm skeleton structure matches explanation layout (9 sections)</li>
              <li>✅ Check 3 expanded sections have multiple skeleton lines (Definition, Core Principles, Related)</li>
              <li>✅ Verify 6 collapsed sections show only header skeleton (single line)</li>
              <li>✅ Test compact skeleton shows minimal structure (title + 1 section)</li>
              <li>✅ Compare skeleton with actual content - visual alignment should match</li>
              <li>✅ Verify fade-in animation on mount (500ms duration)</li>
              <li>✅ Test on mobile - skeleton should be responsive</li>
            </ul>
          </div>

          <div className="mb-4">
            <h4 className="font-semibold text-sm mb-2 text-primary">BookmarkButton (T014)</h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Click interactive bookmark button (top section) - observe 1.5s loading state</li>
              <li>✅ Verify button changes from "Save Explanation" → "Saving..." → "Saved"</li>
              <li>✅ Verify icon changes: empty star → spinner → filled star</li>
              <li>✅ Verify color changes: outline → primary background</li>
              <li>✅ Click icon-only button - should toggle bookmarked/unbookmarked</li>
              <li>✅ Click "With Count" button - count should increment/decrement</li>
              <li>✅ Tab through all buttons - focus indicator should be visible</li>
              <li>✅ Use Enter/Space on focused button - should activate</li>
              <li>✅ Verify loading buttons are disabled (not clickable)</li>
              <li>✅ Verify disabled button is greyed out</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-2 text-primary">ExplanationSection (T013)</h4>
            <ul className="space-y-1 text-sm">
              <li>✅ Click section headers to expand/collapse</li>
              <li>✅ Use Tab key to navigate between sections</li>
              <li>✅ Use Enter or Space to toggle collapsible sections</li>
              <li>✅ Verify smooth expand/collapse animations</li>
              <li>✅ Check visual hierarchy (headings, spacing, colors)</li>
              <li>✅ Verify icons display correctly</li>
              <li>✅ Test on mobile (resize browser to 375px width)</li>
              <li>
                ✅ Screen reader: Should announce "collapsed" vs "expanded" state
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
