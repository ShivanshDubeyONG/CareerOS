from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.resume import (
    router as resume_router,
)

from app.api.routers.leetcode import (
    router as leetcode_router,
)

from app.api.routers.career import (
    router as career_router,
)


app = FastAPI(
    title="CareerOS API",
    version="1.0.0",
    description=(
        "AI-powered career intelligence "
        "and resume analysis platform."
    ),
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "CareerOS API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "careeros-api",
    }


app.include_router(
    resume_router
)

app.include_router(
    leetcode_router
)

app.include_router(
    career_router
)