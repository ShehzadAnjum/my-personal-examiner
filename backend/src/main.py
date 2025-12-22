"""
My Personal Examiner - Backend API

PhD-level A-Level Teaching & Examination System

Phase I: Core Infrastructure & Database
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Application metadata
app = FastAPI(
    title="My Personal Examiner API",
    description="PhD-level A-Level Teaching & Examination System - Core Infrastructure",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware (Phase IV - Frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """
    Root endpoint - Health check

    Returns application status and version.
    """
    return {
        "message": "My Personal Examiner API",
        "status": "running",
        "version": "0.1.0",
        "phase": "Phase I - Core Infrastructure",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint

    Used by monitoring systems to verify API is operational.
    """
    return {"status": "healthy"}


# Application lifecycle events
@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup event

    Initialize connections, load configurations, etc.
    """
    print("🚀 My Personal Examiner API starting up...")
    print("📚 Phase I: Core Infrastructure & Database")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Application shutdown event

    Clean up connections, close resources, etc.
    """
    print("👋 My Personal Examiner API shutting down...")


# Router registration
# Phase 3 (US1): Authentication (register)
from src.routes import auth
from src.routes import coaching  # Phase III US2: Coach Agent
from src.routes import exams
from src.routes import feedback  # Phase III US5: Reviewer Agent
from src.routes import marking  # Phase III US4: Marker Agent
from src.routes import planning  # Phase III US6: Planner Agent
from src.routes import questions
from src.routes import subjects
from src.routes import syllabus
from src.routes import teaching  # Phase III US1: Teacher Agent

app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(questions.router, tags=["questions"])  # Phase II US1: Upload & Storage
app.include_router(exams.router, tags=["exams"])  # Phase II US6: Exam Generation
app.include_router(syllabus.router, tags=["syllabus"])  # Phase II US7: Syllabus Tagging
app.include_router(subjects.router, tags=["subjects"])  # Phase II: Subject listing
app.include_router(teaching.router, tags=["teaching"])  # Phase III US1: Teacher Agent
app.include_router(coaching.router, tags=["coaching"])  # Phase III US2: Coach Agent
app.include_router(marking.router, tags=["marking"])  # Phase III US4: Marker Agent
app.include_router(feedback.router, tags=["feedback"])  # Phase III US5: Reviewer Agent
app.include_router(planning.router, tags=["planning"])  # Phase III US6: Planner Agent

# Phase 6 (US4): app.include_router(students.router, prefix="/api", tags=["students"])
