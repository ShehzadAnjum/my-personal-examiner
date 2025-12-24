#!/bin/bash

# Better-Auth Setup Script
# Copies working implementation from reference project to target project
# Usage: ./scripts/setup-better-auth.sh [source-project-path]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}    Better-Auth Setup - Copy from Reference Project    ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Source project path (default: evolution_to_do)
SOURCE_PROJECT="${1:-$HOME/dev/evolution_to_do/frontend}"

# Validate source project exists
if [ ! -d "$SOURCE_PROJECT" ]; then
    echo -e "${RED}Error: Source project not found at $SOURCE_PROJECT${NC}"
    exit 1
fi

echo -e "${YELLOW}📂 Source: $SOURCE_PROJECT${NC}"
echo -e "${YELLOW}📁 Target: $(pwd)${NC}"
echo ""

# 1. Copy auth infrastructure
echo -e "${GREEN}1. Copying auth infrastructure...${NC}"
mkdir -p ./lib/auth
cp -r "$SOURCE_PROJECT/lib/auth/"* ./lib/auth/ 2>/dev/null || echo "  ⚠️  No auth directory found in source"

# 2. Copy auth.ts (for CLI)
echo -e "${GREEN}2. Copying auth.ts (CLI config)...${NC}"
cp "$SOURCE_PROJECT/auth.ts" ./auth.ts 2>/dev/null || echo "  ⚠️  No auth.ts found in source"

# 3. Copy API route
echo -e "${GREEN}3. Copying API auth route...${NC}"
mkdir -p ./app/api/auth/\[...route\]
cp "$SOURCE_PROJECT/app/api/auth/[...route]/route.ts" "./app/api/auth/[...route]/route.ts" 2>/dev/null || echo "  ⚠️  No auth API route found"

# 4. Copy login page (if exists)
echo -e "${GREEN}4. Copying login page...${NC}"
if [ -f "$SOURCE_PROJECT/app/login/page.tsx" ]; then
    mkdir -p ./app/login
    cp "$SOURCE_PROJECT/app/login/page.tsx" ./app/login/page.tsx
    echo "  ✓ Login page copied"
else
    echo "  ⚠️  No login page found in source"
fi

# 5. Check dependencies
echo ""
echo -e "${GREEN}5. Checking dependencies...${NC}"
MISSING_DEPS=""

if ! grep -q "\"better-auth\"" package.json; then
    MISSING_DEPS="$MISSING_DEPS better-auth"
fi
if ! grep -q "\"@neondatabase/serverless\"" package.json; then
    MISSING_DEPS="$MISSING_DEPS @neondatabase/serverless"
fi
if ! grep -q "\"kysely\"" package.json; then
    MISSING_DEPS="$MISSING_DEPS kysely"
fi
if ! grep -q "\"zod\"" package.json; then
    MISSING_DEPS="$MISSING_DEPS zod"
fi

if [ -n "$MISSING_DEPS" ]; then
    echo -e "${YELLOW}  Installing missing dependencies:$MISSING_DEPS${NC}"
    npm install $MISSING_DEPS
else
    echo "  ✓ All dependencies already installed"
fi

# 6. Create .env.local template if doesn't exist
echo ""
echo -e "${GREEN}6. Checking .env.local...${NC}"
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}  Creating .env.local template...${NC}"
    cat > .env.local << 'EOF'
# Better-Auth Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=change-me-to-32-char-secret
BETTER_AUTH_URL=http://localhost:3000

# Google OAuth (Optional - leave empty to disable)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
EOF
    echo -e "${YELLOW}  ⚠️  IMPORTANT: Update .env.local with your credentials!${NC}"
else
    echo "  ✓ .env.local already exists"
fi

# 7. Create database migration script
echo ""
echo -e "${GREEN}7. Creating database migration script...${NC}"
cat > ./setup-better-auth-db.mjs << 'EOF'
import { Pool } from '@neondatabase/serverless';

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  console.error('❌ DATABASE_URL not set in environment');
  process.exit(1);
}

const pool = new Pool({ connectionString, max: 1 });

async function setupDatabase() {
  try {
    console.log('🔧 Setting up Better-Auth tables...');

    await pool.query(`
      CREATE TABLE IF NOT EXISTS "user" (
          id TEXT PRIMARY KEY,
          name TEXT,
          email TEXT NOT NULL UNIQUE,
          "emailVerified" BOOLEAN NOT NULL DEFAULT false,
          image TEXT,
          "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS session (
          id TEXT PRIMARY KEY,
          token TEXT NOT NULL UNIQUE,
          "expiresAt" TIMESTAMP NOT NULL,
          "ipAddress" TEXT,
          "userAgent" TEXT,
          "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
          "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS account (
          id TEXT PRIMARY KEY,
          "accountId" TEXT NOT NULL,
          "providerId" TEXT NOT NULL,
          "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
          "accessToken" TEXT,
          "refreshToken" TEXT,
          "idToken" TEXT,
          "expiresAt" TIMESTAMP,
          "accessTokenExpiresAt" TIMESTAMP,
          "refreshTokenExpiresAt" TIMESTAMP,
          scope TEXT,
          password TEXT,
          "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS verification (
          id TEXT PRIMARY KEY,
          identifier TEXT NOT NULL,
          value TEXT NOT NULL,
          "expiresAt" TIMESTAMP NOT NULL,
          "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE INDEX IF NOT EXISTS idx_session_userId ON session("userId");
      CREATE INDEX IF NOT EXISTS idx_account_userId ON account("userId");
    `);

    console.log('✅ Better-Auth tables created successfully!');
  } catch (error) {
    console.error('❌ Database setup failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

setupDatabase();
EOF

echo "  ✓ Migration script created: setup-better-auth-db.mjs"

# 8. Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                    Setup Complete! ✅                  ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo "1. Update .env.local with your database credentials"
echo "2. Generate auth secret: openssl rand -base64 32"
echo "3. Run database migration: node setup-better-auth-db.mjs"
echo "4. (Optional) Add Google OAuth credentials"
echo "5. Start dev server: npm run dev"
echo "6. Visit http://localhost:3000/login"
echo ""
echo -e "${GREEN}🎉 Better-Auth is ready to use!${NC}"
