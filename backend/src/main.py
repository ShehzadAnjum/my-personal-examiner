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

# Debug: Print loaded API keys (masked)
print("🔧 Environment loaded from:", env_path)
print("🔑 OPENAI_API_KEY:", "✓ Present" if os.getenv("OPENAI_API_KEY") else "✗ Missing")
print("🔑 ANTHROPIC_API_KEY:", "✓ Present" if os.getenv("ANTHROPIC_API_KEY") else "✗ Missing")
print("🔑 GEMINI_API_KEY:", "✓ Present" if os.getenv("GEMINI_API_KEY") else "✗ Missing")

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
# IMPORTANT: Must be added BEFORE any routes to intercept OPTIONS preflight
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Type", "Content-Length"],
)


# Allowed origins for CORS
ALLOWED_ORIGINS = {"http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"}


# Global OPTIONS handler for CORS preflight (fallback)
@app.middleware("http")
async def catch_options_requests(request: Request, call_next):
    """
    Middleware to handle OPTIONS requests globally
    Ensures all OPTIONS preflight requests return 200 OK
    """
    origin = request.headers.get("origin", "http://localhost:3000")
    if origin not in ALLOWED_ORIGINS:
        origin = "http://localhost:3000"  # fallback

    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            },
        )
    return await call_next(request)


# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions with proper CORS headers.
    This ensures browsers can read error messages even on 500 errors.
    """
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    origin = request.headers.get("origin", "http://localhost:3000")
    if origin not in ALLOWED_ORIGINS:
        origin = "http://localhost:3000"

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        },
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
from src.routes import academic_levels  # Academic Level Hierarchy (008)
from src.routes import admin_resources  # Resource Bank admin review (007 - US4)
from src.routes import admin_setup  # Admin setup wizard (Admin-First Topic Generation)
from src.routes import auth
from src.routes import auth_extra  # Better-auth integration endpoints
from src.routes import coaching  # Phase III US2: Coach Agent
from src.routes import exams
from src.routes import feedback  # Phase III US5: Reviewer Agent
from src.routes import marking  # Phase III US4: Marker Agent
from src.routes import metrics  # Observability metrics (007 - Phase 10)
from src.routes import planning  # Phase III US6: Planner Agent
from src.routes import questions
from src.routes import resources  # Resource Bank (006)
from src.routes import resource_sync  # Resource Bank sync (007 - US2)
from src.routes import resource_tagging  # Resource Bank tagging (007 - US6)
from src.routes import subjects
from src.routes import syllabus
from src.routes import teaching  # Phase III US1: Teacher Agent

app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(auth_extra.router, tags=["auth-extra"])  # Better-auth student lookup
app.include_router(academic_levels.router, prefix="/api", tags=["academic-levels"])  # 008: Academic Level Hierarchy
app.include_router(academic_levels.hierarchy_router, prefix="/api", tags=["hierarchy"])  # 008: Full hierarchy tree
app.include_router(questions.router, tags=["questions"])  # Phase II US1: Upload & Storage
app.include_router(exams.router, tags=["exams"])  # Phase II US6: Exam Generation
app.include_router(syllabus.router, tags=["syllabus"])  # Phase II US7: Syllabus Tagging
app.include_router(subjects.router, tags=["subjects"])  # Phase II: Subject listing
app.include_router(resources.router, tags=["resources"])  # Resource Bank US1: View Explanations
app.include_router(resource_sync.router, tags=["resource-sync"])  # Resource Bank sync (007 - US2)
app.include_router(admin_resources.router, tags=["admin-resources"])  # Admin review (007 - US4)
app.include_router(admin_setup.router, tags=["admin-setup"])  # Admin setup wizard
app.include_router(resource_tagging.router, tags=["resource-tagging"])  # Admin tagging (007 - US6)
app.include_router(metrics.router, tags=["metrics"])  # Observability metrics (007 - Phase 10)
app.include_router(teaching.router, tags=["teaching"])  # Phase III US1: Teacher Agent
app.include_router(coaching.router, tags=["coaching"])  # Phase III US2: Coach Agent
app.include_router(marking.router, tags=["marking"])  # Phase III US4: Marker Agent
app.include_router(feedback.router, tags=["feedback"])  # Phase III US5: Reviewer Agent
app.include_router(planning.router, tags=["planning"])  # Phase III US6: Planner Agent

# Phase 6 (US4): app.include_router(students.router, prefix="/api", tags=["students"])
