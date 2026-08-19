from app.integrations.linkedin.linkedin_parser import (
    linkedin_parser,
)
from app.services.linkedin.linkedin_rater import (
    linkedin_rater,
)


RAW_PROFILE = {
    "fullName": "Shivansh Dubey",

    "headline": "",

    "location": "",

    "about": "",

    "experience": [
        {
            "company_name": (
                "Manipal Institute of Technology"
            ),
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
                "Issued Jan 2025 "
                "Expires May 2025"
            ),
        }
    ],

    "projects": [],

    "skills": None,
}


def main():

    print("=" * 60)
    print("CAREEROS LINKEDIN INTELLIGENCE")
    print("=" * 60)

    profile = (
        linkedin_parser.parse_api_response(
            RAW_PROFILE
        )
    )

    result = linkedin_rater.rate(
        profile
    )

    print(
        f"\nOverall Score: "
        f"{result.overall_score}/100"
    )

    print("\nSECTION SCORES")
    print("-" * 60)

    for section in result.section_scores:

        print(
            f"{section.section}: "
            f"{section.score}/100"
        )

    print("\nSTRENGTHS")
    print("-" * 60)

    for strength in result.strengths:
        print(f"+ {strength}")

    print("\nISSUES")
    print("-" * 60)

    for issue in result.issues:

        print(
            f"[{issue.priority.upper()}] "
            f"{issue.title}"
        )

        print(
            f"  {issue.explanation}"
        )

        for evidence in issue.evidence:
            print(
                f"  Evidence: {evidence}"
            )

    print("\nRECOMMENDATIONS")
    print("-" * 60)

    for recommendation in (
        result.recommendations
    ):

        print(
            f"[{recommendation.priority.upper()}] "
            f"{recommendation.action}"
        )

        print(
            f"  Why: "
            f"{recommendation.reason}"
        )

        if recommendation.suggested_content:

            print(
                "  Suggested content:"
            )

            print(
                f"    "
                f"{recommendation.suggested_content}"
            )

    print("\n" + "=" * 60)
    print("LINKEDIN INTELLIGENCE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()