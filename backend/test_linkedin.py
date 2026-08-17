from app.integrations.linkedin.linkedin_parser import linkedin_parser
from app.services.linkedin.linkedin_service import linkedin_service


RAW_PROFILE = {
    "fullName": "Shivansh Dubey",
    "headline": "",
    "location": "",
    "experience": [
        {
            "company_name": "Manipal Institute of Technology",
            "position": "",
            "starts_at": "2024",
            "ends_at": "Present",
            "summary": "",
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
            "certification": "Supervised Machine Learning: Regression and Classification",
            "company_name": "DeepLearning.AI",
            "credential_id": "Credential ID LL6LRJQCDYOH",
            "credential_url": "https://www.coursera.org/account/accomplishments/records/LL6LRJQCDYOH",
            "issue_date": "Issued Jan 2025 Expires May 2025",
        }
    ],
    "projects": [],
    "skills": None,
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
    print(f"Certification count: {analysis.certification_count}")

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
    print("LINKEDIN PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()