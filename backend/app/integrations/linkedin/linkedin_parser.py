import re

import pymupdf

from app.schemas.linkedin_schema import (
    LinkedInAward,
    LinkedInCertification,
    LinkedInEducation,
    LinkedInExperience,
    LinkedInLanguage,
    LinkedInOrganization,
    LinkedInProfile,
    LinkedInProject,
    LinkedInPublication,
    LinkedInVolunteerExperience,
)


class LinkedInParser:
    """
    Converts provider-specific LinkedIn data into
    CareerOS's canonical LinkedInProfile schema.

    Supported inputs:
    - LinkedIn PDF/export
    - ScrapingDog LinkedIn Person API response
    """

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

    # ==================================================
    # COMMON HELPERS
    # ==================================================

    @staticmethod
    def _clean(value):
        if value is None:
            return None

        if isinstance(value, str):
            value = re.sub(
                r"\s+",
                " ",
                value,
            ).strip()

            return value or None

        return value

    @staticmethod
    def _get_string(
        data: dict,
        *keys: str,
    ) -> str | None:

        for key in keys:

            value = data.get(key)

            if value is None:
                continue

            if isinstance(value, str):

                value = re.sub(
                    r"\s+",
                    " ",
                    value,
                ).strip()

                if value:
                    return value

            elif isinstance(value, int):

                return str(value)

        return None

    @staticmethod
    def _get_int(
        data: dict,
        *keys: str,
    ) -> int | None:

        for key in keys:

            value = data.get(key)

            if isinstance(value, int):
                return value

            if isinstance(value, str):

                digits = re.sub(
                    r"[^\d]",
                    "",
                    value,
                )

                if digits:
                    return int(digits)

        return None

    @staticmethod
    def _get_list(
        data: dict,
        *keys: str,
    ) -> list:

        for key in keys:

            value = data.get(key)

            if isinstance(value, list):
                return value

        return []

    # ==================================================
    # PDF / EXPORT PARSING
    # ==================================================

    @staticmethod
    def extract_text(
        pdf_bytes: bytes,
    ) -> str:

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

            return "\n".join(
                pages
            ).strip()

        finally:
            document.close()

    @staticmethod
    def _clean_lines(
        text: str,
    ) -> list[str]:

        lines = []

        for line in text.splitlines():

            line = re.sub(
                r"\s+",
                " ",
                line,
            ).strip()

            if line:
                lines.append(line)

        return lines

    @classmethod
    def _split_sections(
        cls,
        lines: list[str],
    ) -> dict[str, list[str]]:

        sections = {
            "header": []
        }

        current = "header"

        for line in lines:

            normalized = (
                line.lower().strip()
            )

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

        return (
            name,
            headline,
            location,
        )

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
                        for part
                        in date_line.split("·")
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
                "Could not extract text from LinkedIn PDF."
            )

        lines = self._clean_lines(
            text
        )

        sections = self._split_sections(
            lines
        )

        (
            name,
            headline,
            location,
        ) = self._parse_header(
            sections.get(
                "header",
                [],
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
            certifications=self._parse_certifications(
                sections.get(
                    "certifications",
                    sections.get(
                        "licenses & certifications",
                        [],
                    ),
                )
            ),
            projects=self._parse_projects(
                sections.get(
                    "projects",
                    [],
                )
            ),
        )

    # ==================================================
    # API EXPERIENCE
    # ==================================================

    @classmethod
    def _parse_api_experience(
        cls,
        data: dict,
    ) -> list[LinkedInExperience]:

        experiences = []

        for item in cls._get_list(
            data,
            "experience",
            "experiences",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            title = cls._get_string(
                item,
                "position",
                "title",
            )

            company = cls._get_string(
                item,
                "company_name",
                "company",
            )

            if not title and not company:
                continue

            experiences.append(
                LinkedInExperience(
                    company=(
                        company
                        or "Unknown"
                    ),
                    title=(
                        title
                        or "Unknown"
                    ),
                    start_date=cls._get_string(
                        item,
                        "starts_at",
                        "start_date",
                    ),
                    end_date=cls._get_string(
                        item,
                        "ends_at",
                        "end_date",
                    ),
                    description=cls._get_string(
                        item,
                        "summary",
                        "description",
                    ),
                    employment_type=cls._get_string(
                        item,
                        "employment_type",
                    ),
                    location=cls._get_string(
                        item,
                        "location",
                    ),
                )
            )

        return experiences

    # ==================================================
    # API EDUCATION
    # ==================================================

    @classmethod
    def _parse_api_education(
        cls,
        data: dict,
    ) -> list[LinkedInEducation]:

        education = []

        for item in cls._get_list(
            data,
            "education",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            institution = cls._get_string(
                item,
                "college_name",
                "school",
                "institution",
            )

            if not institution:
                continue

            education.append(
                LinkedInEducation(
                    institution=institution,
                    degree=cls._get_string(
                        item,
                        "degree",
                    ),
                    field_of_study=cls._get_string(
                        item,
                        "field_of_study",
                    ),
                    start_date=cls._get_string(
                        item,
                        "starts_at",
                        "start_date",
                    ),
                    end_date=cls._get_string(
                        item,
                        "ends_at",
                        "end_date",
                    ),
                    description=cls._get_string(
                        item,
                        "description",
                    ),
                )
            )

        return education

    # ==================================================
    # API CERTIFICATIONS
    # ==================================================

    @classmethod
    def _parse_api_certifications(
        cls,
        data: dict,
    ) -> list[LinkedInCertification]:

        certifications = []

        for item in cls._get_list(
            data,
            "certification",
            "certifications",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = cls._get_string(
                item,
                "certification",
                "name",
                "title",
            )

            if not name:
                continue

            certifications.append(
                LinkedInCertification(
                    name=name,
                    issuer=cls._get_string(
                        item,
                        "company_name",
                        "authority",
                        "issuer",
                        "organization",
                    ),
                    issue_date=cls._get_string(
                        item,
                        "issue_date",
                    ),
                    expiration_date=cls._get_string(
                        item,
                        "expiration_date",
                        "expires_at",
                    ),
                    credential_id=cls._get_string(
                        item,
                        "credential_id",
                    ),
                    credential_url=cls._get_string(
                        item,
                        "credential_url",
                    ),
                )
            )

        return certifications

    # ==================================================
    # API PROJECTS
    # ==================================================

    @classmethod
    def _parse_api_projects(
        cls,
        data: dict,
    ) -> list[LinkedInProject]:

        projects = []

        for item in cls._get_list(
            data,
            "projects",
            "project",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = cls._get_string(
                item,
                "name",
                "title",
                "project_name",
            )

            if not name:
                continue

            projects.append(
                LinkedInProject(
                    name=name,
                    description=cls._get_string(
                        item,
                        "description",
                        "summary",
                    ),
                    url=cls._get_string(
                        item,
                        "url",
                        "project_url",
                    ),
                )
            )

        return projects

    # ==================================================
    # API SKILLS
    # ==================================================

    @classmethod
    def _parse_api_skills(
        cls,
        data: dict,
    ) -> list[str]:

        raw_skills = data.get(
            "skills"
        )

        if not isinstance(
            raw_skills,
            list,
        ):
            return []

        skills = []

        for item in raw_skills:

            if isinstance(
                item,
                str,
            ):

                value = cls._clean(
                    item
                )

                if value:
                    skills.append(value)

            elif isinstance(
                item,
                dict,
            ):

                value = cls._get_string(
                    item,
                    "name",
                    "skill",
                    "title",
                )

                if value:
                    skills.append(value)

        return list(
            dict.fromkeys(skills)
        )

    # ==================================================
    # API LANGUAGES
    # ==================================================

    @classmethod
    def _parse_api_languages(
        cls,
        data: dict,
    ) -> list[LinkedInLanguage]:

        languages = []

        for item in cls._get_list(
            data,
            "languages",
            "language",
        ):

            if isinstance(
                item,
                str,
            ):

                name = cls._clean(item)
                proficiency = None

            elif isinstance(
                item,
                dict,
            ):

                name = cls._get_string(
                    item,
                    "name",
                    "language",
                )

                proficiency = cls._get_string(
                    item,
                    "proficiency",
                    "level",
                )

            else:
                continue

            if name:

                languages.append(
                    LinkedInLanguage(
                        name=name,
                        proficiency=proficiency,
                    )
                )

        return languages

    # ==================================================
    # API ORGANIZATIONS
    # ==================================================

    @classmethod
    def _parse_api_organizations(
        cls,
        data: dict,
    ) -> list[LinkedInOrganization]:

        organizations = []

        for item in cls._get_list(
            data,
            "organizations",
            "organization",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = cls._get_string(
                item,
                "name",
                "organization",
            )

            if not name:
                continue

            organizations.append(
                LinkedInOrganization(
                    name=name,
                    role=cls._get_string(
                        item,
                        "role",
                        "position",
                        "title",
                    ),
                    description=cls._get_string(
                        item,
                        "description",
                        "summary",
                    ),
                )
            )

        return organizations

    # ==================================================
    # API AWARDS
    # ==================================================

    @classmethod
    def _parse_api_awards(
        cls,
        data: dict,
    ) -> list[LinkedInAward]:

        awards = []

        for item in cls._get_list(
            data,
            "awards",
            "award",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = cls._get_string(
                item,
                "name",
                "title",
                "award",
            )

            if not name:
                continue

            awards.append(
                LinkedInAward(
                    name=name,
                    issuer=cls._get_string(
                        item,
                        "issuer",
                        "organization",
                        "company_name",
                    ),
                    date=cls._get_string(
                        item,
                        "date",
                        "issued_at",
                    ),
                    description=cls._get_string(
                        item,
                        "description",
                    ),
                )
            )

        return awards

    # ==================================================
    # API PUBLICATIONS
    # ==================================================

    @classmethod
    def _parse_api_publications(
        cls,
        data: dict,
    ) -> list[LinkedInPublication]:

        publications = []

        for item in cls._get_list(
            data,
            "publications",
            "publication",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            title = cls._get_string(
                item,
                "title",
                "name",
            )

            if not title:
                continue

            publications.append(
                LinkedInPublication(
                    title=title,
                    publisher=cls._get_string(
                        item,
                        "publisher",
                        "company_name",
                    ),
                    date=cls._get_string(
                        item,
                        "date",
                        "published_at",
                    ),
                    url=cls._get_string(
                        item,
                        "url",
                        "publication_url",
                    ),
                    description=cls._get_string(
                        item,
                        "description",
                    ),
                )
            )

        return publications

    # ==================================================
    # API VOLUNTEERING
    # ==================================================

    @classmethod
    def _parse_api_volunteering(
        cls,
        data: dict,
    ) -> list[LinkedInVolunteerExperience]:

        volunteering = []

        for item in cls._get_list(
            data,
            "volunteering",
            "volunteer_experience",
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            organization = cls._get_string(
                item,
                "organization",
                "organization_name",
                "company_name",
            )

            if not organization:
                continue

            volunteering.append(
                LinkedInVolunteerExperience(
                    organization=organization,
                    role=cls._get_string(
                        item,
                        "role",
                        "position",
                        "title",
                    ),
                    cause=cls._get_string(
                        item,
                        "cause",
                    ),
                    description=cls._get_string(
                        item,
                        "description",
                        "summary",
                    ),
                    start_date=cls._get_string(
                        item,
                        "starts_at",
                        "start_date",
                    ),
                    end_date=cls._get_string(
                        item,
                        "ends_at",
                        "end_date",
                    ),
                )
            )

        return volunteering

    # ==================================================
    # API RESPONSE → CANONICAL PROFILE
    # ==================================================

    @classmethod
    def parse_api_response(
        cls,
        data: dict,
    ) -> LinkedInProfile:

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "LinkedIn API response must be a dictionary."
            )

        return LinkedInProfile(
            name=cls._get_string(
                data,
                "fullName",
                "full_name",
                "name",
            ),
            headline=cls._get_string(
                data,
                "headline",
            ),
            location=cls._get_string(
                data,
                "location",
            ),
            about=cls._get_string(
                data,
                "about",
                "summary",
            ),
            profile_url=cls._get_string(
                data,
                "profile_url",
                "linkedin_url",
                "url",
            ),
            public_identifier=cls._get_string(
                data,
                "public_identifier",
            ),
            followers=cls._get_int(
                data,
                "followers",
            ),
            connections=cls._get_int(
                data,
                "connections",
            ),
            experiences=cls._parse_api_experience(
                data
            ),
            education=cls._parse_api_education(
                data
            ),
            skills=cls._parse_api_skills(
                data
            ),
            certifications=cls._parse_api_certifications(
                data
            ),
            projects=cls._parse_api_projects(
                data
            ),
            languages=cls._parse_api_languages(
                data
            ),
            organizations=cls._parse_api_organizations(
                data
            ),
            awards=cls._parse_api_awards(
                data
            ),
            publications=cls._parse_api_publications(
                data
            ),
            volunteering=cls._parse_api_volunteering(
                data
            ),
            links=[],
        )


linkedin_parser = LinkedInParser()