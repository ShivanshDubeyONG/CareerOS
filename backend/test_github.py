from app.integrations.github.github_client import GitHubClient
from app.integrations.github.github_analyzer import GitHubAnalyzer
from app.services.ai.github_ai_analyzer import GitHubAIAnalyzer
from app.services.ai.github_scoring import GitHubScorer

from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)


USERNAME = "ShivanshDubeyONG"


print()
print("=" * 40)
print("        CAREEROS GITHUB ANALYSIS")
print("=" * 40)
print()


client = GitHubClient()
github_analyzer = GitHubAnalyzer()
github_ai = GitHubAIAnalyzer()
scorer = GitHubScorer()


# ==================================================
# 1. PROFILE
# ==================================================

print("[1/4] Fetching GitHub profile...")

profile_data = client.get_user(
    USERNAME
)

print(
    f"Found: {profile_data.get('login')}"
)


# ==================================================
# 2. REPOSITORIES
# ==================================================

print()
print("[2/4] Fetching repositories...")

repositories_data = (
    client.get_repositories(
        USERNAME
    )
)

print(
    f"Found {len(repositories_data)} repositories."
)


# ==================================================
# 3. BUILD CAREEROS PROFILE
# ==================================================

print()
print("[3/4] Building CareerOS profile...")
print()


repositories = []

dependency_files_to_check = [
    "requirements.txt",
    "pyproject.toml",
    "package.json",
]


for repo in repositories_data:

    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    print(
        f"  Processing: {repo_name}"
    )

    # ----------------------------------------------
    # Languages
    # ----------------------------------------------

    try:

        languages = (
            client.get_repository_languages(
                owner,
                repo_name,
            )
        )

    except Exception:

        languages = {}

    print(
        "    Languages: "
        + (
            ", ".join(
                languages.keys()
            )
            if languages
            else "None"
        )
    )

    # ----------------------------------------------
    # README
    # ----------------------------------------------

    try:

        readme = (
            client.get_repository_readme(
                owner,
                repo_name,
            )
        )

    except Exception:

        readme = None

    # ----------------------------------------------
    # Repository tree
    # ----------------------------------------------

    default_branch = (
        repo.get(
            "default_branch"
        )
        or "main"
    )

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

    # ----------------------------------------------
    # Dependency extraction
    # ----------------------------------------------

    dependencies = []
    dependency_names = []

    for dependency_file in (
        dependency_files_to_check
    ):

        if dependency_file not in file_paths:
            continue

        try:

            content = (
                client.get_repository_file(
                    owner,
                    repo_name,
                    dependency_file,
                )
            )

        except Exception:

            content = None

        if not content:
            continue

        try:

            extracted = (
                github_analyzer
                .extract_dependencies(
                    content,
                    dependency_file,
                )
            )

            if extracted:

                dependencies.extend(
                    extracted
                )

                dependency_names.append(
                    dependency_file
                )

        except Exception:

            pass

    # ----------------------------------------------
    # Remove duplicates
    # ----------------------------------------------

    dependencies = list(
        dict.fromkeys(
            dependencies
        )
    )

    print(
        "    Dependencies: "
        + (
            ", ".join(
                dependencies
            )
            if dependencies
            else "None"
        )
    )

    print(
        "    Dependency files: "
        + (
            ", ".join(
                dependency_names
            )
            if dependency_names
            else "None"
        )
    )

    # ----------------------------------------------
    # Repository structure
    # ----------------------------------------------

    try:

        structure = (
            github_analyzer
            .analyze_repository_structure(
                file_paths
            )
        )

    except Exception:

        structure = {}

    source_directories = (
        structure.get(
            "source_directories",
            [],
        )
    )

    test_files = (
        structure.get(
            "test_files",
            [],
        )
    )

    config_files = (
        structure.get(
            "config_files",
            [],
        )
    )

    has_docker = (
        structure.get(
            "has_docker",
            False,
        )
    )

    has_frontend = (
        structure.get(
            "has_frontend",
            False,
        )
    )

    has_tests = (
        structure.get(
            "has_tests",
            False,
        )
    )

    # ----------------------------------------------
    # Commit activity
    # ----------------------------------------------

    try:

        activity = (
            client.analyze_commit_history(
                owner,
                repo_name,
            )
        )

    except Exception:

        activity = {
            "available": False,
            "total_commits": 0,
            "active_months_last_year": 0,
            "commits_last_30_days": 0,
            "commits_last_90_days": 0,
            "commits_last_180_days": 0,
            "commits_last_365_days": 0,
            "latest_commit_at": None,
        }

    # ----------------------------------------------
    # Fork evidence
    # ----------------------------------------------

    fork_parent = None

    fork_unique_commits = 0
    fork_changed_files = 0
    fork_additions = 0
    fork_deletions = 0

    fork_contribution_available = False

    if repo.get(
        "fork",
        False,
    ):

        parent = (
            repo.get(
                "parent"
            )
            or {}
        )

        parent_full_name = (
            parent.get(
                "full_name"
            )
        )

        parent_branch = (
            parent.get(
                "default_branch"
            )
            or "main"
        )

        if parent_full_name:

            try:

                fork_comparison = (
                    client.compare_fork_to_parent(
                        fork_owner=owner,
                        fork_repo=repo_name,
                        fork_branch=default_branch,
                        parent_full_name=parent_full_name,
                        parent_branch=parent_branch,
                    )
                )

                fork_contribution_available = (
                    fork_comparison.get(
                        "available",
                        False,
                    )
                )

                fork_unique_commits = (
                    fork_comparison.get(
                        "unique_commits",
                        0,
                    )
                )

                fork_changed_files = (
                    fork_comparison.get(
                        "changed_files",
                        0,
                    )
                )

                fork_additions = (
                    fork_comparison.get(
                        "additions",
                        0,
                    )
                )

                fork_deletions = (
                    fork_comparison.get(
                        "deletions",
                        0,
                    )
                )

                fork_parent = (
                    parent_full_name
                )

            except Exception:

                pass

    # ----------------------------------------------
    # Build repository schema
    # ----------------------------------------------

    repository = GitHubRepository(

        name=repo_name,

        full_name=repo.get(
            "full_name",
            repo_name,
        ),

        description=repo.get(
            "description"
        ),

        url=repo.get(
            "html_url",
            "",
        ),

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

        dependency_files=dependency_names,

        file_paths=file_paths,

        source_directories=(
            source_directories
        ),

        test_files=test_files,

        config_files=config_files,

        has_docker=has_docker,

        has_frontend=has_frontend,

        has_tests=has_tests,

        total_commits=activity.get(
            "total_commits",
            0,
        ),

        commits_last_30_days=(
            activity.get(
                "commits_last_30_days",
                0,
            )
        ),

        commits_last_90_days=(
            activity.get(
                "commits_last_90_days",
                0,
            )
        ),

        commits_last_180_days=(
            activity.get(
                "commits_last_180_days",
                0,
            )
        ),

        commits_last_365_days=(
            activity.get(
                "commits_last_365_days",
                0,
            )
        ),

        active_months_last_year=(
            activity.get(
                "active_months_last_year",
                0,
            )
        ),

        latest_commit_at=(
            activity.get(
                "latest_commit_at"
            )
        ),

        commit_history_available=(
            activity.get(
                "available",
                False,
            )
        ),

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


# ==================================================
# BUILD PROFILE
# ==================================================

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


# ==================================================
# 4. CAREEROS AI INTELLIGENCE
# ==================================================

print()
print("[4/4] Running CareerOS intelligence...")
print()


# IMPORTANT:
#
# Use GitHubAIAnalyzer here.
#
# GitHubAnalyzer is only the deterministic
# repository-evidence extractor.
#
# GitHubAIAnalyzer is the Gemini intelligence layer.

analysis = github_ai.analyze(
    github_profile
)


# ==================================================
# PROJECT ANALYSIS
# ==================================================

print()
print("=" * 40)
print("          PROJECT ANALYSIS")
print("=" * 40)
print()


for project in (
    analysis.projects
    or []
):

    print(
        project.repository
    )

    print(
        "Meaningful:",
        project.meaningful_project,
    )

    print(
        "Project score:",
        project.project_score,
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
        )
        if project.technologies
        else "None",
    )

    # --------------------------------------------------
    # NEW TECHNOLOGY EVIDENCE
    # --------------------------------------------------

    if project.technology_evidence:

        print(
            "Technology evidence:"
        )

        for technology in (
            project.technology_evidence
        ):

            print(
                "  - "
                + technology.technology
                + " | "
                + technology.confidence
                + " | "
                + ", ".join(
                    technology.evidence_sources
                )
            )

    print(
        "Assessment:",
        project.assessment,
    )

    print()


