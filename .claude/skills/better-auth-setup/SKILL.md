# Better-Auth Setup Skill

**Version**: 1.0.0
**Last Updated**: 2025-12-24
**Tested**: ✅ Yes (2 days in evolution_to_do)
**Reference Project**: `~/dev/evolution_to_do`

---

## Purpose

Drop-in authentication setup for Next.js projects using Better-Auth.

**Problem Solved**: Spent 2 days implementing better-auth in evolution_to_do. This skill copies the working implementation to any new project in 5 minutes.

---

## When to Use This Skill

✅ **Use when:**
- Starting a new Next.js project that needs authentication
- Adding auth to an existing Next.js project
- Want email/password + Google OAuth support
- Using Neon PostgreSQL (or any PostgreSQL)

❌ **Don't use when:**
- Need other auth providers (GitHub, Apple) - extend the skill first
- Using different database (MySQL, MongoDB) - adapt schema first
- Need custom auth logic (magic links, OTP, etc.)

---

## Quick Start (Copy-Paste Command)

```bash
# Run this in your Next.js project root
bash /path/to/my_personal_examiner/scripts/setup-better-auth.sh ~/dev/evolution_to_do/frontend
```

---

## What Gets Installed

### 1. File Structure
```
your-project/
├── lib/
│   └── auth/
│       ├── core/
│       │   ├── server.ts      # Better-Auth server instance
│       │   └── client.ts      # Better-Auth client (React hooks)
│       ├── config/
│       │   └── env.ts         # Environment variable validation
│       └── adapters/
│           └── db-adapter.ts  # Neon PostgreSQL Pool adapter
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...route]/
│   │           └── route.ts   # Better-Auth API handler
│   └── login/
│       └── page.tsx           # Login/Signup page UI
└── auth.ts                    # Better-Auth CLI config
```

### 2. Database Tables
- `user` - User accounts
- `session` - Active sessions (with token column)
- `account` - OAuth provider links
- `verification` - Email verification tokens

### 3. Features Enabled
- ✅ Email/password authentication
- ✅ Google OAuth (optional - needs credentials)
- ✅ Session management (httpOnly cookies)
- ✅ User registration
- ✅ Login/logout
- ✅ Protected routes support

---

## Step-by-Step Setup

### Step 1: Run Setup Script

```bash
# In your Next.js project root
cd your-next-project/

# Run the setup script
bash /path/to/my_personal_examiner/scripts/setup-better-auth.sh ~/dev/evolution_to_do/frontend
```

**What it does:**
1. Copies all auth files from evolution_to_do
2. Checks and installs missing npm packages
3. Creates `.env.local` template (if doesn't exist)
4. Generates database migration script
5. Shows next steps

### Step 2: Configure Environment

Update `.env.local`:

```env
# Better-Auth Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-32-char-secret-here
BETTER_AUTH_URL=http://localhost:3000

# Google OAuth (Optional - leave empty to disable)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

**Generate secret:**
```bash
openssl rand -base64 32
```

### Step 3: Create Database Tables

```bash
node setup-better-auth-db.mjs
```

**Output should be:**
```
🔧 Setting up Better-Auth tables...
✅ Better-Auth tables created successfully!
```

### Step 4: Start Development Server

```bash
npm run dev
```

### Step 5: Test Authentication

1. Visit: http://localhost:3000/login
2. Try email signup: Enter email + password
3. Check database: Verify user created
4. Try login: Use same credentials
5. (Optional) Try Google login if credentials added

---

## Configuration

### Redirect URLs

**Default redirect**: `/teaching` (from my_personal_examiner)

**Change redirect:**
Edit `lib/auth/core/server.ts`:
```typescript
// In socialProviders.google config
redirectURI: `${env.BETTER_AUTH_URL}/api/auth/callback/google`,

// In your login page
await authClient.signIn.social({
  provider: 'google',
  callbackURL: '/your-custom-page', // ← Change this
});
```

### Google OAuth Setup

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
4. Copy Client ID and Secret
5. Add to `.env.local`
6. Restart dev server

### Database Customization

**Add custom user fields:**

1. Update SQL in `setup-better-auth-db.mjs`:
   ```sql
   CREATE TABLE IF NOT EXISTS "user" (
       id TEXT PRIMARY KEY,
       name TEXT,
       email TEXT NOT NULL UNIQUE,
       "emailVerified" BOOLEAN NOT NULL DEFAULT false,
       image TEXT,
       -- ADD YOUR CUSTOM FIELDS HERE
       role TEXT DEFAULT 'user',
       organization TEXT,
       -- END CUSTOM FIELDS
       "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. Update TypeScript types in your app

---

## Integration with Backend

### Get Student ID from Better-Auth Session

Create API route to sync better-auth user → your backend models:

```typescript
// app/api/student/route.ts
import { auth } from "@/lib/auth/core/server";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  const cookieStore = await cookies();
  const session = await auth.api.getSession({
    headers: new Headers({ cookie: cookieStore.toString() }),
  });

  if (!session?.user) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  // Check if Student exists in your backend
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/auth/student-by-email?email=${session.user.email}`
  );

  if (response.ok) {
    const student = await response.json();
    return NextResponse.json({ student_id: student.id });
  }

  // Create Student if not found
  const createResponse = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: session.user.email,
        password: `better-auth-${session.user.id}-${Date.now()}`,
        full_name: session.user.name || session.user.email.split("@")[0],
      }),
    }
  );

  if (!createResponse.ok) {
    return NextResponse.json(
      { error: "Failed to create student record" },
      { status: 500 }
    );
  }

  const newStudent = await createResponse.json();
  return NextResponse.json({ student_id: newStudent.id });
}
```

### Use in API Calls

```typescript
// lib/api/your-api.ts
async function getStudentId(): Promise<string> {
  const response = await fetch('/api/student');
  if (!response.ok) {
    throw new Error('Not authenticated. Please log in.');
  }
  const data = await response.json();
  return data.student_id;
}

