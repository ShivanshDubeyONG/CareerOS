import traceback

from app.extractors.resume_extractor import resume_extractor
from app.parsers.resume_parser import resume_parser
from app.services.resume_extraction_service import (
    resume_extraction_service,
)
from app.services.resume.resume_rater import resume_rater

from app.integrations.github.github_client import GitHubClient
from app.integrations.github.github_analyzer import GitHubAnalyzer
from app.services.ai.github_ai_analyzer import GitHubAIAnalyzer

from app.schemas.github_schema import (
    GitHubProfile,
    GitHubRepository,
)

from app.integrations.leetcode.leetcode_client import (
    LeetCodeClient,
)
from app.services.leetcode.leetcode_service import (
    leetcode_service,
)

from app.integrations.linkedin.apify_client import (
    apify_linkedin_client,
)
from app.integrations.linkedin.apify_adapter import (
    apify_linkedin_adapter,
)
from app.services.linkedin.linkedin_service import (
    linkedin_service,
)

from app.services.unified.unified_service import (
    unified_service,
)


class CareerAnalysisService:

    def __init__(self):

        self.github_client = GitHubClient()
        self.github_analyzer = GitHubAnalyzer()
        self.github_ai = GitHubAIAnalyzer()
        self.leetcode_client = LeetCodeClient()

    # ==================================================
    # RESUME
    # ==================================================

    def analyze_resume(self, resume_path):

        print(
            "RESUME: parsing START",
            flush=True,
        )

        text = resume_parser.extract_text(
            resume_path
        )

        print(
            "RESUME: parsing DONE",
            flush=True,
        )

        resume = resume_extractor.extract(
            text
        )

        print(
            "RESUME: links extraction START",
            flush=True,
        )

        pdf_links = resume_parser.extract_links(
            resume_path
        )

        resume.links = (
            resume_extraction_service.classify_links(
                pdf_links
            )
        )

        print(
            "RESUME: links extraction DONE",
            flush=True,
        )

        print(
            "RESUME: rating START",
            flush=True,
        )

        rating = resume_rater.rate(
            resume=resume
        )

        print(
            "RESUME: rating DONE",
            flush=True,
        )

        return {
            "profile": resume,
            "rating": rating,
        }

    # ==================================================
    # GITHUB
    # ==================================================

    def analyze_github(self, username):

        print(
            "GH 1: get_user",
            flush=True,
        )

        profile_data = (
            self.github_client.get_user(
                username
            )
        )

        print(
            "GH 2: get_repositories",
            flush=True,
        )

        repositories_data = (
            self.github_client.get_repositories(
                username
            )
        )

        # --------------------------------------------------
        # Ignore forks and archived repositories.
        # --------------------------------------------------

        repositories_data = [
            repo
            for repo in repositories_data
            if not repo.get(
                "fork",
                False,
            )
            and not repo.get(
                "archived",
                False,
            )
        ]

        # --------------------------------------------------
        # Most recently updated first.
        # --------------------------------------------------

        repositories_data = sorted(
            repositories_data,
            key=lambda repo: (
                repo.get(
                    "updated_at"
                )
                or ""
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # Render/free-tier safety limit.
        # --------------------------------------------------

        MAX_ANALYZED_REPOSITORIES = 12

        repositories_data = (
            repositories_data[
                :MAX_ANALYZED_REPOSITORIES
            ]
        )

        print(
            f"GH 3: repositories="
            f"{len(repositories_data)}",
            flush=True,
        )

        owner = (
            profile_data.get(
                "login"
            )
            or username
        )

        repositories = []

        # ==================================================
        # SINGLE REPOSITORY PASS
        # ==================================================

        for repo in repositories_data:

            repo_name = repo["name"]

            print(
                f"GH 4: repo START "
                f"{owner}/{repo_name}",
                flush=True,
            )

            # --------------------------------------------------
            # Languages
            # --------------------------------------------------

            languages = {}

            try:

                print(
                    f"GH 5: languages "
                    f"{repo_name}",
                    flush=True,
                )

                languages = (
                    self.github_client
                    .get_repository_languages(
                        owner,
                        repo_name,
                    )
                )

                print(
                    f"GH 6: languages DONE "
                    f"{repo_name}",
                    flush=True,
                )

            except Exception as exc:

                print(
                    f"GH 6: languages FAILED "
                    f"{repo_name}: "
                    f"{exc!r}",
                    flush=True,
                )

            # --------------------------------------------------
            # README
            # --------------------------------------------------

            readme = None

            try:

                print(
                    f"GH 7: README "
                    f"{repo_name}",
                    flush=True,
                )

                readme = (
                    self.github_client
                    .get_repository_readme(
                        owner,
                        repo_name,
                    )
                )

                print(
                    f"GH 8: README DONE "
                    f"{repo_name}",
                    flush=True,
                )

            except Exception as exc:

                print(
                    f"GH 8: README FAILED "
                    f"{repo_name}: "
                    f"{exc!r}",
                    flush=True,
                )

            # --------------------------------------------------
            # Dependency files
            # --------------------------------------------------

            dependency_files = [
                "requirements.txt",
                "pyproject.toml",
                "package.json",
            ]

            dependency_data = {}
            dependency_names = []

            for filename in dependency_files:

                try:

                    content = (
                        self.github_client
                        .get_repository_file(
                            owner,
                            repo_name,
                            filename,
                        )
                    )

                    if content:

                        dependency_data[
                            filename
                        ] = content

                        dependency_names.append(
                            filename
                        )

                except Exception as exc:

                    print(
                        f"GH dependency skipped "
                        f"{owner}/"
                        f"{repo_name}/"
                        f"{filename}: "
                        f"{exc!r}",
                        flush=True,
                    )

            # --------------------------------------------------
            # Extract dependencies
            # --------------------------------------------------

            dependencies = []

            for (
                filename,
                content,
            ) in dependency_data.items():

                try:

                    extracted = (
                        self.github_analyzer
                        .extract_dependencies(
                            content,
                            filename,
                        )
                    )

                    dependencies.extend(
                        extracted
                    )

                except Exception as exc:

                    print(
                        f"GH dependency parsing "
                        f"failed {filename}: "
                        f"{exc!r}",
                        flush=True,
                    )

            dependencies = sorted(
                set(
                    dependencies
                )
            )

            # --------------------------------------------------
            # Repository tree
            # --------------------------------------------------

            file_paths = []

            try:

                print(
                    f"GH tree START "
                    f"{repo_name}",
                    flush=True,
                )

                file_paths = (
                    self.github_client
                    .get_repository_tree(
                        owner,
                        repo_name,
                        repo.get(
                            "default_branch"
                        )
                        or "main",
                    )
                )

                print(
                    f"GH tree DONE "
                    f"{repo_name}: "
                    f"{len(file_paths)} files",
                    flush=True,
                )

            except Exception as exc:

                print(
                    f"GH tree FAILED "
                    f"{repo_name}: "
                    f"{exc!r}",
                    flush=True,
                )

            # --------------------------------------------------
            # Repository structure
            # --------------------------------------------------

            try:

                structure = (
                    self.github_analyzer
                    .analyze_repository_structure(
                        file_paths
                    )
                )

            except Exception as exc:

                print(
                    f"GH structure FAILED "
                    f"{repo_name}: "
                    f"{exc!r}",
                    flush=True,
                )

                structure = {
                    "source_directories": [],
                    "test_files": [],
                    "config_files": [],
                    "has_docker": False,
                    "has_frontend": False,
                    "has_tests": False,
                }

            # --------------------------------------------------
            # Build repository object
            # --------------------------------------------------

            print(
                f"GH BUILD repository START "
                f"{repo_name}",
                flush=True,
            )

            try:

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

                    dependency_files=dependency_names,

                    file_paths=file_paths,

                    source_directories=(
                        structure.get(
                            "source_directories",
                            [],
                        )
                    ),

                    test_files=(
                        structure.get(
                            "test_files",
                            [],
                        )
                    ),

                    config_files=(
                        structure.get(
                            "config_files",
                            [],
                        )
                    ),

                    has_docker=(
                        structure.get(
                            "has_docker",
                            False,
                        )
                    ),

                    has_frontend=(
                        structure.get(
                            "has_frontend",
                            False,
                        )
                    ),

                    has_tests=(
                        structure.get(
                            "has_tests",
                            False,
                        )
                    ),
                )

            except Exception as exc:

                print(
                    f"GH BUILD repository FAILED "
                    f"{repo_name}: "
                    f"{exc!r}",
                    flush=True,
                )

                traceback.print_exc()

                continue

            print(
                f"GH BUILD repository DONE "
                f"{repo_name}",
                flush=True,
            )

            repositories.append(
                repository
            )

            print(
                f"GH 4: repo DONE "
                f"{repo_name}",
                flush=True,
            )

        # ==================================================
        # BUILD GITHUB PROFILE
        # ==================================================

        print(
            "GH BUILD profile START",
            flush=True,
        )

        try:

            github_profile = GitHubProfile(

                username=profile_data.get(
                    "login"
                )
                or username,

                name=profile_data.get(
                    "name"
                ),

                bio=profile_data.get(
                    "bio"
                ),

                profile_url=profile_data.get(
                    "html_url"
                )
                or (
                    f"https://github.com/"
                    f"{username}"
                ),

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

        except Exception as exc:

            print(
                "GH BUILD profile FAILED:",
                repr(exc),
                flush=True,
            )

            traceback.print_exc()

            raise

        print(
            "GH BUILD profile DONE",
            flush=True,
        )

        # ==================================================
        # GITHUB AI ANALYSIS
        # ==================================================

        print(
            "GH 9: GitHub AI analysis START",
            flush=True,
        )

        try:

            analysis = (
                self.github_ai.analyze(
                    github_profile
                )
            )

        except Exception as exc:

            print(
                "GH 9: GitHub AI analysis FAILED:",
                repr(exc),
                flush=True,
            )

            traceback.print_exc()

            raise

        print(
            "GH 10: GitHub AI analysis DONE",
            flush=True,
        )

        return {
            "profile": github_profile,
            "analysis": analysis,
        }

    # ==================================================
    # LEETCODE
    # ==================================================

    def analyze_leetcode(
        self,
        username,
    ):

        print(
            f"LC: analysis START "
            f"{username}",
            flush=True,
        )

        profile = (
            self.leetcode_client
            .get_user_profile(
                username
            )
        )

        print(
            f"LC: profile DONE "
            f"{username}",
            flush=True,
        )

        analysis = (
            leetcode_service.analyze(
                profile
            )
        )

        print(
            f"LC: analysis DONE "
            f"{username}",
            flush=True,
        )

        return {
            "profile": profile,
            "analysis": analysis,
        }

    # ==================================================
    # LINKEDIN
    # ==================================================

    def analyze_linkedin(
        self,
        url,
    ):

        print(
            f"LI: fetch START "
            f"{url}",
            flush=True,
        )

        raw_profile = (
            apify_linkedin_client.fetch_profile(
                url
            )
        )

        print(
            "LI: fetch DONE",
            flush=True,
        )

        profile, metadata = (
            apify_linkedin_adapter.parse(
                raw_profile
            )
        )

        print(
            "LI: analysis START",
            flush=True,
        )

        analysis = (
            linkedin_service.analyze(
                profile
            )
        )

        print(
            "LI: analysis DONE",
            flush=True,
        )

        return {
            "profile": profile,
            "metadata": metadata,
            "analysis": analysis,
        }

    # ==================================================
    # FULL CAREER ANALYSIS
    # ==================================================

    def analyze(
        self,
        resume_path,
    ):

        print(
            "=== CAREER ANALYSIS START ===",
            flush=True,
        )

        # ==================================================
        # 1. RESUME
        # ==================================================

        print(
            "STEP 1: Resume analysis START",
            flush=True,
        )

        resume_result = (
            self.analyze_resume(
                resume_path
            )
        )

        print(
            "STEP 1: Resume analysis DONE",
            flush=True,
        )

        resume = (
            resume_result[
                "profile"
            ]
        )

        # ==================================================
        # 2. LINKEDIN
        # ==================================================

        linkedin_result = None

        if resume.links.linkedin:

            print(
                f"STEP 2: LinkedIn START: "
                f"{resume.links.linkedin}",
                flush=True,
            )

            try:

                linkedin_result = (
                    self.analyze_linkedin(
                        resume.links.linkedin
                    )
                )

                print(
                    "STEP 2: LinkedIn DONE",
                    flush=True,
                )

            except Exception as exc:

                print(
                    "STEP 2: LinkedIn FAILED:",
                    repr(exc),
                    flush=True,
                )

                traceback.print_exc()

        else:

            print(
                "STEP 2: LinkedIn SKIPPED",
                flush=True,
            )

        # ==================================================
        # 3. GITHUB
        # ==================================================

        github_result = None

        if resume.links.github:

            print(
                f"STEP 3: GitHub START: "
                f"{resume.links.github}",
                flush=True,
            )

            try:

                github_username = (
                    resume.links.github
                    .rstrip("/")
                    .split("/")
                    [-1]
                )

                github_result = (
                    self.analyze_github(
                        github_username
                    )
                )

                print(
                    "STEP 3: GitHub DONE",
                    flush=True,
                )

            except Exception as exc:

                print(
                    "STEP 3: GitHub FAILED:",
                    repr(exc),
                    flush=True,
                )

                traceback.print_exc()

        else:

            print(
                "STEP 3: GitHub SKIPPED",
                flush=True,
            )

        # ==================================================
        # 4. LEETCODE
        # ==================================================

        leetcode_result = None

        if resume.links.leetcode:

            print(
                f"STEP 4: LeetCode START: "
                f"{resume.links.leetcode}",
                flush=True,
            )

            try:

                leetcode_username = (
                    resume.links.leetcode
                    .rstrip("/")
                    .split("/")
                    [-1]
                )

                leetcode_result = (
                    self.analyze_leetcode(
                        leetcode_username
                    )
                )

                print(
                    "STEP 4: LeetCode DONE",
                    flush=True,
                )

            except Exception as exc:

                print(
                    "STEP 4: LeetCode FAILED:",
                    repr(exc),
                    flush=True,
                )

                traceback.print_exc()

        else:

            print(
                "STEP 4: LeetCode SKIPPED",
                flush=True,
            )

        # ==================================================
        # 5. UNIFIED ANALYSIS
        # ==================================================

        print(
            "STEP 5: Unified analysis START",
            flush=True,
        )

        try:

            unified_result = (
                unified_service.analyze(
                    resume=resume_result,
                    linkedin=linkedin_result,
                    github=github_result,
                    leetcode=leetcode_result,
                )
            )

            print(
                "STEP 5: Unified analysis DONE",
                flush=True,
            )

        except Exception as exc:

            print(
                "STEP 5: Unified analysis FAILED:",
                repr(exc),
                flush=True,
            )

            traceback.print_exc()

            unified_result = None

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        print(
            "=== CAREER ANALYSIS COMPLETE ===",
            flush=True,
        )

        return {
            "resume": resume_result,
            "linkedin": linkedin_result,
            "github": github_result,
            "leetcode": leetcode_result,
            "unified": unified_result,
        }


career_analysis_service = (
    CareerAnalysisService()
)