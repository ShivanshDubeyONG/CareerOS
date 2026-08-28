import json

from app.services.ai.gemini_client import GeminiClient
from app.services.ai.github_scoring import GitHubScorer

from app.schemas.github_ai_schema import (
    GitHubAIAnalysis,
)

from app.schemas.github_score_schema import (
    GitHubPortfolioScore,
)

from app.schemas.github_schema import (
    GitHubProfile,
)


class GitHubAIAnalyzer:

    def __init__(self):

        self.gemini = GeminiClient()
        self.scorer = GitHubScorer()

    def analyze(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:

        repository_evidence = []

        # ==================================================
        # LLM PAYLOAD LIMITS
        # ==================================================

        MAX_FILE_PATHS_FOR_AI = 100
        MAX_README_CHARS_FOR_AI = 6000
        MAX_DEPENDENCIES_FOR_AI = 50
        MAX_TEST_FILES_FOR_AI = 50
        MAX_CONFIG_FILES_FOR_AI = 50
        MAX_SOURCE_DIRECTORIES_FOR_AI = 30

        for repository in profile.repositories:

            # --------------------------------------------------
            # README
            # --------------------------------------------------

            readme = (
                repository.readme
                or ""
            )

            if len(readme) > MAX_README_CHARS_FOR_AI:

                readme = (
                    readme[
                        :MAX_README_CHARS_FOR_AI
                    ]
                    + "\n\n[README truncated]"
                )

            # --------------------------------------------------
            # File paths
            # --------------------------------------------------

            file_paths = (
                repository.file_paths
                or []
            )

            file_paths = file_paths[
                :MAX_FILE_PATHS_FOR_AI
            ]

            # --------------------------------------------------
            # Dependencies
            # --------------------------------------------------

            dependencies = (
                repository.dependencies
                or []
            )

            dependencies = dependencies[
                :MAX_DEPENDENCIES_FOR_AI
            ]

            # --------------------------------------------------
            # Tests
            # --------------------------------------------------

            test_files = (
                repository.test_files
                or []
            )

            test_files = test_files[
                :MAX_TEST_FILES_FOR_AI
            ]

            # --------------------------------------------------
            # Config files
            # --------------------------------------------------

            config_files = (
                repository.config_files
                or []
            )

            config_files = config_files[
                :MAX_CONFIG_FILES_FOR_AI
            ]

            # --------------------------------------------------
            # Source directories
            # --------------------------------------------------

            source_directories = (
                repository.source_directories
                or []
            )

            source_directories = (
                source_directories[
                    :MAX_SOURCE_DIRECTORIES_FOR_AI
                ]
            )

            # --------------------------------------------------
            # Evidence
            # --------------------------------------------------

            evidence = {

                "name": repository.name,

                "full_name": repository.full_name,

                "description": repository.description,

                "url": repository.url,

                "language": repository.language,

                "languages": repository.languages,

                "topics": repository.topics,

                "stars": repository.stars,

                "forks": repository.forks,

                "is_fork": repository.is_fork,

                "fork_parent": (
                    repository.fork_parent
                ),

                "fork_contribution": {

                    "available": (
                        repository
                        .fork_contribution_available
                    ),

                    "unique_commits": (
                        repository
                        .fork_unique_commits
                    ),

                    "changed_files": (
                        repository
                        .fork_changed_files
                    ),

                    "additions": (
                        repository
                        .fork_additions
                    ),

                    "deletions": (
                        repository
                        .fork_deletions
                    ),
                },

                "readme": readme,

                "dependencies": dependencies,

                "dependency_files": (
                    repository.dependency_files
                    or []
                ),

                "file_paths": file_paths,

                "source_directories": (
                    source_directories
                ),

                "test_files": test_files,

                "config_files": config_files,

                "has_docker": (
                    repository.has_docker
                ),

                "has_frontend": (
                    repository.has_frontend
                ),

                "has_tests": (
                    repository.has_tests
                ),

                "activity": {

                    "commit_history_available": (
                        repository
                        .commit_history_available
                    ),

                    "total_commits": (
                        repository.total_commits
                    ),

                    "commits_last_30_days": (
                        repository
                        .commits_last_30_days
                    ),

                    "commits_last_90_days": (
                        repository
                        .commits_last_90_days
                    ),

                    "commits_last_180_days": (
                        repository
                        .commits_last_180_days
                    ),

                    "commits_last_365_days": (
                        repository
                        .commits_last_365_days
                    ),

                    "active_months_last_year": (
                        repository
                        .active_months_last_year
                    ),

                    "latest_commit_at": (
                        repository
                        .latest_commit_at
                    ),
                },

                "dates": {

                    "created_at": (
                        repository.created_at
                    ),

                    "updated_at": (
                        repository.updated_at
                    ),

                    "pushed_at": (
                        repository.pushed_at
                    ),
                },
            }

            repository_evidence.append(
                evidence
            )

        # ==================================================
        # PAYLOAD SIZE DIAGNOSTIC
        # ==================================================

        evidence_json = json.dumps(
            repository_evidence,
            ensure_ascii=False,
        )

        print(
            "GH AI evidence size:",
            f"{len(evidence_json):,} chars",
            flush=True,
        )

        # ==================================================
        # PROMPT
        # ==================================================

        prompt = f"""
You are the GitHub intelligence engine for CareerOS.

Evaluate this candidate's GitHub portfolio using ONLY the
repository evidence provided below.

Do NOT invent technologies, features, metrics, deployments,
tests, users, or achievements.

Do NOT assume README claims are implemented.

Judge each repository based on actual evidence.

Return the required GitHubAIAnalysis structured object.

Candidate username:
{profile.username}

Candidate name:
{profile.name}

Candidate bio:
{profile.bio}

Public repositories:
{profile.public_repository_count}

Followers:
{profile.followers}

Following:
{profile.following}

==================================================
REPOSITORY EVIDENCE
==================================================

{evidence_json}

==================================================
TECHNOLOGY EVIDENCE
==================================================

High-confidence evidence includes:

- GitHub language statistics
- dependency names
- dependency files
- Docker configuration
- configuration files
- clear source structure
- clear frontend structure

Medium-confidence evidence includes:

- directory structure
- file paths
- framework-specific files

Low-confidence evidence includes:

- README-only claims
- description-only claims
- topics alone

Only call a technology demonstrated when repository evidence
supports it.

==================================================
PROJECT EVALUATION
==================================================

For each repository:

- determine whether it is a meaningful project
- determine project stage
- determine project type
- score it from 0 to 10
- list technologies
- provide technology evidence
- explain the assessment

Project score should prioritize:

1. technical challenge
2. implementation depth
3. architecture
4. functional completeness
5. meaningful integrations
6. engineering maturity
7. originality
8. usefulness

Do NOT lower a strong project simply because it lacks tests,
Docker, deployment, or other optional engineering practices.

Do NOT reward polish over substance.

Do NOT reward repository size by itself.

Do NOT reward README claims without implementation evidence.

A sophisticated student project can legitimately score 8+.

==================================================
TUTORIALS AND FORKS
==================================================

Tutorial or learning repositories should generally not count
as meaningful portfolio projects unless there is substantial
original work.

A fork is not automatically bad.

Use fork contribution evidence where available.

==================================================
GENERAL RULE
==================================================

Base everything ONLY on the supplied evidence.

Missing evidence means unknown.

Never invent:

- technologies
- deployments
- tests
- databases
- features
- users
- production usage
- performance metrics
- contributions

Return the structured response exactly according to the schema.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        print(
            "GH AI Gemini request START",
            flush=True,
        )

        try:

            result = (
                self.gemini.generate_structured(
                    prompt,
                    GitHubAIAnalysis,
                )
            )

        except Exception as exc:

            print(
                "GH AI Gemini request FAILED:",
                repr(exc),
                flush=True,
            )

            raise

        print(
            "GH AI Gemini request DONE",
            flush=True,
        )

        return result

    def score(
        self,
        profile: GitHubProfile,
        analysis: GitHubAIAnalysis,
    ) -> GitHubPortfolioScore:

        return self.scorer.score(
            profile,
            analysis.projects,
        )