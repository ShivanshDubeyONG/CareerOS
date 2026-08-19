from pathlib import Path

from app.integrations.linkedin.linkedin_parser import linkedin_parser
from app.services.linkedin.linkedin_service import linkedin_service
from app.services.linkedin.linkedin_rater import linkedin_rater


PDF_PATH = Path(__file__).parent / "linkedin_profile.pdf"


def main():
    print("=" * 60)
    print("CAREEROS LINKEDIN PDF PIPELINE")
    print("=" * 60)

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"LinkedIn PDF not found: {PDF_PATH}"
        )

    print(f"\nReading LinkedIn PDF...")
    print(f"File: {PDF_PATH}")

    pdf_bytes = PDF_PATH.read_bytes()

    print(
        f"PDF loaded successfully "
        f"({len(pdf_bytes):,} bytes)."
    )

    print("\nParsing LinkedIn profile...")

    profile = linkedin_parser.parse(pdf_bytes)

    print("Parsing successful.")

    print("\nRunning LinkedIn analysis...")

    analysis = linkedin_service.analyze(profile)

    print("Analysis successful.")

    print("\n" + "=" * 60)
    print("LINKEDIN PROFILE")
    print("=" * 60)

    print(f"Name: {profile.name}")
    print(f"Headline: {profile.headline}")
    print(f"Location: {profile.location}")
    print(f"About: {profile.about}")
    print(f"Profile URL: {profile.profile_url}")

    print("\nEXPERIENCE")
    print("-" * 60)

    for experience in profile.experiences:
        print(
            f"- {experience.title} "
            f"@ {experience.company}"
        )

        if experience.description:
            print(
                f"  {experience.description}"
            )

    print("\nEDUCATION")
    print("-" * 60)

    for education in profile.education:
        print(
            f"- {education.institution}"
        )

        if education.degree:
            print(
                f"  Degree: {education.degree}"
            )

        if education.field_of_study:
            print(
                f"  Field: "
                f"{education.field_of_study}"
            )

    print("\nSKILLS")
    print("-" * 60)

    if profile.skills:
        for skill in profile.skills:
            print(f"- {skill}")
    else:
        print("- None")

    print("\nCERTIFICATIONS")
    print("-" * 60)

    for certification in profile.certifications:
        print(
            f"- {certification.name}"
        )

        if certification.issuer:
            print(
                f"  Issuer: "
                f"{certification.issuer}"
            )

    print("\nPROJECTS")
    print("-" * 60)

    if profile.projects:
        for project in profile.projects:
            print(f"- {project.name}")

            if project.description:
                print(
                    f"  {project.description}"
                )

            if project.url:
                print(
                    f"  URL: {project.url}"
                )
    else:
        print("- None")

    print("\nLANGUAGES")
    print("-" * 60)

    for language in profile.languages:
        print(
            f"- {language.name}: "
            f"{language.proficiency}"
        )

    print("\n" + "=" * 60)
    print("LINKEDIN ANALYSIS")
    print("=" * 60)

    print(f"Current title: {analysis.current_title}")
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

    print("\nClaimed skills:")

    for skill in analysis.claimed_skills:
        print(f"- {skill}")

    print("\nCareer domains:")

    for domain in analysis.career_domains:
        print(f"- {domain}")

    print("\nCareer signals:")

    for signal in analysis.career_signals:
        print(
            f"- {signal.signal}: "
            f"{signal.evidence}"
        )

    print("\nProfile signals:")

    for signal in analysis.signals:
        print(f"- {signal}")

    print("\n" + "=" * 60)
    print("LINKEDIN AI RATING")
    print("=" * 60)

    print("\nRunning Gemini LinkedIn Intelligence...")

    rating = linkedin_rater.rate(
        profile=profile,
        analysis=analysis,
    )

    print("Rating successful.")

    print(
        f"\nOverall Score: "
        f"{rating.overall_score}/100"
    )

    print("\nSECTION SCORES")
    print("-" * 60)

    print(
        f"Headline: "
        f"{rating.headline.score}/100"
    )

    print(
        f"About: "
        f"{rating.about.score}/100"
    )

    print(
        f"Experience: "
        f"{rating.experience.score}/100"
    )

    print(
        f"Projects: "
        f"{rating.projects.score}/100"
    )

    print(
        f"Skills: "
        f"{rating.skills.score}/100"
    )

    print(
        f"Education: "
        f"{rating.education.score}/100"
    )

    print(
        f"Certifications: "
        f"{rating.certifications.score}/100"
    )

    print(
        f"Completeness: "
        f"{rating.completeness.score}/100"
    )

    print("\nSTRENGTHS")
    print("-" * 60)

    for strength in rating.strengths:
        print(f"- {strength}")

    print("\nISSUES")
    print("-" * 60)

    for issue in rating.issues:
        print(f"- {issue}")

    print("\nRECOMMENDATIONS")
    print("-" * 60)

    for recommendation in rating.recommendations:
        print(
            f"[{recommendation.priority}] "
            f"{recommendation.area}"
        )

        print(
            f"  {recommendation.recommendation}"
        )

        print(
            f"  Why: "
            f"{recommendation.reason}"
        )

        for evidence in recommendation.evidence:
            print(
                f"  Evidence: {evidence}"
            )

    print("\nDATA QUALITY")
    print("-" * 60)

    print(
        f"Completeness: "
        f"{rating.data_quality.completeness}/100"
    )

    print(
        f"Note: "
        f"{rating.data_quality.note}"
    )

    print("\n" + "=" * 60)
    print("LINKEDIN PDF PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()