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

        skill_evidence = (
            self._build_skill_evidence(
                resume_skills=resume_skills,
                linkedin_skills=linkedin_skills,
                github_skills=github_skills,
                leetcode_skills=leetcode_skills,
            )
        )

        project_evidence = (
            self._build_project_evidence(
                resume=resume,
                github_profile=github_profile,
                github_analysis=github_analysis,
                linkedin_profile=linkedin_profile,
            )
        )

        findings = (
            self._build_cross_source_findings(
                skill_evidence=skill_evidence,
                project_evidence=project_evidence,
            )
        )

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

        career_domains = (
            linkedin_analysis.career_domains
            if linkedin_analysis
            else []
        )

        return UnifiedCandidateProfile(
            name=name,
            headline=headline,
            location=location,
            skills=all_skills,
            career_domains=career_domains,
            current_title=current_title,
            current_company=current_company,
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
    # SKILL NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_skill(
        skill: str,
    ) -> str:

        aliases = {
            "python3": "python",
            "python": "python",

            "cpp": "c++",
            "c++": "c++",

            "javascript": "javascript",
            "js": "javascript",

            "typescript": "typescript",
            "ts": "typescript",

            "react.js": "react",
            "reactjs": "react",
            "react": "react",

            "node.js": "node.js",
            "nodejs": "node.js",

            "fastapi": "fastapi",
            "fast api": "fastapi",

            "spring boot": "spring boot",

            "machine learning": (
                "machine learning"
            ),
            "ml": "machine learning",

            "deep learning": "deep learning",

            "artificial intelligence": (
                "artificial intelligence"
            ),
            "ai": "artificial intelligence",

            "scikit-learn": "scikit-learn",
            "scikit learn": "scikit-learn",

            "postgres": "postgresql",
            "postgresql": "postgresql",

            "mysql": "mysql",
            "mongodb": "mongodb",

            "docker": "docker",
            "kubernetes": "kubernetes",

            "aws": "aws",

            "gcp": "google cloud",
            "google cloud": "google cloud",

            "azure": "azure",

            "git": "git",
            "github": "github",

            "rest api": "rest api",
            "rest apis": "rest api",

            "sql": "sql",
        }

        cleaned = (
            " ".join(
                skill.strip().split()
            )
            .lower()
        )

        return aliases.get(
            cleaned,
            cleaned,
        )

    @classmethod
    def _normalize_skills(
        cls,
        skills: list[str],
    ) -> list[str]:

        normalized = []
        seen = set()

        for skill in skills:

            if not skill:
                continue

            value = cls._normalize_skill(
                skill
            )

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            normalized.append(value)

        return normalized

    @staticmethod
    def _merge_unique(
        *skill_lists: list[str],
    ) -> list[str]:

        result = []
        seen = set()

        for skills in skill_lists:

            for skill in skills:

                key = skill.lower()

                if key in seen:
                    continue

                seen.add(key)
                result.append(skill)

        return sorted(
            result
        )

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

        for item in (
            analysis.demonstrated_skills
        ):

            if item.skill:
                skills.append(
                    item.skill
                )

        skills.extend(
            analysis.technical_strengths
        )

        for project in analysis.projects:

            if not project.meaningful_project:
                continue

            skills.extend(
                project.technologies
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

        skills.extend(
            analysis.languages
        )

        skills.extend(
            analysis.strongest_skills
        )

        skills.extend(
            analysis.strong_areas
        )

        skills.extend(
            analysis.developing_areas
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
    ) -> list[SkillEvidence]:

        all_skills = cls._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
        )

        evidence = []

        for skill in all_skills:

            resume = skill in resume_skills
            linkedin = skill in linkedin_skills
            github = skill in github_skills
            leetcode = skill in leetcode_skills

            supporting_sources = []

            if resume:
                supporting_sources.append(
                    "resume"
                )

            if linkedin:
                supporting_sources.append(
                    "linkedin"
                )

            if github:
                supporting_sources.append(
                    "github"
                )

            if leetcode:
                supporting_sources.append(
                    "leetcode"
                )

            demonstrated = (
                github
                or leetcode
            )

            claimed = (
                resume
                or linkedin
            )

            if (
                demonstrated
                and len(supporting_sources) >= 3
            ):

                status = (
                    "strongly_supported"
                )

            elif demonstrated:

                status = "demonstrated"

            elif claimed:

                status = "claimed_only"

            else:

                status = "unknown"

            missing_sources = []

            if claimed and not github:
                missing_sources.append(
                    "github"
                )

            if claimed and not leetcode:
                missing_sources.append(
                    "leetcode"
                )

            items = []

            if resume:

                items.append(
                    EvidenceItem(
                        source="resume",
                        evidence_type="claim",
                        value=skill,
                        strength="claim",
                    )
                )

            if linkedin:

                items.append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="claim",
                        value=skill,
                        strength="claim",
                    )
                )

            if github:

                items.append(
                    EvidenceItem(
                        source="github",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=skill,
                        strength="demonstrated",
                    )
                )

            if leetcode:

                items.append(
                    EvidenceItem(
                        source="leetcode",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=skill,
                        strength="demonstrated",
                    )
                )

            evidence.append(
                SkillEvidence(
                    skill=skill,
                    resume_claimed=resume,
                    linkedin_claimed=linkedin,
                    github_demonstrated=github,
                    leetcode_demonstrated=leetcode,
                    supporting_sources=(
                        supporting_sources
                    ),
                    missing_supporting_sources=(
                        missing_sources
                    ),
                    status=status,
                    evidence=items,
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

        # ------------------------------
        # GitHub
        # ------------------------------

        if github_analysis:

            for project in (
                github_analysis.projects
            ):

                if not project.meaningful_project:
                    continue

                name = cls._repository_name(
                    project.repository
                )

                key = cls._project_key(
                    name
                )

                projects.setdefault(
                    key,
                    {
                        "name": name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    },
                )

                projects[key]["github"] = True

                projects[key][
                    "repository"
                ] = project.repository

        elif github_profile:

            for repository in (
                github_profile.repositories
            ):

                key = cls._project_key(
                    repository.name
                )

                projects.setdefault(
                    key,
                    {
                        "name": repository.name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    },
                )

                projects[key]["github"] = True

                projects[key][
                    "repository"
                ] = repository.full_name

        # ------------------------------
        # LinkedIn
        # ------------------------------

        if linkedin_profile:

            for project in (
                linkedin_profile.projects
            ):

                key = cls._project_key(
                    project.name
                )

                projects.setdefault(
                    key,
                    {
                        "name": project.name,
                        "github": False,
                        "linkedin": False,
                        "resume": False,
                        "repository": None,
                    },
                )

                projects[key]["linkedin"] = True

        # ------------------------------
        # Resume
        # ------------------------------

        if resume and resume.projects:

            resume_text = (
                resume.projects.lower()
            )

            for item in projects.values():

                if (
                    item["name"].lower()
                    in resume_text
                ):

                    item["resume"] = True

        results = []

        for item in projects.values():

            github_present = item[
                "github"
            ]

            linkedin_present = item[
                "linkedin"
            ]

            resume_present = item[
                "resume"
            ]

            if (
                github_present
                and not linkedin_present
            ):

                status = (
                    "missing_from_linkedin"
                )

                finding = (
                    "Project is present on "
                    "GitHub but is not represented "
                    "in LinkedIn project evidence."
                )

            elif (
                github_present
                and linkedin_present
            ):

                status = "cross_source_supported"

                finding = (
                    "Project is represented "
                    "on both GitHub and LinkedIn."
                )

            elif linkedin_present:

                status = "linkedin_only"

                finding = (
                    "Project is listed on LinkedIn "
                    "but no matching GitHub project "
                    "was found."
                )

            else:

                status = "resume_only"

                finding = None

            evidence = []

            if github_present:

                evidence.append(
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

                evidence.append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="project",
                        value=item["name"],
                        strength="claim",
                    )
                )

            if resume_present:

                evidence.append(
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
                    resume_present=resume_present,
                    linkedin_present=linkedin_present,
                    github_present=github_present,
                    github_repository=item[
                        "repository"
                    ],
                    status=status,
                    finding=finding,
                    evidence=evidence,
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
    ) -> list[CrossSourceFinding]:

        findings = []

        # ------------------------------
        # Unsupported claims
        # ------------------------------

        for skill in skill_evidence:

            if not (
                skill.resume_claimed
                or skill.linkedin_claimed
            ):

                continue

            if (
                skill.github_demonstrated
                or skill.leetcode_demonstrated
            ):

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

            evidence = [
                EvidenceItem(
                    source=source,
                    evidence_type="claim",
                    value=skill.skill,
                    strength="claim",
                )
                for source in claim_sources
            ]

            findings.append(
                CrossSourceFinding(
                    finding_type=(
                        "unsupported_skill_claim"
                    ),
                    subject=skill.skill,
                    severity="warning",
                    message=(
                        f"{skill.skill} is claimed "
                        "in connected sources, but "
                        "no supporting evidence was "
                        "found in GitHub or LeetCode."
                    ),
                    sources=claim_sources,
                    evidence=evidence,
                )
            )

        # ------------------------------
        # GitHub project missing LinkedIn
        # ------------------------------

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

        # ------------------------------
        # LinkedIn project without GitHub
        # ------------------------------

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

        if resume and resume.name:
            return resume.name

        if (
            linkedin_analysis
            and linkedin_analysis.name
        ):
            return linkedin_analysis.name

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

        value = repository.strip()

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
            name.lower()
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

        return " ".join(
            value.split()
        )


unified_service = UnifiedService()