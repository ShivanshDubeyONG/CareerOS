from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    original_filename: str