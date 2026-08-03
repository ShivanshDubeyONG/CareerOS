from fastapi import HTTPException, UploadFile

from app.schemas.resume_schema import ResumeUploadResponse
from app.utils.file_utils import (
    generate_unique_filename,
    is_allowed_file,
    save_file,
)


class ResumeService:

    async def upload_resume(self, file: UploadFile) -> ResumeUploadResponse:

        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed."
            )

        unique_filename = generate_unique_filename(file.filename)

        await save_file(file, unique_filename)

        return ResumeUploadResponse(
            message="Resume uploaded successfully",
            file_id=unique_filename.split(".")[0],
            filename=unique_filename,
            original_filename=file.filename
        )


resume_service = ResumeService()