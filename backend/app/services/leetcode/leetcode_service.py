from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.schemas.leetcode_schema import (
    LeetCodeAnalysis,
    LeetCodeProfile,
)

from app.services.leetcode.leetcode_skill_map import (
    build_core_dsa_coverage,
)


class LeetCodeService:

    @staticmethod
    def analyze(
        profile: LeetCodeProfile,
    ) -> LeetCodeAnalysis:

        total = max(
            profile.total_solved,
            0,
        )

        easy = max(
            profile.easy_solved,
            0,
        )

        medium = max(
            profile.medium_solved,
            0,
        )

        hard = max(
            profile.hard_solved,
            0,
        )
        
        if total > 0:

            difficulty_distribution = {
                "easy": round(
                    easy / total,
                    3,
                ),
                "medium": round(
                    medium / total,
                    3,
                ),
                "hard": round(
                    hard / total,
                    3,
                ),
            }

        else:

            difficulty_distribution = {
                "easy": 0.0,
                "medium": 0.0,
                "hard": 0.0,
            }

        if total > 0:

            medium_hard_ratio = round(
                (
                    medium
                    + hard
                )
                / total,
                3,
            )

        else:

            medium_hard_ratio = 0.0

        if total == 0:

            difficulty_exposure = (
                "no_evidence"
            )

        elif (
            hard >= 10
            or medium_hard_ratio >= 0.60
        ):

            difficulty_exposure = "high"

        elif (
            medium >= 20
            or medium_hard_ratio >= 0.35
        ):

            difficulty_exposure = "moderate"

        else:

            difficulty_exposure = (
                "foundational"
            )

        skill_counts = {}

        for skill in profile.skills:

            name = skill.skill.strip()

            if not name:
                continue

            count = max(
                skill.problems_solved,
                0,
            )

            skill_counts[name] = (
                skill_counts.get(
                    name,
                    0,
                )
                + count
            )

        strongest_skills = [
            skill
            for skill, count in sorted(
                skill_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if count > 0
        ][:7]

        # --------------------------------
        # LANGUAGES
        # --------------------------------

        language_counts = {}

        for language in profile.languages:

            name = language.language.strip()

            if not name:
                continue

            count = max(
                language.problems_solved,
                0,
            )

            language_counts[name] = (
                language_counts.get(
                    name,
                    0,
                )
                + count
            )

        languages = [
            language
            for language, count in sorted(
                language_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if count > 0
        ]

        dsa_coverage = (
            build_core_dsa_coverage(
                skill_counts
            )
        )

        strong_areas = [
            area
            for area, data
            in dsa_coverage.items()
            if data["evidence"]
            == "strong"
        ]

        developing_areas = [
            area
            for area, data
            in dsa_coverage.items()
            if data["evidence"]
            in {
                "limited",
                "developing",
            }
        ]

        evidence_gaps = [
            area
            for area, data
            in dsa_coverage.items()
            if data["evidence"]
            == "no_evidence"
        ]

        breadth_points = 0.0

        for data in dsa_coverage.values():

            evidence = data["evidence"]

            if evidence == "strong":

                breadth_points += 1.0

            elif evidence == "developing":

                breadth_points += 0.6

            elif evidence == "limited":

                breadth_points += 0.25

        if dsa_coverage:

            dsa_breadth_score = round(
                (
                    breadth_points
                    / len(dsa_coverage)
                )
                * 100,
                1,
            )

        else:

            dsa_breadth_score = 0.0

        volume_score = min(
            total / 150,
            1.0,
        )

        difficulty_score = (
            (
                medium * 1.0
                + hard * 1.75
            )
            / max(
                total * 1.75,
                1,
            )
        )

        problem_solving_score = round(
            (
                volume_score * 0.45
                + difficulty_score * 0.55
            )
            * 100,
            1,
        )

        calendar = (
            profile.submission_calendar
        )

        now = datetime.now(
            timezone.utc
        )

        today = now.date()

        active_dates = set()

        for timestamp, count in (
            calendar.items()
        ):

            if count <= 0:
                continue

            try:

                activity_date = (
                    datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc,
                    ).date()
                )

                active_dates.add(
                    activity_date
                )

            except (
                OverflowError,
                OSError,
                ValueError,
            ):

                continue

        active_days = len(
            active_dates
        )

        cutoff_30 = (
            today
            - timedelta(days=29)
        )

        cutoff_90 = (
            today
            - timedelta(days=89)
        )

        active_days_30d = sum(
            1
            for date in active_dates
            if cutoff_30
            <= date
            <= today
        )

        active_days_90d = sum(
            1
            for date in active_dates
            if cutoff_90
            <= date
            <= today
        )

        active_months = len({
            (
                date.year,
                date.month,
            )
            for date in active_dates
        })

        if active_dates:

            latest_date = max(
                active_dates
            )

            latest_activity = (
                latest_date.isoformat()
            )

        else:

            latest_activity = None

        recent_activity_ratio = round(
            active_days_30d
            / max(
                active_days_90d,
                1,
            ),
            3,
        )

        # --------------------------------
        # ACTIVITY CONSISTENCY
        # --------------------------------

        if not active_dates:

            activity_consistency = (
                "no_evidence"
            )

        elif active_days_90d >= 45:

            activity_consistency = (
                "high"
            )

        elif active_days_90d >= 20:

            activity_consistency = (
                "moderate"
            )

        elif active_days_90d >= 5:

            activity_consistency = (
                "occasional"
            )

        else:

            activity_consistency = (
                "low"
            )

        # --------------------------------
        # SIGNALS
        # --------------------------------

        signals = []

        if total >= 150:

            signals.append(
                "high_problem_solving_volume"
            )

        elif total >= 75:

            signals.append(
                "meaningful_problem_solving_volume"
            )

        elif total > 0:

            signals.append(
                "early_problem_solving_experience"
            )

        if difficulty_exposure == "high":

            signals.append(
                "high_difficulty_exposure"
            )

        elif difficulty_exposure == "moderate":

            signals.append(
                "moderate_difficulty_exposure"
            )

        elif difficulty_exposure == "foundational":

            signals.append(
                "foundational_difficulty_exposure"
            )

        if hard >= 10:

            signals.append(
                "meaningful_hard_problem_exposure"
            )

        elif hard > 0:

            signals.append(
                "some_hard_problem_exposure"
            )

        else:

            signals.append(
                "no_hard_problem_evidence"
            )

        if len(strong_areas) >= 5:

            signals.append(
                "broad_core_dsa_coverage"
            )

        elif len(strong_areas) >= 3:

            signals.append(
                "solid_core_dsa_coverage"
            )

        elif strong_areas:

            signals.append(
                "developing_core_dsa_coverage"
            )

        if len(evidence_gaps) >= 6:

            signals.append(
                "significant_core_dsa_gaps"
            )

        elif len(evidence_gaps) >= 3:

            signals.append(
                "multiple_core_dsa_gaps"
            )

        elif evidence_gaps:

            signals.append(
                "limited_core_dsa_gaps"
            )

        if activity_consistency == "high":

            signals.append(
                "high_recent_activity"
            )

        elif activity_consistency == "moderate":

            signals.append(
                "moderate_recent_activity"
            )

        elif activity_consistency == "occasional":

            signals.append(
                "occasional_recent_activity"
            )

        elif activity_consistency == "low":

            signals.append(
                "limited_recent_activity"
            )

        if (
            active_days_30d >= 10
        ):

            signals.append(
                "active_in_last_30_days"
            )

        return LeetCodeAnalysis(
            username=profile.username,
            total_solved=total,
            difficulty_distribution=(
                difficulty_distribution
            ),
            medium_hard_ratio=(
                medium_hard_ratio
            ),
            difficulty_exposure=(
                difficulty_exposure
            ),
            strongest_skills=(
                strongest_skills
            ),
            languages=languages,
            dsa_coverage=dsa_coverage,
            strong_areas=strong_areas,
            developing_areas=developing_areas,
            evidence_gaps=evidence_gaps,
            dsa_breadth_score=(
                dsa_breadth_score
            ),
            problem_solving_score=(
                problem_solving_score
            ),
            active_days=active_days,
            active_days_30d=(
                active_days_30d
            ),
            active_days_90d=(
                active_days_90d
            ),
            active_months=active_months,
            latest_activity=(
                latest_activity
            ),
            recent_activity_ratio=(
                recent_activity_ratio
            ),
            activity_consistency=(
                activity_consistency
            ),
            signals=signals,
        )


leetcode_service = LeetCodeService()