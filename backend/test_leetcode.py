from app.integrations.leetcode.leetcode_client import (
    LeetCodeClient,
)
from app.services.leetcode.leetcode_service import (
    leetcode_service,
)


client = LeetCodeClient()

try:

    profile = client.get_user_profile(
        "shivanshdubeyfr"
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
        "Difficulty level:",
        analysis.difficulty_level,
    )

    print(
        "\nLanguages:"
    )

    for language in profile.languages:

        print(
            f"  {language.language}: "
            f"{language.problems_solved}"
        )

    print(
        "\nTop skills:"
    )

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

    print(
        "\nSignals:",
        analysis.signals,
    )

finally:

    client.close()