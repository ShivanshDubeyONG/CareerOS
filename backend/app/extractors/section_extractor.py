import re


class SectionExtractor:

    SECTION_ALIASES = {
        "education": [
            "education",
            "educations",
            "academic background",
            "academic qualifications",
            "qualifications",
            "academics",
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "work history",
            "internship experience",
            "internships",
        ],

        "projects": [
            "projects",
            "project",
            "personal projects",
            "academic projects",
            "key projects",
        ],

        "skills": [
            "skills",
            "technical skills",
            "technical expertise",
            "core skills",
        ],

        "interests": [
            "interests",
            "hobbies",
            "activities",
        ],

        "certifications": [
            "certifications",
            "certificates",
            "licenses",
        ],
    }

    @classmethod
    def extract(cls, text: str) -> dict:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        sections = {
            "education": [],
            "experience": [],
            "projects": [],
            "skills": [],
            "interests": [],
            "certifications": [],
        }

        current_section = None

        for line in lines:

            normalized = cls.normalize_heading(line)

            detected_section = cls.detect_section(normalized)

            if detected_section:
                current_section = detected_section
                continue

            if current_section:
                sections[current_section].append(line)

        return {
            key: "\n".join(value).strip()
            for key, value in sections.items()
        }

    @staticmethod
    def normalize_heading(line: str) -> str:

        line = line.lower().strip()

        line = re.sub(r"[^a-zA-Z\s]", "", line)
        line = re.sub(r"\s+", " ", line)

        return line.strip()

    @classmethod
    def detect_section(cls, line: str):

        for section, aliases in cls.SECTION_ALIASES.items():

            if line in aliases:
                return section

        return None


section_extractor = SectionExtractor()