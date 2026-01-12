"""Check admin status of all students in database."""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("ALL STUDENTS IN DATABASE")
print("="*80)

query = """
SELECT
    id,
    email,
    full_name,
    is_admin,
    created_at
FROM students
ORDER BY created_at DESC;
"""

cur.execute(query)
results = cur.fetchall()

print(f"\nTotal students: {len(results)}\n")

admin_count = 0
student_count = 0

for row in results:
    student_id, email, full_name, is_admin, created_at = row

    if is_admin:
        admin_count += 1
        print(f"👑 ADMIN:")
    else:
        student_count += 1
        print(f"👤 STUDENT:")

    print(f"   Email: {email}")
    print(f"   Name: {full_name}")
    print(f"   ID: {student_id}")
    print(f"   is_admin: {is_admin}")
    print(f"   Created: {created_at}")
    print()

print("="*80)
print(f"Summary:")
print(f"  - Admins: {admin_count}")
print(f"  - Students: {student_count}")
print("="*80)

cur.close()
conn.close()
