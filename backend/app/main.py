from fastapi import FastAPI

from app.api.routers.resume import router as resume_router

app = FastAPI(
    title="AI Career Coach API",
    version="1.0.0"
)

app.include_router(resume_router)