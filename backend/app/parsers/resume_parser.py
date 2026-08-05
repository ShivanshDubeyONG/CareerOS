import fitz
from fastapi import HTTPException


class ResumeParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        try:
            document = fitz.open(file_path)

            text = ""

            for page in document:
                text += page.get_text()

            document.close()

            return text.strip()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume: {str(e)}"
            )


resume_parser = ResumeParser()