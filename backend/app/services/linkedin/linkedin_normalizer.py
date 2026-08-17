import re

from app.schemas.linkedin_schema import (
    LinkedInExperience,
    LinkedInProfile,
)


class LinkedInNormalizer:

    SKILL_ALIASES = {
        "python": "Python",
        "python3": "Python",
        "c++": "C++",
        "cpp": "C++",
        "java": "Java",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "react.js": "React",
        "reactjs": "React",
        "react js": "React",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "fast api": "FastAPI",
        "fastapi": "FastAPI",
        "spring boot": "Spring Boot",
        "scikit learn": "Scikit-learn",
        "scikit-learn": "Scikit-learn",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "artificial intelligence": "Artificial Intelligence",
        "ai": "Artificial Intelligence",
        "natural language processing": "NLP",
        "nlp": "NLP",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "aws": "AWS",
        "google cloud": "Google Cloud",
        "gcp": "Google Cloud",
        "git": "Git",
        "github": "GitHub",
    }

    DOMAIN_KEYWORDS = {
        "software_engineering": {
            "software engineer",
            "software developer",
            "backend engineer",
            "backend developer",
            "frontend engineer",
            "frontend developer",
            "full stack",
            "fullstack",
            "web developer",
            "application developer",
        },
        "machine_learning": {
            "machine learning",
            "ml engineer",
            "machine learning engineer",
            "machine learning intern",
            "deep learning",
            "artificial intelligence",
            "ai engineer",
            "ai developer",
        },
        "data_science": {
            "data scientist",
            "data science",
            "data analyst",
            "analytics",
            "business intelligence",
        },
        "devops_cloud": {
            "devops",
            "devops engineer",
            "site reliability",
            "sre",
            "cloud engineer",
            "platform engineer",
            "cloud",
        },
        "cybersecurity": {
            "cybersecurity",
            "security engineer",
            "security analyst",
            "information security",
        },
        "product": {
            "product manager",
            "product management",
            "product analyst",
        },
    }

    @classmethod
    def normalize_skill(
        cls,
        skill: str,
    ) -> str:

        cleaned = " ".join(
            skill.strip().split()
        )

        if not cleaned:
            return ""

        key = cleaned.lower()

        return cls.SKILL_ALIASES.get(
            key,
            cleaned,
        )

    @classmethod
    def normalize_skills(
        cls,
        skills: list[str],
    ) -> list[str]:

        normalized = []
        seen = set()

        for skill in skills:

            value = cls.normalize_skill(
                skill
            )

            if not value:
                continue

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)
            normalized.append(value)

        return sorted(
            normalized,
            key=str.lower,
        )

    @staticmethod
    def normalize_text(
        value: str | None,
    ) -> str | None:

        if not value:
            return None

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @classmethod
    def normalize_experience(
        cls,
        experiences: list[LinkedInExperience],
    ) -> list[LinkedInExperience]:

        normalized = []

        for experience in experiences:

            company = cls.normalize_text(
                experience.company
            )

            title = cls.normalize_text(
                experience.title
            )

            if not company and not title:
                continue

            normalized.append(
                LinkedInExperience(
                    company=(
                        company
                        or "Unknown"
                    ),
                    title=(
                        title
                        or "Unknown"
                    ),
                    start_date=(
                        cls.normalize_text(
                            experience.start_date
                        )
                    ),
                    end_date=(
                        cls.normalize_text(
                            experience.end_date
                        )
                    ),
                    description=(
                        cls.normalize_text(
                            experience.description
                        )
                    ),
                    employment_type=(
                        cls.normalize_text(
                            experience.employment_type
                        )
                    ),
                )
            )

        return normalized

    @classmethod
    def detect_career_domains(
        cls,
        profile: LinkedInProfile,
    ) -> list[str]:

        text_parts = []

        if profile.headline:
            text_parts.append(
                profile.headline
            )

        for experience in profile.experiences:

            text_parts.append(
                experience.title
            )

            if experience.description:
                text_parts.append(
                    experience.description
                )

        combined = " ".join(
            text_parts
        ).lower()

        domains = []

        for domain, keywords in (
            cls.DOMAIN_KEYWORDS.items()
        ):

            if any(
                keyword in combined
                for keyword in keywords
            ):
                domains.append(domain)

        return domains

    @classmethod
    def normalize_profile(
        cls,
        profile: LinkedInProfile,
    ) -> LinkedInProfile:

        return LinkedInProfile(
            name=cls.normalize_text(
                profile.name
            ),
            headline=cls.normalize_text(
                profile.headline
            ),
            location=cls.normalize_text(
                profile.location
            ),
            experiences=(
                cls.normalize_experience(
                    profile.experiences
                )
            ),
            education=profile.education,
            skills=cls.normalize_skills(
                profile.skills
            ),
            certifications=profile.certifications,
            projects=profile.projects,
            links=profile.links,
        )


linkedin_normalizer = LinkedInNormalizer()