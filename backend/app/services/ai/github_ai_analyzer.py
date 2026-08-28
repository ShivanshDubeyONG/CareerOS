import json

from app.services.ai.gemini_client import GeminiClient

from app.schemas.github_ai_schema import GitHubAIAnalysis
from app.schemas.github_schema import GitHubProfile


class GitHubAIAnalyzer:

    def __init__(self):
        self.gemini = GeminiClient()

    def analyze(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:

        # ==================================================
        # BUILD SMALL, HIGH-VALUE EVIDENCE PACKET
        # ==================================================

        repositories = []

        for repository in profile.repositories:

            readme = repository.readme or ""

            if len(readme) > 2500:
                readme = (
                    readme[:2500]
                    + "\n[README truncated]"
                )

            file_paths = (
                repository.file_paths or []
            )[:60]

            dependencies = (
                repository.dependencies or []
            )[:30]

            dependency_files = (
                repository.dependency_files or []
            )[:10]

            source_directories = (
                repository.source_directories or []
            )[:20]

            test_files = (
                repository.test_files or []
            )[:20]

            config_files = (
                repository.config_files or []
            )[:20]

            repositories.append(
                {
                    "name": repository.name,
                    "description": repository.description,
                    "language": repository.language,
                    "languages": repository.languages,
                    "topics": repository.topics,
                    "stars": repository.stars,
                    "forks": repository.forks,
                    "is_fork": repository.is_fork,

                    "readme": readme,

                    "dependencies": dependencies,
                    "dependency_files": dependency_files,

                    "file_paths": file_paths,

                    "source_directories": (
                        source_directories
                    ),

                    "test_files": test_files,
                    "config_files": config_files,

                    "has_docker": repository.has_docker,
                    "has_frontend": repository.has_frontend,
                    "has_tests": repository.has_tests,
                }
            )

        evidence = {
            "username": profile.username,
            "name": profile.name,
            "bio": profile.bio,
            "public_repository_count": (
                profile.public_repository_count
            ),
            "followers": profile.followers,
            "following": profile.following,
            "repositories": repositories,
        }

        evidence_json = json.dumps(
            evidence,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        # HARD GLOBAL LIMIT.
        # This is intentionally conservative for Render.
        MAX_EVIDENCE_CHARS = 14000

        if len(evidence_json) > MAX_EVIDENCE_CHARS:
            evidence_json = (
                evidence_json[
                    :MAX_EVIDENCE_CHARS
                ]
                + "\n[Evidence truncated]"
            )

        print(
            "GH AI evidence size:",
            f"{len(evidence_json):,} chars",
            flush=True,
        )

        # ==================================================
        # SMALL GEMINI PROMPT
        # ==================================================

        prompt = f"""
You are CareerOS GitHub Intelligence.

Analyze the candidate's GitHub portfolio using ONLY the evidence
below.

Never invent facts.

Do not treat README claims as implemented unless other evidence
supports them.

Evaluate actual technical substance, implementation depth,
architecture, usefulness, originality, and engineering maturity.

Do not over-penalize missing tests, Docker, deployment, or
professional experience.

Tutorial repositories and untouched forks should generally not
count as meaningful projects.

A meaningful student project can score 8+ when the technical
evidence supports it.

Return ONLY valid JSON.
No markdown.
No ```json fences.

The JSON must contain:

projects:
array of objects containing:
repository
meaningful_project
project_score
project_stage
project_type
technologies
technology_evidence
assessment

technology_evidence:
array of objects containing:
technology
evidence_sources
confidence

demonstrated_skills:
array of objects containing:
skill
confidence
evidence

evidence_gaps:
array of objects containing:
area
reason

Also return:
technical_strengths
overall_assessment
career_relevance
recommendations

Project score is 0-10.

Use evidence confidence values:
high
medium
low

Evidence:

{evidence_json}
"""

        # ==================================================
        # GEMINI
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

            cleaned = (
                raw_response.strip()
            )

            # Remove markdown fences if Gemini
            # ignores the instruction.
            if cleaned.startswith(
                "```"
            ):

                if cleaned.startswith(
                    "```json"
                ):
                    cleaned = cleaned[7:]
                else:
                    cleaned = cleaned[3:]

                if cleaned.endswith(
                    "```"
                ):
                    cleaned = cleaned[:-3]

                cleaned = cleaned.strip()

            result = (
                GitHubAIAnalysis
                .model_validate_json(
                    cleaned
                )
            )

            print(
                "GH AI JSON validation DONE",
                flush=True,
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
