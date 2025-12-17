"""
Vercel Serverless Function Entry Point

This file is required for Vercel to properly route requests to FastAPI.
"""

import sys
from pathlib import Path

# Add backend directory to Python path for imports
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from src.main import app

# Vercel expects this handler
handler = app
