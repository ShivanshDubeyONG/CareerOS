from app.integrations.linkedin.apify_client import (
    apify_linkedin_client,
)

from app.integrations.linkedin.apify_adapter import (
    apify_linkedin_adapter,
)

from app.services.linkedin.linkedin_service import (
    linkedin_service,
)

from app.services.linkedin.linkedin_rater import (
    linkedin_rater,
)

from app.services.unified.unified_service import (
    unified_service,
)


LINKEDIN_URL = (
    "https://www.linkedin.com/in/"
    "shivansh-dubey-69a825310/"
)


def main():

    print("=" * 70)
    print("CAREEROS REAL LINKEDIN INTELLIGENCE PIPELINE")
    print("=" * 70)

    # ==================================================
    # 1. ACQUISITION
    # ==================================================

    print("\n1. Acquiring LinkedIn profile...")
    print(f"URL: {LINKEDIN_URL}")

    raw_profile = (
        apify_linkedin_client.fetch_profile(
            LINKEDIN_URL
        )
    )

    print(
        "Acquisition successful."
    )

    # ==================================================
    # 2. NORMALIZATION
    # ==================================================

    print(
        "\n2. Normalizing provider data..."
    )

    profile, metadata = (
        apify_linkedin_adapter.parse(
            raw_profile
        )
    )

    print(
        "Canonical parsing successful."
    )

    # ==================================================
    # 3. LINKEDIN ANALYSIS
    # ==================================================

    print(
        "\n3. Running LinkedIn analysis..."
    )

    analysis = (
        linkedin_service.analyze(
            profile
        )
    )

    print(
        "LinkedIn analysis successful."
    )

    # ==================================================
    # 4. PROFILE SUMMARY
    # ==================================================

    print(
        "\n4. LINKEDIN PROFILE"
    )
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

    # ==================================================
    # 5. UNIFIED EVIDENCE
    # ==================================================

    print(
        "\n5. BUILDING UNIFIED CAREEROS EVIDENCE..."
    )

    print(
        "NOTE: This test currently has only "
        "LinkedIn acquisition data available."
    )

    unified_profile = (
        unified_service.build_profile(
            linkedin_profile=profile,
            linkedin_analysis=analysis,
        )
    )

    print(
        "Unified evidence built successfully."
    )

    print(
        f"Unified skills: "
        f"{len(unified_profile.skills)}"
    )

    print(
        f"Skill evidence: "
        f"{len(unified_profile.skill_evidence)}"
    )

    print(
        f"Project evidence: "
        f"{len(unified_profile.project_evidence)}"
    )

    print(
        f"Cross-source findings: "
        f"{len(unified_profile.findings)}"
    )

    # ==================================================
    # 6. GEMINI LINKEDIN INTELLIGENCE
    # ==================================================

    print(
        "\n6. Running Gemini LinkedIn Intelligence..."
    )

    rating = (
        linkedin_rater.rate(
            profile=profile,
            analysis=analysis,
            unified_profile=unified_profile,
        )
    )

    print(
        "Gemini rating successful."
    )

    # ==================================================
    # 7. SCORE
    # ==================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "LINKEDIN PROFILE SCORE"
    )

    print(
        "=" * 70
    )

    print(
        f"Overall: "
        f"{rating.overall_score}/100"
    )

    # ==================================================
    # 8. SECTION SCORES
    # ==================================================

    print(
        "\nSECTION SCORES"
    )
    print("-" * 70)

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
    # ==================================================
    # 9. STRENGTHS
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
    # 10. ISSUES
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
    # 11. RECOMMENDATIONS
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
            f"{recommendation.section}"
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
    # 12. SUGGESTED CONTENT
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

        if content.evidence_basis:

            print(
                "Evidence basis:"
            )

            for evidence in (
                content.evidence_basis
            ):

                print(
                    f"  - {evidence}"
                )

    # ==================================================
    # 13. DATA QUALITY
    # ==================================================

    print(
        "\nDATA QUALITY"
    )
    print("-" * 70)

    print(
        f"Profile data available: "
        f"{rating.profile_data_available}"
    )

    print(
        f"Completeness: "
        f"{rating.data_completeness}/100"
    )

    if rating.data_quality_note:

        print(
            f"Note: "
            f"{rating.data_quality_note}"
        )

    if rating.missing_sections:

        print(
            "Unavailable/missing sections:"
        )

        for section in (
            rating.missing_sections
        ):

            print(
                f"  - {section}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "REAL LINKEDIN INTELLIGENCE COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()