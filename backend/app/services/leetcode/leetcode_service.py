from app.schemas.leetcode_schema import (
    LeetCodeAnalysis,
    LeetCodeProfile,
)


class LeetCodeService:

    @staticmethod
    def analyze(
        profile: LeetCodeProfile,
    ) -> LeetCodeAnalysis:

        total = profile.total_solved

        if total == 0:

            distribution = {
                "easy": 0.0,
                "medium": 0.0,
                "hard": 0.0,
            }

        else:

            distribution = {
                "easy": round(
                    profile.easy_solved / total,
                    3,
                ),
                "medium": round(
                    profile.medium_solved / total,
                    3,
                ),
                "hard": round(
                    profile.hard_solved / total,
                    3,
                ),
            }

        medium_hard_ratio = 0.0

        if total > 0:

            medium_hard_ratio = round(
                (
                    profile.medium_solved
                    + profile.hard_solved
                )
                / total,
                3,
            )

        if total == 0:

            difficulty_level = "no_evidence"

        elif (
            profile.hard_solved >= 20
            or medium_hard_ratio >= 0.65
        ):

            difficulty_level = "advanced"

        elif (
            profile.medium_solved >= 20
            or medium_hard_ratio >= 0.40
        ):

            difficulty_level = "intermediate"

        else:

            difficulty_level = "foundational"

        strongest_skills = [
            skill.skill
            for skill in sorted(
                profile.skills,
                key=lambda x: x.problems_solved,
                reverse=True,
            )[:5]
        ]

        languages = [
            language.language
            for language in sorted(
                profile.languages,
                key=lambda x: x.problems_solved,
                reverse=True,
            )
        ]

        signals = []

        if profile.total_solved >= 150:

            signals.append(
                "strong_problem_solving_volume"
            )

        elif profile.total_solved >= 75:

            signals.append(
                "meaningful_problem_solving_volume"
            )

        elif profile.total_solved > 0:

            signals.append(
                "early_problem_solving_experience"
            )

        if profile.medium_solved >= 30:

            signals.append(
                "strong_medium_problem_exposure"
            )

        if profile.hard_solved >= 10:

            signals.append(
                "meaningful_hard_problem_exposure"
            )

        if profile.hard_solved == 0:

            signals.append(
                "no_hard_problem_evidence"
            )

        return LeetCodeAnalysis(
            username=profile.username,
            total_solved=profile.total_solved,
            difficulty_distribution=distribution,
            medium_hard_ratio=medium_hard_ratio,
            difficulty_level=difficulty_level,
            strongest_skills=strongest_skills,
            languages=languages,
            signals=signals,
        )


leetcode_service = LeetCodeService()