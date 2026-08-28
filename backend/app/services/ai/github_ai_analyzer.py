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
            # Test files
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
            # Repository evidence
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
        # GEMINI PROMPT
        # ==================================================

        prompt = f"""
You are the GitHub intelligence engine for CareerOS.

Evaluate this candidate's GitHub portfolio using ONLY the
repository evidence provided below.

Do NOT invent technologies, features, metrics, deployments,
tests, users, or achievements.

Do NOT assume README claims are implemented.

Judge each repository based on actual evidence.

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

For every meaningful technology, identify:

- technology
- evidence sources
- confidence

Confidence must be one of:

- high
- medium
- low

Evidence sources may include:

- language
- dependency
- dependency_file
- source_structure
- configuration
- docker
- frontend_structure
- file_path
- readme
- topic

==================================================
PROJECT EVALUATION
==================================================

For each repository:

1. Determine whether it is a meaningful portfolio project.

2. Determine the project stage.

Possible stages:

- learning
- prototype
- active_development
- completed
- maintained
- abandoned

3. Determine the project type.

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

4. Score the project from 0 to 10.

Use these dimensions:

A. Technical challenge — 20%

Consider:

- algorithmic complexity
- ML/AI complexity
- backend/system complexity
- data processing
- architecture
- external APIs
- engineering constraints

B. Implementation depth — 20%

Consider:

- substantive implementation
- application logic
- model implementation
- data pipelines
- APIs
- reusable modules
- error handling
- actual functionality

Do NOT equate repository size with implementation depth.

C. Architecture and system design — 15%

Consider:

- modularity
- separation of concerns
- service boundaries
- reusable components
- data flow
- API structure
- maintainability

D. Functional completeness — 15%

Consider:

- whether the main problem is actually solved
- whether core workflows are implemented
- whether components connect correctly
- whether the project represents a usable system

A prototype can still score highly if it is technically substantial.

E. Integrations and technical sophistication — 10%

Reward meaningful integration of:

- external APIs
- LLMs
- databases
- authentication
- ML models
- third-party services
- frontend/backend systems
- data pipelines

Only reward integrations supported by evidence.

F. Engineering maturity — 10%

Consider:

- testing
- dependency management
- configuration
- logging
- error handling
- CI/CD
- Docker
- documentation
- code organization

Missing tests or Docker should NOT destroy an otherwise
technically strong project.

G. Originality and ownership — 5%

Consider:

- original problem selection
- personal implementation
- unique features
- meaningful modifications

Tutorials and untouched forks should score poorly.

H. Real-world usefulness — 5%

Consider:

- practical problem solved
- usefulness to users
- applicability outside tutorials
- meaningful automation/productivity value

==================================================
SCORING CALIBRATION
==================================================

9.0–10.0:

Exceptional student/early-career project with substantial
technical challenge, deep implementation, strong architecture,
meaningful functionality and clear ownership.

8.0–8.9:

Very strong project clearly beyond a basic tutorial.

7.0–7.9:

Strong project with meaningful implementation and good depth,
but with noticeable limitations.

6.0–6.9:

Solid project that is functional and meaningful but relatively
standard or limited in depth.

5.0–5.9:

Moderate project with useful implementation but limited depth.

4.0–4.9:

Weak project that is basic, incomplete, highly tutorial-like,
or shallow.

0.0–3.9:

Very weak portfolio project, trivial implementation,
placeholder work, or extremely incomplete.

IMPORTANT:

- Missing tests do NOT automatically mean a low score.
- Missing Docker does NOT automatically mean a low score.
- Deployment is NOT required for a high score.
- A sophisticated student project can score 8+.
- Prototype is a project stage, not a quality score.
- Do not reward repository size by itself.
- Do not reward README claims without supporting evidence.
- Do not penalize the same missing feature multiple times.
- Missing evidence means unknown, not false.
- Do not invent planned features.
- Judge projects according to what they actually attempt to accomplish.

==================================================
TUTORIALS AND FORKS
==================================================

Tutorial or learning repositories should generally be:

meaningful_project = false

unless there is strong evidence of substantial original work.

A fork is not automatically bad.

Use:

- unique commits
- changed files
- additions
- deletions

to determine whether meaningful original contribution exists.

==================================================
ACTIVITY
==================================================

Do not confuse activity with quality.

Recent commits do not automatically mean high quality.

Frequent commits do not automatically mean strong engineering.

Inactivity does not automatically mean low quality if the project
appears complete.

==================================================
FINAL RESPONSE FORMAT
==================================================

Return ONLY valid JSON.

Do NOT use markdown.

Do NOT wrap the response in ```json fences.

The top-level JSON object MUST contain:

projects
technical_strengths
demonstrated_skills
evidence_gaps
overall_assessment
career_relevance
recommendations

Each project MUST contain:

repository
meaningful_project
project_score
project_stage
project_type
technologies
technology_evidence
assessment

Each technology_evidence item MUST contain:

technology
evidence_sources
confidence

Each demonstrated_skills item MUST contain:

skill
confidence
evidence

Each evidence_gaps item MUST contain:

area
reason

Return JSON only.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        print(
            "GH AI Gemini request START",
            flush=True,
        )

        try:

            raw_response = (
                self.gemini.generate_text(
                    prompt
                )
            )

            print(
                "GH AI raw response received",
                flush=True,
            )

            # ----------------------------------------------
            # Remove accidental markdown fences if Gemini
            # ignores the instruction and returns them.
            # ----------------------------------------------

            cleaned_response = (
                raw_response.strip()
            )

            if (
                cleaned_response.startswith(
                    "```"
                )
            ):

                cleaned_response = (
                    cleaned_response
                    .replace(
                        "```json",
                        "",
                        1,
                    )
                    .replace(
                        "```",
                        "",
                        1,
                    )
                    .strip()
                )

            result = (
                GitHubAIAnalysis
                .model_validate_json(
                    cleaned_response
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