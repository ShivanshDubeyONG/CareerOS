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

        project_quality = self.project_quality(
            meaningful_projects
        )

        portfolio_depth = self.portfolio_depth(
            meaningful_projects
        )

        technical_breadth = self.technical_breadth(
            profile,
            meaningful_projects,
        )

        activity = self.activity(
            profile,
            meaningful_projects,
        )

        documentation = self.documentation(
            profile,
            meaningful_projects,
        )

        originality = self.originality(
            profile,
            meaningful_projects,
        )

        # Project quality is the most important signal.
        # Portfolio depth measures quantity separately.
        # Activity is intentionally low-weight because an old,
        # completed project should not be treated as a bad project.

        overall = (
            project_quality * 0.40
            + portfolio_depth * 0.20
            + technical_breadth * 0.15
            + documentation * 0.10
            + originality * 0.10
            + activity * 0.05
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
                    "Measures the demonstrated technical and "
                    "implementation quality of meaningful projects."
                ),
            ),

            portfolio_depth=ScoreDimension(
                score=round(
                    portfolio_depth,
                    1,
                ),
                rationale=(
                    "Measures the depth of the portfolio based "
                    "on the number of meaningful projects."
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
                    "Measures development activity and consistency "
                    "without treating inactivity as poor project quality."
                ),
            ),

            documentation=ScoreDimension(
                score=round(
                    documentation,
                    1,
                ),
                rationale=(
                    "Based on README quality and useful "
                    "documentation signals."
                ),
            ),

            originality_ownership=ScoreDimension(
                score=round(
                    originality,
                    1,
                ),
                rationale=(
                    "Measures originality and demonstrated "
                    "personal contribution."
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

        scores = sorted(
            (
                max(
                    0,
                    min(
                        project.project_score,
                        10,
                    ),
                )
                for project in projects
            ),
            reverse=True,
        )

        # Strong projects matter more than weak experimental
        # repositories. This prevents one mediocre repository
        # from dragging down an otherwise strong portfolio.

        weights = [
            0.45,
            0.30,
            0.15,
            0.07,
            0.03,
        ]

        weighted_scores = []

        for index, score in enumerate(scores):

            weight = (
                weights[index]
                if index < len(weights)
                else 0
            )

            weighted_scores.append(
                score * 10 * weight
            )

        total_weight = sum(
            weights[:len(scores)]
        )

        if total_weight == 0:
            return 0

        return min(
            sum(weighted_scores) / total_weight,
            100,
        )

    @staticmethod
    def portfolio_depth(
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        count = len(projects)

        # Portfolio depth measures quantity only.
        # Project quality is intentionally NOT used here,
        # preventing the same weakness from being counted twice.

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
            quantity_score,
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

            for technology in project.technologies:

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

                for language in repository.languages.keys():

                    languages.add(
                        language
                        .strip()
                        .lower()
                    )

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

        type_score = min(
            len(project_types) * 25,
            100,
        )

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

                timestamp = (
                    repository.pushed_at
                    or repository.updated_at
                )

                if not timestamp:
                    project_scores.append(0)
                    continue

                try:

                    updated = datetime.fromisoformat(
                        timestamp.replace(
                            "Z",
                            "+00:00",
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

            score = min(
                recency_score
                + commit_score
                + consistency_score,
                100,
            )

            # IMPORTANT:
            # Do not cap the score simply because there were
            # zero commits in the last year. A completed project
            # can legitimately be inactive.

            if yearly == 0:
                score = max(
                    score,
                    35,
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