"""
Check for admin-uploaded resources that are still showing as pending.
This should return 0 results after migration 012.
"""

import sys
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import Session, create_engine, select
from models.resource import Resource
from models.student import Student
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

def check_pending_admin_resources():
    """Check for resources uploaded by admins that are still pending."""
    with Session(engine) as session:
        # Query 1: Resources uploaded by admin users that are still pending
        query1 = (
            select(Resource, Student)
            .join(Student, Resource.uploaded_by_student_id == Student.id)
            .where(Student.is_admin == True)
            .where(Resource.visibility == "pending_review")
        )
        results1 = session.exec(query1).all()

        print("\n" + "="*80)
        print("ADMIN-UPLOADED RESOURCES STILL SHOWING AS PENDING")
        print("="*80)

        if not results1:
            print("✅ GOOD: No admin-uploaded resources are pending")
        else:
            print(f"❌ PROBLEM: Found {len(results1)} admin-uploaded resources still pending:")
            for resource, student in results1:
                print(f"  - Resource ID: {resource.id}")
                print(f"    Title: {resource.title}")
                print(f"    Uploader: {student.email} (admin={student.is_admin})")
                print(f"    Visibility: {resource.visibility}")
                print(f"    Admin Approved: {resource.admin_approved}")
                print()

        # Query 2: Resources with NULL uploader (non-user_upload) that are pending
        query2 = (
            select(Resource)
            .where(Resource.uploaded_by_student_id == None)
            .where(Resource.resource_type != "user_upload")
            .where(Resource.visibility == "pending_review")
        )
        results2 = session.exec(query2).all()

        print("\n" + "="*80)
        print("ADMIN-SYSTEM RESOURCES (NULL UPLOADER) STILL SHOWING AS PENDING")
        print("="*80)

        if not results2:
            print("✅ GOOD: No system-uploaded resources are pending")
        else:
            print(f"❌ PROBLEM: Found {len(results2)} system-uploaded resources still pending:")
            for resource in results2:
                print(f"  - Resource ID: {resource.id}")
                print(f"    Title: {resource.title}")
                print(f"    Type: {resource.resource_type}")
                print(f"    Visibility: {resource.visibility}")
                print(f"    Admin Approved: {resource.admin_approved}")
                print()

        # Query 3: Count all pending resources by uploader type
        print("\n" + "="*80)
        print("SUMMARY: ALL PENDING RESOURCES")
        print("="*80)

        all_pending = session.exec(
            select(Resource).where(Resource.visibility == "pending_review")
        ).all()

        print(f"Total pending resources: {len(all_pending)}")

        if all_pending:
            admin_pending = 0
            student_pending = 0
            null_pending = 0

            for resource in all_pending:
                if resource.uploaded_by_student_id is None:
                    null_pending += 1
                else:
                    uploader = session.get(Student, resource.uploaded_by_student_id)
                    if uploader and uploader.is_admin:
                        admin_pending += 1
                    else:
                        student_pending += 1

            print(f"  - By admin users: {admin_pending} (should be 0)")
            print(f"  - By students: {student_pending} (OK if students uploaded)")
            print(f"  - System uploads (NULL): {null_pending} (should be 0)")

if __name__ == "__main__":
    check_pending_admin_resources()
