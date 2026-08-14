from datetime import datetime, timezone
from typing import List

from app.schemas.github_ai_schema import ProjectInsight
from app.schemas.github_score_schema import (
    GitHubPortfolioScore,
    ScoreDimension,
)
from app.schemas.github_schema import GitHubProfile


class GitHubScorer:

    def score(
        self,
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> GitHubPortfolioScore:

        meaningful_projects = [
            project
            for project in projects
            if project.meaningful_project
        ]

        project_quality = (
            self.project_quality(
                meaningful_projects
            )
        )

        portfolio_depth = (
            self.portfolio_depth(
                meaningful_projects
            )
        )

        technical_breadth = (
            self.technical_breadth(
                profile,
                meaningful_projects,
            )
        )

        activity = (
            self.activity(
                profile,
                meaningful_projects,
            )
        )

        documentation = (
            self.documentation(
                profile,
                meaningful_projects,
            )
        )

        originality = (
            self.originality(
                profile,
                meaningful_projects,
            )
        )

        overall = (
            project_quality * 0.35
            + portfolio_depth * 0.20
            + technical_breadth * 0.15
            + activity * 0.10
            + documentation * 0.10
            + originality * 0.10
        )

        dimensions = {
            "Project Quality": project_quality,
            "Portfolio Depth": portfolio_depth,
            "Technical Breadth": technical_breadth,
            "Activity & Consistency": activity,
            "Documentation": documentation,
            "Originality & Ownership": originality,
        }

        strongest = max(
            dimensions,
            key=dimensions.get,
        )

        weakest = min(
            dimensions,
            key=dimensions.get,
        )

        recommendations = []

        if documentation < 65:

            recommendations.append(
                "Improve README documentation with clear "
                "setup, architecture, usage, and implementation details."
            )

        if portfolio_depth < 65:

            recommendations.append(
                "Build additional substantive projects while "
                "maintaining the quality of existing work."
            )

        if technical_breadth < 60:

            recommendations.append(
                "Add projects that demonstrate different "
                "technologies, domains, or engineering patterns."
            )

        if activity < 55:

            recommendations.append(
                "Maintain meaningful repositories and demonstrate "
                "consistent development over time."
            )

        if originality < 70:

            recommendations.append(
                "Prioritize original projects and clearly demonstrate "
                "personal contributions to forked repositories."
            )

        return GitHubPortfolioScore(

            overall_score=round(
                overall,
                1,
            ),

            project_quality=ScoreDimension(
                score=round(
                    project_quality,
                    1,
                ),
                rationale=(
                    "Average quality of meaningful projects "
                    "identified by the GitHub intelligence engine."
                ),
            ),

            portfolio_depth=ScoreDimension(
                score=round(
                    portfolio_depth,
                    1,
                ),
                rationale=(
                    "Rewards meaningful project depth while "
                    "applying diminishing returns to quantity."
                ),
            ),

            technical_breadth=ScoreDimension(
                score=round(
                    technical_breadth,
                    1,
                ),
                rationale=(
                    "Measures meaningful technical diversity "
                    "rather than raw technology count."
                ),
            ),

            activity_consistency=ScoreDimension(
                score=round(
                    activity,
                    1,
                ),
                rationale=(
                    "Based on actual commit history, recency, "
                    "and development consistency."
                ),
            ),

            documentation=ScoreDimension(
                score=round(
                    documentation,
                    1,
                ),
                rationale=(
                    "Based on actual README presence and "
                    "useful documentation signals."
                ),
            ),

            originality_ownership=ScoreDimension(
                score=round(
                    originality,
                    1,
                ),
                rationale=(
                    "Based on fork status and measurable "
                    "candidate contribution."
                ),
            ),

            meaningful_project_count=len(
                meaningful_projects
            ),

            strongest_area=strongest,

            biggest_weakness=weakest,

            recommendations=recommendations,
        )

    @staticmethod
    def _find_repository(
        profile: GitHubProfile,
        project: ProjectInsight,
    ):

        target = (
            project.repository
            .strip()
            .lower()
        )

        for repository in profile.repositories:

            name = (
                repository.name
                .strip()
                .lower()
            )

            full_name = (
                repository.full_name
                .strip()
                .lower()
            )

            if target == name:
                return repository

            if target == full_name:
                return repository

            if target.endswith(
                "/" + name
            ):
                return repository

        return None

    @staticmethod
    def project_quality(
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        average = (
            sum(
                project.project_score
                for project in projects
            )
            / len(projects)
        )

        return average * 10

    @staticmethod
    def portfolio_depth(
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        count = len(projects)

        average_quality = (
            sum(
                project.project_score
                for project in projects
            )
            / count
        )

        # Quality multiplier.
        #
        # 10/10 projects get the full quantity value.
        # Weak projects receive progressively less depth credit.

        quality_multiplier = (
            0.65
            + (
                0.35
                * (
                    average_quality / 10
                )
            )
        )

        # Diminishing returns.
        #
        # 1 -> 55
        # 2 -> ~72
        # 3 -> ~82
        # 4 -> ~88
        # 5 -> ~92
        # 6+ -> gradually approaches 100

        quantity_score = (
            100
            * (
                1
                - (
                    0.45
                    * (
                        0.58
                        ** (count - 1)
                    )
                )
            )
        )

        return min(
            quantity_score
            * quality_multiplier,
            100,
        )

    @staticmethod
    def technical_breadth(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        languages = set()

        technologies = set()

        project_types = set()

        for project in projects:

            if project.project_type:

                project_types.add(
                    project.project_type
                    .strip()
                    .lower()
                )

            for technology in (
                project.technologies
            ):

                technologies.add(
                    technology
                    .strip()
                    .lower()
                )

            repository = (
                GitHubScorer._find_repository(
                    profile,
                    project,
                )
            )

            if repository:

                if repository.language:

                    languages.add(
                        repository.language
                        .strip()
                        .lower()
                    )

                for language in (
                    repository.languages
                    .keys()
                ):

                    languages.add(
                        language
                        .strip()
                        .lower()
                    )

        # Languages:
        # 1 meaningful language = 35
        # 2 = 55
        # 3 = 70
        # 4 = 82
        # 5+ approaches 100

        language_score = min(
            100,
            35
            + (
                max(
                    len(languages) - 1,
                    0,
                )
                * 15
            ),
        )

        # Project type diversity
        type_score = min(
            len(project_types) * 25,
            100,
        )

        # Technology diversity, with diminishing returns.
        technology_score = min(
            100,
            30
            + (
                max(
                    len(technologies) - 3,
                    0,
                )
                * 5
            ),
        )

        return (
            language_score * 0.35
            + type_score * 0.30
            + technology_score * 0.35
        )

    @staticmethod
    def activity(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        project_scores = []

        now = datetime.now(
            timezone.utc
        )

        for project in projects:

            repository = (
                GitHubScorer._find_repository(
                    profile,
                    project,
                )
            )

            if not repository:
                continue

            if not repository.commit_history_available:

                # Fall back to pushed_at/updated_at
                # rather than pretending we know the
                # commit history.

                timestamp = (
                    repository.pushed_at
                    or repository.updated_at
                )

                if not timestamp:
                    project_scores.append(0)
                    continue

                try:

                    updated = (
                        datetime.fromisoformat(
                            timestamp.replace(
                                "Z",
                                "+00:00",
                            )
                        )
                    )

                    age = (
                        now - updated
                    ).days

                    if age <= 30:
                        project_scores.append(80)

                    elif age <= 90:
                        project_scores.append(65)

                    elif age <= 180:
                        project_scores.append(45)

                    elif age <= 365:
                        project_scores.append(25)

                    else:
                        project_scores.append(10)

                except ValueError:

                    project_scores.append(0)

                continue

            recent = (
                repository.commits_last_90_days
            )

            yearly = (
                repository.commits_last_365_days
            )

            active_months = (
                repository.active_months_last_year
            )

            latest = (
                repository.latest_commit_at
            )

            recency_score = 0

            if latest:

                try:

                    latest_date = (
                        datetime.fromisoformat(
                            latest
                        )
                    )

                    days = (
                        now - latest_date
                    ).days

                    if days <= 30:
                        recency_score = 35

                    elif days <= 90:
                        recency_score = 28

                    elif days <= 180:
                        recency_score = 20

                    elif days <= 365:
                        recency_score = 10

                    else:
                        recency_score = 3

                except ValueError:

                    recency_score = 0

            commit_score = min(
                40,
                recent * 2,
            )

            consistency_score = min(
                25,
                active_months * 2.5,
            )

            # A project with some activity should score
            # better than a completely untouched project,
            # but commit spam shouldn't dominate.

            score = min(
                recency_score
                + commit_score
                + consistency_score,
                100,
            )

            # Penalize suspiciously tiny activity.
            if yearly == 0:

                score = min(
                    score,
                    20,
                )

            project_scores.append(
                score
            )

        if not project_scores:
            return 0

        return (
            sum(project_scores)
            / len(project_scores)
        )

    @staticmethod
    def _score_readme(
        readme: str,
    ) -> float:

        if not readme:
            return 0

        text = readme.strip()

        if not text:
            return 0

        lower = text.lower()

        score = 10

        length = len(text)

        if length >= 3000:
            score += 15

        elif length >= 1500:
            score += 12

        elif length >= 750:
            score += 9

        elif length >= 300:
            score += 6

        else:
            score += 2

        signals = {

            "setup": [
                "installation",
                "setup",
                "getting started",
                "prerequisites",
            ],

            "usage": [
                "usage",
                "how to use",
                "running",
                "run locally",
            ],

            "architecture": [
                "architecture",
                "system design",
                "project structure",
            ],

            "features": [
                "features",
                "functionality",
                "capabilities",
            ],

            "api": [
                "api",
                "endpoints",
                "rest api",
            ],

            "deployment": [
                "deployment",
                "deploy",
                "docker",
                "render",
                "vercel",
            ],

            "testing": [
                "testing",
                "tests",
                "pytest",
                "junit",
            ],

            "demo": [
                "demo",
                "live",
                "screenshots",
                "video",
            ],
        }

        for signal_group in signals.values():

            if any(
                signal in lower
                for signal in signal_group
            ):

                score += 7

        if "```" in text:
            score += 5

        if (
            "http://"
            in lower
            or "https://"
            in lower
        ):

            score += 5

        return min(
            score,
            100,
        )

    @staticmethod
    def documentation(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        scores = []

        for project in projects:

            repository = (
                GitHubScorer._find_repository(
                    profile,
                    project,
                )
            )

            if not repository:
                continue

            scores.append(
                GitHubScorer._score_readme(
                    repository.readme or ""
                )
            )

        if not scores:
            return 0

        return (
            sum(scores)
            / len(scores)
        )

    @staticmethod
    def originality(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        scores = []

        for project in projects:

            repository = (
                GitHubScorer._find_repository(
                    profile,
                    project,
                )
            )

            if not repository:
                continue

            if not repository.is_fork:

                scores.append(100)

                continue

            if not repository.fork_contribution_available:

                scores.append(25)

                continue

            commits = (
                repository.fork_unique_commits
            )

            changed_files = (
                repository.fork_changed_files
            )

            additions = (
                repository.fork_additions
            )

            if (
                commits == 0
                and changed_files == 0
                and additions == 0
            ):

                scores.append(5)

                continue

            contribution = 0

            if commits >= 20:
                contribution += 40

            elif commits >= 10:
                contribution += 30

            elif commits >= 5:
                contribution += 20

            elif commits >= 2:
                contribution += 10

            else:
                contribution += 5

            if changed_files >= 50:
                contribution += 30

            elif changed_files >= 20:
                contribution += 25

            elif changed_files >= 10:
                contribution += 20

            elif changed_files >= 5:
                contribution += 10

            else:
                contribution += 5

            if additions >= 2000:
                contribution += 30

            elif additions >= 1000:
                contribution += 25

            elif additions >= 500:
                contribution += 20

            elif additions >= 100:
                contribution += 10

            else:
                contribution += 5

            scores.append(
                min(
                    contribution,
                    100,
                )
            )

        if not scores:
            return 0

        return (
            sum(scores)
            / len(scores)
        )