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
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "react js": "React",
        "node": "Node.js",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "fast api": "FastAPI",
        "fastapi": "FastAPI",
        "spring boot": "Spring Boot",
        "scikit learn": "Scikit-learn",
        "scikit-learn": "Scikit-learn",
        "machine learning": "Machine Learning",
        "ml": "Machine Learning",
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
        "azure": "Azure",
        "git": "Git",
        "github": "GitHub",
        "rest api": "REST API",
        "rest apis": "REST API",
        "restful api": "REST API",
        "sql": "SQL",
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
            "software development",
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

    @staticmethod
    def normalize_text(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = re.sub(
            r"\s+",
            " ",
            str(value),
        ).strip()

        return value or None

    @classmethod
    def normalize_skill(
        cls,
        skill: str,
    ) -> str:

        cleaned = cls.normalize_text(skill)

        if not cleaned:
            return ""

        return cls.SKILL_ALIASES.get(
            cleaned.lower(),
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
                    company=company or "Unknown",
                    title=title or "Unknown",
                    start_date=cls.normalize_text(
                        experience.start_date
                    ),
                    end_date=cls.normalize_text(
                        experience.end_date
                    ),
                    description=cls.normalize_text(
                        experience.description
                    ),
                    employment_type=cls.normalize_text(
                        experience.employment_type
                    ),
                    location=cls.normalize_text(
                        experience.location
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

        for value in (
            profile.headline,
            profile.about,
        ):

            if value:
                text_parts.append(value)

        for experience in profile.experiences:

            if experience.title:
                text_parts.append(
                    experience.title
                )

            if experience.description:
                text_parts.append(
                    experience.description
                )

        for project in profile.projects:

            if project.name:
                text_parts.append(
                    project.name
                )

            if project.description:
                text_parts.append(
                    project.description
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

        return profile.model_copy(
            update={
                "name": cls.normalize_text(
                    profile.name
                ),
                "headline": cls.normalize_text(
                    profile.headline
                ),
                "location": cls.normalize_text(
                    profile.location
                ),
                "about": cls.normalize_text(
                    profile.about
                ),
                "experiences": cls.normalize_experience(
                    profile.experiences
                ),
                "skills": cls.normalize_skills(
                    profile.skills
                ),
            }
        )


linkedin_normalizer = LinkedInNormalizer()