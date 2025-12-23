/**
 * VirtualizedMessageList Component
 *
 * Optimized message list using @tanstack/react-virtual for 50+ message conversations.
 * Only renders visible messages in the viewport for better performance.
 *
 * Features:
 * - Virtual scrolling with @tanstack/react-virtual
 * - Auto-scroll to latest message
 * - Maintains ChatScope UI styling
 * - Optimized for large conversations (50+ messages)
 */

'use client';

import { useRef, useEffect } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Message, Avatar, TypingIndicator } from '@chatscope/chat-ui-kit-react';
import type { Message as MessageType } from '@/types/coaching';

interface VirtualizedMessageListProps {
  messages: MessageType[];
  isCoachTyping?: boolean;
  autoScrollToBottom?: boolean;
}

export function VirtualizedMessageList({
  messages,
  isCoachTyping = false,
  autoScrollToBottom = true,
}: VirtualizedMessageListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  // Virtualizer for efficient rendering
  const virtualizer = useVirtualizer({
    count: messages.length + (isCoachTyping ? 1 : 0), // +1 for typing indicator
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Estimated message height in pixels
    overscan: 5, // Render 5 extra items above/below viewport
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScrollToBottom && messages.length > 0) {
      // Scroll to last message after a brief delay for rendering
      setTimeout(() => {
        virtualizer.scrollToIndex(messages.length - 1, {
          align: 'end',
          behavior: 'smooth',
        });
      }, 100);
    }
  }, [messages.length, autoScrollToBottom, virtualizer]);

  const items = virtualizer.getVirtualItems();

  return (
    <div
      ref={parentRef}
      className="flex-1 overflow-y-auto"
      style={{
        height: '100%',
        overflowY: 'auto',
      }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {items.map((virtualItem) => {
          const isTypingIndicator = virtualItem.index === messages.length;

          if (isTypingIndicator && isCoachTyping) {
            return (
              <div
                key="typing-indicator"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                <TypingIndicator
                  content="AI Coach is thinking..."
                  style={{ marginLeft: '1rem' }}
                />
              </div>
            );
          }

          const message = messages[virtualItem.index];
          if (!message) return null;

          const isCoach = message.role === 'coach';
          const timestamp = new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
          });

          return (
            <div
              key={message.id || virtualItem.index}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
              data-index={virtualItem.index}
              ref={virtualizer.measureElement}
            >
              <Message
                model={{
                  message: message.content,
                  sentTime: timestamp,
                  sender: isCoach ? 'AI Coach' : 'You',
                  direction: isCoach ? 'incoming' : 'outgoing',
                  position: 'single',
                }}
                avatarPosition={isCoach ? 'tl' : 'tr'}
              >
                {isCoach && (
                  <Avatar
                    name="AI Coach"
                    src="/coach-avatar.png" // Placeholder - can be customized
                  />
                )}
                <Message.Footer sentTime={timestamp} />
              </Message>
            </div>
          );
        })}
      </div>
    </div>
  );
}
