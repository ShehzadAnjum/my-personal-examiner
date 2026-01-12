"""
Simple script to check pending admin resources without importing models.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found")
    sys.exit(1)

# Connect to database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("CHECKING PENDING RESOURCES")
print("="*80)

# Check for admin-uploaded resources that are still pending
query = """
SELECT
    r.id,
    r.title,
    r.visibility,
    r.admin_approved,
    s.email,
    s.is_admin
FROM resources r
LEFT JOIN students s ON r.uploaded_by_student_id = s.id
WHERE r.visibility = 'pending_review'
ORDER BY s.is_admin DESC NULLS LAST, r.created_at;
"""

cur.execute(query)
results = cur.fetchall()

if not results:
    print("✅ GOOD: No pending resources found")
else:
    print(f"\n⚠️  Found {len(results)} pending resources:\n")

    admin_count = 0
    student_count = 0
    null_count = 0

    for row in results:
        resource_id, title, visibility, admin_approved, email, is_admin = row

        if is_admin:
            admin_count += 1
            print(f"❌ ADMIN RESOURCE (should not be pending):")
        elif email is None:
            null_count += 1
            print(f"⚠️  NULL UPLOADER:")
        else:
            student_count += 1
            print(f"✅ STUDENT RESOURCE (OK to be pending):")

        print(f"   ID: {resource_id}")
        print(f"   Title: {title}")
        print(f"   Uploader: {email or 'NULL'} (admin={is_admin})")
        print(f"   Visibility: {visibility}")
        print(f"   Admin Approved: {admin_approved}")
        print()

    print("="*80)
    print("SUMMARY:")
    print(f"  - Admin-uploaded: {admin_count} (❌ should be 0)")
    print(f"  - Student-uploaded: {student_count} (✅ OK)")
    print(f"  - NULL uploader: {null_count} (⚠️  should be 0)")
    print("="*80)

cur.close()
conn.close()
