from app.schemas.github_ai_schema import (
    GitHubAIAnalysis,
    ProjectInsight,
    SkillEvidence,
)
from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)
from app.schemas.leetcode_schema import (
    LeetCodeAnalysis,
)
from app.schemas.linkedin_schema import (
    LinkedInAnalysis,
    LinkedInProfile,
    LinkedInProject,
)
from app.schemas.resume_schema import (
    ResumeData,
    ResumeLinks,
)
from app.services.unified.unified_service import (
    unified_service,
)


def build_resume():
    return ResumeData(
        name="Shivansh Dubey",
        skills=[
            "Python",
            "FastAPI",
            "Machine Learning",
            "Docker",
            "AWS",
        ],
        projects=(
            "CareerOS - AI career intelligence "
            "platform"
        ),
        links=ResumeLinks(
            github=(
                "https://github.com/"
                "ShivanshDubeyONG"
            ),
            linkedin=(
                "https://www.linkedin.com/in/"
                "shivansh-dubey-69a825310/"
            ),
            leetcode=(
                "https://leetcode.com/u/"
                "shivanshdubeyfr/"
            ),
        ),
    )


def build_github_profile():
    return GitHubProfile(
        username="ShivanshDubeyONG",
        name="Shivansh Dubey",
        bio="AI/ML developer",
        profile_url=(
            "https://github.com/"
            "ShivanshDubeyONG"
        ),
        public_repository_count=3,
        repositories=[
            GitHubRepository(
                name="CareerOS",
                full_name=(
                    "ShivanshDubeyONG/CareerOS"
                ),
                description=(
                    "AI-powered career "
                    "intelligence platform"
                ),
                url=(
                    "https://github.com/"
                    "ShivanshDubeyONG/CareerOS"
                ),
                language="Python",
                languages={
                    "Python": 12000,
                },
                dependencies=[
                    "fastapi",
                    "pydantic",
                    "google-generativeai",
                ],
                has_docker=True,
                has_tests=True,
            ),
            GitHubRepository(
                name="Marks-Predictor",
                full_name=(
                    "ShivanshDubeyONG/"
                    "Marks-Predictor"
                ),
                description=(
                    "Machine learning prediction "
                    "project"
                ),
                url=(
                    "https://github.com/"
                    "ShivanshDubeyONG/"
                    "Marks-Predictor"
                ),
                language="Python",
                languages={
                    "Python": 5000,
                },
                dependencies=[
                    "scikit-learn",
                    "pandas",
                    "numpy",
                ],
            ),
        ],
    )


def build_github_analysis():
    return GitHubAIAnalysis(
        projects=[
            ProjectInsight(
                repository=(
                    "ShivanshDubeyONG/CareerOS"
                ),
                meaningful_project=True,
                project_score=9.0,
                project_stage="active_development",
                project_type="ai_application",
                technologies=[
                    "Python",
                    "FastAPI",
                    "Gemini",
                    "Docker",
                    "GitHub API",
                ],
                assessment=(
                    "Substantial AI career "
                    "intelligence platform."
                ),
            ),
            ProjectInsight(
                repository=(
                    "ShivanshDubeyONG/"
                    "Marks-Predictor"
                ),
                meaningful_project=True,
                project_score=7.5,
                project_stage="completed",
                project_type="machine_learning",
                technologies=[
                    "Python",
                    "Scikit-learn",
                    "Pandas",
                    "NumPy",
                ],
                assessment=(
                    "End-to-end machine "
                    "learning project."
                ),
            ),
        ],
        technical_strengths=[
            "Python",
            "FastAPI",
            "Machine Learning",
            "Docker",
        ],
        demonstrated_skills=[
            SkillEvidence(
                skill="Python",
                confidence="high",
                evidence=(
                    "Used across multiple "
                    "meaningful repositories."
                ),
            ),
            SkillEvidence(
                skill="FastAPI",
                confidence="high",
                evidence=(
                    "Used in CareerOS backend."
                ),
            ),
            SkillEvidence(
                skill="Machine Learning",
                confidence="high",
                evidence=(
                    "Demonstrated in ML projects."
                ),
            ),
        ],
        evidence_gaps=[],
        overall_assessment=(
            "Strong technical portfolio."
        ),
        career_relevance=(
            "Relevant to AI/ML/software "
            "engineering roles."
        ),
        recommendations=[],
    )


