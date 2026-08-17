import re

import pymupdf

from app.schemas.linkedin_schema import (
    LinkedInCertification,
    LinkedInEducation,
    LinkedInExperience,
    LinkedInProfile,
    LinkedInProject,
)


class LinkedInParser:

    SECTION_NAMES = {
        "about",
        "experience",
        "education",
        "skills",
        "certifications",
        "projects",
        "licenses & certifications",
        "volunteer experience",
        "languages",
    }

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> str:
        document = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        try:
            pages = []

            for page in document:
                text = page.get_text("text")

                if text:
                    pages.append(text)

            return "\n".join(pages).strip()

        finally:
            document.close()

    @staticmethod
    def _clean_lines(text: str) -> list[str]:
        lines = []

        for line in text.splitlines():
            line = re.sub(r"\s+", " ", line).strip()

            if line:
                lines.append(line)

        return lines

    @classmethod
    def _split_sections(
        cls,
        lines: list[str],
    ) -> dict[str, list[str]]:

        sections: dict[str, list[str]] = {}
        current = "header"

        sections[current] = []

        for line in lines:

            normalized = line.lower().strip()

            if normalized in cls.SECTION_NAMES:
                current = normalized
                sections.setdefault(
                    current,
                    [],
                )
                continue

            sections.setdefault(
                current,
                [],
            ).append(line)

        return sections

    @staticmethod
    def _parse_header(
        lines: list[str],
    ) -> tuple[
        str | None,
        str | None,
        str | None,
    ]:

        if not lines:
            return None, None, None

        name = lines[0]

        headline = (
            lines[1]
            if len(lines) > 1
            else None
        )

        location = None

        for line in lines[1:5]:
            lower = line.lower()

            if any(
                marker in lower
                for marker in (
                    "india",
                    "bengaluru",
                    "bangalore",
                    "mumbai",
                    "delhi",
                    "hyderabad",
                    "pune",
                    "chennai",
                )
            ):
                location = line
                break

        return name, headline, location

    @staticmethod
    def _parse_skills(
        lines: list[str],
    ) -> list[str]:

        skills = []

        for line in lines:

            if line.lower() in {
                "endorsements",
                "endorsement",
            }:
                continue

            if (
                len(line) <= 80
                and not line.isdigit()
            ):
                skills.append(line)

        return list(
            dict.fromkeys(skills)
        )

    @staticmethod
    def _parse_experience(
        lines: list[str],
    ) -> list[LinkedInExperience]:

        experiences = []

        i = 0

        while i < len(lines):

            title = lines[i]

            company = (
                lines[i + 1]
                if i + 1 < len(lines)
                else "Unknown"
            )

            start_date = None
            end_date = None

            if i + 2 < len(lines):

                date_line = lines[i + 2]

                if any(
                    month in date_line.lower()
                    for month in (
                        "jan",
                        "feb",
                        "mar",
                        "apr",
                        "may",
                        "jun",
                        "jul",
                        "aug",
                        "sep",
                        "oct",
                        "nov",
                        "dec",
                    )
                ):
                    parts = [
                        part.strip()
                        for part in date_line.split("·")
                    ]

                    if parts:
                        dates = parts[0]

                        if " - " in dates:
                            start_date, end_date = (
                                dates.split(
                                    " - ",
                                    1,
                                )
                            )

                        else:
                            start_date = dates

            if title and company:

                experiences.append(
                    LinkedInExperience(
                        company=company,
                        title=title,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

            i += 3

        return experiences

    @staticmethod
    def _parse_education(
        lines: list[str],
    ) -> list[LinkedInEducation]:

        education = []

        i = 0

        while i < len(lines):

            institution = lines[i]

            degree = (
                lines[i + 1]
                if i + 1 < len(lines)
                else None
            )

            field = (
                lines[i + 2]
                if i + 2 < len(lines)
                else None
            )

            if institution:

                education.append(
                    LinkedInEducation(
                        institution=institution,
                        degree=degree,
                        field_of_study=field,
                    )
                )

            i += 3

        return education

    @staticmethod
    def _parse_projects(
        lines: list[str],
    ) -> list[LinkedInProject]:

        projects = []

        i = 0

        while i < len(lines):

            name = lines[i]

            description = (
                lines[i + 1]
                if i + 1 < len(lines)
                else None
            )

            if name:

                projects.append(
                    LinkedInProject(
                        name=name,
                        description=description,
                    )
                )

            i += 2

        return projects

    @staticmethod
    def _parse_certifications(
        lines: list[str],
    ) -> list[LinkedInCertification]:

        certifications = []

        i = 0

        while i < len(lines):

            name = lines[i]

            issuer = (
                lines[i + 1]
                if i + 1 < len(lines)
                else None
            )

            if name:

                certifications.append(
                    LinkedInCertification(
                        name=name,
                        issuer=issuer,
                    )
                )

            i += 2

        return certifications

    def parse(
        self,
        pdf_bytes: bytes,
    ) -> LinkedInProfile:

        text = self.extract_text(
            pdf_bytes
        )

        if not text:
            raise ValueError(
                "Could not extract text from "
                "LinkedIn PDF."
            )

        lines = self._clean_lines(text)

        sections = self._split_sections(
            lines
        )

        name, headline, location = (
            self._parse_header(
                sections.get(
                    "header",
                    [],
                )
            )
        )

        return LinkedInProfile(
            name=name,
            headline=headline,
            location=location,
            experiences=self._parse_experience(
                sections.get(
                    "experience",
                    [],
                )
            ),
            education=self._parse_education(
                sections.get(
                    "education",
                    [],
                )
            ),
            skills=self._parse_skills(
                sections.get(
                    "skills",
                    [],
                )
            ),
            certifications=(
                self._parse_certifications(
                    sections.get(
                        "certifications",
                        sections.get(
                            "licenses & certifications",
                            [],
                        ),
                    )
                )
            ),
            projects=self._parse_projects(
                sections.get(
                    "projects",
                    [],
                )
            ),
        )


linkedin_parser = LinkedInParser()