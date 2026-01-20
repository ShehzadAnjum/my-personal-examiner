"""Check all resources in database with details."""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("ALL RESOURCES IN DATABASE")
print("="*80)

query = """
SELECT
    r.id,
    r.title,
    r.resource_type,
    r.visibility,
    r.admin_approved,
    s.email as uploader_email,
    s.is_admin as uploader_is_admin,
    r.created_at
FROM resources r
LEFT JOIN students s ON r.uploaded_by_student_id = s.id
ORDER BY r.created_at DESC
LIMIT 20;
"""

cur.execute(query)
results = cur.fetchall()

if not results:
    print("❌ NO RESOURCES FOUND in database")
else:
    print(f"\nTotal resources (showing last 20): {len(results)}\n")

    for row in results:
        resource_id, title, resource_type, visibility, admin_approved, uploader_email, uploader_is_admin, created_at = row

        icon = "👑" if uploader_is_admin else "👤"
        status_icon = "✅" if visibility == 'public' else "⏳" if visibility == 'pending_review' else "🔒"

        print(f"{status_icon} {icon} {visibility.upper()}")
        print(f"   Title: {title}")
        print(f"   Type: {resource_type}")
        print(f"   Uploaded by: {uploader_email or 'NULL'} (admin={uploader_is_admin})")
        print(f"   Admin approved: {admin_approved}")
        print(f"   Created: {created_at}")
        print(f"   ID: {resource_id}")
        print()

# Count by status
print("="*80)
print("SUMMARY BY STATUS:")
print("="*80)

query = """
SELECT
    visibility,
    COUNT(*) as count,
    SUM(CASE WHEN s.is_admin = true THEN 1 ELSE 0 END) as admin_uploads,
    SUM(CASE WHEN s.is_admin = false OR s.is_admin IS NULL THEN 1 ELSE 0 END) as student_uploads
FROM resources r
LEFT JOIN students s ON r.uploaded_by_student_id = s.id
GROUP BY visibility;
"""

cur.execute(query)
results = cur.fetchall()

for row in results:
    visibility, count, admin_uploads, student_uploads = row
    print(f"{visibility}: {count} total (Admin: {admin_uploads}, Student: {student_uploads})")

cur.close()
conn.close()
