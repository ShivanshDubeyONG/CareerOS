from fastapi import FastAPI

from app.api.routers.resume import router as resume_router

app = FastAPI(
    title="CareerOS API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "CareerOS API is running 🚀"}


app.include_router(resume_router)