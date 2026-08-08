from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    original_filename: str


class ResumeLinks(BaseModel):
    github: Optional[str] = None
    github_projects: List[str] = Field(default_factory=list)

    linkedin: Optional[str] = None
    leetcode: Optional[str] = None
    kaggle: Optional[str] = None
    huggingface: Optional[str] = None
    medium: Optional[str] = None

    portfolio: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    skills: List[str] = Field(default_factory=list)

    education: str = ""
    experience: str = ""
    projects: str = ""
    interests: str = ""

    links: ResumeLinks = Field(default_factory=ResumeLinks)


class ResumeAnalysisResponse(BaseModel):
    file_id: str
    text: str
    resume: ResumeData