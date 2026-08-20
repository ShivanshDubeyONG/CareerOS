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

        findings = self._build_cross_source_findings(
            skill_evidence=skill_evidence,
            project_evidence=project_evidence,
            github_available=(
                github_profile is not None
                and github_analysis is not None
            ),
            leetcode_available=(
                leetcode_analysis is not None
            ),
            linkedin_available=(
                linkedin_profile is not None
                and linkedin_analysis is not None
            ),
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
                "github": (
                    github_profile is not None
                    and github_analysis is not None
                ),
                "linkedin": (
                    linkedin_profile is not None
                    and linkedin_analysis is not None
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

            "node.js": "node",
            "nodejs": "node",

            "scikit learn": "scikit-learn",
            "scikit_learn": "scikit-learn",
            "sklearn": "scikit-learn",
            "scikit-learn": "scikit-learn",

            "machine-learning": "machine learning",
            "machine_learning": "machine learning",

            "deep-learning": "deep learning",
            "deep_learning": "deep learning",

            "artificial intelligence": (
                "artificial intelligence (ai)"
            ),
            "artificial intelligence (ai)": (
                "artificial intelligence (ai)"
            ),
        }

        value = (
            skill
            .strip()
            .lower()
        )

        return aliases.get(
            value,
            value,
        )

    def _normalize_skills(
        self,
        skills: list[str],
    ) -> list[str]:

        normalized = []

        for skill in skills:

            if not skill:
                continue

            value = self._normalize_skill(
                skill
            )

            if value and value not in normalized:
                normalized.append(value)

        return normalized

    @staticmethod
    def _merge_unique(
        *skill_lists: list[str],
    ) -> list[str]:

        result = []

        for skill_list in skill_lists:

            for skill in skill_list:

                if skill not in result:
                    result.append(skill)

        return result

    # ==================================================
    # GITHUB SKILLS
    # ==================================================

    @staticmethod
    def _extract_github_skills(
        analysis: GitHubAIAnalysis | None,
    ) -> list[str]:

        if analysis is None:
            return []

        skills = []

        if hasattr(
            analysis,
            "skills",
        ):

            for skill in analysis.skills:

                if isinstance(
                    skill,
                    str,
                ):
                    skills.append(skill)

                elif isinstance(
                    skill,
                    dict,
                ):

                    value = (
                        skill.get("skill")
                        or skill.get("name")
                    )

                    if value:
                        skills.append(value)

        if hasattr(
            analysis,
            "projects",
        ):

            for project in analysis.projects:

                technologies = getattr(
                    project,
                    "technologies",
                    [],
                )

                for technology in technologies:

                    if technology:
                        skills.append(
                            technology
                        )

        return skills

    # ==================================================
    # LEETCODE SKILLS
    # ==================================================

    @staticmethod
    def _extract_leetcode_skills(
        analysis: LeetCodeAnalysis | None,
    ) -> list[str]:

        if analysis is None:
            return []

        skills = []

        if hasattr(
            analysis,
            "strong_areas",
        ):

            for area in analysis.strong_areas:

                if area:
                    skills.append(area)

        if hasattr(
            analysis,
            "dsa_coverage",
        ):

            coverage = (
                analysis.dsa_coverage
            )

            if isinstance(
                coverage,
                dict,
            ):

                for area in coverage.keys():

                    if area:
                        skills.append(area)

        return skills

    # ==================================================
    # SKILL EVIDENCE
    # ==================================================

    def _build_skill_evidence(
        self,
        resume_skills: list[str],
        linkedin_skills: list[str],
        github_skills: list[str],
        leetcode_skills: list[str],
    ) -> list[SkillEvidence]:

        all_skills = self._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
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

            missing_sources = []

            if not github_demonstrated:
                missing_sources.append(
                    "github"
                )

            if not leetcode_demonstrated:
                missing_sources.append(
                    "leetcode"
                )

            if (
                github_demonstrated
                or leetcode_demonstrated
            ):

                status = "demonstrated"

            elif (
                resume_claimed
                or linkedin_claimed
            ):

                status = "claimed"

            else:

                status = "evidence_only"

            evidence.append(
                SkillEvidence(
                    skill=skill,
                    resume_claimed=resume_claimed,
                    linkedin_claimed=linkedin_claimed,
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
                )
            )

        return evidence

    # ==================================================
    # PROJECT EVIDENCE
    # ==================================================

    def _build_project_evidence(
        self,
        resume: ResumeData | None,
        github_profile: GitHubProfile | None,
        github_analysis: GitHubAIAnalysis | None,
        linkedin_profile: LinkedInProfile | None,
    ) -> list[ProjectEvidence]:

        projects = {}

        # ------------------------------------------
        # GitHub projects
        # ------------------------------------------

        if github_profile:

            for repository in (
                github_profile.repositories
            ):

                name = (
                    repository.name
                )

                key = self._project_key(
                    name
                )

                projects[key] = {
                    "name": name,
                    "resume": False,
                    "github": True,
                    "linkedin": False,
                    "evidence": [],
                }

                projects[key][
                    "evidence"
                ].append(
                    EvidenceItem(
                        source="github",
                        evidence_type="repository",
                        value=(
                            repository.full_name
                        ),
                        strength="demonstrated",
                    )
                )

        # ------------------------------------------
        # Resume projects
        # ------------------------------------------

        if resume:

            resume_text = (
                resume.projects
                or ""
            )

            if resume_text.strip():

                # Resume project text is preserved
                # as evidence rather than inventing
                # project names.
                key = self._project_key(
                    "resume_projects"
                )

                projects.setdefault(
                    key,
                    {
                        "name": "Resume Projects",
                        "resume": False,
                        "github": False,
                        "linkedin": False,
                        "evidence": [],
                    },
                )

                projects[key][
                    "resume"
                ] = True

                projects[key][
                    "evidence"
                ].append(
                    EvidenceItem(
                        source="resume",
                        evidence_type="project",
                        value=resume_text,
                        strength="claim",
                    )
                )

        # ------------------------------------------
        # LinkedIn projects
        # ------------------------------------------

        if linkedin_profile:

            for project in (
                linkedin_profile.projects
            ):

                name = getattr(
                    project,
                    "name",
                    None,
                )

                if not name:
                    continue

                key = self._project_key(
                    name
                )

                projects.setdefault(
                    key,
                    {
                        "name": name,
                        "resume": False,
                        "github": False,
                        "linkedin": False,
                        "evidence": [],
                    },
                )

                projects[key][
                    "linkedin"
                ] = True

                projects[key][
                    "evidence"
                ].append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="project",
                        value=name,
                        strength="claim",
                    )
                )

        # ------------------------------------------
        # Convert to schema
        # ------------------------------------------

        result = []

        for data in projects.values():

            result.append(
                ProjectEvidence(
                    name=data["name"],
                    resume_present=data["resume"],
                    github_present=data["github"],
                    linkedin_present=data["linkedin"],
                    evidence=data["evidence"],
                )
            )

        return result

    # ==================================================
    # CROSS-SOURCE FINDINGS
    # ==================================================

    @staticmethod
    def _build_cross_source_findings(
        skill_evidence: list[SkillEvidence],
        project_evidence: list[ProjectEvidence],
        github_available: bool = False,
        leetcode_available: bool = False,
        linkedin_available: bool = False,
    ) -> list[CrossSourceFinding]:

        findings = []

        # ------------------------------------------
        # Unsupported / unverifiable skill claims
        # ------------------------------------------

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

            verification_sources_available = (
                github_available
                or leetcode_available
            )

            if not verification_sources_available:

                findings.append(
                    CrossSourceFinding(
                        finding_type=(
                            "skill_verification_unavailable"
                        ),
                        subject=skill.skill,
                        severity="info",
                        message=(
                            f"{skill.skill} is claimed "
                            "in connected sources, but "
                            "GitHub and LeetCode evidence "
                            "were unavailable for "
                            "verification."
                        ),
                        sources=claim_sources,
                        evidence=evidence,
                    )
                )

            else:

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
                            "found in the available "
                            "verification sources."
                        ),
                        sources=claim_sources,
                        evidence=evidence,
                    )
                )

        # ------------------------------------------
        # GitHub project missing LinkedIn
        # ------------------------------------------

        if github_available:

            for project in project_evidence:

                if (
                    project.github_present
                    and not project.linkedin_present
                    and linkedin_available
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

        # ------------------------------------------
        # LinkedIn project without GitHub
        # ------------------------------------------

        if linkedin_available:

            for project in project_evidence:

                if (
                    project.linkedin_present
                    and not project.github_present
                    and github_available
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