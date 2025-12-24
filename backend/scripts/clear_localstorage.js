/**
 * Clear all teaching explanation data from browser localStorage
 *
 * Run this in browser console (F12 → Console tab) while on the app
 *
 * This clears:
 * - All cached explanations (explanation_*)
 * - Saved explanations cache
 * - Saved explanations timestamp
 */

(function clearExplanationData() {
  let clearedCount = 0;

  // Get all localStorage keys
  const keys = Object.keys(localStorage);

  console.log('🔍 Found', keys.length, 'total localStorage items');

  // Clear explanation caches (explanation_*)
  const explanationKeys = keys.filter(key => key.startsWith('explanation_'));
  explanationKeys.forEach(key => {
    localStorage.removeItem(key);
    clearedCount++;
    console.log('🗑️  Removed:', key);
  });

  // Clear saved explanations cache
  if (localStorage.getItem('saved_explanations_cache')) {
    localStorage.removeItem('saved_explanations_cache');
    clearedCount++;
    console.log('🗑️  Removed: saved_explanations_cache');
  }

  if (localStorage.getItem('saved_explanations_timestamp')) {
    localStorage.removeItem('saved_explanations_timestamp');
    clearedCount++;
    console.log('🗑️  Removed: saved_explanations_timestamp');
  }

  console.log('\n✅ Cleared', clearedCount, 'explanation-related items from localStorage');
  console.log('📝 Remaining items:', Object.keys(localStorage).length);

  // Show what's left (excluding auth tokens for privacy)
  const remaining = Object.keys(localStorage).filter(k => !k.includes('token') && !k.includes('session'));
  if (remaining.length > 0) {
    console.log('📋 Remaining keys:', remaining);
  }
})();
