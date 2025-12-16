"""
Vercel Serverless Function Entry Point

This file is required for Vercel to properly route requests to FastAPI.
"""

import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app

# Vercel expects this handler
handler = app
