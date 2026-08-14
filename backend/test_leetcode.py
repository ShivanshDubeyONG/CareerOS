from app.integrations.leetcode.leetcode_client import (
    LeetCodeClient,
)

from app.services.leetcode.leetcode_service import (
    leetcode_service,
)


USERNAME = "shivanshdubeyfr"


client = LeetCodeClient()

try:

    profile = client.get_user_profile(
        USERNAME
    )

    analysis = leetcode_service.analyze(
        profile
    )

    print("\n==============================")
    print("LEETCODE INTELLIGENCE")
    print("==============================")

    print(
        "Username:",
        analysis.username,
    )

    print(
        "Total solved:",
        analysis.total_solved,
    )

    print(
        "Difficulty:",
        analysis.difficulty_distribution,
    )

    print(
        "Medium + Hard ratio:",
        analysis.medium_hard_ratio,
    )

    print(
        "Difficulty exposure:",
        analysis.difficulty_exposure,
    )

    print(
        "Problem-solving score:",
        analysis.problem_solving_score,
    )

    print(
        "DSA breadth score:",
        analysis.dsa_breadth_score,
    )

    print("\nLanguages:")

    for language in profile.languages:

        print(
            f"  {language.language}: "
            f"{language.problems_solved}"
        )

    print("\nTop skills:")

    for skill in sorted(
        profile.skills,
        key=lambda x: x.problems_solved,
        reverse=True,
    )[:10]:

        print(
            f"  {skill.skill}: "
            f"{skill.problems_solved} "
            f"({skill.level})"
        )

    print("\nStrong areas:")

    for area in analysis.strong_areas:

        print(
            f"  + {area}"
        )

    print("\nDeveloping areas:")

    for area in analysis.developing_areas:

        print(
            f"  ~ {area}"
        )

    print("\nEvidence gaps:")

    for area in analysis.evidence_gaps:

        print(
            f"  - {area}"
        )

    print("\nActivity:")

    print(
        "  Active days:",
        analysis.active_days,
    )

    print(
        "  Active days (30d):",
        analysis.active_days_30d,
    )

    print(
        "  Active days (90d):",
        analysis.active_days_90d,
    )

    print(
        "  Active months:",
        analysis.active_months,
    )

    print(
        "  Latest activity:",
        analysis.latest_activity,
    )

    print(
        "  Recent activity ratio:",
        analysis.recent_activity_ratio,
    )

    print(
        "  Activity consistency:",
        analysis.activity_consistency,
    )

    print("\nCore DSA Coverage:")

    for area, data in (
        analysis.dsa_coverage.items()
    ):

        print(
            f"  {area}: "
            f"{data['problems_solved']} "
            f"({data['evidence']})"
        )

    print("\nSignals:")

    for signal in analysis.signals:

        print(
            f"  - {signal}"
        )

finally:

    client.close()