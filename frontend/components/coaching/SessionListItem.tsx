/**
 * SessionListItem Component
 *
 * Display a single coaching session in the history list.
 *
 * Features:
 * - Session topic, date, outcome badge
 * - Message count
 * - Click to view full transcript
 * - Keyboard navigable
 * - Accessible
 */

'use client';

import { Clock, MessageCircle, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface SessionListItemProps {
  id: string;
  topic: string;
  createdAt: string;
  outcome: 'resolved' | 'needs_more_help' | 'refer_to_teacher' | 'in_progress' | 'abandoned';
  messageCount?: number;
}

/**
 * Get outcome badge properties
 */
function getOutcomeBadgeProps(outcome: SessionListItemProps['outcome']) {
  switch (outcome) {
    case 'resolved':
      return {
        icon: CheckCircle,
        label: 'Resolved',
        className: 'bg-green-100 text-green-800 border-green-200',
      };
    case 'needs_more_help':
      return {
        icon: AlertCircle,
        label: 'Needs More Help',
        className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      };
    case 'refer_to_teacher':
      return {
        icon: ArrowRight,
        label: 'Refer to Teacher',
        className: 'bg-blue-100 text-blue-800 border-blue-200',
      };
    case 'in_progress':
      return {
        icon: MessageCircle,
        label: 'In Progress',
        className: 'bg-gray-100 text-gray-800 border-gray-200',
      };
    case 'abandoned':
      return {
        icon: AlertCircle,
        label: 'Abandoned',
        className: 'bg-gray-100 text-gray-500 border-gray-200',
      };
  }
}

/**
 * Format date as relative time (e.g., "2 hours ago", "3 days ago")
 */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffDays < 30) {
    return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  } else {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
}

export function SessionListItem({
  id,
  topic,
  createdAt,
  outcome,
  messageCount,
}: SessionListItemProps) {
  const badgeProps = getOutcomeBadgeProps(outcome);
  const BadgeIcon = badgeProps.icon;

  return (
    <Link
      href={`/coaching/${id}`}
      className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
      data-testid="session-list-item"
      role="listitem"
      aria-label={`Coaching session about ${topic}, ${badgeProps.label}`}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          window.location.href = `/coaching/${id}`;
        }
      }}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Left: Topic and metadata */}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate mb-1">
            {topic}
          </h3>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            {/* Date */}
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" aria-hidden="true" />
              <span>{formatRelativeTime(createdAt)}</span>
            </div>

            {/* Message count */}
            {messageCount !== undefined && (
              <div className="flex items-center gap-1">
                <MessageCircle className="w-4 h-4" aria-hidden="true" />
                <span>{messageCount} {messageCount === 1 ? 'message' : 'messages'}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Outcome badge */}
        <div
          className={`flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium flex-shrink-0 ${badgeProps.className}`}
          data-testid="outcome-badge"
        >
          <BadgeIcon className="w-4 h-4" aria-hidden="true" />
          <span>{badgeProps.label}</span>
        </div>
      </div>
    </Link>
  );
}
