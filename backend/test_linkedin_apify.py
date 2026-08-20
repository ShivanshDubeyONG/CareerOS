from app.integrations.linkedin.apify_client import (
    apify_linkedin_client,
)

from app.integrations.linkedin.apify_adapter import (
    apify_linkedin_adapter,
)

from app.services.linkedin.linkedin_service import (
    linkedin_service,
)

from app.services.linkedin.linkedin_rater import (
    linkedin_rater,
)

from app.services.unified.unified_service import (
    unified_service,
)

from app.services.resume_extraction_service import (
    resume_extraction_service,
)

from app.integrations.github.github_client import (
    GitHubClient,
)

from app.integrations.github.github_analyzer import (
    GitHubAnalyzer,
)

from app.services.ai.github_ai_analyzer import (
    GitHubAIAnalyzer,
)

from app.integrations.leetcode.leetcode_client import (
    LeetCodeClient,
)

from app.services.leetcode.leetcode_service import (
    leetcode_service,
)

from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)


# ==================================================
# CONFIG
# ==================================================

LINKEDIN_URL = (
    "https://www.linkedin.com/in/"
    "suryansh-singh-1156a834a/"
)

GITHUB_USERNAME = "SynshAmi"

LEETCODE_USERNAME = "synsh_ami"

RESUME_PATH = (
    "uploads/"
    "2feecdf7-5a91-462d-9c3a-ab8ba832f9a3.pdf"
)


# ==================================================
# GITHUB BUILDER
# ==================================================

