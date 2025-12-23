#!/usr/bin/env python3
"""
Seed Economics 9708 configuration into database

This script loads Economics 9708 configuration from resource files and updates
the subjects table with JSONB config data.

Configuration files:
- resources/subjects/9708/marking_config.json
- resources/subjects/9708/extraction_patterns.yaml
- resources/subjects/9708/paper_templates.json

Database table: subjects
JSONB columns: marking_config, extraction_patterns, paper_templates

Usage:
    uv run python scripts/seed_economics_config.py

Requirements:
- Database migration 002_questions must be applied
- Economics 9708 subject record must exist (from Phase I migration)
"""

import json
import sys
from pathlib import Path

import yaml
from sqlmodel import Session, select

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_engine
from models.subject import Subject


def load_config_files() -> dict[str, dict]:
    """
    Load Economics 9708 configuration from resource files

    Returns:
        Dictionary with keys: marking_config, extraction_patterns, paper_templates
    """
    resources_dir = Path(__file__).parent.parent / "resources" / "subjects" / "9708"

    # Load marking_config.json
    with open(resources_dir / "marking_config.json", "r") as f:
        marking_config = json.load(f)

    # Load extraction_patterns.yaml
    with open(resources_dir / "extraction_patterns.yaml", "r") as f:
        extraction_patterns = yaml.safe_load(f)

    # Load paper_templates.json
    with open(resources_dir / "paper_templates.json", "r") as f:
        paper_templates = json.load(f)

    return {
        "marking_config": marking_config,
        "extraction_patterns": extraction_patterns,
        "paper_templates": paper_templates,
    }


def seed_economics_config() -> None:
    """
    Seed Economics 9708 configuration into database

    Finds the Economics 9708 subject record (code='9708') and updates
    its JSONB config columns with data from resource files.
    """
    print("=" * 80)
    print("Seeding Economics 9708 Configuration")
    print("=" * 80)

    # Load config files
    print("\n[1/4] Loading configuration files from resources/subjects/9708/...")
    try:
        configs = load_config_files()
        print(f"    ✅ Loaded marking_config.json ({len(json.dumps(configs['marking_config']))} bytes)")
        print(f"    ✅ Loaded extraction_patterns.yaml ({len(str(configs['extraction_patterns']))} bytes)")
        print(f"    ✅ Loaded paper_templates.json ({len(json.dumps(configs['paper_templates']))} bytes)")
    except FileNotFoundError as e:
        print(f"    ❌ Error: Config file not found: {e}")
        print("    Ensure T012-T014 tasks completed (config files created)")
        sys.exit(1)
    except Exception as e:
        print(f"    ❌ Error loading config files: {e}")
        sys.exit(1)

    # Connect to database
    print("\n[2/4] Connecting to database...")
    try:
        engine = get_engine()
        with Session(engine) as session:
            print("    ✅ Database connection established")

            # Find Economics 9708 subject
            print("\n[3/4] Finding Economics 9708 subject record...")
            statement = select(Subject).where(Subject.code == "9708")
            economics = session.exec(statement).first()

            if not economics:
                print("    ❌ Error: Economics 9708 subject not found in database")
                print("    Ensure Phase I migration was applied (subjects table seeded)")
                sys.exit(1)

            print(f"    ✅ Found Economics 9708 (ID: {economics.id}, Name: {economics.name})")

            # Update JSONB config columns
            print("\n[4/4] Updating JSONB config columns...")
            economics.marking_config = configs["marking_config"]
            economics.extraction_patterns = configs["extraction_patterns"]
            economics.paper_templates = configs["paper_templates"]

            session.add(economics)
            session.commit()
            session.refresh(economics)

            print("    ✅ Updated marking_config (JSONB)")
            print("    ✅ Updated extraction_patterns (JSONB)")
            print("    ✅ Updated paper_templates (JSONB)")

            # Verify configs were saved
            print("\n[Verification] Confirming configs saved correctly...")
            statement = select(Subject).where(Subject.code == "9708")
            verified = session.exec(statement).first()

            if not verified:
                print("    ❌ Error: Could not re-fetch Economics record for verification")
                sys.exit(1)

            # Check each config is present
            if not verified.marking_config:
                print("    ❌ Error: marking_config is NULL after save")
                sys.exit(1)

            if not verified.extraction_patterns:
                print("    ❌ Error: extraction_patterns is NULL after save")
                sys.exit(1)

            if not verified.paper_templates:
                print("    ❌ Error: paper_templates is NULL after save")
                sys.exit(1)

            print("    ✅ marking_config verified (has version: {})".format(
                verified.marking_config.get("version")
            ))
            print("    ✅ extraction_patterns verified (has version: {})".format(
                verified.extraction_patterns.get("version")
            ))
            print("    ✅ paper_templates verified (has version: {})".format(
                verified.paper_templates.get("version")
            ))

    except Exception as e:
        print(f"    ❌ Database error: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✅ Economics 9708 Configuration Seeded Successfully")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Verify configs in database: SELECT code, marking_config, extraction_patterns FROM subjects WHERE code='9708';")
    print("  2. Download Economics sample PDFs to resources/subjects/9708/sample_papers/")
    print("  3. Proceed with Phase 3: User Story 3 (Filename Parsing)")
    print()


if __name__ == "__main__":
    seed_economics_config()
