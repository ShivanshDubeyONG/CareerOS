from fastapi import APIRouter, File, UploadFile

from app.schemas.resume_schema import (
    ResumeAnalysisResponse,
    ResumeUploadResponse,
)
from app.services.resume_service import resume_service

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.get("/")
def health():
    return {"message": "Resume endpoint is working!"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    return await resume_service.upload_resume(file)


@router.get("/{resume_id}")
def get_resume(resume_id: str):
    return resume_service.get_resume(resume_id)


@router.get("/{resume_id}/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume(resume_id: str):
    return resume_service.analyze_resume(resume_id)