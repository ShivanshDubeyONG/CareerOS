from typing import Dict

from app.schemas.github_ai_schema import GitHubAIAnalysis
from app.schemas.github_schema import GitHubProfile
from app.services.ai.gemini_client import GeminiClient


class GitHubAIAnalyzer:
    def __init__(self):
        self.gemini = GeminiClient()

    def analyze(
        self,
        profile: GitHubProfile,
    ) -> GitHubAIAnalysis:

        evidence = self._build_evidence(profile)

        prompt = f"""
You are the GitHub intelligence engine inside CareerOS,
an AI-powered career intelligence platform.

Your job is to analyze ONLY the evidence provided below.

Do not invent projects, technologies, experience, achievements,
or skills that are not supported by the evidence.

Important rules:

1. Distinguish clearly between evidence and inference.
2. A README claim alone is weaker evidence than actual dependencies,
   languages, repository structure, or repeated technical evidence.
3. Do not treat stars or repository count as proof of technical skill.
4. Do not reward repository quantity over project substance.
5. Identify technologies that are genuinely demonstrated.
6. Identify important areas where evidence is missing or weak.
7. Assess projects from a software-engineering/career perspective.
8. Recommendations must be specific and actionable.
9. Do not produce an arbitrary overall numeric score.
10. This analysis will later be combined with resume, LinkedIn,
    and LeetCode evidence, so keep it evidence-grounded.

GITHUB EVIDENCE:

{evidence}
"""

        return self.gemini.generate_structured(
            prompt=prompt,
            response_schema=GitHubAIAnalysis,
        )

    @staticmethod
    def _build_evidence(
        profile: GitHubProfile,
    ) -> Dict:

        repositories = []

        for repository in profile.repositories:

            readme = repository.readme or ""

            # Prevent an unusually large README from dominating
            # the model input while retaining useful documentation.
            readme_excerpt = readme[:8000]

            repositories.append(
                {
                    "name": repository.name,
                    "description": repository.description,

                    "primary_language": (
                        repository.language
                    ),

                    "languages": repository.languages,

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

                    "readme": readme_excerpt,
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