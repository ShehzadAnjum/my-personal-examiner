/**
 * useKeyboardShortcuts Hook
 *
 * Global keyboard shortcut handler for the application.
 *
 * Usage:
 *   useKeyboardShortcuts({
 *     'Ctrl+Enter': () => sendMessage(),
 *     'Escape': () => closeModal(),
 *   });
 *
 * Supports:
 * - Ctrl/Cmd modifiers (cross-platform)
 * - Shift, Alt modifiers
 * - Single keys
 * - Custom key combinations
 */

'use client';

import { useEffect } from 'react';

type KeyboardShortcut = {
  [key: string]: (event: KeyboardEvent) => void;
};

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Build the key combination string
      const keys: string[] = [];

      if (event.ctrlKey || event.metaKey) keys.push('Ctrl'); // Cmd on Mac is metaKey
      if (event.shiftKey) keys.push('Shift');
      if (event.altKey) keys.push('Alt');

      // Add the actual key (normalized to handle special cases)
      const key = event.key === ' ' ? 'Space' : event.key;
      if (!['Control', 'Shift', 'Alt', 'Meta'].includes(key)) {
        keys.push(key);
      }

      const combination = keys.join('+');

      // Check if this combination has a handler
      const handler = shortcuts[combination];
      if (handler) {
        // Prevent default browser behavior for registered shortcuts
        event.preventDefault();
        handler(event);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts]);
}
