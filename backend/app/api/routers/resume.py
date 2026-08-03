from fastapi import APIRouter, File, UploadFile

from app.schemas.resume_schema import ResumeUploadResponse
from app.services.resume_service import resume_service

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.get("/")
def get_resume():
    return {"message": "Resume endpoint is working!"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    return await resume_service.upload_resume(file)