from app.integrations.linkedin.linkedin_parser import linkedin_parser
from app.services.linkedin.linkedin_service import linkedin_service
from app.services.linkedin.linkedin_rater import linkedin_rater


RAW_PROFILE = {
    "fullName": "Shivansh Dubey",

    "headline": None,
    "location": None,
    "about": None,

    "experience": [
        {
            "company_name": "Manipal Institute of Technology",
            "position": None,
            "starts_at": "2024",
            "ends_at": "Present",
            "summary": None,
        }
    ],

    "education": [
        {
            "college_name": None,
            "starts_at": "2022",
            "ends_at": "2023",
        }
    ],

    "certification": [
        {
            "certification": (
                "Supervised Machine Learning: "
                "Regression and Classification"
            ),
            "company_name": "DeepLearning.AI",
            "credential_id": (
                "Credential ID LL6LRJQCDYOH"
            ),
            "credential_url": (
                "https://www.coursera.org/"
                "account/accomplishments/records/"
                "LL6LRJQCDYOH"
            ),
            "issue_date": (
                "Issued Jan 2025 Expires May 2025"
            ),
        }
    ],

    "projects": [],
    "skills": None,
    "languages": [],
    "organizations": [],
    "awards": [],
    "publications": [],
    "volunteering": [],
}


def main():
    print("=" * 60)
    print("CAREEROS LINKEDIN PIPELINE")
    print("=" * 60)

    print("\nParsing LinkedIn profile...")

    profile = linkedin_parser.parse_api_response(
        RAW_PROFILE
    )

    print("Parsing successful.")

    analysis = linkedin_service.analyze(profile)

    print("Analysis successful.")

    print("\nRESULTS")
    print("-" * 60)

    print(f"Name: {analysis.name}")
    print(f"Headline: {analysis.headline}")
    print(f"Location: {analysis.location}")
    print(f"Current title: {analysis.current_title}")
    print(f"Current company: {analysis.current_company}")
    print(f"Experience count: {analysis.experience_count}")
    print(f"Education count: {analysis.education_count}")
    print(f"Skill count: {analysis.skill_count}")
    print(f"Project count: {analysis.project_count}")
    print(
        f"Certification count: "
        f"{analysis.certification_count}"
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

    # ==================================================
    # LINKEDIN INTELLIGENCE RATER
    # ==================================================

    print("\n" + "=" * 60)
    print("LINKEDIN INTELLIGENCE RATER")
    print("=" * 60)

    print("\nRunning LinkedIn Intelligence Rater...")

    rating = linkedin_rater.rate(
        profile=profile,
        analysis=analysis,
    )

    print("Rating successful.")

    print("\nLINKEDIN PROFILE SCORE")
    print("-" * 60)
    print(
        f"Overall: "
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

    if rating.strengths:
        for strength in rating.strengths:
            print(f"  - {strength}")
    else:
        print("  - None identified.")

    print("\nISSUES")
    print("-" * 60)

    if rating.issues:
        for issue in rating.issues:
            print(f"  - {issue}")
    else:
        print("  - None identified.")

    print("\nRECOMMENDATIONS")
    print("-" * 60)

    if rating.recommendations:
        for recommendation in rating.recommendations:
            print(
                f"  [{recommendation.priority}] "
                f"{recommendation.area}"
            )

            print(
                f"    Recommendation: "
                f"{recommendation.recommendation}"
            )

            print(
                f"    Reason: "
                f"{recommendation.reason}"
            )

            if recommendation.evidence:
                print("    Evidence:")

                for evidence in recommendation.evidence:
                    print(
                        f"      - {evidence}"
                    )
    else:
        print("  - None identified.")

    print("\nSUGGESTED CONTENT")
    print("-" * 60)

    if rating.suggested_content:
        for content in rating.suggested_content:
            print(
                f"  Section: "
                f"{content.section}"
            )

            print(
                f"  Content: "
                f"{content.content}"
            )

            if content.basis:
                print("  Evidence basis:")

                for basis in content.basis:
                    print(
                        f"    - {basis}"
                    )
    else:
        print(
            "  - No content generated. "
            "Insufficient verified evidence."
        )

    print("\nDATA QUALITY")
    print("-" * 60)

    print(
        f"Profile data available: "
        f"{rating.data_quality.profile_data_available}"
    )

    print(
        f"Completeness: "
        f"{rating.data_quality.completeness}/100"
    )

    print(
        f"Note: "
        f"{rating.data_quality.note}"
    )

    if rating.data_quality.missing_sections:
        print("Missing sections:")

        for section in rating.data_quality.missing_sections:
            print(f"  - {section}")

    if rating.data_quality.unavailable_sections:
        print("Unavailable sections:")

        for section in rating.data_quality.unavailable_sections:
            print(f"  - {section}")

    print("\n" + "=" * 60)
    print("LINKEDIN INTELLIGENCE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()