# ==================================================
# PORTFOLIO SCORE
# ==================================================

print()
print("Calculating portfolio score...")
print()


portfolio_score = scorer.score(
    github_profile,
    analysis.projects,
)


print("=" * 40)
print("       GITHUB PORTFOLIO SCORE")
print("=" * 40)
print()


print(
    "OVERALL:",
    portfolio_score.overall_score,
)


print(
    "\nMeaningful projects:",
    portfolio_score.meaningful_project_count,
)


print(
    "\nProject Quality:",
    portfolio_score.project_quality,
)


print(
    "\nPortfolio Depth:",
    portfolio_score.portfolio_depth,
)


print(
    "\nTechnical Breadth:",
    portfolio_score.technical_breadth,
)


print(
    "\nActivity & Consistency:",
    portfolio_score.activity_consistency,
)


print(
    "\nDocumentation:",
    portfolio_score.documentation,
)


print(
    "\nOriginality & Ownership:",
    portfolio_score.originality_ownership,
)


print(
    "\nStrongest area:",
    portfolio_score.strongest_area,
)


print(
    "\nBiggest weakness:",
    portfolio_score.biggest_weakness,
)


print(
    "\nRecommendations:"
)

for recommendation in (
    portfolio_score.recommendations
    or []
):

    print(
        "-",
        recommendation,
    )


# ==================================================
# ACTIVITY EVIDENCE
# ==================================================

print()
print("=" * 40)
print("       ACTIVITY EVIDENCE")
print("=" * 40)
print()


for repository in repositories:

    print(
        repository.name
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

    print()


# ==================================================
# FORK EVIDENCE
# ==================================================

print("=" * 40)
print("          FORK EVIDENCE")
print("=" * 40)
print()


for repository in repositories:

    if not repository.is_fork:
        continue

    print(
        repository.name
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
        "Additions:",
        repository.fork_additions,
    )

    print(
        "Deletions:",
        repository.fork_deletions,
    )

    print()


# ==================================================
# DONE
# ==================================================

print("=" * 40)
print("       CAREEROS ANALYSIS COMPLETE")
print("=" * 40)
print()


client.close()
