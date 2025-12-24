-- Clear all saved explanations (bookmarks) from database
-- This removes bookmark pointers only, not the Student or SyllabusPoint data

-- Show count before deletion
SELECT COUNT(*) as "Bookmarks Before Deletion" FROM saved_explanations;

-- Delete all saved explanations
DELETE FROM saved_explanations;

-- Confirm deletion
SELECT COUNT(*) as "Bookmarks After Deletion" FROM saved_explanations;

-- Optional: Reset the sequence if you want IDs to start from 1 again
-- ALTER SEQUENCE saved_explanations_id_seq RESTART WITH 1;
