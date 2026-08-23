from fastapi import FastAPI

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


@app.get("/")
def root():

    return {
        "message": (
            "CareerOS API is running 🚀"
        )
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