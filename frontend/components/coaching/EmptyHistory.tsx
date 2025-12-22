/**
 * EmptyHistory Component
 *
 * Display empty state when student has no coaching sessions yet.
 *
 * Features:
 * - Friendly message encouraging first session
 * - "Start Your First Session" button
 * - Illustration/icon
 * - Accessible
 */

'use client';

import { MessageCircleQuestion } from 'lucide-react';
import Link from 'next/link';

export function EmptyHistory() {
  return (
    <div
      className="flex items-center justify-center h-96"
      data-testid="empty-history"
      role="status"
      aria-label="No coaching sessions yet"
    >
      <div className="text-center space-y-6 max-w-md">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="p-6 bg-blue-50 rounded-full">
            <MessageCircleQuestion className="w-16 h-16 text-blue-600" aria-hidden="true" />
          </div>
        </div>

        {/* Message */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-gray-900">No Coaching Sessions Yet</h2>
          <p className="text-gray-600 leading-relaxed">
            Start your first coaching session to get personalized help with Economics concepts.
            Our AI coach uses Socratic questioning to help you understand difficult topics.
          </p>
        </div>

        {/* Call to Action */}
        <Link
          href="/coaching"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md hover:shadow-lg"
        >
          <MessageCircleQuestion className="w-5 h-5" aria-hidden="true" />
          Start Your First Session
        </Link>

        {/* Helper Text */}
        <p className="text-sm text-gray-500">
          Sessions are saved automatically so you can review them anytime.
        </p>
      </div>
    </div>
  );
}
