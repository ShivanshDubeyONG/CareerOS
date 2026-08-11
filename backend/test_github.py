from app.integrations.github.github_client import GitHubClient
from app.integrations.github.github_analyzer import GitHubAnalyzer
from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)


USERNAME = "ShivanshDubeyONG"


client = GitHubClient()
analyzer = GitHubAnalyzer()


print("\n========================================")
print("        CAREEROS GITHUB ANALYSIS")
print("========================================")


# --------------------------------------------------
# 1. FETCH PROFILE
# --------------------------------------------------

print("\n[1/4] Fetching GitHub profile...")

profile_data = client.get_user(USERNAME)

print(
    "Found:",
    profile_data.get("login"),
)


# --------------------------------------------------
# 2. FETCH REPOSITORIES
# --------------------------------------------------

print("\n[2/4] Fetching repositories...")

repositories_data = client.get_repositories(
    USERNAME
)

print(
    f"Found {len(repositories_data)} repositories."
)


# --------------------------------------------------
# 3. BUILD STRUCTURED PROFILE
# --------------------------------------------------

print("\n[3/4] Building CareerOS profile...")

repositories = []


DEPENDENCY_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "package.json",
]


for repo in repositories_data:

    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    print(
        f"\n  Processing: {repo_name}"
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
    # Dependency files
    # ----------------------------------------------

    dependency_files = {}
    dependency_file_names = []

    for filename in DEPENDENCY_FILES:

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

    # ----------------------------------------------
    # Extract dependencies
    # ----------------------------------------------

    dependencies = (
        analyzer.extract_dependencies(
            dependency_files
        )
    )

    print(
        "    Languages:",
        ", ".join(languages.keys())
        if languages
        else "None",
    )

    print(
        "    Dependencies:",
        ", ".join(dependencies)
        if dependencies
        else "None",
    )

    print(
        "    Dependency files:",
        ", ".join(dependency_file_names)
        if dependency_file_names
        else "None",
    )

    # ----------------------------------------------
    # Pydantic repository
    # ----------------------------------------------

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


# --------------------------------------------------
# 4. ANALYZE
# --------------------------------------------------

print(
    "\n[4/4] Running CareerOS intelligence..."
)

analysis = analyzer.analyze_profile(
    github_profile
)


# --------------------------------------------------
# PROFILE SUMMARY
# --------------------------------------------------

print("\n========================================")
print("           PROFILE INTELLIGENCE")
print("========================================")

print(
    "Username:",
    analysis["username"],
)

print(
    "Repositories analyzed:",
    analysis[
        "total_repositories_analyzed"
    ],
)

print(
    "Original repositories:",
    analysis[
        "original_repository_count"
    ],
)

print(
    "Active repositories:",
    analysis[
        "active_repository_count"
    ],
)

print(
    "Total stars:",
    analysis["total_stars"],
)

print(
    "Total forks:",
    analysis["total_forks"],
)

print(
    "Languages:",
    ", ".join(
        analysis["languages_used"]
    ),
)

print(
    "Dependencies:",
    ", ".join(
        analysis[
            "dependencies_used"
        ]
    ),
)


# --------------------------------------------------
# REPOSITORY INTELLIGENCE
# --------------------------------------------------

print("\n========================================")
print("        REPOSITORY INTELLIGENCE")
print("========================================")


for repository in analysis[
    "repositories"
]:

    print(
        "\n----------------------------------------"
    )

    print(
        "Repository:",
        repository["name"],
    )

    print(
        "Primary language:",
        repository[
            "primary_language"
        ],
    )

    print(
        "Languages:",
        ", ".join(
            repository[
                "languages"
            ].keys()
        )
        if repository["languages"]
        else "None",
    )

    print(
        "Dependencies:",
        ", ".join(
            repository[
                "dependencies"
            ]
        )
        if repository[
            "dependencies"
        ]
        else "None",
    )

    print(
        "Dependency files:",
        ", ".join(
            repository[
                "dependency_files"
            ]
        )
        if repository[
            "dependency_files"
        ]
        else "None",
    )

    print(
        "Stars:",
        repository["stars"],
    )

    print(
        "Forks:",
        repository["forks"],
    )

    print(
        "Topics:",
        ", ".join(
            repository["topics"]
        )
        if repository["topics"]
        else "None",
    )

    print(
        "Original project:",
        not repository[
            "is_fork"
        ],
    )

    print(
        "README:",
        "Yes"
        if repository[
            "has_readme"
        ]
        else "No",
    )

    print(
        "README length:",
        repository[
            "readme_length"
        ],
    )

    print(
        "Activity score:",
        repository[
            "activity_score"
        ],
    )

    print(
        "Documentation score:",
        repository[
            "documentation_score"
        ],
    )

    print(
        "Project strength:",
        repository[
            "project_strength_score"
        ],
    )


client.close()


print("\n========================================")
print("       GITHUB ANALYSIS COMPLETE")
print("========================================")