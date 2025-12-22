'use client';

import { useState, useEffect, useRef } from 'react';
import {
  getSyllabusPoints,
  explainConcept,
  SyllabusPoint,
  TopicExplanation,
  APIError,
} from '@/lib/api';
import mermaid from 'mermaid';

// Mermaid Diagram Component
function MermaidDiagram({ code, id }: { code: string; id: string }) {
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    async function renderDiagram() {
      try {
        const { svg } = await mermaid.render(id, code);
        setSvg(svg);
      } catch (err) {
        console.error('Mermaid render error:', err);
        setError('Failed to render diagram');
      }
    }

    if (code) {
      renderDiagram();
    }
  }, [code, id]);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div className="mermaid-container bg-white p-4 rounded border overflow-x-auto">
      <div dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  );
}

// Cache interface for explanations
interface CachedExplanation {
  explanation: TopicExplanation;
  timestamp: number;
  versions: Array<{
    explanation: TopicExplanation;
    requestType: string;
    timestamp: number;
  }>;
}

export default function TeachPage() {
  const [syllabusPoints, setSyllabusPoints] = useState<SyllabusPoint[]>([]);
  const [loadingSyllabus, setLoadingSyllabus] = useState(true);
  const [selectedConceptId, setSelectedConceptId] = useState('');
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<TopicExplanation | null>(null);
  const [error, setError] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [showExplainMenu, setShowExplainMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const [currentVersion, setCurrentVersion] = useState(0);
  const [explanationVersions, setExplanationVersions] = useState<CachedExplanation['versions']>([]);
  const [usingCache, setUsingCache] = useState(false);

  // Demo student ID - will be replaced with auth later
  const DEMO_STUDENT_ID = process.env.NEXT_PUBLIC_DEMO_STUDENT_ID || '550e8400-e29b-41d4-a716-446655440000';

  // Clear syllabus cache (call this when syllabus is updated)
  const clearSyllabusCache = () => {
    localStorage.removeItem('syllabus_points_9708');
    localStorage.removeItem('syllabus_points_9708_timestamp');
    localStorage.removeItem('syllabus_version');
    console.log('🗑️ Syllabus cache cleared');
  };

  // Load cached explanation from localStorage
  const loadCachedExplanation = (conceptId: string): CachedExplanation | null => {
    try {
      const cached = localStorage.getItem(`explanation_${conceptId}`);
      return cached ? JSON.parse(cached) : null;
    } catch (err) {
      console.error('Failed to load cached explanation:', err);
      return null;
    }
  };

  // Save explanation to cache
  const saveToCached = (conceptId: string, exp: TopicExplanation, requestType: string = 'default') => {
    try {
      const existing = loadCachedExplanation(conceptId);
      const newVersion = {
        explanation: exp,
        requestType,
        timestamp: Date.now(),
      };

      const cached: CachedExplanation = existing
        ? {
            ...existing,
            explanation: requestType === 'default' ? exp : existing.explanation,
            timestamp: Date.now(),
            versions: [...existing.versions, newVersion],
          }
        : {
            explanation: exp,
            timestamp: Date.now(),
            versions: [newVersion],
          };

      localStorage.setItem(`explanation_${conceptId}`, JSON.stringify(cached));
      setExplanationVersions(cached.versions);
    } catch (err) {
      console.error('Failed to save to cache:', err);
    }
  };

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);

  // Organize syllabus points into hierarchical structure
  const organizeHierarchy = (points: SyllabusPoint[]) => {
    const hierarchy: Record<string, SyllabusPoint[]> = {};

    points.forEach(point => {
      // Extract main section (e.g., "9708.1" from "9708.1.1")
      const parts = point.code.split('.');
      const mainSection = `${parts[0]}.${parts[1]}`;

      if (!hierarchy[mainSection]) {
        hierarchy[mainSection] = [];
      }
      hierarchy[mainSection].push(point);
    });

    return hierarchy;
  };

  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  // Fetch syllabus points on component mount with localStorage cache
  useEffect(() => {
    async function fetchSyllabusPoints() {
      const CACHE_KEY = 'syllabus_points_9708';
      const CACHE_VERSION_KEY = 'syllabus_version';
      const CACHE_DURATION_MS = 1000 * 60 * 60 * 24; // 24 hours

      try {
        // Try to load from localStorage first (instant load)
        const cached = localStorage.getItem(CACHE_KEY);
        const cachedVersion = localStorage.getItem(CACHE_VERSION_KEY);
        const cacheTimestamp = localStorage.getItem(`${CACHE_KEY}_timestamp`);

        if (cached && cacheTimestamp) {
          const points = JSON.parse(cached);
          const age = Date.now() - parseInt(cacheTimestamp);

          // Instantly show cached data
          console.log('📦 Loaded syllabus from cache (instant load)');
          setSyllabusPoints(points);
          setLoadingSyllabus(false);
          setUsingCache(true);

          // If cache is fresh (<24h), we're done
          if (age < CACHE_DURATION_MS) {
            console.log('✅ Cache is fresh, skipping API call');
            return;
          }

          console.log('⏰ Cache is stale, syncing in background...');
        } else {
          // No cache, show loading state
          setLoadingSyllabus(true);
          setUsingCache(false);
          console.log('🔄 No cache found, fetching from API...');
        }

        // Fetch from API (either no cache, or background sync)
        const points = await getSyllabusPoints('9708');

        // Update state
        setSyllabusPoints(points);

        // Save to cache with timestamp and version
        localStorage.setItem(CACHE_KEY, JSON.stringify(points));
        localStorage.setItem(`${CACHE_KEY}_timestamp`, Date.now().toString());
        localStorage.setItem(CACHE_VERSION_KEY, '1'); // Increment when syllabus changes

        console.log('💾 Syllabus cached to localStorage');
      } catch (err) {
        console.error('Failed to fetch syllabus points:', err);
        // If we have cache, keep showing it even if API fails
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached && !syllabusPoints.length) {
          const points = JSON.parse(cached);
          setSyllabusPoints(points);
          console.log('⚠️ API failed, using stale cache');
        } else if (!syllabusPoints.length) {
          setError('Failed to load concepts. Please refresh the page.');
        }
      } finally {
        setLoadingSyllabus(false);
      }
    }

    fetchSyllabusPoints();
  }, []);

  const handleTeachMe = async (conceptId?: string, forceRegenerate: boolean = false, context?: string) => {
    const idToUse = conceptId || selectedConceptId;

    if (!idToUse) {
      setError('Please select a concept first');
      return;
    }

    // Check cache first (unless forcing regeneration)
    if (!forceRegenerate && !context) {
      const cached = loadCachedExplanation(idToUse);
      if (cached) {
        console.log('📦 Loading from cache');
        setExplanation(cached.explanation);
        setExplanationVersions(cached.versions);
        setCurrentVersion(0);
        setError('');
        return;
      }
    }

    setLoading(true);
    setError('');
    setExplanation(null);

    try {
      const requestType = context || 'default';

      const explanation = await explainConcept({
        syllabus_point_id: idToUse,
        student_id: DEMO_STUDENT_ID,
        include_diagrams: true,
        include_practice: true,
        context,
      });

      setExplanation(explanation);
      saveToCached(idToUse, explanation, requestType);
      setCurrentVersion(explanationVersions.length);

      // Scroll to top after loading explanation
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err instanceof APIError) {
        setError(`Failed to get explanation: ${err.detail || err.message}`);
      } else {
        setError('Failed to get explanation. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRelatedConceptClick = (conceptCode: string) => {
    // Find the syllabus point by code
    const relatedPoint = syllabusPoints.find(point => point.code === conceptCode);
    if (relatedPoint) {
      setSelectedConceptId(relatedPoint.id);
      handleTeachMe(relatedPoint.id);
    }
  };

  // Handle text selection
  const handleTextSelection = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 10) {
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();

      if (rect) {
        setSelectedText(text);
        setMenuPosition({ x: rect.left, y: rect.bottom + window.scrollY });
        setShowExplainMenu(true);
      }
    } else {
      setShowExplainMenu(false);
    }
  };

  // Generate alternative explanation
  const explainDifferently = async (type: string) => {
    setShowExplainMenu(false);

    const contextMap: Record<string, string> = {
      simpler: `Please explain the following in simpler terms, suitable for someone with less background knowledge: "${selectedText}"`,
      detailed: `Please provide a more detailed explanation of the following, with additional examples and depth: "${selectedText}"`,
      examples: `Please explain the following using more real-world examples and practical applications: "${selectedText}"`,
      different: `Please explain the following from a different perspective or using a different approach: "${selectedText}"`,
      full_simpler: 'Please re-explain this entire concept in simpler, more accessible language suitable for beginners.',
      full_detailed: 'Please provide a more comprehensive and detailed explanation of this concept with additional depth.',
      full_examples: 'Please re-explain this concept with many more real-world examples and practical applications.',
    };

    await handleTeachMe(selectedConceptId, true, contextMap[type]);
    setSelectedText('');
  };

  // Switch between explanation versions
  const switchVersion = (index: number) => {
    if (explanationVersions[index]) {
      setExplanation(explanationVersions[index].explanation);
      setCurrentVersion(index);
    }
  };

  const hierarchy = organizeHierarchy(syllabusPoints);
  const sectionNames: Record<string, string> = {
    '9708.1': 'Basic Economic Ideas',
    '9708.2': 'Price System and Microeconomics',
    '9708.3': 'Government Intervention',
    '9708.4': 'International Trade',
    '9708.5': 'Macroeconomic Problems',
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Sidebar - Syllabus Navigation */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">📚 Economics 9708</h2>
          <p className="text-sm text-gray-600 mt-1">Select a topic to learn</p>
          {usingCache && (
            <p className="text-xs text-green-600 mt-2 flex items-center gap-1">
              <span>⚡</span>
              <span>Loaded from cache (instant)</span>
            </p>
          )}
        </div>

        {loadingSyllabus ? (
          <div className="p-6 text-center text-gray-500">
            Loading syllabus...
          </div>
        ) : (
          <div className="p-4">
            {Object.entries(hierarchy).map(([section, points]) => (
              <div key={section} className="mb-2">
                <button
                  onClick={() => toggleSection(section)}
                  className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition flex items-center justify-between"
                >
                  <span className="font-semibold text-gray-700">
                    {section} {sectionNames[section] || ''}
                  </span>
                  <span className="text-gray-500">
                    {expandedSections.has(section) ? '▼' : '▶'}
                  </span>
                </button>

                {expandedSections.has(section) && (
                  <div className="ml-4 mt-1 space-y-1">
                    {points.map((point) => (
                      <button
                        key={point.id}
                        onClick={() => {
                          setSelectedConceptId(point.id);
                          handleTeachMe(point.id);
                        }}
                        className={`w-full text-left px-4 py-2 rounded transition ${
                          selectedConceptId === point.id
                            ? 'bg-blue-100 text-blue-900 border-l-4 border-blue-600'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        <div className="text-sm font-medium">{point.code}</div>
                        <div className="text-xs text-gray-600">{point.description}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="max-w-4xl mx-auto p-8">
          <h1 className="text-4xl font-bold mb-4">🎓 AI Teacher</h1>
          <p className="text-lg mb-8 text-gray-700">
            PhD-level explanations with examples and practice problems
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Generating explanation...</p>
            </div>
          )}

      {/* Explanation Display */}
      {explanation && (
        <div className="space-y-6" onMouseUp={handleTextSelection}>
          {/* Version Switcher & Regenerate */}
          <div className="bg-white rounded-lg shadow-md p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-700">Explanation Version:</span>
              <div className="flex gap-1">
                {explanationVersions.map((version, idx) => (
                  <button
                    key={idx}
                    onClick={() => switchVersion(idx)}
                    className={`px-3 py-1 rounded text-xs font-medium transition ${
                      currentVersion === idx
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                    title={`Version ${idx + 1}: ${version.requestType}`}
                  >
                    v{idx + 1}
                  </button>
                ))}
              </div>
              {explanationVersions.length > 1 && (
                <span className="text-xs text-gray-500 ml-2">
                  ({explanationVersions[currentVersion]?.requestType || 'default'})
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => explainDifferently('full_simpler')}
                className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition"
              >
                Simpler
              </button>
              <button
                onClick={() => explainDifferently('full_detailed')}
                className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition"
              >
                More Detail
              </button>
              <button
                onClick={() => explainDifferently('full_examples')}
                className="px-3 py-1 text-xs bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition"
              >
                More Examples
              </button>
              <button
                onClick={() => handleTeachMe(selectedConceptId, true)}
                className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
                title="Generate a fresh explanation"
              >
                🔄 Regenerate
              </button>
            </div>
          </div>

          {/* Definition */}
          <div className="bg-blue-50 border-l-4 border-blue-600 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-3 text-blue-900">
              {explanation.concept_name}
            </h2>
            <p className="text-lg text-gray-800">{explanation.definition}</p>
          </div>

          {/* Key Terms */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">📚 Key Terms</h3>
            <div className="space-y-3">
              {explanation.key_terms.map((term, idx) => (
                <div key={idx} className="border-l-2 border-gray-300 pl-4">
                  <strong className="text-blue-600">{term.term}:</strong>{' '}
                  <span className="text-gray-700">{term.definition}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Explanation */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">💡 Explanation</h3>
            <p className="text-gray-700 leading-relaxed">{explanation.explanation}</p>
          </div>

          {/* Examples */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">🌟 Real-World Examples</h3>
            <div className="space-y-4">
              {explanation.examples.map((example, idx) => (
                <div key={idx} className="border rounded-lg p-4 bg-gray-50">
                  <h4 className="font-semibold text-lg mb-2">{example.title}</h4>
                  <p className="text-gray-600 mb-2">
                    <strong>Scenario:</strong> {example.scenario}
                  </p>
                  <p className="text-gray-700">
                    <strong>Analysis:</strong> {example.analysis}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Visual Aids */}
          {explanation.visual_aids && explanation.visual_aids.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">📊 Visual Aids</h3>
              <div className="space-y-4">
                {explanation.visual_aids.map((aid, idx) => (
                  <div key={idx} className="border rounded-lg p-4 bg-yellow-50">
                    <h4 className="font-semibold text-lg mb-2">{aid.title}</h4>
                    <p className="text-gray-600 text-sm mb-3">{aid.description}</p>
                    {aid.ascii_art && (
                      <pre className="bg-gray-900 text-green-400 p-4 rounded overflow-x-auto text-xs font-mono">
                        {aid.ascii_art}
                      </pre>
                    )}
                    {aid.mermaid_code && (
                      <div className="mt-3">
                        <MermaidDiagram
                          code={aid.mermaid_code}
                          id={`mermaid-${idx}`}
                        />
                        <details className="mt-2">
                          <summary className="cursor-pointer text-sm text-gray-600 hover:text-blue-600">
                            Show diagram code
                          </summary>
                          <pre className="mt-2 bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                            {aid.mermaid_code}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Worked Examples */}
          {explanation.worked_examples && explanation.worked_examples.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">📝 Worked Examples</h3>
              <div className="space-y-4">
                {explanation.worked_examples.map((example, idx) => (
                  <div key={idx} className="border rounded-lg p-4 bg-blue-50">
                    <h4 className="font-semibold text-lg mb-2">Problem:</h4>
                    <p className="text-gray-700 mb-3">{example.problem}</p>
                    <h4 className="font-semibold text-lg mb-2">Solution:</h4>
                    <p className="text-gray-700 whitespace-pre-line mb-3">{example.step_by_step_solution}</p>
                    <div className="bg-white rounded p-2 text-sm">
                      <strong>Marks Breakdown:</strong> {example.marks_breakdown}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Common Misconceptions */}
          {explanation.common_misconceptions && explanation.common_misconceptions.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">⚠️ Common Misconceptions</h3>
              <div className="space-y-4">
                {explanation.common_misconceptions.map((misc, idx) => (
                  <div key={idx} className="border-l-4 border-orange-500 pl-4 py-2">
                    <p className="text-red-600 mb-2">
                      <strong>❌ Misconception:</strong> {misc.misconception}
                    </p>
                    <p className="text-gray-600 mb-2">
                      <strong>Why wrong:</strong> {misc.why_wrong}
                    </p>
                    <p className="text-green-600">
                      <strong>✅ Correct understanding:</strong> {misc.correct_understanding}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Practice Problems */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">✍️ Practice Problems</h3>
            <div className="space-y-4">
              {explanation.practice_problems.map((problem, idx) => (
                <div key={idx} className="border-l-4 border-green-500 pl-4 py-3">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-gray-700 flex-1">{problem.question}</span>
                    <div className="flex items-center gap-2 ml-4">
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-semibold">
                        {problem.marks} marks
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        problem.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                        problem.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {problem.difficulty.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <details className="mt-2">
                    <summary className="cursor-pointer text-blue-600 text-sm hover:underline">
                      Show answer outline
                    </summary>
                    <p className="mt-2 text-gray-600 text-sm bg-gray-50 p-3 rounded">
                      {problem.answer_outline}
                    </p>
                  </details>
                </div>
              ))}
            </div>
          </div>

          {/* Related Concepts */}
          {explanation.related_concepts && explanation.related_concepts.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">🔗 Related Concepts</h3>
              <p className="text-sm text-gray-600 mb-3">
                Click on a concept to learn more about it:
              </p>
              <div className="flex flex-wrap gap-2">
                {explanation.related_concepts.map((conceptCode, idx) => {
                  const relatedPoint = syllabusPoints.find(p => p.code === conceptCode);
                  return (
                    <button
                      key={idx}
                      onClick={() => handleRelatedConceptClick(conceptCode)}
                      disabled={!relatedPoint}
                      className={`px-3 py-1 rounded-full text-sm transition ${
                        relatedPoint
                          ? 'bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer'
                          : 'bg-gray-100 text-gray-500 cursor-not-allowed'
                      }`}
                      title={relatedPoint ? `Learn about: ${relatedPoint.description}` : 'Concept not found in database'}
                    >
                      {conceptCode}
                      {relatedPoint && <span className="ml-1">→</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* AI Attribution */}
          <div className="text-center text-sm text-gray-500 mt-8">
            Generated by {explanation.generated_by} • PhD-level Economics teaching
          </div>
        </div>
      )}

      {/* Floating "Explain This" Menu */}
      {showExplainMenu && (
        <>
          {/* Backdrop to close menu */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowExplainMenu(false)}
          />
          {/* Floating menu */}
          <div
            className="fixed z-50 bg-white rounded-lg shadow-2xl border-2 border-blue-500 p-2 min-w-[240px]"
            style={{
              left: `${menuPosition.x}px`,
              top: `${menuPosition.y + 10}px`,
            }}
          >
            <div className="text-xs font-semibold text-gray-700 px-3 py-2 border-b border-gray-200">
              💡 Explain This Differently
            </div>
            <div className="py-1">
              <button
                onClick={() => explainDifferently('simpler')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-green-50 transition flex items-center gap-2"
              >
                <span>🟢</span>
                <span>Simpler Language</span>
              </button>
              <button
                onClick={() => explainDifferently('detailed')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-purple-50 transition flex items-center gap-2"
              >
                <span>🔍</span>
                <span>More Detail</span>
              </button>
              <button
                onClick={() => explainDifferently('examples')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-orange-50 transition flex items-center gap-2"
              >
                <span>📚</span>
                <span>More Examples</span>
              </button>
              <button
                onClick={() => explainDifferently('different')}
                className="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition flex items-center gap-2"
              >
                <span>🔄</span>
                <span>Different Perspective</span>
              </button>
            </div>
            <div className="text-xs text-gray-500 px-3 py-2 border-t border-gray-200">
              Selected: &quot;{selectedText.slice(0, 50)}{selectedText.length > 50 ? '...' : ''}&quot;
            </div>
          </div>
        </>
      )}
        </div>
      </div>
    </div>
  );
}
