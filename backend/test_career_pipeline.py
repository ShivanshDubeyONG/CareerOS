import sys

from app.services.career.career_analysis_service import (
    career_analysis_service,
)


RESUME_PATH = (
    "uploads/"
    "myresume.pdf"
)


def section(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_model(
    obj,
    indent=0,
):

    if obj is None:
        return

    prefix = " " * indent

    if hasattr(
        obj,
        "model_dump",
    ):

        data = obj.model_dump()

    elif isinstance(
        obj,
        dict,
    ):

        data = obj

    else:

        print(
            prefix + str(obj)
        )

        return

    for key, value in data.items():

        label = key.replace(
            "_",
            " ",
        ).title()

        if isinstance(
            value,
            (dict, list),
        ):

            print(
                f"{prefix}{label}:"
            )

            if isinstance(
                value,
                dict,
            ):

                for k, v in value.items():

                    print(
                        f"{prefix}  "
                        f"{k}: {v}"
                    )

            else:

                for item in value:

                    if hasattr(
                        item,
                        "model_dump",
                    ):

                        print(
                            f"{prefix}  -"
                        )

                        print_model(
                            item,
                            indent + 4,
                        )

                    else:

                        print(
                            f"{prefix}  - "
                            f"{item}"
                        )

        else:

            print(
                f"{prefix}{label}: "
                f"{value}"
            )


def main():

    section(
        "CAREEROS FULL CAREER INTELLIGENCE"
    )

    print(
        f"\nResume: {RESUME_PATH}"
    )

    print(
        "\nRunning complete pipeline..."
    )

    result = (
        career_analysis_service.analyze(
            RESUME_PATH
        )
    )

    # ==================================================
    # RESUME
    # ==================================================

    section(
        "[1/5] RESUME INTELLIGENCE"
    )

    resume_result = result[
        "resume"
    ]

    resume = resume_result[
        "profile"
    ]

    rating = resume_result[
        "rating"
    ]

    print(
        f"\nName: {resume.name}"
    )

    print(
        f"Skills: {len(resume.skills)}"
    )

    print(
        "Education:",
        "Present"
        if resume.education.strip()
        else "Missing",
    )

    print(
        "Experience:",
        "Present"
        if resume.experience.strip()
        else "Missing",
    )

    print(
        "Projects:",
        "Present"
        if resume.projects.strip()
        else "Missing",
    )

    print(
        "\nRESUME ANALYSIS"
    )

    print_model(
        rating
    )

    # ==================================================
    # GITHUB
    # ==================================================

    section(
        "[2/5] GITHUB INTELLIGENCE"
    )

    github_result = result[
        "github"
    ]

    if github_result:

        github = github_result[
            "profile"
        ]

        github_analysis = (
            github_result[
                "analysis"
            ]
        )

        print(
            f"\nUsername: "
            f"{github.username}"
        )

        print(
            f"Repositories: "
            f"{len(github.repositories)}"
        )

        print(
            "\nGITHUB AI ANALYSIS"
        )

        print_model(
            github_analysis
        )

    else:

        print(
            "\nGitHub unavailable."
        )

    # ==================================================
    # LEETCODE
    # ==================================================

    section(
        "[3/5] LEETCODE INTELLIGENCE"
    )

    leetcode_result = result[
        "leetcode"
    ]

    if leetcode_result:

        analysis = leetcode_result[
            "analysis"
        ]

        print_model(
            analysis
        )

    else:

        print(
            "\nLeetCode unavailable."
        )

    # ==================================================
    # LINKEDIN
    # ==================================================

    section(
        "[4/5] LINKEDIN INTELLIGENCE"
    )

    linkedin_result = result[
        "linkedin"
    ]

    if linkedin_result:

        profile = linkedin_result[
            "profile"
        ]

        analysis = linkedin_result[
            "analysis"
        ]

        print(
            f"\nName: {profile.name}"
        )

        print(
            f"Headline: "
            f"{profile.headline}"
        )

        print(
            f"Location: "
            f"{profile.location}"
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
            f"Projects: "
            f"{len(profile.projects)}"
        )

        print(
            "\nLINKEDIN ANALYSIS"
        )

        print_model(
            analysis
        )

    else:

        print(
            "\nLinkedIn unavailable."
        )

    # ==================================================
    # UNIFIED
    # ==================================================

    section(
        "[5/5] UNIFIED CAREEROS EVIDENCE"
    )

    unified = result[
        "unified"
    ]

    print(
        f"\nUnified skills: "
        f"{len(unified.skills)}"
    )

    print(
        f"Skill evidence: "
        f"{len(unified.skill_evidence)}"
    )

    print(
        f"Project evidence: "
        f"{len(unified.project_evidence)}"
    )

    print(
        f"Cross-source findings: "
        f"{len(unified.findings)}"
    )

    print(
        "\nSOURCE STATUS"
    )

    for source, available in (
        unified.source_status.items()
    ):

        print(
            f"  {source}: "
            f"{'AVAILABLE' if available else 'UNAVAILABLE'}"
        )

    print(
        "\nSKILL EVIDENCE"
    )

    for item in (
        unified.skill_evidence
    ):

        print(
            f"\n{item.skill}"
        )

        print(
            f"  Resume: "
            f"{item.resume_claimed}"
        )

        print(
            f"  LinkedIn: "
            f"{item.linkedin_claimed}"
        )

        print(
            f"  GitHub: "
            f"{item.github_demonstrated}"
        )

        print(
            f"  LeetCode: "
            f"{item.leetcode_demonstrated}"
        )

        print(
            f"  Status: "
            f"{item.status}"
        )

    print(
        "\nPROJECT EVIDENCE"
    )

    for item in (
        unified.project_evidence
    ):

        print(
            f"\n{item.name}"
        )

        print(
            f"  Resume: "
            f"{item.resume_present}"
        )

        print(
            f"  LinkedIn: "
            f"{item.linkedin_present}"
        )

        print(
            f"  GitHub: "
            f"{item.github_present}"
        )

        print(
            f"  Status: "
            f"{item.status}"
        )

        if item.finding:

            print(
                f"  Finding: "
                f"{item.finding}"
            )

    print(
        "\nCROSS-SOURCE FINDINGS"
    )

    for finding in (
        unified.findings
    ):

        print(
            f"\n[{finding.severity}] "
            f"{finding.finding_type}"
        )

        print(
            f"Subject: "
            f"{finding.subject}"
        )

        print(
            f"Message: "
            f"{finding.message}"
        )

    section(
        "CAREEROS FULL PIPELINE COMPLETE"
    )


if __name__ == "__main__":

    try:

        main()

    finally:

        career_analysis_service.close()