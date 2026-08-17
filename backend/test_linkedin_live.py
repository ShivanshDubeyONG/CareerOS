from app.integrations.linkedin.linkedin_client import (
    linkedin_client,
)
from app.integrations.linkedin.linkedin_parser import (
    linkedin_parser,
)
from app.services.linkedin.linkedin_service import (
    linkedin_service,
)


LINKEDIN_URL = (
    "https://www.linkedin.com/in/"
    "shivansh-dubey-69a825310/"
)


def main():
    print("=" * 60)
    print("CAREEROS LINKEDIN LIVE PIPELINE")
    print("=" * 60)

    print("\n[1/4] Acquiring LinkedIn profile...")

    raw_profile = linkedin_client.fetch_profile(
        LINKEDIN_URL
    )

    print("Acquisition successful.")

    print("\nProvider fields:")
    print(
        list(raw_profile.keys())
    )

    print("\n[2/4] Parsing profile...")

    profile = (
        linkedin_parser.parse_api_response(
            raw_profile
        )
    )

    print("Parsing successful.")

    print("\n[3/4] Running intelligence...")

    analysis = linkedin_service.analyze(
        profile
    )

    print("Analysis successful.")

    print("\n[4/4] RESULTS")
    print("-" * 60)

    print(f"Name: {analysis.name}")
    print(f"Headline: {analysis.headline}")
    print(f"Location: {analysis.location}")
    print(f"About: {analysis.about}")

    print(
        f"Current title: "
        f"{analysis.current_title}"
    )

    print(
        f"Current company: "
        f"{analysis.current_company}"
    )

    print(
        f"Experience count: "
        f"{analysis.experience_count}"
    )

    print(
        f"Education count: "
        f"{analysis.education_count}"
    )

    print(
        f"Skill count: "
        f"{analysis.skill_count}"
    )

    print(
        f"Project count: "
        f"{analysis.project_count}"
    )

    print(
        f"Certification count: "
        f"{analysis.certification_count}"
    )

    print(
        f"Language count: "
        f"{analysis.language_count}"
    )

    print(
        f"Organization count: "
        f"{analysis.organization_count}"
    )

    print(
        f"Award count: "
        f"{analysis.award_count}"
    )

    print(
        f"Publication count: "
        f"{analysis.publication_count}"
    )

    print(
        f"Volunteering count: "
        f"{analysis.volunteering_count}"
    )

    print("\nClaimed skills:")

    for skill in analysis.claimed_skills:
        print(f"  - {skill}")

    print("\nCareer domains:")

    for domain in analysis.career_domains:
        print(f"  - {domain}")

    print("\nCareer signals:")

    for signal in analysis.career_signals:
        print(
            f"  - {signal.signal}: "
            f"{signal.evidence}"
        )

    print("\nProfile signals:")

    for signal in analysis.signals:
        print(f"  - {signal}")

    print("\n" + "=" * 60)
    print("LIVE LINKEDIN PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()