"""Check database indexes on students table."""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("INDEXES ON STUDENTS TABLE")
print("="*80)

query = """
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'students'
ORDER BY indexname;
"""

cur.execute(query)
results = cur.fetchall()

if not results:
    print("❌ NO INDEXES FOUND on students table!")
else:
    for indexname, indexdef in results:
        print(f"\n✅ {indexname}")
        print(f"   {indexdef}")

cur.close()
conn.close()