def build_github_profile(
    client,
    github_analyzer,
):
    """
    Build the same rich GitHubProfile used by
    test_gemini.py.

    This preserves:
    - languages
    - README
    - dependencies
    - repository structure
    - commit intelligence
    - fork contribution evidence
    """

    print(
        "\n[GitHub] Fetching profile..."
    )

    profile_data = client.get_user(
        GITHUB_USERNAME
    )

    print(
        "[GitHub] Fetching repositories..."
    )

    repositories_data = (
        client.get_repositories(
            GITHUB_USERNAME
        )
    )

    print(
        f"[GitHub] Found "
        f"{len(repositories_data)} repositories."
    )

    repositories = []

    dependency_file_names_list = [
        "requirements.txt",
        "pyproject.toml",
        "package.json",
    ]

    for repo in repositories_data:

        owner = repo["owner"]["login"]

        repo_name = repo["name"]

        default_branch = repo.get(
            "default_branch",
            "main",
        )

        print(
            f"[GitHub] Processing: "
            f"{repo_name}"
        )

        # ------------------------------------------
        # Languages
        # ------------------------------------------

        try:

            languages = (
                client.get_repository_languages(
                    owner,
                    repo_name,
                )
            )

        except Exception:

            languages = {}

        # ------------------------------------------
        # README
        # ------------------------------------------

        try:

            readme = (
                client.get_repository_readme(
                    owner,
                    repo_name,
                )
            )

        except Exception:

            readme = None

        # ------------------------------------------
        # Dependencies
        # ------------------------------------------

        dependency_files = {}

        dependency_file_names = []

        for filename in (
            dependency_file_names_list
        ):

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

        # ------------------------------------------
        # Repository structure
        # ------------------------------------------

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
            github_analyzer
            .analyze_repository_structure(
                file_paths
            )
        )

        # ------------------------------------------
        # Commit intelligence
        # ------------------------------------------

        try:

            commit_data = (
                client.analyze_commit_history(
                    owner,
                    repo_name,
                )
            )

        except Exception as error:

            print(
                f"[GitHub] Commit analysis failed "
                f"for {repo_name}: {error}"
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

        # ------------------------------------------
        # Fork ownership
        # ------------------------------------------

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
                        client
                        .compare_fork_to_parent(
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
                        f"[GitHub] Fork comparison "
                        f"failed for {repo_name}: "
                        f"{error}"
                    )

        # ------------------------------------------
        # Build repository schema
        # ------------------------------------------

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

    return github_profile


# ==================================================
# MAIN
# ==================================================

def main():

    print("=" * 70)

    print(
        "CAREEROS REAL MULTI-SOURCE "
        "LINKEDIN INTELLIGENCE PIPELINE"
    )

    print("=" * 70)

    github_client = GitHubClient()

    leetcode_client = LeetCodeClient()

    try:

        # ==================================================
        # 1. RESUME
        # ==================================================

        print(
            "\n1. Loading real Resume..."
        )

        resume = (
            resume_extraction_service.extract(
                RESUME_PATH
            )
        )

        print(
            "Resume extraction successful."
        )

        print(
            f"Resume name: "
            f"{getattr(resume, 'name', None)}"
        )

        print(
            f"Resume skills: "
            f"{len(getattr(resume, 'skills', []))}"
        )

        # ==================================================
        # 2. GITHUB
        # ==================================================

        print(
            "\n2. Building real GitHub profile..."
        )

        github_analyzer = GitHubAnalyzer()

        github_profile = (
            build_github_profile(
                github_client,
                github_analyzer,
            )
        )

        print(
            "GitHub profile built successfully."
        )

        print(
            f"GitHub repositories: "
            f"{len(github_profile.repositories)}"
        )

        # ==================================================
        # 3. GITHUB AI ANALYSIS
        # ==================================================

        print(
            "\n3. Running GitHub AI analysis..."
        )

        github_ai_analyzer = (
            GitHubAIAnalyzer()
        )

        github_analysis = (
            github_ai_analyzer.analyze(
                github_profile
            )
        )

        print(
            "GitHub AI analysis successful."
        )

        print(
            f"GitHub projects analyzed: "
            f"{len(github_analysis.projects)}"
        )

        # ==================================================
        # 4. LEETCODE
        # ==================================================

        print(
            "\n4. Acquiring real LeetCode..."
        )

        leetcode_profile = (
            leetcode_client.get_user_profile(
                LEETCODE_USERNAME
            )
        )

        print(
            "LeetCode acquisition successful."
        )

        leetcode_analysis = (
            leetcode_service.analyze(
                leetcode_profile
            )
        )

        print(
            "LeetCode analysis successful."
        )

        print(
            f"LeetCode solved: "
            f"{leetcode_analysis.total_solved}"
        )

        # ==================================================
        # 5. LINKEDIN ACQUISITION
        # ==================================================

        print(
            "\n5. Acquiring real LinkedIn..."
        )

        print(
            f"URL: {LINKEDIN_URL}"
        )

        raw_profile = (
            apify_linkedin_client.fetch_profile(
                LINKEDIN_URL
            )
        )

        print(
            "LinkedIn acquisition successful."
        )

        # ==================================================
        # 6. LINKEDIN NORMALIZATION
        # ==================================================

        print(
            "\n6. Normalizing LinkedIn..."
        )

        linkedin_profile, metadata = (
            apify_linkedin_adapter.parse(
                raw_profile
            )
        )

        print(
            "LinkedIn normalization successful."
        )

        # ==================================================
        # 7. LINKEDIN ANALYSIS
        # ==================================================

        print(
            "\n7. Running LinkedIn analysis..."
        )

        linkedin_analysis = (
            linkedin_service.analyze(
                linkedin_profile
            )
        )

        print(
            "LinkedIn analysis successful."
        )

        # ==================================================
        # 8. UNIFIED EVIDENCE
        # ==================================================

        print(
            "\n8. BUILDING UNIFIED CAREEROS "
            "EVIDENCE..."
        )

        unified_profile = (
            unified_service.build_profile(
                resume=resume,

                github_profile=github_profile,

                github_analysis=github_analysis,

                linkedin_profile=linkedin_profile,

                linkedin_analysis=linkedin_analysis,

                leetcode_analysis=leetcode_analysis,
            )
        )

        print(
            "Unified evidence built successfully."
        )

        print(
            f"Unified skills: "
            f"{len(unified_profile.skills)}"
        )

        print(
            f"Skill evidence: "
            f"{len(unified_profile.skill_evidence)}"
        )

        print(
            f"Project evidence: "
            f"{len(unified_profile.project_evidence)}"
        )

        print(
            f"Cross-source findings: "
            f"{len(unified_profile.findings)}"
        )

        print(
            "\nSOURCE STATUS"
        )

        for source, available in (
            unified_profile.source_status.items()
        ):

            print(
                f"  {source}: "
                f"{'AVAILABLE' if available else 'UNAVAILABLE'}"
            )

        # ==================================================
        # 9. GEMINI LINKEDIN INTELLIGENCE
        # ==================================================

        print(
            "\n9. Running Gemini LinkedIn "
            "Intelligence..."
        )

        rating = (
            linkedin_rater.rate(
                profile=linkedin_profile,

                analysis=linkedin_analysis,

                unified_profile=unified_profile,
            )
        )

        print(
            "Gemini rating successful."
        )

        # ==================================================
        # 10. SCORE
        # ==================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "LINKEDIN PROFILE SCORE"
        )

        print(
            "=" * 70
        )

        print(
            f"Overall: "
            f"{rating.overall_score}/100"
        )

        # ==================================================
        # 11. SECTION SCORES
        # ==================================================

        print(
            "\nSECTION SCORES"
        )

        print("-" * 70)

        sections = [
            ("Headline", rating.headline),
            ("About", rating.about),
            ("Experience", rating.experience),
            ("Projects", rating.projects),
            ("Skills", rating.skills),
            ("Education", rating.education),
            (
                "Certifications",
                rating.certifications,
            ),
            (
                "Completeness",
                rating.completeness,
            ),
        ]

        for name, section in sections:

            print(
                f"{name}: "
                f"{section.score}/100"
            )

        # ==================================================
        # 12. STRENGTHS
        # ==================================================

        print(
            "\nSTRENGTHS"
        )

        print("-" * 70)

        for strength in rating.strengths:

            print(
                f"- {strength}"
            )

        # ==================================================
        # 13. ISSUES
        # ==================================================

        print(
            "\nISSUES"
        )

        print("-" * 70)

        for issue in rating.issues:

            print(
                f"- {issue}"
            )

        # ==================================================
        # 14. RECOMMENDATIONS
        # ==================================================

        print(
            "\nRECOMMENDATIONS"
        )

        print("-" * 70)

        for recommendation in (
            rating.recommendations
        ):

            print(
                f"\n[{recommendation.priority}] "
                f"{recommendation.area}"
            )

            print(
                f"Recommendation: "
                f"{recommendation.recommendation}"
            )

            print(
                f"Reason: "
                f"{recommendation.reason}"
            )

            if recommendation.evidence:

                print(
                    "Evidence:"
                )

                for evidence in (
                    recommendation.evidence
                ):

                    print(
                        f"  - {evidence}"
                    )

        # ==================================================
        # 15. SUGGESTED CONTENT
        # ==================================================

        print(
            "\nSUGGESTED CONTENT"
        )

        print("-" * 70)

        for content in (
            rating.suggested_content
        ):

            print(
                f"\nSection: "
                f"{content.section}"
            )

            print(
                f"Content: "
                f"{content.content}"
            )

            if content.basis:

                print(
                    "Evidence basis:"
                )

                for evidence in (
                    content.basis
                ):

                    print(
                        f"  - {evidence}"
                    )

        # ==================================================
        # 16. DATA QUALITY
        # ==================================================

        print(
            "\nDATA QUALITY"
        )

        print("-" * 70)

        data_quality = (
            rating.data_quality
        )

        print(
            f"Profile data available: "
            f"{data_quality.profile_data_available}"
        )

        print(
            f"Completeness: "
            f"{data_quality.completeness}/100"
        )

        if data_quality.note:

            print(
                f"Note: "
                f"{data_quality.note}"
            )

        if data_quality.missing_sections:

            print(
                "Missing sections:"
            )

            for section in (
                data_quality.missing_sections
            ):

                print(
                    f"  - {section}"
                )

        if data_quality.unavailable_sections:

            print(
                "Unavailable sections:"
            )

            for section in (
                data_quality.unavailable_sections
            ):

                print(
                    f"  - {section}"
                )

        # ==================================================
        # COMPLETE
        # ==================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "REAL MULTI-SOURCE LINKEDIN "
            "INTELLIGENCE COMPLETE"
        )

        print(
            "=" * 70
        )

    finally:

        github_client.close()

        leetcode_client.close()


if __name__ == "__main__":

    main()