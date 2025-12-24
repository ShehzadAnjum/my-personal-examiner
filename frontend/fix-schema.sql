-- Fix Better Auth schema - add missing token column
ALTER TABLE session ADD COLUMN IF NOT EXISTS token TEXT NOT NULL UNIQUE DEFAULT gen_random_uuid()::text;

-- Also add any other missing columns
ALTER TABLE account ADD COLUMN IF NOT EXISTS "accessTokenExpiresAt" TIMESTAMP;
ALTER TABLE account ADD COLUMN IF NOT EXISTS "refreshTokenExpiresAt" TIMESTAMP;
