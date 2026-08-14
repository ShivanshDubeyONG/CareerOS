from app.integrations.github.github_analyzer import (
    GitHubAnalyzer,
)
from app.integrations.github.github_client import (
    GitHubClient,
)
from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)
from app.services.ai.github_ai_analyzer import (
    GitHubAIAnalyzer,
)


USERNAME = "ShivanshDubeyONG"


client = GitHubClient()

github_analyzer = GitHubAnalyzer()

ai_analyzer = GitHubAIAnalyzer()


print("\n========================================")
print("       CAREEROS GITHUB INTELLIGENCE")
print("========================================")


profile_data = client.get_user(
    USERNAME
)

repositories_data = client.get_repositories(
    USERNAME
)


repositories = []


for repo in repositories_data:

    owner = repo["owner"]["login"]

    repo_name = repo["name"]

    default_branch = repo.get(
        "default_branch",
        "main",
    )

    print(
        f"Processing: {repo_name}"
    )

    # -------------------------------
    # Languages
    # -------------------------------

    try:

        languages = (
            client.get_repository_languages(
                owner,
                repo_name,
            )
        )

    except Exception:

        languages = {}

    # -------------------------------
    # README
    # -------------------------------

    try:

        readme = (
            client.get_repository_readme(
                owner,
                repo_name,
            )
        )

    except Exception:

        readme = None

    # -------------------------------
    # Dependencies
    # -------------------------------

    dependency_files = {}

    dependency_file_names = []

    for filename in [
        "requirements.txt",
        "pyproject.toml",
        "package.json",
    ]:

        try:

            content = (
                client.get_repository_file(
                    owner,
                    repo_name,
                    filename,
                )
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

    # -------------------------------
    # Repository structure
    # -------------------------------

    try:

        file_paths = (
            client.get_repository_tree(
                owner,
                repo_name,
                default_branch,
            )
        )

    except Exception:

        file_paths = []

    structure = (
        github_analyzer.analyze_repository_structure(
            file_paths
        )
    )

    # -------------------------------
    # Commit intelligence
    # -------------------------------

    try:

        commit_data = (
            client.analyze_commit_history(
                owner,
                repo_name,
            )
        )

    except Exception as error:

        print(
            f"Commit analysis failed for "
            f"{repo_name}: {error}"
        )

        commit_data = {
            "available": False,
            "total_commits": 0,
            "commits_last_30_days": 0,
            "commits_last_90_days": 0,
            "commits_last_180_days": 0,
            "commits_last_365_days": 0,
            "active_months_last_year": 0,
            "latest_commit_at": None,
        }

    # -------------------------------
    # Fork ownership
    # -------------------------------

    fork_parent = None

    fork_unique_commits = 0

    fork_changed_files = 0

    fork_additions = 0

    fork_deletions = 0

    fork_contribution_available = False

    if repo.get("fork"):

        parent = repo.get(
            "parent"
        )

        if parent:

            fork_parent = parent.get(
                "full_name"
            )

            parent_branch = (
                parent.get(
                    "default_branch",
                    "main",
                )
            )

            try:

                comparison = (
                    client.compare_fork_to_parent(
                        fork_owner=owner,
                        fork_repo=repo_name,
                        fork_branch=default_branch,
                        parent_full_name=fork_parent,
                        parent_branch=parent_branch,
                    )
                )

                fork_contribution_available = (
                    comparison[
                        "available"
                    ]
                )

                fork_unique_commits = (
                    comparison[
                        "unique_commits"
                    ]
                )

                fork_changed_files = (
                    comparison[
                        "changed_files"
                    ]
                )

                fork_additions = (
                    comparison[
                        "additions"
                    ]
                )

                fork_deletions = (
                    comparison[
                        "deletions"
                    ]
                )

            except Exception as error:

                print(
                    f"Fork comparison failed for "
                    f"{repo_name}: {error}"
                )

    repository = GitHubRepository(

        name=repo["name"],

        full_name=repo[
            "full_name"
        ],

        description=repo.get(
            "description"
        ),

        url=repo[
            "html_url"
        ],

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

        default_branch=default_branch,

        created_at=repo.get(
            "created_at"
        ),

        updated_at=repo.get(
            "updated_at"
        ),

        pushed_at=repo.get(
            "pushed_at"
        ),

        readme=readme,

        dependencies=dependencies,

        dependency_files=(
            dependency_file_names
        ),

        file_paths=file_paths,

        source_directories=(
            structure[
                "source_directories"
            ]
        ),

        test_files=(
            structure[
                "test_files"
            ]
        ),

        config_files=(
            structure[
                "config_files"
            ]
        ),

        has_docker=(
            structure[
                "has_docker"
            ]
        ),

        has_frontend=(
            structure[
                "has_frontend"
            ]
        ),

        has_tests=(
            structure[
                "has_tests"
            ]
        ),

        # Commit intelligence
        total_commits=(
            commit_data[
                "total_commits"
            ]
        ),

        commits_last_30_days=(
            commit_data[
                "commits_last_30_days"
            ]
        ),

        commits_last_90_days=(
            commit_data[
                "commits_last_90_days"
            ]
        ),

        commits_last_180_days=(
            commit_data[
                "commits_last_180_days"
            ]
        ),

        commits_last_365_days=(
            commit_data[
                "commits_last_365_days"
            ]
        ),

        active_months_last_year=(
            commit_data[
                "active_months_last_year"
            ]
        ),

        latest_commit_at=(
            commit_data[
                "latest_commit_at"
            ]
        ),

        commit_history_available=(
            commit_data[
                "available"
            ]
        ),

        # Fork ownership
        fork_parent=fork_parent,

        fork_unique_commits=(
            fork_unique_commits
        ),

        fork_changed_files=(
            fork_changed_files
        ),

        fork_additions=(
            fork_additions
        ),

        fork_deletions=(
            fork_deletions
        ),

        fork_contribution_available=(
            fork_contribution_available
        ),
    )

    repositories.append(
        repository
    )


github_profile = GitHubProfile(

    username=profile_data[
        "login"
    ],

    name=profile_data.get(
        "name"
    ),

    bio=profile_data.get(
        "bio"
    ),

    profile_url=profile_data[
        "html_url"
    ],

    public_repository_count=(
        profile_data.get(
            "public_repos",
            0,
        )
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


print(
    "\nSending actual GitHub evidence "
    "to Gemini..."
)


analysis = ai_analyzer.analyze(
    github_profile
)


print("\n========================================")
print("          PROJECT ANALYSIS")
print("========================================")


for project in analysis.projects:

    print(
        f"\n{project.repository}"
    )

    print(
        "Meaningful:",
        project.meaningful_project,
    )

    print(
        "Project score:",
        f"{project.project_score}/10",
    )

    print(
        "Stage:",
        project.project_stage,
    )

    print(
        "Type:",
        project.project_type,
    )

    print(
        "Technologies:",
        ", ".join(
            project.technologies
        ),
    )

    print(
        "Assessment:",
        project.assessment,
    )


print(
    "\nCalculating portfolio score..."
)


score = ai_analyzer.score(
    github_profile,
    analysis,
)


print("\n========================================")
print("       GITHUB PORTFOLIO SCORE")
print("========================================")


print(
    f"\nOVERALL: "
    f"{score.overall_score}/100"
)


print(
    f"\nMeaningful projects: "
    f"{score.meaningful_project_count}"
)


dimensions = [

    (
        "Project Quality",
        score.project_quality,
    ),

    (
        "Portfolio Depth",
        score.portfolio_depth,
    ),

    (
        "Technical Breadth",
        score.technical_breadth,
    ),

    (
        "Activity & Consistency",
        score.activity_consistency,
    ),

    (
        "Documentation",
        score.documentation,
    ),

    (
        "Originality & Ownership",
        score.originality_ownership,
    ),
]


for name, dimension in dimensions:

    print(
        f"\n{name}: "
        f"{dimension.score}/100"
    )

    print(
        dimension.rationale
    )


print(
    "\nStrongest area:",
    score.strongest_area,
)


print(
    "Biggest weakness:",
    score.biggest_weakness,
)


print(
    "\nRecommendations:"
)


for recommendation in (
    score.recommendations
):

    print(
        f"- {recommendation}"
    )


print(
    "\n========================================"
)

print(
    "       ACTIVITY EVIDENCE"
)

print(
    "========================================"
)


for repository in repositories:

    if not repository.commit_history_available:
        continue

    print(
        f"\n{repository.name}"
    )

    print(
        "Total commits:",
        repository.total_commits,
    )

    print(
        "Last 30 days:",
        repository.commits_last_30_days,
    )

    print(
        "Last 90 days:",
        repository.commits_last_90_days,
    )

    print(
        "Last 180 days:",
        repository.commits_last_180_days,
    )

    print(
        "Last 365 days:",
        repository.commits_last_365_days,
    )

    print(
        "Active months:",
        repository.active_months_last_year,
    )

    print(
        "Latest commit:",
        repository.latest_commit_at,
    )


print(
    "\n========================================"
)

print(
    "          FORK EVIDENCE"
)

print(
    "========================================"
)


for repository in repositories:

    if repository.is_fork:

        print(
            f"\n{repository.name}"
        )

        print(
            "Parent:",
            repository.fork_parent,
        )

        print(
            "Unique commits:",
            repository.fork_unique_commits,
        )

        print(
            "Changed files:",
            repository.fork_changed_files,
        )

        print(
            "Lines added:",
            repository.fork_additions,
        )

        print(
            "Lines deleted:",
            repository.fork_deletions,
        )


client.close()


print("\n========================================")
print("       CAREEROS ANALYSIS COMPLETE")
print("========================================")