from app.schemas.github_ai_schema import (
    GitHubAIAnalysis,
)
from app.schemas.github_schema import (
    GitHubProfile,
)
from app.schemas.leetcode_schema import (
    LeetCodeAnalysis,
)
from app.schemas.linkedin_schema import (
    LinkedInAnalysis,
    LinkedInProfile,
)
from app.schemas.resume_schema import (
    ResumeData,
)
from app.schemas.unified_schema import (
    CrossSourceFinding,
    EvidenceItem,
    ProjectEvidence,
    SkillEvidence,
    UnifiedCandidateProfile,
)


class UnifiedService:

    # ==================================================
    # MAIN ENTRY POINT
    # ==================================================

    def build_profile(
        self,
        resume: ResumeData | None = None,
        github_profile: GitHubProfile | None = None,
        github_analysis: GitHubAIAnalysis | None = None,
        linkedin_profile: LinkedInProfile | None = None,
        linkedin_analysis: LinkedInAnalysis | None = None,
        leetcode_analysis: LeetCodeAnalysis | None = None,
    ) -> UnifiedCandidateProfile:

        # ----------------------------------------------
        # SKILLS
        # ----------------------------------------------

        resume_skills = self._normalize_skills(
            resume.skills
            if resume
            else []
        )

        linkedin_skills = self._normalize_skills(
            linkedin_analysis.claimed_skills
            if linkedin_analysis
            else []
        )

        github_skills = (
            self._extract_github_skills(
                github_analysis
            )
        )

        leetcode_skills = (
            self._extract_leetcode_skills(
                leetcode_analysis
            )
        )

        all_skills = self._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
        )

        # ----------------------------------------------
        # CAREER DOMAIN
        # ----------------------------------------------

        career_domains = (
            linkedin_analysis.career_domains
            if linkedin_analysis
            else []
        )

        source_relevance = (
            self._source_relevance(
                career_domains
            )
        )

        # ----------------------------------------------
        # SKILL EVIDENCE
        # ----------------------------------------------

        skill_evidence = (
            self._build_skill_evidence(
                resume_skills=resume_skills,
                linkedin_skills=linkedin_skills,
                github_skills=github_skills,
                leetcode_skills=leetcode_skills,
                career_domains=career_domains,
            )
        )

        # ----------------------------------------------
        # PROJECT EVIDENCE
        # ----------------------------------------------

        project_evidence = (
            self._build_project_evidence(
                resume=resume,
                github_profile=github_profile,
                github_analysis=github_analysis,
                linkedin_profile=linkedin_profile,
            )
        )

        # ----------------------------------------------
        # CROSS-SOURCE FINDINGS
        # ----------------------------------------------

        findings = (
            self._build_cross_source_findings(
                skill_evidence=skill_evidence,
                project_evidence=project_evidence,
                career_domains=career_domains,
                github_available=(
                    github_profile is not None
                ),
                leetcode_available=(
                    leetcode_analysis is not None
                ),
            )
        )

        # ----------------------------------------------
        # IDENTITY
        # ----------------------------------------------

        name = self._resolve_name(
            resume=resume,
            github_profile=github_profile,
            linkedin_analysis=linkedin_analysis,
        )

        headline = (
            linkedin_analysis.headline
            if linkedin_analysis
            else None
        )

        location = (
            linkedin_analysis.location
            if linkedin_analysis
            else None
        )

        current_title = (
            linkedin_analysis.current_title
            if linkedin_analysis
            else None
        )

        current_company = (
            linkedin_analysis.current_company
            if linkedin_analysis
            else None
        )

        # ----------------------------------------------
        # FINAL UNIFIED PROFILE
        # ----------------------------------------------

        return UnifiedCandidateProfile(
            name=name,
            headline=headline,
            location=location,
            skills=all_skills,
            career_domains=career_domains,
            current_title=current_title,
            current_company=current_company,

            primary_career_domain=(
                career_domains[0]
                if career_domains
                else None
            ),

            source_relevance=(
                source_relevance
            ),

            skill_evidence=skill_evidence,
            project_evidence=project_evidence,
            findings=findings,

            source_status={
                "resume": resume is not None,
                "github": github_profile is not None,
                "linkedin": (
                    linkedin_analysis is not None
                ),
                "leetcode": (
                    leetcode_analysis is not None
                ),
            },
        )

    # ==================================================
    # SOURCE RELEVANCE
    # ==================================================

    @staticmethod
    def _source_relevance(
        career_domains: list[str] | None,
    ) -> dict[str, str]:

        domains = {
            str(domain)
            .strip()
            .lower()
            for domain in (
                career_domains or []
            )
        }

        # ----------------------------------------------
        # Default
        # ----------------------------------------------

        if not domains:

            return {
                "resume": "high",
                "linkedin": "high",
                "github": "medium",
                "leetcode": "medium",
            }

        relevance = {
            "resume": "high",
            "linkedin": "high",
            "github": "medium",
            "leetcode": "low",
        }

        # ----------------------------------------------
        # MACHINE LEARNING / AI / DATA SCIENCE
        # ----------------------------------------------

        if domains.intersection({
            "machine_learning",
            "artificial_intelligence",
            "ai",
            "data_science",
        }):

            relevance.update({
                "resume": "high",
                "linkedin": "high",
                "github": "very_high",
                "leetcode": "medium",
            })

        # ----------------------------------------------
        # SOFTWARE / BACKEND
        # ----------------------------------------------

        if domains.intersection({
            "software_engineering",
            "software_development",
            "backend",
            "backend_development",
        }):

            relevance.update({
                "resume": "high",
                "linkedin": "high",
                "github": "very_high",
                "leetcode": "medium",
            })

        # ----------------------------------------------
        # FRONTEND / WEB
        # ----------------------------------------------

        if domains.intersection({
            "frontend",
            "frontend_development",
            "web_development",
            "full_stack",
            "full_stack_development",
        }):

            relevance.update({
                "resume": "high",
                "linkedin": "high",
                "github": "very_high",
                "leetcode": "low",
            })

        # ----------------------------------------------
        # DATA ENGINEERING / ANALYTICS
        # ----------------------------------------------

        if domains.intersection({
            "data_engineering",
            "data_analytics",
            "data_analysis",
        }):

            relevance.update({
                "resume": "high",
                "linkedin": "high",
                "github": "high",
                "leetcode": "low",
            })

        # ----------------------------------------------
        # DESIGN / NON-CODING
        # ----------------------------------------------

        if domains.intersection({
            "ui_ux",
            "design",
            "product_design",
            "graphic_design",
        }):

            relevance.update({
                "resume": "high",
                "linkedin": "high",
                "github": "low",
                "leetcode": "not_relevant",
            })

        return relevance

    # ==================================================
    # SKILL NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_skill(
        skill: str,
    ) -> str:

        value = (
            str(skill)
            .strip()
            .lower()
        )

        aliases = {

            # ------------------------------------------
            # Programming languages
            # ------------------------------------------

            "python": "python",
            "python3": "python",

            "cpp": "c++",
            "c plus plus": "c++",
            "c++": "c++",

            "javascript": "javascript",
            "js": "javascript",

            "typescript": "typescript",
            "ts": "typescript",

            "java": "java",

            "c": "c",

            # ------------------------------------------
            # AI / ML
            # ------------------------------------------

            "ai": (
                "artificial intelligence (ai)"
            ),

            "artificial intelligence":
                "artificial intelligence (ai)",

            "artificial intelligence (ai)":
                "artificial intelligence (ai)",

            "ml":
                "machine learning",

            "machine learning":
                "machine learning",

            "dl":
                "deep learning",

            "deep learning":
                "deep learning",

            "scikit learn":
                "scikit-learn",

            "scikit-learn":
                "scikit-learn",

            "sklearn":
                "scikit-learn",

            "tensorflow":
                "tensorflow",

            "xgboost":
                "xgboost",

            "xg boost":
                "xgboost",

            "catboost":
                "catboost",

            "cat boost":
                "catboost",

            "numpy":
                "numpy",

            "pandas":
                "pandas",

            # ------------------------------------------
            # Backend / Web
            # ------------------------------------------

            "fastapi":
                "fastapi",

            "flask":
                "flask",

            "react":
                "react",

            "react.js":
                "react",

            "reactjs":
                "react",

            "next.js":
                "next.js",

            "nextjs":
                "next.js",

            "html":
                "html",

            "css":
                "css",

            # ------------------------------------------
            # Databases
            # ------------------------------------------

            "mysql":
                "mysql",

            "postgres":
                "postgresql",

            "postgresql":
                "postgresql",

            "sql":
                "sql",

            # ------------------------------------------
            # Tools
            # ------------------------------------------

            "git":
                "git",

            "github":
                "github",

            "docker":
                "docker",

            "render":
                "render",

            "jupyter":
                "jupyter notebook",

            "jupyter notebook":
                "jupyter notebook",

            # ------------------------------------------
            # DSA / LeetCode
            # ------------------------------------------

            "dsa":
                "dsa",

            "data structures":
                "data structures",

            "array":
                "arrays",

            "arrays":
                "arrays",

            "string":
                "strings",

            "strings":
                "strings",

            "linked list":
                "linked list",

            "hash table":
                "hash table",

            "hashmap":
                "hash table",

            "hash map":
                "hash table",

            "stack":
                "stack",

            "queue":
                "queue",

            "binary search":
                "binary search",

            "sorting":
                "sorting",

            "two pointers":
                "two pointers",

            "sliding window":
                "sliding window",

            "tree":
                "trees",

            "trees":
                "trees",

            "graph":
                "graphs",

            "graphs":
                "graphs",

            "heap":
                "heap / priority queue",

            "priority queue":
                "heap / priority queue",

            "greedy":
                "greedy",

            "dynamic programming":
                "dynamic programming",
        }

        return aliases.get(
            value,
            value,
        )

    @classmethod
    def _normalize_skills(
        cls,
        skills,
    ) -> list[str]:

        normalized = []

        for skill in skills or []:

            if not isinstance(
                skill,
                str,
            ):

                skill_value = getattr(
                    skill,
                    "skill",
                    None,
                )

                if not skill_value:
                    continue

                skill = skill_value

            value = cls._normalize_skill(
                skill
            )

            if (
                value
                and value not in normalized
            ):
                normalized.append(value)

        return normalized

    @classmethod
    def _merge_unique(
        cls,
        *skill_lists,
    ) -> list[str]:

        merged = []

        for skills in skill_lists:

            for skill in skills or []:

                if not isinstance(
                    skill,
                    str,
                ):

                    skill_value = getattr(
                        skill,
                        "skill",
                        None,
                    )

                    if not skill_value:
                        continue

                    skill = skill_value

                value = cls._normalize_skill(
                    skill
                )

                if (
                    value
                    and value not in merged
                ):
                    merged.append(value)

        return merged

    # ==================================================
    # GITHUB SKILLS
    # ==================================================

    @classmethod
    def _extract_github_skills(
        cls,
        analysis: GitHubAIAnalysis | None,
    ) -> list[str]:

        if not analysis:
            return []

        skills = []

        # ----------------------------------------------
        # Demonstrated skills
        # ----------------------------------------------

        for item in (
            analysis.demonstrated_skills
            or []
        ):

            if isinstance(
                item,
                str,
            ):

                value = item

            else:

                value = getattr(
                    item,
                    "skill",
                    None,
                )

            if value:
                skills.append(
                    value
                )

        # ----------------------------------------------
        # Project technologies
        # ----------------------------------------------

        for project in (
            analysis.projects
            or []
        ):

            for technology in (
                project.technologies
                or []
            ):

                if technology:
                    skills.append(
                        technology
                    )

        return cls._normalize_skills(
            skills
        )

    # ==================================================
    # LEETCODE SKILLS
    # ==================================================

    @classmethod
    def _extract_leetcode_skills(
        cls,
        analysis: LeetCodeAnalysis | None,
    ) -> list[str]:

        if not analysis:
            return []

        skills = []

        # ----------------------------------------------
        # Languages
        # ----------------------------------------------

        skills.extend(
            analysis.languages
            or []
        )

        # ----------------------------------------------
        # Strong skills
        # ----------------------------------------------

        skills.extend(
            analysis.strongest_skills
            or []
        )

        skills.extend(
            analysis.strong_areas
            or []
        )

        # ----------------------------------------------
        # Developing areas
        # ----------------------------------------------

        skills.extend(
            analysis.developing_areas
            or []
        )

        return cls._normalize_skills(
            skills
        )

    # ==================================================
    # SKILL EVIDENCE
    # ==================================================

    @classmethod
    def _build_skill_evidence(
        cls,
        resume_skills: list[str],
        linkedin_skills: list[str],
        github_skills: list[str],
        leetcode_skills: list[str],
        career_domains: list[str] | None = None,
    ) -> list[SkillEvidence]:

        all_skills = cls._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
        )

        source_relevance = (
            cls._source_relevance(
                career_domains
            )
        )

        evidence = []

        for skill in all_skills:

            resume_claimed = (
                skill in resume_skills
            )

            linkedin_claimed = (
                skill in linkedin_skills
            )

            github_demonstrated = (
                skill in github_skills
            )

            leetcode_demonstrated = (
                skill in leetcode_skills
            )

            supporting_sources = []

            if resume_claimed:
                supporting_sources.append(
                    "resume"
                )

            if linkedin_claimed:
                supporting_sources.append(
                    "linkedin"
                )

            if github_demonstrated:
                supporting_sources.append(
                    "github"
                )

            if leetcode_demonstrated:
                supporting_sources.append(
                    "leetcode"
                )

            demonstrated = (
                github_demonstrated
                or leetcode_demonstrated
            )

            claimed = (
                resume_claimed
                or linkedin_claimed
            )

            # ------------------------------------------
            # Evidence status
            # ------------------------------------------

            if (
                demonstrated
                and len(
                    supporting_sources
                ) >= 3
            ):

                status = (
                    "strongly_supported"
                )

            elif demonstrated:

                status = (
                    "demonstrated"
                )

            elif claimed:

                status = (
                    "claimed_only"
                )

            else:

                status = (
                    "unknown"
                )

            # ------------------------------------------
            # Missing supporting sources
            # ------------------------------------------

            missing_sources = []

            if (
                claimed
                and not github_demonstrated
            ):

                missing_sources.append(
                    "github"
                )

            if (
                claimed
                and not leetcode_demonstrated
            ):

                missing_sources.append(
                    "leetcode"
                )

            # ------------------------------------------
            # Evidence items
            # ------------------------------------------

            evidence_items = []

            if resume_claimed:

                evidence_items.append(
                    EvidenceItem(
                        source="resume",
                        evidence_type="claim",
                        value=skill,
                        strength="claim",
                    )
                )

            if linkedin_claimed:

                evidence_items.append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="claim",
                        value=skill,
                        strength="claim",
                    )
                )

            if github_demonstrated:

                evidence_items.append(
                    EvidenceItem(
                        source="github",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=skill,
                        strength="demonstrated",
                    )
                )

            if leetcode_demonstrated:

                evidence_items.append(
                    EvidenceItem(
                        source="leetcode",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=skill,
                        strength="demonstrated",
                    )
                )

            # ------------------------------------------
            # Skill relevance
            # ------------------------------------------

            if github_demonstrated:

                if (
                    source_relevance["github"]
                    == "very_high"
                ):

                    relevance = "high"

                elif (
                    source_relevance["github"]
                    == "high"
                ):

                    relevance = "medium"

                else:

                    relevance = "standard"

            elif leetcode_demonstrated:

                if (
                    source_relevance["leetcode"]
                    == "very_high"
                ):

                    relevance = "high"

                elif (
                    source_relevance["leetcode"]
                    == "medium"
                ):

                    relevance = "medium"

                else:

                    relevance = "low"

            else:

                relevance = "standard"

            evidence.append(
                SkillEvidence(
                    skill=skill,
                    resume_claimed=(
                        resume_claimed
                    ),
                    linkedin_claimed=(
                        linkedin_claimed
                    ),
                    github_demonstrated=(
                        github_demonstrated
                    ),
                    leetcode_demonstrated=(
                        leetcode_demonstrated
                    ),
                    supporting_sources=(
                        supporting_sources
                    ),
                    missing_supporting_sources=(
                        missing_sources
                    ),
                    status=status,
                    relevance=relevance,
                    evidence=evidence_items,
                )
            )

        return evidence

    # ==================================================
    # PROJECT EVIDENCE
    # ==================================================

    @classmethod
    def _build_project_evidence(
        cls,
        resume: ResumeData | None,
        github_profile: GitHubProfile | None,
        github_analysis: GitHubAIAnalysis | None,
        linkedin_profile: LinkedInProfile | None,
    ) -> list[ProjectEvidence]:

        projects = {}

        # ----------------------------------------------
        # GitHub AI projects
        # ----------------------------------------------

        if github_analysis:

            for project in (
                github_analysis.projects
                or []
            ):

                name = cls._repository_name(
                    project.repository
                )

                key = cls._project_key(
                    name
                )

                if key not in projects:

                    projects[key] = {
                        "name": name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    }

                projects[key][
                    "github"
                ] = True

                projects[key][
                    "repository"
                ] = project.repository

        # ----------------------------------------------
        # Raw GitHub fallback
        # ----------------------------------------------

        if github_profile:

            for repository in (
                github_profile.repositories
                or []
            ):

                name = repository.name

                key = cls._project_key(
                    name
                )

                if key not in projects:

                    projects[key] = {
                        "name": name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    }

                projects[key][
                    "github"
                ] = True

                projects[key][
                    "repository"
                ] = (
                    repository.full_name
                    if getattr(
                        repository,
                        "full_name",
                        None,
                    )
                    else name
                )

        # ----------------------------------------------
        # LinkedIn projects
        # ----------------------------------------------

        if linkedin_profile:

            for project in (
                linkedin_profile.projects
                or []
            ):

                name = project.name

                key = cls._project_key(
                    name
                )

                if key not in projects:

                    projects[key] = {
                        "name": name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    }

                projects[key][
                    "linkedin"
                ] = True

        # ----------------------------------------------
        # Resume project matching
        # ----------------------------------------------

        if (
            resume
            and resume.projects
        ):

            resume_text = (
                resume.projects.lower()
            )

            normalized_resume = (
                cls._project_key(
                    resume_text
                )
            )

            for item in (
                projects.values()
            ):

                normalized_name = (
                    cls._project_key(
                        item["name"]
                    )
                )

                if (
                    normalized_name
                    and normalized_name
                    in normalized_resume
                ):

                    item["resume"] = True

        # ----------------------------------------------
        # Build result
        # ----------------------------------------------

        results = []

        for item in (
            projects.values()
        ):

            github_present = (
                item["github"]
            )

            linkedin_present = (
                item["linkedin"]
            )

            resume_present = (
                item["resume"]
            )

            if (
                github_present
                and linkedin_present
            ):

                status = (
                    "cross_source_supported"
                )

                finding = (
                    "Project is represented "
                    "on both GitHub and LinkedIn."
                )

            elif github_present:

                status = (
                    "missing_from_linkedin"
                )

                finding = (
                    "Project is present on "
                    "GitHub but is not represented "
                    "in LinkedIn project evidence."
                )

            elif linkedin_present:

                status = (
                    "linkedin_only"
                )

                finding = (
                    "Project is listed on LinkedIn "
                    "but no matching GitHub project "
                    "was found."
                )

            elif resume_present:

                status = (
                    "resume_only"
                )

                finding = (
                    "Project is present in the "
                    "resume but was not matched "
                    "to GitHub or LinkedIn."
                )

            else:

                status = "unknown"
                finding = None

            project_evidence = []

            if github_present:

                project_evidence.append(
                    EvidenceItem(
                        source="github",
                        evidence_type="project",
                        value=item["name"],
                        strength="demonstrated",
                        details=(
                            item["repository"]
                        ),
                    )
                )

            if linkedin_present:

                project_evidence.append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="project",
                        value=item["name"],
                        strength="claim",
                    )
                )

            if resume_present:

                project_evidence.append(
                    EvidenceItem(
                        source="resume",
                        evidence_type="project",
                        value=item["name"],
                        strength="claim",
                    )
                )

            results.append(
                ProjectEvidence(
                    name=item["name"],
                    resume_present=(
                        resume_present
                    ),
                    linkedin_present=(
                        linkedin_present
                    ),
                    github_present=(
                        github_present
                    ),
                    github_repository=(
                        item["repository"]
                    ),
                    status=status,
                    finding=finding,
                    evidence=project_evidence,
                )
            )

        return results

    # ==================================================
    # CROSS-SOURCE FINDINGS
    # ==================================================

    @staticmethod
    def _build_cross_source_findings(
        skill_evidence: list[SkillEvidence],
        project_evidence: list[ProjectEvidence],
        career_domains: list[str] | None = None,
        github_available: bool = False,
        leetcode_available: bool = False,
    ) -> list[CrossSourceFinding]:

        findings = []

        # ----------------------------------------------
        # Determine relevant verification sources
        # ----------------------------------------------

        source_relevance = (
            UnifiedService
            ._source_relevance(
                career_domains
            )
        )

        verification_sources = []

        if (
            github_available
            and source_relevance["github"]
            != "not_relevant"
        ):

            verification_sources.append(
                "github"
            )

        if (
            leetcode_available
            and source_relevance["leetcode"]
            not in {
                "low",
                "not_relevant",
            }
        ):

            verification_sources.append(
                "leetcode"
            )

        # ----------------------------------------------
        # Skill claims that are not independently
        # demonstrated by a relevant source
        # ----------------------------------------------

        for skill in skill_evidence:

            if not (
                skill.resume_claimed
                or skill.linkedin_claimed
            ):

                continue

            # Already demonstrated.
            if (
                skill.github_demonstrated
                or skill.leetcode_demonstrated
            ):

                continue

            # Nothing relevant is connected.
            if not verification_sources:

                continue

            claim_sources = []

            if skill.resume_claimed:

                claim_sources.append(
                    "resume"
                )

            if skill.linkedin_claimed:

                claim_sources.append(
                    "linkedin"
                )

            evidence = []

            for source in claim_sources:

                evidence.append(
                    EvidenceItem(
                        source=source,
                        evidence_type="claim",
                        value=skill.skill,
                        strength="claim",
                    )
                )

            findings.append(
                CrossSourceFinding(
                    finding_type=(
                        "skill_not_independently_verified"
                    ),
                    subject=skill.skill,
                    severity="warning",
                    message=(
                        f"{skill.skill} is claimed "
                        f"in {', '.join(claim_sources)}, "
                        "but no independent supporting "
                        "evidence was found in the "
                        "currently relevant connected "
                        "verification sources "
                        f"({', '.join(verification_sources)}). "
                        "This does not mean the skill "
                        "is incorrect or that the "
                        "candidate does not possess it."
                    ),
                    sources=(
                        claim_sources
                        + verification_sources
                    ),
                    evidence=evidence,
                )
            )

        # ----------------------------------------------
        # GitHub project missing from LinkedIn
        # ----------------------------------------------

        for project in project_evidence:

            if (
                project.github_present
                and not project.linkedin_present
            ):

                findings.append(
                    CrossSourceFinding(
                        finding_type=(
                            "project_missing_from_linkedin"
                        ),
                        subject=project.name,
                        severity="info",
                        message=(
                            f"{project.name} appears "
                            "as a GitHub project but "
                            "is not represented in "
                            "LinkedIn project evidence."
                        ),
                        sources=[
                            "github",
                            "linkedin",
                        ],
                        evidence=project.evidence,
                    )
                )

        # ----------------------------------------------
        # LinkedIn project without GitHub
        # ----------------------------------------------

        for project in project_evidence:

            if (
                project.linkedin_present
                and not project.github_present
            ):

                findings.append(
                    CrossSourceFinding(
                        finding_type=(
                            "linkedin_project_without_github_evidence"
                        ),
                        subject=project.name,
                        severity="info",
                        message=(
                            f"{project.name} is listed "
                            "on LinkedIn but no matching "
                            "GitHub project was found."
                        ),
                        sources=[
                            "linkedin",
                            "github",
                        ],
                        evidence=project.evidence,
                    )
                )

        return findings

    # ==================================================
    # IDENTITY
    # ==================================================

    @staticmethod
    def _resolve_name(
        resume: ResumeData | None,
        github_profile: GitHubProfile | None,
        linkedin_analysis: LinkedInAnalysis | None,
    ) -> str | None:

        if (
            resume
            and resume.name
        ):

            return resume.name

        if (
            linkedin_analysis
            and linkedin_analysis.name
        ):

            return (
                linkedin_analysis.name
            )

        if (
            github_profile
            and github_profile.name
        ):

            return github_profile.name

        return None

    # ==================================================
    # PROJECT NAME HELPERS
    # ==================================================

    @staticmethod
    def _repository_name(
        repository: str,
    ) -> str:

        value = (
            str(repository)
            .strip()
        )

        if "/" in value:

            return value.split(
                "/"
            )[-1]

        return value

    @staticmethod
    def _project_key(
        name: str,
    ) -> str:

        value = (
            str(name)
            .lower()
            .strip()
        )

        value = value.replace(
            "_",
            " ",
        )

        value = value.replace(
            "-",
            " ",
        )

        value = value.replace(
            "|",
            " ",
        )

        return " ".join(
            value.split()
        )


unified_service = UnifiedService()