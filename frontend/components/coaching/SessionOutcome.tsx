/**
 * SessionOutcome Component
 *
 * Displays session conclusion with outcome status, summary, and next actions.
 *
 * Features:
 * - Outcome status badge (resolved/needs_more_help/refer_to_teacher)
 * - Session summary
 * - Next action cards with links
 * - "Start New Session" button
 * - Confidence score display (if available)
 * - Accessible (ARIA roles, keyboard navigation)
 */

'use client';

import { CheckCircle, AlertCircle, ArrowRight, RefreshCw } from 'lucide-react';

interface SessionOutcomeProps {
  /** Session outcome status */
  outcome: 'resolved' | 'needs_more_help' | 'refer_to_teacher';
  /** Summary of what was learned/accomplished */
  summary?: string;
  /** Next action recommendations */
  nextActions?: Array<{
    type: 'practice' | 'review_topic' | 'teacher_help' | 'new_session';
    label: string;
    description: string;
    link?: string;
    priority: number;
  }>;
  /** Confidence score (0-100) */
  confidence?: number;
  /** Callback when "Start New Session" is clicked */
  onStartNewSession: () => void;
}

/**
 * Get outcome display properties based on status
 */
function getOutcomeProps(outcome: SessionOutcomeProps['outcome']) {
  switch (outcome) {
    case 'resolved':
      return {
        icon: CheckCircle,
        label: 'Resolved',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        description: 'Great! You now understand this concept.',
      };
    case 'needs_more_help':
      return {
        icon: AlertCircle,
        label: 'Needs More Help',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        description: "You're making progress, but need more practice.",
      };
    case 'refer_to_teacher':
      return {
        icon: ArrowRight,
        label: 'Refer to Teacher',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        description: 'This topic needs in-depth explanation from the Teacher Agent.',
      };
  }
}

export function SessionOutcome({
  outcome,
  summary,
  nextActions = [],
  confidence,
  onStartNewSession,
}: SessionOutcomeProps) {
  const outcomeProps = getOutcomeProps(outcome);
  const Icon = outcomeProps.icon;

  // Sort next actions by priority
  const sortedActions = [...nextActions].sort((a, b) => b.priority - a.priority);

  return (
    <div
      className="session-outcome mt-6 p-6 rounded-lg border-2 border-gray-200 bg-white"
      data-testid="session-outcome"
      role="region"
      aria-label="Session outcome and next steps"
    >
      {/* Outcome Status Banner */}
      <div
        className={`flex items-center gap-3 p-4 rounded-lg ${outcomeProps.bgColor} ${outcomeProps.borderColor} border mb-4`}
        data-testid="outcome-banner"
      >
        <Icon className={`w-6 h-6 ${outcomeProps.color} flex-shrink-0`} aria-hidden="true" />
        <div className="flex-1">
          <h3
            className={`text-lg font-semibold ${outcomeProps.color}`}
            data-testid="outcome-status"
          >
            {outcomeProps.label}
          </h3>
          <p className="text-sm text-gray-700 mt-1">{outcomeProps.description}</p>
        </div>

        {/* Confidence Score */}
        {confidence !== undefined && confidence > 0 && (
          <div
            className="text-right"
            data-testid="outcome-confidence"
            aria-label={`Confidence: ${confidence}%`}
          >
            <div className="text-2xl font-bold text-gray-700">{confidence}%</div>
            <div className="text-xs text-gray-500">confidence</div>
          </div>
        )}
      </div>

      {/* Session Summary */}
      {summary && (
        <div className="mb-6" data-testid="outcome-summary">
          <h4 className="text-md font-semibold text-gray-800 mb-2">Session Summary</h4>
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Next Actions */}
      {sortedActions.length > 0 && (
        <div className="mb-6" data-testid="next-actions">
          <h4 className="text-md font-semibold text-gray-800 mb-3">Recommended Next Steps</h4>
          <div className="space-y-3">
            {sortedActions.map((action, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                data-testid="next-action-card"
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{action.label}</div>
                  <div className="text-sm text-gray-600 mt-1">{action.description}</div>
                </div>

                {action.link && (
                  <a
                    href={action.link}
                    className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    aria-label={`Go to ${action.label}`}
                  >
                    Go
                    <ArrowRight className="w-4 h-4 inline ml-1" aria-hidden="true" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Start New Session Button */}
      <div className="flex items-center justify-center pt-4 border-t border-gray-200">
        <button
          onClick={onStartNewSession}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md hover:shadow-lg font-medium"
          aria-label="Start a new coaching session"
        >
          <RefreshCw className="w-5 h-5" aria-hidden="true" />
          Start New Session
        </button>
      </div>

      {/* Session End Message */}
      <div className="mt-4 text-center text-sm text-gray-500">
        This session has ended. Start a new session to continue learning.
      </div>
    </div>
  );
}
