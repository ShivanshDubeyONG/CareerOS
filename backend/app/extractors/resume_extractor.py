import re

from app.schemas.resume_schema import ResumeData


class ResumeExtractor:

    @staticmethod
    def extract(text: str) -> ResumeData:

        return ResumeData(
            name=ResumeExtractor.extract_name(text),
            email=ResumeExtractor.extract_email(text),
            phone=ResumeExtractor.extract_phone(text),
            skills=ResumeExtractor.extract_skills(text),
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
            r"(\+91[- ]?)?[6-9]\d{9}",
            text,
        )
        return match.group(0) if match else None

    @staticmethod
    def extract_name(text: str):

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if lines:
            first_line = lines[0]

            if len(first_line.split()) <= 4:
                return first_line

        return None

    @staticmethod
    def extract_skills(text: str):

        skill_database = [
            "Python",
            "Java",
            "C++",
            "SQL",
            "FastAPI",
            "Docker",
            "Git",
            "GitHub",
            "React",
            "TensorFlow",
            "PyTorch",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "Machine Learning",
            "Deep Learning",
        ]

        found = []

        lower_text = text.lower()

        for skill in skill_database:
            if skill.lower() in lower_text:
                found.append(skill)

        return sorted(set(found))


resume_extractor = ResumeExtractor()