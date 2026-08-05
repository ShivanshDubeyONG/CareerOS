from typing import List

from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    original_filename: str


class ResumeData(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    projects: List[str] = []


class ResumeAnalysisResponse(BaseModel):
    file_id: str
    text: str
    resume: ResumeData