from typing import List

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

Do NOT assume that README claims are true unless
repository evidence supports them.

Do NOT reward a project simply because its name sounds
impressive.

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
EVALUATION RULES
==================================================

For EVERY repository:

1. Determine whether it is a meaningful portfolio project.

A meaningful project should demonstrate substantial
engineering, problem solving, implementation, or domain
knowledge.

Examples:

- End-to-end applications
- ML/data projects with actual implementation
- Backend systems
- Full-stack applications
- APIs
- Developer tools
- AI applications
- Data engineering systems
- Infrastructure/DevOps projects
- Non-trivial browser/mobile applications

Do NOT automatically mark something meaningful merely
because it contains many files.

Do NOT automatically reject small projects if they solve
a real problem well.

2. Identify the project stage:

Possible values include:

- learning
- prototype
- active_development
- completed
- maintained
- abandoned

Use repository evidence.

3. Identify the project type.

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

IMPORTANT:

A project that is technically sophisticated but incomplete
can still score well, but do not treat planned features
as implemented features.

5. Identify technologies ONLY when supported by:

- source files
- dependency files
- language data
- configuration
- repository structure

Do not blindly copy technologies mentioned in a README.

6. Write a concise assessment explaining WHY the project
received its score.

7. Detect tutorial/learning repositories.

Repositories clearly following a tutorial/course should
generally be marked:

meaningful_project = false

unless there is strong evidence of substantial original
development.

8. Detect forks carefully.

A fork is NOT automatically bad.

Use the fork comparison evidence:

- unique commits
- changed files
- additions
- deletions

A fork with essentially no candidate changes should
generally NOT count as meaningful original portfolio work.

A heavily modified fork may still be meaningful.

Never claim that a candidate made substantial changes
unless the supplied evidence supports it.

9. Quantity matters.

A candidate with several substantive projects should
receive more portfolio-depth credit than a candidate with
only one project.

However, do NOT reward repository spam.

Ten tiny projects should not beat three substantial ones.

10. Distinguish repository activity from project quality.

Recent commits do NOT automatically mean a project is good.

A project can be high quality but inactive because it is
finished.

Likewise, frequent commits do not automatically indicate
high engineering quality.


==================================================
IMPORTANT
==================================================

Base every evaluation on the supplied evidence.

Do not invent:

- technologies
- deployments
- tests
- databases
- frontend code
- features
- users
- production usage
- contributions

If evidence is missing, say that evidence is missing.

Return the structured response exactly according to the
provided schema.
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