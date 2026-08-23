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

        for repository in profile.repositories:

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

                "readme": (
                    repository.readme
                    or ""
                ),

                "dependencies": (
                    repository.dependencies
                ),

                "dependency_files": (
                    repository.dependency_files
                ),

                "file_paths": (
                    repository.file_paths
                ),

                "source_directories": (
                    repository.source_directories
                ),

                "test_files": (
                    repository.test_files
                ),

                "config_files": (
                    repository.config_files
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

        prompt = f"""
You are the GitHub intelligence engine for CareerOS.

Your job is to evaluate a candidate's GitHub portfolio
using ONLY the repository evidence provided below.

Do NOT invent information.

Do NOT assume README claims are implemented.

Do NOT reward repository names.

Do NOT confuse repository size with engineering quality.

The candidate is:

Username:
{profile.username}

Name:
{profile.name}

Bio:
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

{repository_evidence}


==================================================
TECHNOLOGY EVIDENCE RULES
==================================================

For every meaningful repository, identify technologies
that are actually supported by the supplied evidence.

Technology evidence has different strengths.

HIGH CONFIDENCE evidence:

- GitHub language statistics
- Explicit dependency names
- dependency files such as requirements.txt,
  pyproject.toml, package.json
- Docker configuration
- configuration files
- clear source-code structure
- clear frontend structure

MEDIUM CONFIDENCE evidence:

- source directory structure
- file extensions
- framework-specific project files
- repository configuration

LOW CONFIDENCE evidence:

- README-only claims
- repository description-only claims
- topics alone

IMPORTANT:

A README saying:

"Built with React, FastAPI, PostgreSQL and Docker"

does NOT prove all four technologies.

Only mark them as demonstrated when the repository evidence
supports them.

For every technology returned in technology_evidence:

technology:
    canonical technology name

evidence_sources:
    one or more of:
        "language"
        "dependency"
        "dependency_file"
        "source_structure"
        "configuration"
        "docker"
        "frontend_structure"
        "file_path"
        "readme"
        "topic"

confidence:
    "high"
    "medium"
    "low"

Examples:

Python detected in GitHub language statistics:

technology:
    Python

evidence_sources:
    ["language"]

confidence:
    high


FastAPI found in dependency information:

technology:
    FastAPI

evidence_sources:
    ["dependency", "dependency_file"]

confidence:
    high


Dockerfile detected:

technology:
    Docker

evidence_sources:
    ["docker", "configuration"]

confidence:
    high


React appears ONLY in README:

technology:
    React

evidence_sources:
    ["readme"]

confidence:
    low


==================================================
PROJECT EVALUATION RULES
==================================================

For EVERY repository:

1. Determine whether it is a meaningful portfolio project.

Meaningful examples:

- End-to-end applications
- ML/data projects with actual implementation
- Backend systems
- Full-stack applications
- APIs
- Developer tools
- AI applications
- Data engineering systems
- Infrastructure/DevOps projects
- Browser/mobile applications

Do NOT automatically mark something meaningful merely
because it contains many files.

Do NOT automatically reject small projects if they solve
a real problem well.

2. Identify project stage:

Possible values:

- learning
- prototype
- active_development
- completed
- maintained
- abandoned

3. Identify project type.

Examples:

- machine_learning
- backend_service
- full_stack
- web_application
- ai_application
- data_engineering
- browser_extension
- mobile_application
- developer_tool
- cli
- automation
- library
- learning_project

4. Give a project score from 0 to 10.

Consider:

- technical complexity
- implementation depth
- completeness
- engineering practices
- testing
- architecture
- integrations
- deployment
- originality
- real-world usefulness

Do NOT treat planned features as implemented.

5. Detect tutorial/learning repositories.

Tutorial/course repositories should generally be:

meaningful_project = false

unless strong evidence shows substantial original
development.

6. Detect forks carefully.

A fork is not automatically bad.

Use:

- unique commits
- changed files
- additions
- deletions

A fork with essentially no candidate changes should
generally NOT count as meaningful original portfolio work.

7. Distinguish activity from quality.

Recent commits do not automatically mean high quality.

Frequent commits do not automatically mean strong
engineering.

==================================================
GENERAL RULE
==================================================

Base every evaluation ONLY on supplied evidence.

Never invent:

- technologies
- deployments
- tests
- databases
- frontend code
- features
- users
- production usage
- contributions

If evidence is missing, say it is missing.

Return the structured response exactly according
to the provided schema.
"""

        return self.gemini.generate_structured(
            prompt,
            GitHubAIAnalysis,
        )

    def score(
        self,
        profile: GitHubProfile,
        analysis: GitHubAIAnalysis,
    ) -> GitHubPortfolioScore:

        return self.scorer.score(
            profile,
            analysis.projects,
        )