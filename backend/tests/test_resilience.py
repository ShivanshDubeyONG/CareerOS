import unittest.mock as mock
import pytest

from app.schemas.resume_schema import ResumeData, ResumeLinks
from app.schemas.github_schema import GitHubProfile, GitHubRepository
from app.services.ai.gemini_client import GeminiClient
from app.services.resume.resume_rater import ResumeRater
from app.services.ai.github_ai_analyzer import GitHubAIAnalyzer
from app.integrations.github.github_client import GitHubClient


def test_gemini_client_without_api_key():
    """Verify GeminiClient does not crash the application when GEMINI_API_KEY is not set."""
    with mock.patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
        client = GeminiClient()
        assert client.client is None


def test_resume_rater_heuristic_fallback():
    """Verify ResumeRater generates a complete valid rating even when Gemini fails."""
    resume = ResumeData(
        name="Alex Engineer",
        email="alex@example.com",
        phone="+1 555-0100",
        skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        education="Tech University - B.S. Computer Science",
        experience="Software Corp - Backend Engineer: Built scalable FastAPI services and pipelines.",
        projects="CareerOS - Fullstack AI career intelligence platform.",
        links=ResumeLinks(github="https://github.com/alex"),
    )

    rater = ResumeRater()
    # Mock Gemini to raise an exception simulating quota expiration or 503
    with mock.patch.object(rater.gemini, "generate_text", side_effect=Exception("503 Service Unavailable")):
        rating = rater.rate(resume)
        assert rating is not None
        assert rating.overall_score >= 0
        assert rating.overall_score <= 100
        assert rating.skills.score > 0
        assert rating.data_quality.profile_data_available is True
        assert len(rating.recommendations) > 0


def test_github_ai_analyzer_heuristic_fallback():
    """Verify GitHubAIAnalyzer generates complete valid analysis even when Gemini fails."""
    profile = GitHubProfile(
        username="alexdev",
        name="Alex Developer",
        bio="Full stack developer",
        profile_url="https://github.com/alexdev",
        public_repository_count=2,
        repositories=[
            GitHubRepository(
                name="my-project",
                full_name="alexdev/my-project",
                url="https://github.com/alexdev/my-project",
                language="Python",
                languages={"Python": 10000},
                dependencies=["fastapi", "uvicorn"],
                has_docker=True,
                has_tests=True,
                file_paths=["main.py", "test_main.py", "Dockerfile"],
                readme="# My Project\nA production-grade API service.",
            )
        ],
    )

    analyzer = GitHubAIAnalyzer()
    with mock.patch.object(analyzer.gemini, "generate_text", side_effect=Exception("ResourceExhausted 429")):
        analysis = analyzer.analyze(profile)
        assert analysis is not None
        assert len(analysis.projects) == 1
        assert analysis.projects[0].repository == "my-project"
        assert analysis.projects[0].project_score > 0
        assert len(analysis.demonstrated_skills) > 0
        assert len(analysis.recommendations) > 0


def test_github_client_auto_fallback_on_401():
    """Verify GitHubClient drops invalid/expired tokens and retries unauthenticated."""
    client = GitHubClient()
    client.client.headers["Authorization"] = "Bearer expired_fake_pat_token"

    mock_401 = mock.MagicMock(status_code=401)
    mock_200 = mock.MagicMock(status_code=200)

    # First request returns 401, subsequent unauthenticated request returns 200
    with mock.patch.object(client.client, "get", side_effect=[mock_401, mock_200]) as mock_get:
        response = client._get("/users/octocat")
        assert response.status_code == 200
        assert "Authorization" not in client.client.headers
        assert mock_get.call_count == 2