def build_linkedin():
    profile = LinkedInProfile(
        name="Shivansh Dubey",
        headline="AI/ML Developer",
        location="India",
        skills=[
            "Python",
            "FastAPI",
            "AWS",
            "React",
        ],
        projects=[
            LinkedInProject(
                name="Marks Predictor",
                description=(
                    "Machine learning "
                    "prediction project."
                ),
            ),
        ],
    )

    analysis = LinkedInAnalysis(
        name="Shivansh Dubey",
        headline="AI/ML Developer",
        location="India",
        about=None,
        experience_count=1,
        education_count=0,
        skill_count=4,
        certification_count=1,
        project_count=1,
        language_count=0,
        organization_count=0,
        award_count=0,
        publication_count=0,
        volunteering_count=0,
        current_title="AI/ML Developer",
        current_company="CareerOS",
        claimed_skills=[
            "Python",
            "FastAPI",
            "AWS",
            "React",
        ],
        career_domains=[
            "machine_learning",
        ],
        skill_evidence=[],
        career_signals=[],
        signals=[],
    )

    return profile, analysis


def build_leetcode():
    return LeetCodeAnalysis(
        username="shivanshdubeyfr",
        total_solved=127,
        difficulty_distribution={
            "easy": 40.0,
            "medium": 45.0,
            "hard": 15.0,
        },
        medium_hard_ratio=0.60,
        difficulty_exposure="strong",
        strongest_skills=[
            "arrays",
            "hash table",
            "dynamic programming",
        ],
        languages=[
            "Python",
            "C++",
        ],
        dsa_coverage={
            "arrays": {},
            "strings": {},
            "trees": {},
            "graphs": {},
        },
        strong_areas=[
            "arrays",
            "dynamic programming",
        ],
        developing_areas=[
            "graphs",
        ],
        evidence_gaps=[],
        dsa_breadth_score=78.0,
        problem_solving_score=81.0,
        active_days=60,
        active_days_30d=12,
        active_days_90d=30,
        active_months=8,
        latest_activity="2026-08-16",
        recent_activity_ratio=0.50,
        activity_consistency="consistent",
        signals=[
            "active_problem_solver",
        ],
    )


def build_unified_profile():
    resume = build_resume()
    github_profile = build_github_profile()
    github_analysis = build_github_analysis()
    linkedin_profile, linkedin_analysis = build_linkedin()
    leetcode_analysis = build_leetcode()

    return unified_service.build_profile(
        resume=resume,
        github_profile=github_profile,
        github_analysis=github_analysis,
        linkedin_profile=linkedin_profile,
        linkedin_analysis=linkedin_analysis,
        leetcode_analysis=leetcode_analysis,
    )


def test_unified_profile_builds():
    unified = build_unified_profile()

    assert unified is not None


def test_all_sources_are_reconciled():
    unified = build_unified_profile()

    assert unified.source_status["resume"] is True
    assert unified.source_status["github"] is True
    assert unified.source_status["linkedin"] is True
    assert unified.source_status["leetcode"] is True


def test_skill_evidence_is_generated():
    unified = build_unified_profile()

    assert unified.skill_evidence

    skills = {
        skill.skill
        for skill in unified.skill_evidence
    }

    assert "python" in skills


def test_skill_evidence_tracks_sources():
    unified = build_unified_profile()

    python_skill = next(
        skill
        for skill in unified.skill_evidence
        if skill.skill == "python"
    )

    assert python_skill.resume_claimed is True
    assert python_skill.github_demonstrated is True


def test_project_evidence_is_generated():
    unified = build_unified_profile()

    assert unified.project_evidence

    project_names = {
        project.name
        for project in unified.project_evidence
    }

    assert "CareerOS" in project_names


def test_cross_source_findings_are_structured():
    unified = build_unified_profile()

    for finding in unified.findings:
        assert finding.severity
        assert finding.finding_type
        assert finding.subject
        assert finding.message