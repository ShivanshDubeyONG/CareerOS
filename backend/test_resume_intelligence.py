from app.services.resume_extraction_service import (
    resume_extraction_service,
)

from app.services.resume.resume_rater import (
    resume_rater,
)


RESUME_PATH = (
    "uploads/"
    "19b95751-bd60-4210-9f16-f88589a05b61.pdf"
)


def main():

    print("=" * 70)

    print(
        "CAREEROS RESUME INTELLIGENCE"
    )

    print("=" * 70)

    # ==================================================
    # 1. EXTRACTION
    # ==================================================

    print(
        "\n1. Extracting resume..."
    )

    resume = (
        resume_extraction_service.extract(
            RESUME_PATH
        )
    )

    print(
        "Resume extraction successful."
    )

    print(
        f"Name: "
        f"{getattr(resume, 'name', None)}"
    )

    print(
        f"Skills: "
        f"{len(resume.skills)}"
    )

    print(
    f"Education: "
    f"{'Present' if resume.education.strip() else 'Missing'}"
    )

    print(
        f"Experience: "
        f"{'Present' if resume.experience.strip() else 'Missing'}"
    )

    print(
        f"Projects: "
        f"{'Present' if resume.projects.strip() else 'Missing'}"
    )

    # ==================================================
    # 2. GEMINI
    # ==================================================

    print(
        "\n2. Running Gemini Resume Intelligence..."
    )

    rating = resume_rater.rate(
        resume
    )

    print(
        "Gemini rating successful."
    )

    # ==================================================
    # 3. SCORE
    # ==================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "RESUME SCORE"
    )

    print(
        "=" * 70
    )

    print(
        f"Overall: "
        f"{rating.overall_score}/100"
    )

    # ==================================================
    # 4. SECTION SCORES
    # ==================================================

    print(
        "\nSECTION SCORES"
    )

    print("-" * 70)

    sections = [
        ("Summary", rating.summary),
        ("Experience", rating.experience),
        ("Projects", rating.projects),
        ("Skills", rating.skills),
        ("Education", rating.education),
        ("Achievements", rating.achievements),
        ("Structure", rating.structure),
        ("ATS", rating.ats),
        (
            "Quantified Impact",
            rating.quantified_impact,
        ),
        (
            "Target Role Alignment",
            rating.target_role_alignment,
        ),
    ]

    for name, section in sections:

        print(
            f"{name}: "
            f"{section.score}/100"
        )

    # ==================================================
    # 5. STRENGTHS
    # ==================================================

    print(
        "\nSTRENGTHS"
    )

    print("-" * 70)

    for strength in rating.strengths:

        print(
            f"- {strength}"
        )

    # ==================================================
    # 6. ISSUES
    # ==================================================

    print(
        "\nISSUES"
    )

    print("-" * 70)

    for issue in rating.issues:

        print(
            f"- {issue}"
        )

    # ==================================================
    # 7. RECOMMENDATIONS
    # ==================================================

    print(
        "\nRECOMMENDATIONS"
    )

    print("-" * 70)

    for recommendation in (
        rating.recommendations
    ):

        print(
            f"\n[{recommendation.priority}] "
            f"{recommendation.area}"
        )

        print(
            f"Recommendation: "
            f"{recommendation.recommendation}"
        )

        print(
            f"Reason: "
            f"{recommendation.reason}"
        )

        if recommendation.evidence:

            print(
                "Evidence:"
            )

            for evidence in (
                recommendation.evidence
            ):

                print(
                    f"  - {evidence}"
                )

    # ==================================================
    # 8. SUGGESTED CONTENT
    # ==================================================

    print(
        "\nSUGGESTED CONTENT"
    )

    print("-" * 70)

    for content in (
        rating.suggested_content
    ):

        print(
            f"\nSection: "
            f"{content.section}"
        )

        print(
            f"Content: "
            f"{content.content}"
        )

        if content.basis:

            print(
                "Basis:"
            )

            for basis in (
                content.basis
            ):

                print(
                    f"  - {basis}"
                )

    # ==================================================
    # 9. DATA QUALITY
    # ==================================================

    print(
        "\nDATA QUALITY"
    )

    print("-" * 70)

    quality = rating.data_quality

    print(
        f"Profile data available: "
        f"{quality.profile_data_available}"
    )

    print(
        f"Completeness: "
        f"{quality.completeness}/100"
    )

    print(
        f"Note: "
        f"{quality.note}"
    )

    if quality.missing_sections:

        print(
            "Missing sections:"
        )

        for section in (
            quality.missing_sections
        ):

            print(
                f"  - {section}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "RESUME INTELLIGENCE COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()