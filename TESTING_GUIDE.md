# Testing Guide - Resource Redirect Issue

**Date:** 2026-01-05
**Issue:** Student users being redirected to `/resources/admin`

---

## 🧪 IMMEDIATE TEST STEPS

### Step 1: Clear Cache (Automatic on Page Load)

1. **Open your browser** and go to any page
2. **Open browser console** (F12 → Console tab)
3. **Click "Resources"** link
4. **Look for this log:**
   ```
   [Resources] FORCE CLEARING CACHE (one-time fix)
   ```

This will automatically clear corrupted cache on first page load.

---

### Step 2: Check Which Account You're Logged In As

**Look for these console logs:**

```
[StudentCache] ===== LOGGED IN AS =====
[StudentCache] Email: YOUR_EMAIL_HERE
[StudentCache] Student ID: ...
[StudentCache] is_admin (raw): true/false
[StudentCache] is_admin (coerced): true/false
[StudentCache] ========================
```

**Check the email:**
- If email is `sanjum77@gmail.com` or `demo@example.com` → **YOU ARE ADMIN** (redirect is correct)
- If email is `hamza@test.com` or `tredanjum@gmail.com` → **YOU ARE STUDENT** (should NOT redirect)

---

### Step 3: Check Redirect Decision

**Look for these console logs:**

```
[Resources] ===== REDIRECT DECISION =====
[Resources] Email: YOUR_EMAIL_HERE
[Resources] Student ID: ...
[Resources] is_admin: true/false
[Resources] is_admin === true: true/false
[Resources] ============================
```

**Then one of these:**

**If Admin:**
```
[Resources] ✅ ADMIN ACCOUNT - Redirecting to /resources/admin
[Resources] If you see this but you are NOT sanjum77@gmail.com, logout and login with correct account
```

**If Student:**
```
[Resources] ✅ STUDENT ACCOUNT - Loading student page
[Resources] You are logged in as: hamza@test.com
```

---

## 📊 Expected Console Output

### For Admin Account (sanjum77@gmail.com or demo@example.com):

```
[Resources] FORCE CLEARING CACHE (one-time fix)
[StudentCache] Cache miss, fetching from API
[StudentCache] ===== LOGGED IN AS =====
[StudentCache] Email: sanjum77@gmail.com
[StudentCache] Student ID: 699f98ee-69bf-4fc7-85a4-63b84a42a172
[StudentCache] is_admin (raw): true (type: boolean)
[StudentCache] is_admin (coerced): true
[StudentCache] ========================
[StudentCache] Caching student data: { student_id: "...", is_admin: true, version: 2 }
[Resources] ===== REDIRECT DECISION =====
[Resources] Email: sanjum77@gmail.com
[Resources] Student ID: 699f98ee-69bf-4fc7-85a4-63b84a42a172
[Resources] is_admin: true (type: boolean)
[Resources] is_admin === true: true
[Resources] ============================
[Resources] ✅ ADMIN ACCOUNT - Redirecting to /resources/admin
```

**Result:** ✅ Redirects to `/resources/admin`

---

### For Student Account (hamza@test.com, tredanjum@gmail.com, etc.):

```
[Resources] FORCE CLEARING CACHE (one-time fix)
[StudentCache] Cache miss, fetching from API
[StudentCache] ===== LOGGED IN AS =====
[StudentCache] Email: hamza@test.com
[StudentCache] Student ID: 46bcecd6-b90a-4228-aad8-b700e482fe94
[StudentCache] is_admin (raw): false (type: boolean)
[StudentCache] is_admin (coerced): false
[StudentCache] ========================
[StudentCache] Caching student data: { student_id: "...", is_admin: false, version: 2 }
[Resources] ===== REDIRECT DECISION =====
[Resources] Email: hamza@test.com
[Resources] Student ID: 46bcecd6-b90a-4228-aad8-b700e482fe94
[Resources] is_admin: false (type: boolean)
[Resources] is_admin === true: false
[Resources] ============================
[Resources] ✅ STUDENT ACCOUNT - Loading student page
[Resources] You are logged in as: hamza@test.com
```

**Result:** ✅ Stays on `/resources` (student page)

---

## 🔍 Troubleshooting

### Problem: "I'm logged in as hamza@test.com but still redirecting"

**Check console logs:**

1. **If you see:**
   ```
   [StudentCache] Email: sanjum77@gmail.com
   ```
   **Problem:** You're actually logged in as admin, not as hamza@test.com

   **Solution:** Logout and login with hamza@test.com

2. **If you see:**
   ```
   [StudentCache] Email: hamza@test.com
   [StudentCache] is_admin (raw): true
   ```
   **Problem:** Database has hamza@test.com marked as admin

   **Solution:** Check database (see below)

3. **If you see:**
   ```
   [StudentCache] Email: hamza@test.com
   [StudentCache] is_admin (raw): false
   [Resources] ✅ ADMIN ACCOUNT - Redirecting
   ```
   **Problem:** Logic error (this should NOT happen)

   **Solution:** Report exact console logs

---

### How to Check Database

**Run this command:**
```bash
cd backend
uv run python scripts/check_student_admin_status.py
```

**Look for the email you're testing with:**
```
👤 STUDENT:
   Email: hamza@test.com
   is_admin: False   ← Should be False for students

👑 ADMIN:
   Email: sanjum77@gmail.com
   is_admin: True    ← Should be True for admins
```

---

### How to Manually Change Admin Status in Database

**If you need to make hamza@test.com an admin for testing:**

```python
# backend/scripts/make_admin.py
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

# Make user admin
cur.execute("UPDATE students SET is_admin = true WHERE email = %s", ("hamza@test.com",))
conn.commit()

print("✅ hamza@test.com is now admin")
cur.close()
conn.close()
```

**To remove admin:**
```python
cur.execute("UPDATE students SET is_admin = false WHERE email = %s", ("hamza@test.com",))
```

---

## ✅ Success Criteria

### For Student Account:
- [ ] Console shows correct email
- [ ] Console shows `is_admin: false`
- [ ] Console shows "✅ STUDENT ACCOUNT - Loading student page"
- [ ] Page stays on `/resources` (does NOT redirect)
- [ ] Can see student resource browser

### For Admin Account:
- [ ] Console shows correct email (sanjum77@gmail.com or demo@example.com)
- [ ] Console shows `is_admin: true`
- [ ] Console shows "✅ ADMIN ACCOUNT - Redirecting to /resources/admin"
- [ ] Page redirects to `/resources/admin`
- [ ] Can see admin dashboard

---

## 📝 What to Send Me

If the issue persists, **copy and paste the ENTIRE console output** including:

1. **The logged in email:**
   ```
   [StudentCache] Email: ???
   ```

2. **The is_admin value:**
   ```
   [StudentCache] is_admin (raw): ???
   [StudentCache] is_admin (coerced): ???
   ```

3. **The redirect decision:**
   ```
   [Resources] ✅ ADMIN ACCOUNT or ✅ STUDENT ACCOUNT
   ```

4. **What email you THINK you're logged in as**

5. **What page you end up on** (/resources or /resources/admin)

---

## 🎯 Quick Summary

**The console will tell you:**
1. **Which email you're logged in as** (might not be what you think!)
2. **Whether that account is admin** (true/false)
3. **Why it's redirecting or not**

**Most likely issue:** You're logged in as `sanjum77@gmail.com` (admin) but think you're logged in as `hamza@test.com` (student).

**Solution:** Logout and login with the student account.

---

**Status:** ✅ Debugging tools deployed
**Next:** Open browser console and click "Resources" to see detailed logs
