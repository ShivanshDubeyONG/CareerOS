from fastapi import HTTPException, UploadFile

from app.extractors.resume_extractor import resume_extractor
from app.parsers.resume_parser import resume_parser
from app.repositories.resume_repository import resume_repository
from app.schemas.resume_schema import (
    ResumeAnalysisResponse,
    ResumeUploadResponse,
)
from app.utils.file_utils import (
    generate_unique_filename,
    get_file_path,
    is_allowed_file,
    save_file,
)


class ResumeService:

    async def upload_resume(self, file: UploadFile) -> ResumeUploadResponse:

        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed.",
            )

        unique_filename = generate_unique_filename(file.filename)

        await save_file(file, unique_filename)

        resume_id = unique_filename.split(".")[0]

        resume_repository.save(
            resume_id=resume_id,
            filename=unique_filename,
            original_filename=file.filename,
        )

        return ResumeUploadResponse(
            message="Resume uploaded successfully",
            file_id=resume_id,
            filename=unique_filename,
            original_filename=file.filename,
        )

    def get_resume(self, resume_id: str):

        resume = resume_repository.get(resume_id)

        if resume is None:
            raise HTTPException(
                status_code=404,
                detail="Resume not found.",
            )

        return resume

    def analyze_resume(self, resume_id: str) -> ResumeAnalysisResponse:

        resume = resume_repository.get(resume_id)

        if resume is None:
            raise HTTPException(
                status_code=404,
                detail="Resume not found.",
            )

        filename = resume["filename"]

        file_path = get_file_path(filename)

        extracted_text = resume_parser.extract_text(file_path)

        resume_data = resume_extractor.extract(extracted_text)

        return ResumeAnalysisResponse(
            file_id=resume_id,
            text=extracted_text,
            resume=resume_data,
        )


resume_service = ResumeService()