import json

from app.services.ai.gemini_client import GeminiClient
from app.services.ai.github_scoring import GitHubScorer

from app.schemas.github_ai_schema import (
    GitHubAIAnalysis,
    ProjectInsight,
    TechnologyEvidence,
    SkillEvidence,
    EvidenceGap,
)
from app.schemas.github_schema import GitHubProfile


class GitHubAIAnalyzer:

    def __init__(self):
        self.gemini = GeminiClient()

    def analyze(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:

        if not self.gemini.client:
            print(
                "GH AI: Gemini client not configured, using heuristic fallback",
                flush=True,
            )
            return self._heuristic_fallback(profile)

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

Untouched or empty forks without candidate contributions should not
count as meaningful projects. However, collaborative, hackathon, and active
forks with substantive technical depth, architecture, or implementation (e.g.,
digital twin models, ML pipelines, or software platforms) MUST be recognized
and fully credited as meaningful projects.

A meaningful student or hackathon project can score 8+ when the technical
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
                "GH AI Gemini request FAILED, using deterministic heuristic fallback:",
                repr(exc),
                flush=True,
            )

            return self._heuristic_fallback(profile)

        print(
            "GH AI Gemini request DONE",
            flush=True,
        )

        return result

    def _heuristic_fallback(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:
        insights: list[ProjectInsight] = []
        tech_to_repos: dict[str, list[str]] = {}
        has_tests_any = False
        has_docs_any = False

        for repo in profile.repositories:
            techs = []
            if repo.language:
                techs.append(repo.language)
            if repo.languages:
                techs.extend(list(repo.languages.keys())[:5])
            if repo.dependencies:
                techs.extend(repo.dependencies[:6])
            techs = list(dict.fromkeys(techs))

            for t in techs:
                tech_to_repos.setdefault(t, []).append(repo.name)

            has_readme = bool(repo.readme and len(repo.readme.strip()) > 80)
            if has_readme:
                has_docs_any = True
            if repo.has_tests:
                has_tests_any = True

            base_score = 5.0
            if has_readme:
                base_score += 1.5
            if repo.has_tests:
                base_score += 1.5
            if repo.has_docker:
                base_score += 1.0
            if repo.stars and repo.stars > 0:
                base_score += 1.0
            project_score = min(10.0, max(2.0, base_score))

            has_substance = (
                repo.stars > 0
                or len(repo.file_paths or []) >= 2
                or has_readme
                or (repo.dependencies and len(repo.dependencies) > 0)
                or repo.fork_unique_commits > 0
            )
            is_meaningful = (
                not repo.is_fork
                or repo.fork_contribution_available
                or repo.fork_unique_commits > 0
                or has_readme
                or len(repo.file_paths or []) >= 2
            ) and has_substance

            stage = "production" if repo.has_docker and repo.has_tests else "in_progress" if (repo.file_paths or []) else "prototype"
            p_type = "fullstack" if repo.has_frontend and repo.has_tests else "frontend" if repo.has_frontend else "backend"

            insights.append(
                ProjectInsight(
                    repository=repo.name,
                    meaningful_project=is_meaningful,
                    project_score=round(project_score, 1),
                    project_stage=stage,
                    project_type=p_type,
                    technologies=techs[:8],
                    technology_evidence=[
                        TechnologyEvidence(
                            technology=t,
                            evidence_sources=[f"Repository {repo.name}"],
                            confidence="high" if len(tech_to_repos.get(t, [])) > 1 else "medium",
                        )
                        for t in techs[:5]
                    ],
                    assessment=f"Repository '{repo.name}' demonstrates implementation in {', '.join(techs[:3]) or 'software development'}.",
                )
            )

        top_techs = sorted(tech_to_repos.keys(), key=lambda k: len(tech_to_repos[k]), reverse=True)
        demonstrated_skills = [
            SkillEvidence(
                skill=t,
                confidence="high" if len(tech_to_repos[t]) > 1 else "medium",
                evidence=f"Demonstrated across {len(tech_to_repos[t])} project(s): {', '.join(tech_to_repos[t][:3])}",
            )
            for t in top_techs[:8]
        ]

        gaps = []
        if not has_tests_any:
            gaps.append(
                EvidenceGap(
                    area="Automated Testing",
                    reason="No explicit test frameworks or test files were identified across repositories.",
                )
            )
        if not has_docs_any:
            gaps.append(
                EvidenceGap(
                    area="Documentation",
                    reason="README documentation is minimal or absent in one or more core repositories.",
                )
            )

        top_str = ", ".join(top_techs[:4]) or "software development"
        return GitHubAIAnalysis(
            projects=insights,
            technical_strengths=top_techs[:8],
            demonstrated_skills=demonstrated_skills,
            evidence_gaps=gaps,
            overall_assessment=f"Candidate maintains {len(profile.repositories)} public repositories demonstrating practical capability in {top_str}.",
            career_relevance=f"Demonstrates hands-on repository activity and project development in {top_str}.",
            recommendations=[
                "Add automated unit and integration tests across core projects to signal engineering rigor.",
                "Include detailed README files with architecture overview and setup instructions.",
                "Add live deployment links and demo credentials in project descriptions.",
            ],
        )
