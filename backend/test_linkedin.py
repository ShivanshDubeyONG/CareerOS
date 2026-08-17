from pathlib import Path

from app.integrations.linkedin.linkedin_parser import linkedin_parser
from app.services.linkedin.linkedin_normalizer import linkedin_normalizer
from app.services.linkedin.linkedin_service import linkedin_service


# Change this to wherever you keep the LinkedIn export.
LINKEDIN_EXPORT_DIR = Path("data/linkedin")


def main():
    print("=" * 50)
    print("LINKEDIN INTELLIGENCE")
    print("=" * 50)

    print(f"Export directory: {LINKEDIN_EXPORT_DIR}")

    if not LINKEDIN_EXPORT_DIR.exists():
        print()
        print("ERROR: LinkedIn export directory not found.")
        print()
        print("Create:")
        print("  data/linkedin/")
        print()
        print("and put your LinkedIn CSV export files there.")
        return

    # ---------------------------------------------
    # PARSE
    # ---------------------------------------------

    profile = linkedin_parser.parse(
        LINKEDIN_EXPORT_DIR
    )

    print("\nPROFILE")
    print(f"Name: {profile.name}")
    print(f"Headline: {profile.headline}")
    print(f"Location: {profile.location}")

    # ---------------------------------------------
    # NORMALIZE
    # ---------------------------------------------

    profile = linkedin_normalizer.normalize_profile(
        profile
    )

    print("\nEXPERIENCE")

    for experience in profile.experiences:

        print(
            f"  {experience.title} "
            f"@ {experience.company}"
        )

        if experience.start_date or experience.end_date:
            print(
                f"    {experience.start_date or '?'}"
                f" → "
                f"{experience.end_date or 'Present'}"
            )

    # ---------------------------------------------
    # SKILLS
    # ---------------------------------------------

    print("\nSKILLS")

    if profile.skills:
        for skill in profile.skills:
            print(f"  - {skill}")
    else:
        print("  None found")

    # ---------------------------------------------
    # EDUCATION
    # ---------------------------------------------

    print("\nEDUCATION")

    for education in profile.education:

        print(
            f"  {education.institution}"
        )

        if education.degree:
            print(
                f"    Degree: {education.degree}"
            )

        if education.field_of_study:
            print(
                f"    Field: {education.field_of_study}"
            )

    # ---------------------------------------------
    # PROJECTS
    # ---------------------------------------------

    print("\nPROJECTS")

    if profile.projects:

        for project in profile.projects:

            print(
                f"  - {project.name}"
            )

            if project.url:
                print(
                    f"    URL: {project.url}"
                )

    else:
        print("  None found")

    # ---------------------------------------------
    # CERTIFICATIONS
    # ---------------------------------------------

    print("\nCERTIFICATIONS")

    if profile.certifications:

        for certification in (
            profile.certifications
        ):

            print(
                f"  - {certification.name}"
            )

            if certification.issuer:
                print(
                    f"    Issuer: "
                    f"{certification.issuer}"
                )

    else:
        print("  None found")

    # ---------------------------------------------
    # ANALYSIS
    # ---------------------------------------------

    analysis = linkedin_service.analyze(
        profile
    )

    print("\n" + "=" * 50)
    print("CAREER ANALYSIS")
    print("=" * 50)

    print(
        f"Current role: "
        f"{analysis.current_title or 'Not found'}"
    )

    print(
        f"Current company: "
        f"{analysis.current_company or 'Not found'}"
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

    print("\nCareer domains:")

    for domain in analysis.career_domains:
        print(f"  + {domain}")

    print("\nCareer signals:")

    for signal in analysis.signals:
        print(f"  - {signal}")

    print("\nEvidence signals:")

    for signal in analysis.career_signals:

        print(
            f"  {signal.signal}: "
            f"{signal.evidence}"
        )

    print("\nClaimed skills:")

    for skill in analysis.skill_evidence:
        print(
            f"  {skill.skill}: "
            f"claimed via {', '.join(skill.sources)}"
        )

    print("\n" + "=" * 50)
    print("LINKEDIN ANALYSIS COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()