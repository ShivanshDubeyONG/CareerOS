from app.integrations.linkedin.linkedin_parser import (
    linkedin_parser,
)
from app.schemas.linkedin_acquisition_schema import (
    LinkedInAcquisitionMetadata,
    LinkedInSectionAvailability,
)


class ApifyLinkedInAdapter:

    PROVIDER_NAME = (
        "apimaestro_linkedin_full_sections"
    )

    @staticmethod
    def _date_text(
        value,
    ) -> str | None:

        if value is None:
            return None

        if isinstance(value, str):
            return value.strip() or None

        if isinstance(value, dict):

            year = value.get("year")
            month = value.get("month")

            if year and month:
                return f"{month} {year}"

            if year:
                return str(year)

            return None

        return str(value)

    @staticmethod
    def _location_text(
        value,
    ) -> str | None:

        if isinstance(value, str):
            return value.strip() or None

        if isinstance(value, dict):

            full = value.get("full")

            if full:
                return full

            city = value.get("city")
            country = value.get("country")

            parts = [
                part
                for part in (
                    city,
                    country,
                )
                if part
            ]

            if parts:
                return ", ".join(parts)

        return None

    @staticmethod
    def _skills(
        skills,
    ) -> list[str]:

        if not isinstance(
            skills,
            list,
        ):
            return []

        result = []

        for skill in skills:

            if isinstance(
                skill,
                str,
            ):
                result.append(skill)

            elif isinstance(
                skill,
                dict,
            ):
                name = skill.get("name")

                if name:
                    result.append(name)

        return result

    @staticmethod
    def _education(
        education,
    ) -> list[dict]:

        if not isinstance(
            education,
            list,
        ):
            return []

        result = []

        for item in education:

            if not isinstance(
                item,
                dict,
            ):
                continue

            result.append(
                {
                    "school": item.get(
                        "school"
                    ),

                    "degree": (
                        item.get(
                            "degree_name"
                        )
                        or item.get(
                            "degree"
                        )
                    ),

                    "field_of_study": item.get(
                        "field_of_study"
                    ),

                    "start_date": (
                        ApifyLinkedInAdapter
                        ._date_text(
                            item.get(
                                "start_date"
                            )
                        )
                    ),

                    "end_date": (
                        ApifyLinkedInAdapter
                        ._date_text(
                            item.get(
                                "end_date"
                            )
                        )
                    ),

                    "description": (
                        item.get(
                            "description"
                        )
                        or item.get(
                            "grade"
                        )
                    ),
                }
            )

        return result

    @staticmethod
    def _certifications(
        certifications,
    ) -> list[dict]:

        if not isinstance(
            certifications,
            list,
        ):
            return []

        result = []

        for item in certifications:

            if not isinstance(
                item,
                dict,
            ):
                continue

            result.append(
                {
                    "name": item.get(
                        "name"
                    ),

                    "issuer": item.get(
                        "issuer"
                    ),

                    "issue_date": item.get(
                        "issued_date"
                    ),

                    "expiration_date": item.get(
                        "expiration_date"
                    ),

                    "credential_id": item.get(
                        "credential_id"
                    ),

                    "credential_url": item.get(
                        "credential_url"
                    ),
                }
            )

        return result

    @staticmethod
    def _featured_links(
        featured,
    ) -> list[str]:

        if not isinstance(
            featured,
            list,
        ):
            return []

        result = []

        for item in featured:

            if not isinstance(
                item,
                dict,
            ):
                continue

            url = item.get(
                "url"
            )

            if url:
                result.append(url)

        return result

    @classmethod
    def transform(
        cls,
        data: dict,
    ) -> tuple[
        dict,
        LinkedInAcquisitionMetadata,
    ]:

        basic_info = data.get(
            "basic_info",
            {},
        )

        if not isinstance(
            basic_info,
            dict,
        ):
            basic_info = {}

        fullname = (
            basic_info.get(
                "fullname"
            )
            or (
                f"{basic_info.get('first_name', '')} "
                f"{basic_info.get('last_name', '')}"
            ).strip()
        )

        sections = {}

        def record_section(
            name: str,
            key: str,
        ):
            present = (
                key in data
            )

            value = data.get(
                key
            )

            count = (
                len(value)
                if isinstance(
                    value,
                    list,
                )
                else 0
            )

            sections[name] = (
                LinkedInSectionAvailability(
                    available=present,
                    item_count=count,
                    source=cls.PROVIDER_NAME,
                    note=(
                        None
                        if present
                        else (
                            "Section was not "
                            "returned by the "
                            "acquisition provider."
                        )
                    ),
                )
            )

        record_section(
            "experience",
            "experience",
        )

        record_section(
            "education",
            "education",
        )

        record_section(
            "skills",
            "skills",
        )

        record_section(
            "certifications",
            "certifications",
        )

        record_section(
            "projects",
            "projects",
        )

        record_section(
            "languages",
            "languages",
        )

        record_section(
            "organizations",
            "organizations",
        )

        record_section(
            "awards",
            "awards",
        )

        record_section(
            "publications",
            "publications",
        )

        record_section(
            "volunteering",
            "volunteering",
        )

        record_section(
            "featured",
            "featured",
        )

        transformed = {
            "fullName": fullname,

            "headline": basic_info.get(
                "headline"
            ),

            "location": (
                cls._location_text(
                    basic_info.get(
                        "location"
                    )
                )
            ),

            "about": basic_info.get(
                "about"
            ),

            "profile_url": (
                basic_info.get(
                    "profile_url"
                )
                or data.get(
                    "profileUrl"
                )
            ),

            "public_identifier": (
                basic_info.get(
                    "public_identifier"
                )
            ),

            "followers": basic_info.get(
                "follower_count"
            ),

            "connections": basic_info.get(
                "connection_count"
            ),

            "experience": (
                data.get(
                    "experience",
                    []
                )
            ),

            "education": cls._education(
                data.get(
                    "education",
                    []
                )
            ),

            "skills": cls._skills(
                data.get(
                    "skills",
                    []
                )
            ),

            "certification": (
                cls._certifications(
                    data.get(
                        "certifications",
                        []
                    )
                )
            ),

            "projects": (
                data.get(
                    "projects",
                    []
                )
            ),

            "languages": (
                data.get(
                    "languages",
                    []
                )
            ),

            "organizations": (
                data.get(
                    "organizations",
                    []
                )
            ),

            "awards": (
                data.get(
                    "honorsAndAwards",
                    []
                )
            ),

            "publications": (
                data.get(
                    "publications",
                    []
                )
            ),

            "volunteering": (
                data.get(
                    "volunteering",
                    []
                )
            ),

            "links": cls._featured_links(
                data.get(
                    "featured",
                    []
                )
            ),
        }

        metadata = (
            LinkedInAcquisitionMetadata(
                provider=cls.PROVIDER_NAME,
                profile_url=(
                    transformed[
                        "profile_url"
                    ]
                    or ""
                ),
                sections=sections,
            )
        )

        return (
            transformed,
            metadata,
        )

    @classmethod
    def parse(
        cls,
        data: dict,
    ):
        transformed, metadata = (
            cls.transform(
                data
            )
        )

        profile = (
            linkedin_parser.parse_api_response(
                transformed
            )
        )

        return profile, metadata


apify_linkedin_adapter = (
    ApifyLinkedInAdapter()
)