from app.integrations.github.github_analyzer import GitHubAnalyzer
from app.integrations.github.github_client import GitHubClient
from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)
from app.services.ai.github_ai_analyzer import GitHubAIAnalyzer


USERNAME = "ShivanshDubeyONG"


client = GitHubClient()
github_analyzer = GitHubAnalyzer()
ai_analyzer = GitHubAIAnalyzer()


print("\n========================================")
print("       CAREEROS GITHUB AI ANALYSIS")
print("========================================")


print("\nFetching GitHub profile...")

profile_data = client.get_user(USERNAME)

repositories_data = client.get_repositories(
    USERNAME
)

print(
    f"Found {len(repositories_data)} repositories."
)


repositories = []


for repo in repositories_data:

    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    print(
        f"Processing: {repo_name}"
    )

    try:
        languages = (
            client.get_repository_languages(
                owner,
                repo_name,
            )
        )
    except Exception:
        languages = {}

    try:
        readme = (
            client.get_repository_readme(
                owner,
                repo_name,
            )
        )
    except Exception:
        readme = None

    dependency_files = {}
    dependency_file_names = []

    for filename in [
        "requirements.txt",
        "pyproject.toml",
        "package.json",
    ]:

        try:
            content = client.get_repository_file(
                owner,
                repo_name,
                filename,
            )

            if content:
                dependency_files[
                    filename
                ] = content

                dependency_file_names.append(
                    filename
                )

        except Exception:
            pass

    dependencies = (
        github_analyzer.extract_dependencies(
            dependency_files
        )
    )

    repository = GitHubRepository(
        name=repo["name"],
        full_name=repo["full_name"],
        description=repo.get(
            "description"
        ),
        url=repo["html_url"],

        language=repo.get(
            "language"
        ),

        languages=languages,

        stars=repo.get(
            "stargazers_count",
            0,
        ),

        forks=repo.get(
            "forks_count",
            0,
        ),

        topics=repo.get(
            "topics",
            [],
        ),

        is_fork=repo.get(
            "fork",
            False,
        ),

        is_archived=repo.get(
            "archived",
            False,
        ),

        default_branch=repo.get(
            "default_branch"
        ),

        created_at=repo.get(
            "created_at"
        ),

        updated_at=repo.get(
            "updated_at"
        ),

        readme=readme,

        dependencies=dependencies,

        dependency_files=dependency_file_names,
    )

    repositories.append(
        repository
    )


github_profile = GitHubProfile(
    username=profile_data["login"],

    name=profile_data.get(
        "name"
    ),

    bio=profile_data.get(
        "bio"
    ),

    profile_url=profile_data[
        "html_url"
    ],

    public_repository_count=profile_data.get(
        "public_repos",
        0,
    ),

    followers=profile_data.get(
        "followers",
        0,
    ),

    following=profile_data.get(
        "following",
        0,
    ),

    repositories=repositories,
)


print("\nSending actual GitHub evidence to Gemini...")

analysis = ai_analyzer.analyze(
    github_profile
)


print("\n========================================")
print("          CAREEROS AI RESULT")
print("========================================")


print("\nOVERALL ASSESSMENT")
print(analysis.overall_assessment)


print("\nTECHNICAL STRENGTHS")

for strength in analysis.technical_strengths:
    print(f"- {strength}")


print("\nDEMONSTRATED SKILLS")

for skill in analysis.demonstrated_skills:

    print(
        f"- {skill.skill} "
        f"[{skill.confidence}]"
    )

    print(
        f"  Evidence: {skill.evidence}"
    )


print("\nSTRONGEST PROJECTS")

for project in analysis.strongest_projects:

    print(
        f"\n- {project.repository}"
    )

    print(
        f"  Type: {project.project_type}"
    )

    print(
        "  Technologies:",
        ", ".join(
            project.technologies
        ),
    )

    print(
        f"  Assessment: "
        f"{project.assessment}"
    )


print("\nEVIDENCE GAPS")

for gap in analysis.evidence_gaps:

    print(
        f"- {gap.area}"
    )

    print(
        f"  Reason: {gap.reason}"
    )


print("\nCAREER RELEVANCE")
print(analysis.career_relevance)


print("\nRECOMMENDATIONS")

for recommendation in analysis.recommendations:
    print(
        f"- {recommendation}"
    )


client.close()


print("\n========================================")
print("       GITHUB AI ANALYSIS COMPLETE")
print("========================================")