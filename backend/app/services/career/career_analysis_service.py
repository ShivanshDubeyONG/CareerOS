import os
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

        text = resume_parser.extract_text(
            resume_path
        )

        resume = resume_extractor.extract(
            text
        )

        pdf_links = resume_parser.extract_links(
            resume_path
        )

        resume.links = (
            resume_extraction_service.classify_links(
                pdf_links
            )
        )

        rating = resume_rater.rate(
            resume=resume
        )

        return {
            "profile": resume,
            "rating": rating,
        }

    # ==================================================
    # GITHUB
    # ==================================================

    def analyze_github(self, username):

        profile_data = (
            self.github_client.get_user(
                username
            )
        )

        repositories_data = (
            self.github_client.get_repositories(
                username
            )
        )

        repositories = []

        dependency_files = [
            "requirements.txt",
            "pyproject.toml",
            "package.json",
        ]

        for repo in repositories_data:

            owner = repo["owner"]["login"]
            repo_name = repo["name"]

            try:

                languages = (
                    self.github_client
                    .get_repository_languages(
                        owner,
                        repo_name,
                    )
                )

            except Exception:

                languages = {}

            try:

                readme = (
                    self.github_client
                    .get_repository_readme(
                        owner,
                        repo_name,
                    )
                )

            except Exception:

                readme = None

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

                except Exception:

                    pass

            dependencies = []

            for filename, content in dependency_data.items():

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

            dependencies = sorted(
                set(dependencies)
            )

            file_paths = []

            try:

                file_paths = (
                    self.github_client
                    .get_repository_tree(
                        owner,
                        repo_name,
                        repo.get(
                            "default_branch"
                        ) or "main",
                    )
                )

            except Exception:

                file_paths = []

            structure = (
                self.github_analyzer
                .analyze_repository_structure(
                    file_paths
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

                dependency_files=dependency_names,

                file_paths=file_paths,

                source_directories=structure[
                    "source_directories"
                ],

                test_files=structure[
                    "test_files"
                ],

                config_files=structure[
                    "config_files"
                ],

                has_docker=structure[
                    "has_docker"
                ],

                has_frontend=structure[
                    "has_frontend"
                ],

                has_tests=structure[
                    "has_tests"
                ],
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

        analysis = self.github_ai.analyze(
            github_profile
        )

        return {
            "profile": github_profile,
            "analysis": analysis,
        }

    # ==================================================
    # LEETCODE
    # ==================================================

    def analyze_leetcode(self, username):

        profile = (
            self.leetcode_client
            .get_user_profile(
                username
            )
        )

        analysis = (
            leetcode_service.analyze(
                profile
            )
        )

        return {
            "profile": profile,
            "analysis": analysis,
        }

    # ==================================================
    # LINKEDIN
    # ==================================================

    def analyze_linkedin(self, url):

        raw_profile = (
            apify_linkedin_client
            .fetch_profile(
                url
            )
        )

        profile, metadata = (
            apify_linkedin_adapter.parse(
                raw_profile
            )
        )

        analysis = (
            linkedin_service.analyze(
                profile
            )
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

        print("=== CAREER ANALYSIS START ===", flush=True)

        # -------------------------------
        # 1. Resume
        # -------------------------------
        print("STEP 1: Resume analysis START", flush=True)

        resume_result = self.analyze_resume(
            resume_path
        )

        print("STEP 1: Resume analysis DONE", flush=True)

        resume = resume_result["profile"]

        # -------------------------------
        # 2. LinkedIn
        # -------------------------------
        linkedin_result = None

        if resume.links.linkedin:

            print(
                f"STEP 2: LinkedIn START: {resume.links.linkedin}",
                flush=True,
            )

            try:
                linkedin_result = self.analyze_linkedin(
                    resume.links.linkedin
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

        # -------------------------------
        # 3. GitHub
        # -------------------------------
        github_result = None

        if resume.links.github:

            print(
                f"STEP 3: GitHub START: {resume.links.github}",
                flush=True,
            )

            try:
                github_username = self._extract_username(
                    resume.links.github
                )

                if github_username:
                    github_result = self.analyze_github(
                        github_username
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

        # -------------------------------
        # 4. LeetCode
        # -------------------------------
        leetcode_result = None

        if resume.links.leetcode:

            print(
                f"STEP 4: LeetCode START: {resume.links.leetcode}",
                flush=True,
            )

            try:
                leetcode_username = self._extract_username(
                    resume.links.leetcode
                )

                if leetcode_username:
                    leetcode_result = self.analyze_leetcode(
                        leetcode_username
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

        # -------------------------------
        # 5. Unified Evidence
        # -------------------------------
        print(
            "STEP 5: Unified analysis START",
            flush=True,
        )

        unified_profile = unified_service.build_profile(
            resume=resume,

            github_profile=(
                github_result["profile"]
                if github_result
                else None
            ),

            github_analysis=(
                github_result["analysis"]
                if github_result
                else None
            ),

            linkedin_profile=(
                linkedin_result["profile"]
                if linkedin_result
                else None
            ),

            linkedin_analysis=(
                linkedin_result["analysis"]
                if linkedin_result
                else None
            ),

            leetcode_analysis=(
                leetcode_result["analysis"]
                if leetcode_result
                else None
            ),
        )

        print(
            "STEP 5: Unified analysis DONE",
            flush=True,
        )

        print(
            "=== CAREER ANALYSIS COMPLETE ===",
            flush=True,
        )

        return {
            "resume": resume_result,
            "github": github_result,
            "leetcode": leetcode_result,
            "linkedin": linkedin_result,
            "unified": unified_profile,
        }

        # -------------------------------
        # 1. Resume
        # -------------------------------

        resume_result = (
            self.analyze_resume(
                resume_path
            )
        )

        resume = resume_result[
            "profile"
        ]

        # -------------------------------
        # 2. LinkedIn
        # -------------------------------

        linkedin_result = None

        if resume.links.linkedin:

            try:

                linkedin_result = (
                    self.analyze_linkedin(
                        resume.links.linkedin
                    )
                )

            except Exception as exc:

                print(
                    "\nLinkedIn unavailable:",
                    repr(exc),
                )

                traceback.print_exc()

        # -------------------------------
        # 3. GitHub
        # -------------------------------

        github_result = None

        if resume.links.github:

            try:

                github_username = (
                    self._extract_username(
                        resume.links.github
                    )
                )

                if github_username:

                    github_result = (
                        self.analyze_github(
                            github_username
                        )
                    )

            except Exception as exc:

                print(
                    "\nGitHub unavailable:",
                    repr(exc),
                )

                traceback.print_exc()

        # -------------------------------
        # 4. LeetCode
        # -------------------------------

        leetcode_result = None

        if resume.links.leetcode:

            try:

                leetcode_username = (
                    self._extract_username(
                        resume.links.leetcode
                    )
                )

                if leetcode_username:

                    leetcode_result = (
                        self.analyze_leetcode(
                            leetcode_username
                        )
                    )

            except Exception as exc:

                print(
                    "\nLeetCode unavailable:",
                    repr(exc),
                )

                traceback.print_exc()

        # -------------------------------
        # 5. Unified Evidence
        # -------------------------------

        unified_profile = (
            unified_service.build_profile(
                resume=resume,

                github_profile=(
                    github_result["profile"]
                    if github_result
                    else None
                ),

                github_analysis=(
                    github_result["analysis"]
                    if github_result
                    else None
                ),

                linkedin_profile=(
                    linkedin_result["profile"]
                    if linkedin_result
                    else None
                ),

                linkedin_analysis=(
                    linkedin_result["analysis"]
                    if linkedin_result
                    else None
                ),

                leetcode_analysis=(
                    leetcode_result["analysis"]
                    if leetcode_result
                    else None
                ),
            )
        )

        return {
            "resume": resume_result,
            "github": github_result,
            "leetcode": leetcode_result,
            "linkedin": linkedin_result,
            "unified": unified_profile,
        }

    # ==================================================
    # URL → USERNAME
    # ==================================================

    @staticmethod
    def _extract_username(url):

        if not url:
            return None

        value = url.rstrip(
            "/"
        )

        username = value.split(
            "/"
        )[-1]

        return (
            username
            if username
            else None
        )

    def close(self):

        try:

            self.github_client.close()

        except Exception:

            pass

        try:

            self.leetcode_client.close()

        except Exception:

            pass


career_analysis_service = (
    CareerAnalysisService()
)