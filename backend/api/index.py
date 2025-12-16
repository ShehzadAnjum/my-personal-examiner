"""
Vercel Serverless Function Entry Point

This file is required for Vercel to properly route requests to FastAPI.
"""

from src.main import app

# Vercel expects this handler
handler = app
