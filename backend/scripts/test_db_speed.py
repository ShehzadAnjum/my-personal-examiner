"""Test database connection and query speed."""

import os
import time
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Testing database connection speed...")

# Test 1: Connection time
start = time.time()
conn = psycopg2.connect(DATABASE_URL)
connect_time = time.time() - start
print(f"✓ Connection established in {connect_time:.3f}s")

# Test 2: Simple query
start = time.time()
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM students')
result = cur.fetchone()
query_time = time.time() - start
print(f"✓ COUNT query executed in {query_time:.3f}s (count={result[0]})")

# Test 3: Email lookup query
start = time.time()
cur.execute("SELECT id, email, is_admin FROM students WHERE email = %s LIMIT 1", ("test@example.com",))
result = cur.fetchone()
email_query_time = time.time() - start
print(f"✓ Email lookup query executed in {email_query_time:.3f}s")

cur.close()
conn.close()

total_time = connect_time + email_query_time
print(f"\n📊 Total time for auth check: {total_time:.3f}s")

if total_time > 1.0:
    print("⚠️  WARNING: Database is slow! This causes the 5-second page load.")
    print("   Recommendation: Use connection pooling or cache student data")
else:
    print("✅ Database speed is acceptable")
