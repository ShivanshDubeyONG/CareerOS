from app.integrations.linkedin.apify_client import (
    apify_linkedin_client,
)
from app.integrations.linkedin.apify_adapter import (
    apify_linkedin_adapter,
)


LINKEDIN_URL = (
    "https://www.linkedin.com/in/"
    "shivansh-dubey-69a825310/"
)


def main():

    print("=" * 70)
    print("CAREEROS LINKEDIN ACQUISITION PIPELINE")
    print("=" * 70)

    print("\n1. Acquiring LinkedIn profile...")

    raw_profile = (
        apify_linkedin_client.fetch_profile(
            LINKEDIN_URL
        )
    )

    print(
        "Acquisition successful."
    )

    print("\n2. Normalizing provider data...")

    profile, metadata = (
        apify_linkedin_adapter.parse(
            raw_profile
        )
    )

    print(
        "Canonical parsing successful."
    )

    print("\n3. CANONICAL PROFILE")
    print("-" * 70)

    print(
        f"Name: {profile.name}"
    )

    print(
        f"Headline: {profile.headline}"
    )

    print(
        f"Location: {profile.location}"
    )

    print(
        f"About length: "
        f"{len(profile.about or '')}"
    )

    print(
        f"Profile URL: "
        f"{profile.profile_url}"
    )

    print(
        f"Followers: "
        f"{profile.followers}"
    )

    print(
        f"Connections: "
        f"{profile.connections}"
    )

    print(
        f"Experience: "
        f"{len(profile.experiences)}"
    )

    print(
        f"Education: "
        f"{len(profile.education)}"
    )

    print(
        f"Skills: "
        f"{len(profile.skills)}"
    )

    print(
        f"Certifications: "
        f"{len(profile.certifications)}"
    )

    print(
        f"Projects: "
        f"{len(profile.projects)}"
    )

    print(
        f"Featured links: "
        f"{len(profile.links)}"
    )

    print("\nSKILLS")
    print("-" * 70)

    for skill in profile.skills:
        print(
            f"- {skill}"
        )

    print("\nEDUCATION")
    print("-" * 70)

    for education in profile.education:

        print(
            f"- {education.institution}"
        )

        print(
            f"  Degree: "
            f"{education.degree}"
        )

        print(
            f"  Field: "
            f"{education.field_of_study}"
        )

        print(
            f"  Start: "
            f"{education.start_date}"
        )

        print(
            f"  End: "
            f"{education.end_date}"
        )

        print(
            f"  Description: "
            f"{education.description}"
        )

    print("\nCERTIFICATIONS")
    print("-" * 70)

    for certification in (
        profile.certifications
    ):

        print(
            f"- {certification.name}"
        )

        print(
            f"  Issuer: "
            f"{certification.issuer}"
        )

        print(
            f"  Credential: "
            f"{certification.credential_url}"
        )

    print("\nFEATURED LINKS")
    print("-" * 70)

    for link in profile.links:
        print(
            f"- {link}"
        )

    print("\n4. ACQUISITION AVAILABILITY")
    print("-" * 70)

    print(
        f"Provider: "
        f"{metadata.provider}"
    )

    for (
        section,
        availability,
    ) in metadata.sections.items():

        state = (
            "AVAILABLE"
            if availability.available
            else "UNAVAILABLE"
        )

        print(
            f"- {section}: "
            f"{state} "
            f"({availability.item_count} items)"
        )

        if availability.note:
            print(
                f"  {availability.note}"
            )

    print("\n" + "=" * 70)
    print(
        "LINKEDIN ACQUISITION PIPELINE COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()