// Use in API functions
export async function createExam(examData: ExamData) {
  const studentId = await getStudentId();

  const response = await fetch(`${API_URL}/api/exams`, {
    method: 'POST',
    body: JSON.stringify({ ...examData, student_id: studentId }),
  });

  return response.json();
}
```

---

## Troubleshooting

### Error: "relation 'user' does not exist"

**Cause**: Database tables not created

**Fix**:
```bash
node setup-better-auth-db.mjs
```

---

### Error: "Provider not found" (Google)

**Cause**: Google OAuth credentials are empty strings

**Fix**: Either:
1. Add real Google credentials to `.env.local`, OR
2. Remove Google button from login page

The skill properly handles empty credentials - Google provider won't be added to config.

---

### Error: "column 'token' does not exist"

**Cause**: Old database schema missing token column

**Fix**:
```sql
ALTER TABLE session ADD COLUMN IF NOT EXISTS token TEXT NOT NULL UNIQUE DEFAULT gen_random_uuid()::text;
```

Or drop and recreate tables:
```bash
node setup-better-auth-db.mjs
```

---

### Error: "Failed to sign up"

**Check**:
1. DATABASE_URL in `.env.local` is correct
2. BETTER_AUTH_SECRET is >= 32 characters
3. Database tables exist: `node setup-better-auth-db.mjs`
4. Check browser console for detailed error
5. Check backend logs

---

### Login works but session not persisted

**Check**:
1. Cookies enabled in browser
2. `useSecureCookies` set correctly in `lib/auth/core/server.ts`:
   ```typescript
   useSecureCookies: env.BETTER_AUTH_URL.startsWith("https://")
   ```
   Should be `false` for localhost HTTP

---

## Advanced Usage

### Protect Routes

```typescript
// middleware.ts
import { auth } from "@/lib/auth/core/server";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session?.user) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/teaching/:path*'],
};
```

### Custom Login UI

Replace `app/login/page.tsx` with your own design:

```tsx
import { authClient } from '@/lib/auth/core/client';

export default function CustomLogin() {
  const handleLogin = async () => {
    const result = await authClient.signIn.email({
      email: 'user@example.com',
      password: 'password',
    });

    if (result.error) {
      console.error(result.error);
    } else {
      router.push('/dashboard');
    }
  };

  // Your custom UI here
}
```

---

## Testing Checklist

After setup, verify these work:

- [ ] Email signup creates user in database
- [ ] Email login works with correct credentials
- [ ] Login fails with wrong password
- [ ] Session persists across page refreshes
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] Google OAuth redirects correctly (if enabled)
- [ ] Student record syncs with backend (if applicable)

---

## Performance Notes

- **Session storage**: PostgreSQL (fast for reads)
- **Cookie-based**: No localStorage/sessionStorage needed
- **Token column**: Required by Better-Auth 1.4+
- **Connection pooling**: Uses Neon Pool (max: 1 connection for serverless)

---

## Security Considerations

✅ **Handled by Better-Auth:**
- Password hashing (bcrypt)
- CSRF protection
- Session token rotation
- HttpOnly cookies
- Secure cookies (HTTPS only in production)

⚠️ **You must handle:**
- Rate limiting (add middleware)
- Email verification (enable in Better-Auth config)
- Two-factor auth (add Better-Auth plugin)
- Password reset (add Better-Auth plugin)

---

## Cost Estimate

Using Neon PostgreSQL Free Tier:
- ✅ Unlimited auth users (database rows)
- ✅ 500MB storage (enough for ~100k users)
- ✅ 100 hours compute/month (typical for side projects)

**Cost**: $0/month for most indie projects

---

## Migration from Other Auth Systems

### From NextAuth.js

1. Export users from NextAuth database
2. Run Better-Auth migration
3. Import users to Better-Auth tables
4. Update API routes
5. Update login components

Better-Auth uses similar concepts (sessions, accounts) so migration is straightforward.

---

## Future Enhancements

- [ ] Add email verification flow
- [ ] Add password reset flow
- [ ] Add two-factor authentication
- [ ] Add magic link login
- [ ] Support other databases (Supabase, PlanetScale)
- [ ] Add GitHub OAuth
- [ ] Add Apple OAuth
- [ ] Create npm package: `npx create-better-auth`

---

## Version History

- **1.0.0** (2025-12-24): Initial version with email/password + Google OAuth

---

## Sources

- [Better Auth PostgreSQL](https://www.better-auth.com/docs/adapters/postgresql)
- [Better Auth Database](https://www.better-auth.com/docs/concepts/database)
- [Better Auth CLI](https://www.better-auth.com/docs/concepts/cli)
- [Session Schema Issue](https://github.com/better-auth/better-auth/issues/3281)

---

## Support

**Reference implementations:**
- `~/dev/evolution_to_do` - 2 days of testing, fully working
- `~/dev/my_personal_examiner` - This project (uses the skill)

**Questions?** Check `BETTER_AUTH_SETUP.md` in project root.
