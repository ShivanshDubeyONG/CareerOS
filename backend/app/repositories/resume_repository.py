from typing import Dict


class ResumeRepository:

    def __init__(self):
        self.resumes: Dict[str, dict] = {}

    def save(self, resume_id: str, filename: str, original_filename: str):

        self.resumes[resume_id] = {
            "filename": filename,
            "original_filename": original_filename,
        }

    def get(self, resume_id: str):

        return self.resumes.get(resume_id)


resume_repository = ResumeRepository()