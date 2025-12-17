"""
Simple test endpoint to verify Vercel deployment works
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Vercel deployment working!", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Vercel handler
handler = app
