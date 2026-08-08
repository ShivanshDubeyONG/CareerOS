import re

from app.extractors.section_extractor import section_extractor
from app.extractors.skill_extractor import skill_extractor
from app.schemas.resume_schema import ResumeData


class ResumeExtractor:

    @staticmethod
    def extract(text: str) -> ResumeData:

        sections = section_extractor.extract(text)

        return ResumeData(
            name=ResumeExtractor.extract_name(text),
            email=ResumeExtractor.extract_email(text),
            phone=ResumeExtractor.extract_phone(text),

            skills=skill_extractor.extract(
                sections["skills"] or text
            ),

            education=sections["education"],
            experience=sections["experience"],
            projects=sections["projects"],
            interests=sections["interests"],
        )

    @staticmethod
    def extract_email(text: str):

        match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text,
        )

        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str):

        match = re.search(
            r"(?:\+91[- ]?)?[6-9]\d{9}",
            text,
        )

        return match.group(0) if match else None

    @staticmethod
    def extract_name(text: str):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return None

        first_line = lines[0]

        if len(first_line.split()) <= 4:
            return first_line

        return None


resume_extractor = ResumeExtractor()