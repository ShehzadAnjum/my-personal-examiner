/**
 * Enhanced Loading State for Explanation Generation
 *
 * Features:
 * - Cycling animated messages
 * - Blur overlay
 * - Progress indication
 * - Interactive feedback
 */

'use client';

import { useEffect, useState } from 'react';
import { Loader2, Brain, BookOpen, Lightbulb, Search } from 'lucide-react';

const LOADING_MESSAGES = [
  { text: "Researching the topic...", icon: Search },
  { text: "Analyzing syllabus context...", icon: BookOpen },
  { text: "Generating PhD-level explanation...", icon: Brain },
  { text: "Creating examples and diagrams...", icon: Lightbulb },
  { text: "Adding practice problems...", icon: BookOpen },
  { text: "Finalizing comprehensive content...", icon: Brain },
];

export interface ExplanationLoadingStateProps {
  /** Optional custom message */
  message?: string;
  /** Show with blur background overlay */
  withBlur?: boolean;
}

export function ExplanationLoadingState({
  message,
  withBlur = true,
}: ExplanationLoadingStateProps) {
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  // Cycle through messages every 2.5 seconds
  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2500);

    return () => clearInterval(messageInterval);
  }, []);

  // Simulate progress (0-90%, never reaches 100% until actually loaded)
  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return 90; // Cap at 90%
        return prev + Math.random() * 5;
      });
    }, 500);

    return () => clearInterval(progressInterval);
  }, []);

  const currentMessage = message || LOADING_MESSAGES[messageIndex].text;
  const Icon = LOADING_MESSAGES[messageIndex].icon;

  return (
    <div className={`relative ${withBlur ? 'min-h-[60vh]' : ''}`}>
      {/* Blur Overlay */}
      {withBlur && (
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm rounded-lg z-10" />
      )}

      {/* Loading Content */}
      <div className={`${withBlur ? 'absolute inset-0 z-20' : ''} flex items-center justify-center`}>
        <div className="max-w-md w-full space-y-6 p-8">
          {/* Animated Icon */}
          <div className="flex justify-center">
            <div className="relative">
              {/* Pulsing background circle */}
              <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping" />

              {/* Icon */}
              <div className="relative bg-primary/10 rounded-full p-6 border-2 border-primary/30">
                <Icon className="h-12 w-12 text-primary animate-pulse" />
              </div>
            </div>
          </div>

          {/* Message with fade animation */}
          <div className="text-center space-y-3">
            <h3
              key={messageIndex}
              className="text-xl font-semibold text-primary animate-in fade-in-50 slide-in-from-bottom-3 duration-500"
            >
              {currentMessage}
            </h3>

            {/* Progress Bar */}
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Spinning loader */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>This may take 10-15 seconds...</span>
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-3 gap-3 text-center text-xs">
            <div className="bg-muted/50 rounded-lg p-3 space-y-1">
              <div className="font-semibold text-primary">9</div>
              <div className="text-muted-foreground">Components</div>
            </div>
            <div className="bg-muted/50 rounded-lg p-3 space-y-1">
              <div className="font-semibold text-primary">PhD</div>
              <div className="text-muted-foreground">Level</div>
            </div>
            <div className="bg-muted/50 rounded-lg p-3 space-y-1">
              <div className="font-semibold text-primary">A*</div>
              <div className="text-muted-foreground">Standard</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Inline loading state without blur (for regeneration)
 */
export function ExplanationLoadingInline() {
  return (
    <div className="flex items-center justify-center gap-3 p-8 bg-primary/5 border border-primary/20 rounded-lg">
      <Loader2 className="h-5 w-5 animate-spin text-primary" />
      <span className="text-sm font-medium text-primary">
        Generating alternative explanation...
      </span>
    </div>
  );
}
