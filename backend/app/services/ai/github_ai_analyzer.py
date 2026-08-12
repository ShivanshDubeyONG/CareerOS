from app.schemas.github_ai_schema import GitHubAIAnalysis
from app.schemas.github_schema import GitHubProfile
from app.services.ai.github_scoring import GitHubScorer
from app.services.ai.gemini_client import GeminiClient


class GitHubAIAnalyzer:

    def __init__(self):
        self.gemini = GeminiClient()
        self.scorer = GitHubScorer()

    def analyze(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:

        evidence = self._build_evidence(
            profile
        )

        prompt = f"""
You are CareerOS's GitHub intelligence engine.

Your job is to evaluate a candidate's GitHub
portfolio using ONLY the repository evidence provided.

Evaluate EVERY repository.

For each repository determine:

1. Whether it is a meaningful professional project.
2. Project quality from 0 to 10.
3. Current project stage.
4. Project type.
5. Technologies actually demonstrated.
6. Evidence-based assessment.

PROJECT STAGES:

Use one of:

- prototype
- active_development
- completed
- production
- maintained
- learning
- archived

IMPORTANT EVALUATION RULES:

A project can be incomplete and still be technically
impressive.

Do NOT treat unfinished implementation as proof
that a project is low quality.

Distinguish between:

- technical ambition
- implementation quality
- current completeness
- engineering maturity
- real-world usefulness

An active project with substantial implementation
and sophisticated architecture can score highly even
if some planned components are unfinished.

Do not reward README claims when repository evidence
contradicts them.

Actual code structure, dependencies, languages,
configuration, tests, integrations, and repository
content are stronger evidence than future plans.

Do not invent technologies.

Do not assume a technology merely because the README
mentions that it is planned.

FORK OWNERSHIP:

Forks require special treatment.

A fork of a sophisticated upstream project is NOT
automatically evidence of the candidate's engineering
ability.

Use the provided fork comparison evidence.

If a fork has:

- zero unique commits
- zero changed files
- zero meaningful additions

then it should generally NOT count as a meaningful
original portfolio project.

If a fork contains substantial candidate-specific
changes, it may count as meaningful work.

Do NOT claim that the candidate contributed code
unless the supplied evidence supports that conclusion.

TUTORIAL / LEARNING PROJECTS:

Tutorials, coursework exercises, trivial experiments,
empty repositories, and basic practice projects should
generally not count as meaningful professional projects.

A small project can still be meaningful if it
demonstrates genuine engineering ability.

STARS:

Do not use GitHub stars as proof of technical ability.

QUANTITY:

Do not judge portfolio strength simply by repository
count.

The portfolio scoring engine separately rewards
meaningful project depth with diminishing returns.

YOUR TASK:

Evaluate every repository independently and provide
evidence-based conclusions.

GITHUB EVIDENCE:

{evidence}
"""

        return self.gemini.generate_structured(
            prompt=prompt,
            response_schema=GitHubAIAnalysis,
        )

    def score(
        self,
        profile: GitHubProfile,
        analysis: GitHubAIAnalysis,
    ):

        return self.scorer.score(
            profile,
            analysis.projects,
        )

    @staticmethod
    def _build_evidence(
        profile: GitHubProfile,
    ) -> dict:

        repositories = []

        for repository in profile.repositories:

            repositories.append(
                {
                    "name": repository.name,

                    "full_name": repository.full_name,

                    "description": repository.description,

                    "primary_language": (
                        repository.language
                    ),

                    "languages": (
                        repository.languages
                    ),

                    "dependencies": (
                        repository.dependencies
                    ),

                    "dependency_files": (
                        repository.dependency_files
                    ),

                    "topics": repository.topics,

                    "stars": repository.stars,

                    "forks": repository.forks,

                    "is_fork": repository.is_fork,

                    "is_archived": (
                        repository.is_archived
                    ),

                    "created_at": (
                        repository.created_at
                    ),

                    "updated_at": (
                        repository.updated_at
                    ),

                    "readme": (
                        repository.readme[:8000]
                        if repository.readme
                        else None
                    ),

                    # Repository structure
                    "source_directories": (
                        repository.source_directories
                    ),

                    "test_files": (
                        repository.test_files[:50]
                    ),

                    "config_files": (
                        repository.config_files[:50]
                    ),

                    "has_docker": (
                        repository.has_docker
                    ),

                    "has_frontend": (
                        repository.has_frontend
                    ),

                    "has_tests": (
                        repository.has_tests
                    ),

                    # Fork ownership evidence
                    "fork_parent": (
                        repository.fork_parent
                    ),

                    "fork_unique_commits": (
                        repository.fork_unique_commits
                    ),

                    "fork_changed_files": (
                        repository.fork_changed_files
                    ),

                    "fork_additions": (
                        repository.fork_additions
                    ),

                    "fork_deletions": (
                        repository.fork_deletions
                    ),

                    "fork_contribution_available": (
                        repository.fork_contribution_available
                    ),
                }
            )

        return {
            "profile": {
                "username": profile.username,

                "name": profile.name,

                "bio": profile.bio,

                "public_repository_count": (
                    profile.public_repository_count
                ),

                "followers": profile.followers,

                "following": profile.following,
            },

            "repositories": repositories,
        }