import os
import uuid

import fitz
from fastapi import HTTPException, UploadFile

from app.schemas.resume_schema import (
    ResumeAnalysisResponse,
    ResumeUploadResponse,
)
from app.services.resume_extraction_service import resume_extraction_service


class ResumeService:

    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_resume(
        self,
        file: UploadFile,
    ) -> ResumeUploadResponse:

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided.",
            )

        extension = os.path.splitext(file.filename)[1].lower()

        if extension not in [".pdf", ".docx"]:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed.",
            )

        file_id = str(uuid.uuid4())
        filename = f"{file_id}{extension}"

        file_path = os.path.join(
            self.upload_dir,
            filename,
        )

        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        return ResumeUploadResponse(
            message="Resume uploaded successfully",
            file_id=file_id,
            filename=filename,
            original_filename=file.filename,
        )

    def get_resume(self, resume_id: str):

        filename = resume_id

        if not filename.endswith((".pdf", ".docx")):
            pdf_path = os.path.join(
                self.upload_dir,
                f"{resume_id}.pdf",
            )

            docx_path = os.path.join(
                self.upload_dir,
                f"{resume_id}.docx",
            )

            if os.path.exists(pdf_path):
                filename = f"{resume_id}.pdf"

            elif os.path.exists(docx_path):
                filename = f"{resume_id}.docx"

            else:
                raise HTTPException(
                    status_code=404,
                    detail="Resume not found.",
                )

        file_path = os.path.join(
            self.upload_dir,
            filename,
        )

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Resume not found.",
            )

        extension = os.path.splitext(filename)[1].lower()

        if extension == ".pdf":

            doc = fitz.open(file_path)

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

        else:
            from docx import Document

            document = Document(file_path)

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )

        return {
            "file_id": resume_id.replace(".pdf", "").replace(".docx", ""),
            "filename": filename,
            "text": text,
        }

    def analyze_resume(
        self,
        resume_id: str,
    ) -> ResumeAnalysisResponse:

        filename = resume_id

        if not filename.endswith((".pdf", ".docx")):

            pdf_path = os.path.join(
                self.upload_dir,
                f"{resume_id}.pdf",
            )

            docx_path = os.path.join(
                self.upload_dir,
                f"{resume_id}.docx",
            )

            if os.path.exists(pdf_path):
                filename = f"{resume_id}.pdf"

            elif os.path.exists(docx_path):
                filename = f"{resume_id}.docx"

            else:
                raise HTTPException(
                    status_code=404,
                    detail="Resume not found.",
                )

        file_path = os.path.join(
            self.upload_dir,
            filename,
        )

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Resume not found.",
            )

        extracted_resume = resume_extraction_service.extract(
            file_path
        )

        resume = self.get_resume(resume_id)

        return ResumeAnalysisResponse(
            file_id=resume_id.replace(".pdf", "").replace(".docx", ""),
            text=resume["text"],
            resume=extracted_resume,
        )


resume_service = ResumeService()