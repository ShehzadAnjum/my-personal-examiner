#!/usr/bin/env python3
"""
Seed Academic Levels Script

Seeds the default academic levels into the database if they don't already exist.

Feature: 008-academic-level-hierarchy

Usage:
    uv run python scripts/seed_academic_levels.py

Default Academic Levels:
    - A-Level (Cambridge International A-Level)
    - AS-Level (Cambridge International AS-Level)
    - O-Level (Cambridge International O-Level)
    - IGCSE (Cambridge IGCSE)
    - IB (International Baccalaureate)
"""

import asyncio
import os
import sys
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, create_engine

# Load environment variables
load_dotenv()

# Default academic levels from the AcademicLevel model
DEFAULT_ACADEMIC_LEVELS = [
    {
        "name": "A-Level",
        "code": "A",
        "description": "Cambridge International A-Level qualifications",
        "exam_board": "Cambridge International",
    },
    {
        "name": "AS-Level",
        "code": "AS",
        "description": "Cambridge International AS-Level qualifications",
        "exam_board": "Cambridge International",
    },
    {
        "name": "O-Level",
        "code": "O",
        "description": "Cambridge International O-Level qualifications",
        "exam_board": "Cambridge International",
    },
    {
        "name": "IGCSE",
        "code": "IGCSE",
        "description": "Cambridge International General Certificate of Secondary Education",
        "exam_board": "Cambridge International",
    },
    {
        "name": "International Baccalaureate",
        "code": "IB",
        "description": "International Baccalaureate Diploma Programme",
        "exam_board": "IB Organization",
    },
]


def seed_academic_levels():
    """Seed default academic levels into the database."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    engine = create_engine(database_url)

    with Session(engine) as session:
        print("Seeding academic levels...")

        for level_data in DEFAULT_ACADEMIC_LEVELS:
            # Check if level already exists by code
            result = session.exec(
                text("SELECT id, name FROM academic_levels WHERE code = :code"),
                params={"code": level_data["code"]}
            ).first()

            if result:
                print(f"  - {level_data['code']}: {level_data['name']} (already exists)")
                continue

            # Insert new academic level
            new_id = uuid4()
            session.exec(
                text("""
                    INSERT INTO academic_levels (id, name, code, description, exam_board, created_at, updated_at)
                    VALUES (:id, :name, :code, :description, :exam_board, NOW(), NOW())
                """),
                params={
                    "id": str(new_id),
                    "name": level_data["name"],
                    "code": level_data["code"],
                    "description": level_data["description"],
                    "exam_board": level_data["exam_board"],
                }
            )
            print(f"  + {level_data['code']}: {level_data['name']} (created)")

        session.commit()
        print("\nSeeding complete!")

        # Show summary
        result = session.exec(text("SELECT COUNT(*) FROM academic_levels"))
        count = result.scalar()
        print(f"Total academic levels: {count}")


if __name__ == "__main__":
    seed_academic_levels()
