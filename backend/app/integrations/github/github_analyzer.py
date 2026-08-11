import json
import re
from typing import Dict, List

from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)


class GitHubAnalyzer:

    def analyze_repository(
        self,
        repository: GitHubRepository,
    ) -> Dict:
        language_count = len(repository.languages)

        readme_length = (
            len(repository.readme.strip())
            if repository.readme
            else 0
        )

        has_readme = repository.readme is not None

        activity_score = self._calculate_activity_score(
            repository
        )

        documentation_score = (
            self._calculate_documentation_score(
                repository
            )
        )

        project_strength_score = (
            self._calculate_project_strength(
                repository,
                documentation_score,
                activity_score,
            )
        )

        return {
            "name": repository.name,
            "url": repository.url,
            "description": repository.description,

            "primary_language": repository.language,
            "languages": repository.languages,
            "language_count": language_count,

            "stars": repository.stars,
            "forks": repository.forks,
            "topics": repository.topics,

            "is_fork": repository.is_fork,
            "is_archived": repository.is_archived,

            "has_readme": has_readme,
            "readme_length": readme_length,

            "dependencies": repository.dependencies,
            "dependency_files": repository.dependency_files,

            "activity_score": activity_score,
            "documentation_score": documentation_score,
            "project_strength_score": project_strength_score,
        }

    def analyze_profile(
        self,
        profile: GitHubProfile,
    ) -> Dict:
        repository_analysis: List[Dict] = []

        for repository in profile.repositories:
            analysis = self.analyze_repository(
                repository
            )

            repository_analysis.append(analysis)

        original_repositories = [
            repo
            for repo in profile.repositories
            if not repo.is_fork
        ]

        active_repositories = [
            repo
            for repo in profile.repositories
            if not repo.is_archived
        ]

        total_stars = sum(
            repo.stars
            for repo in profile.repositories
        )

        total_forks = sum(
            repo.forks
            for repo in profile.repositories
        )

        languages = self._collect_languages(
            profile.repositories
        )

        dependencies = self._collect_dependencies(
            profile.repositories
        )

        return {
            "username": profile.username,
            "name": profile.name,
            "bio": profile.bio,
            "profile_url": profile.profile_url,

            "public_repository_count": (
                profile.public_repository_count
            ),
            "followers": profile.followers,
            "following": profile.following,

            "total_repositories_analyzed": len(
                profile.repositories
            ),

            "original_repository_count": len(
                original_repositories
            ),

            "active_repository_count": len(
                active_repositories
            ),

            "total_stars": total_stars,
            "total_forks": total_forks,

            "languages_used": languages,

            "dependencies_used": dependencies,

            "repositories": repository_analysis,
        }

    @staticmethod
    def extract_dependencies(
        files: Dict[str, str],
    ) -> List[str]:
        dependencies = set()

        # ------------------------------------------
        # requirements.txt
        # ------------------------------------------

        requirements = files.get("requirements.txt")

        if requirements:
            for line in requirements.splitlines():
                line = line.strip()

                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("-")
                ):
                    continue

                match = re.match(
                    r"^([A-Za-z0-9_.-]+)",
                    line,
                )

                if match:
                    dependencies.add(
                        match.group(1).lower()
                    )

        # ------------------------------------------
        # package.json
        # ------------------------------------------

        package_json = files.get("package.json")

        if package_json:
            try:
                data = json.loads(package_json)

                for section in [
                    "dependencies",
                    "devDependencies",
                ]:
                    section_data = data.get(
                        section,
                        {},
                    )

                    for dependency in section_data:
                        dependencies.add(
                            dependency.lower()
                        )

            except json.JSONDecodeError:
                pass

        # ------------------------------------------
        # pyproject.toml
        # ------------------------------------------

        pyproject = files.get("pyproject.toml")

        if pyproject:
            dependency_section = False

            for line in pyproject.splitlines():
                stripped = line.strip()

                if stripped.startswith("["):
                    dependency_section = (
                        "dependencies"
                        in stripped.lower()
                    )

                if dependency_section:
                    match = re.match(
                        r'^["\']?([A-Za-z0-9_.-]+)',
                        stripped,
                    )

                    if match:
                        dependency = match.group(1)

                        if dependency.lower() not in {
                            "dependencies",
                            "optional",
                        }:
                            dependencies.add(
                                dependency.lower()
                            )

        return sorted(dependencies)

    @staticmethod
    def _calculate_activity_score(
        repository: GitHubRepository,
    ) -> int:
        if repository.is_archived:
            return 10

        if not repository.updated_at:
            return 30

        return 70

    @staticmethod
    def _calculate_documentation_score(
        repository: GitHubRepository,
    ) -> int:
        if not repository.readme:
            return 0

        readme_length = len(
            repository.readme.strip()
        )

        if readme_length >= 2000:
            return 100

        if readme_length >= 1000:
            return 80

        if readme_length >= 500:
            return 60

        if readme_length >= 200:
            return 40

        return 20

    @staticmethod
    def _calculate_project_strength(
        repository: GitHubRepository,
        documentation_score: int,
        activity_score: int,
    ) -> int:
        score = 0

        if repository.description:
            score += 15

        if repository.language:
            score += 15

        if repository.languages:
            score += 15

        if repository.topics:
            score += 10

        if repository.dependencies:
            score += 10

        if not repository.is_fork:
            score += 15

        if not repository.is_archived:
            score += 10

        score += int(
            documentation_score * 0.10
        )

        score += int(
            activity_score * 0.10
        )

        score += min(
            repository.stars,
            10,
        )

        return min(score, 100)

    @staticmethod
    def _collect_languages(
        repositories: List[GitHubRepository],
    ) -> List[str]:
        languages = set()

        for repository in repositories:
            for language in repository.languages:
                languages.add(language)

        return sorted(languages)

    @staticmethod
    def _collect_dependencies(
        repositories: List[GitHubRepository],
    ) -> List[str]:
        dependencies = set()

        for repository in repositories:
            for dependency in repository.dependencies:
                dependencies.add(dependency)

        return sorted(dependencies)