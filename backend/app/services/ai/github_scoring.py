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

        if documentation < 70:
            recommendations.append(
                "Improve README documentation with clear "
                "setup, architecture, usage, and implementation details."
            )

        if portfolio_depth < 60:
            recommendations.append(
                "Build additional substantive projects while "
                "maintaining the quality of existing work."
            )

        if technical_breadth < 60:
            recommendations.append(
                "Add projects that demonstrate different "
                "technologies, domains, or engineering patterns."
            )

        if activity < 60:
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
            overall_score=round(overall, 1),

            project_quality=ScoreDimension(
                score=round(project_quality, 1),
                rationale=(
                    "Average quality of meaningful projects "
                    "identified by the GitHub intelligence engine."
                ),
            ),

            portfolio_depth=ScoreDimension(
                score=round(portfolio_depth, 1),
                rationale=(
                    "Rewards multiple meaningful projects "
                    "with diminishing returns on quantity."
                ),
            ),

            technical_breadth=ScoreDimension(
                score=round(technical_breadth, 1),
                rationale=(
                    "Based on meaningful language, technology, "
                    "and project-type diversity."
                ),
            ),

            activity_consistency=ScoreDimension(
                score=round(activity, 1),
                rationale=(
                    "Based on recent maintenance of meaningful "
                    "repositories."
                ),
            ),

            documentation=ScoreDimension(
                score=round(documentation, 1),
                rationale=(
                    "Based on README presence and the quality "
                    "of documented project information."
                ),
            ),

            originality_ownership=ScoreDimension(
                score=round(originality, 1),
                rationale=(
                    "Based on actual fork status and measurable "
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

        project_name = (
            project.repository.strip().lower()
        )

        for repository in profile.repositories:

            name = repository.name.strip().lower()

            full_name = (
                repository.full_name.strip().lower()
            )

            if project_name == name:
                return repository

            if project_name == full_name:
                return repository

            if project_name.endswith(
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

        return (
            sum(
                project.project_score
                for project in projects
            )
            / len(projects)
        ) * 10

    @staticmethod
    def portfolio_depth(
        projects: List[ProjectInsight],
    ) -> float:

        count = len(projects)

        if count == 0:
            return 0

        quantity_score = 100 * (
            1 - (
                0.50 * (
                    0.55 ** (count - 1)
                )
            )
        )

        average_quality = (
            sum(
                project.project_score
                for project in projects
            )
            / count
        )

        quality_factor = (
            0.70
            + (
                0.30
                * (
                    average_quality / 10
                )
            )
        )

        return min(
            quantity_score * quality_factor,
            100,
        )

    @staticmethod
    def technical_breadth(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        languages = set()

        for repository in profile.repositories:

            if repository.language:
                languages.add(
                    repository.language.lower()
                )

            for language in repository.languages.keys():
                languages.add(
                    language.lower()
                )

        project_types = {
            project.project_type.lower()
            for project in projects
            if project.project_type
        }

        technologies = set()

        for project in projects:

            for technology in project.technologies:
                technologies.add(
                    technology.lower()
                )

        language_score = min(
            len(languages) / 6,
            1,
        )

        project_type_score = min(
            len(project_types) / 4,
            1,
        )

        technology_score = min(
            len(technologies) / 15,
            1,
        )

        return (
            language_score * 40
            + project_type_score * 30
            + technology_score * 30
        )

    @staticmethod
    def activity(
        profile: GitHubProfile,
        projects: List[ProjectInsight],
    ) -> float:

        if not projects:
            return 0

        recent_projects = 0
        evaluated_projects = 0

        now = datetime.now(timezone.utc)

        for project in projects:

            repository = GitHubScorer._find_repository(
                profile,
                project,
            )

            if not repository:
                continue

            evaluated_projects += 1

            if not repository.updated_at:
                continue

            try:

                updated = datetime.fromisoformat(
                    repository.updated_at.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if (
                    now - updated
                ).days <= 180:
                    recent_projects += 1

            except ValueError:
                continue

        if evaluated_projects == 0:
            return 0

        return min(
            (
                recent_projects
                / evaluated_projects
            ) * 100,
            100,
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

        score = 0

        # README exists
        score += 15

        # Length / substance
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

        # Useful documentation sections
        section_signals = {
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
                "structure",
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

        for signals in section_signals.values():

            if any(
                signal in lower
                for signal in signals
            ):
                score += 7

        # Code blocks / commands are useful evidence
        if "```" in text:
            score += 5

        # Links usually indicate useful external
        # resources, demos, or documentation.
        if "http://" in lower or "https://" in lower:
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

            repository = GitHubScorer._find_repository(
                profile,
                project,
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

            repository = GitHubScorer._find_repository(
                profile,
                project,
            )

            if not repository:
                continue

            if not repository.is_fork:
                scores.append(100)
                continue

            if not repository.fork_contribution_available:
                scores.append(25)
                continue

            commits = repository.fork_unique_commits
            changed_files = repository.fork_changed_files
            additions = repository.fork_additions

            if (
                commits == 0
                and changed_files == 0
                and additions == 0
            ):
                scores.append(5)
                continue

            contribution_score = 0

            if commits >= 20:
                contribution_score += 40
            elif commits >= 10:
                contribution_score += 30
            elif commits >= 5:
                contribution_score += 20
            elif commits >= 2:
                contribution_score += 10
            else:
                contribution_score += 5

            if changed_files >= 50:
                contribution_score += 30
            elif changed_files >= 20:
                contribution_score += 25
            elif changed_files >= 10:
                contribution_score += 20
            elif changed_files >= 5:
                contribution_score += 10
            else:
                contribution_score += 5

            if additions >= 2000:
                contribution_score += 30
            elif additions >= 1000:
                contribution_score += 25
            elif additions >= 500:
                contribution_score += 20
            elif additions >= 100:
                contribution_score += 10
            else:
                contribution_score += 5

            scores.append(
                min(
                    contribution_score,
                    100,
                )
            )

        if not scores:
            return 0

        return (
            sum(scores)
            / len(scores)
        )