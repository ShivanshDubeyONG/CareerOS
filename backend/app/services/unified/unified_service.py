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

import re


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

        # --------------------------------------------------
        # RESUME SKILLS
        # --------------------------------------------------

        resume_skills = self._normalize_skills(
            resume.skills
            if resume
            else []
        )

        # --------------------------------------------------
        # LINKEDIN SKILLS
        # --------------------------------------------------

        linkedin_skills = self._normalize_skills(
            linkedin_analysis.claimed_skills
            if linkedin_analysis
            else []
        )

        # --------------------------------------------------
        # GITHUB SKILLS
        # --------------------------------------------------

        github_skills = (
            self._extract_github_skills(
                github_analysis
            )
        )

        # --------------------------------------------------
        # LEETCODE SKILLS
        # --------------------------------------------------

        leetcode_skills = (
            self._extract_leetcode_skills(
                leetcode_analysis
            )
        )

        # --------------------------------------------------
        # MERGED SKILLS
        # --------------------------------------------------

        all_skills = self._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
        )

        # --------------------------------------------------
        # SKILL EVIDENCE
        # --------------------------------------------------

        skill_evidence = (
            self._build_skill_evidence(
                resume_skills=resume_skills,
                linkedin_skills=linkedin_skills,
                github_skills=github_skills,
                leetcode_skills=leetcode_skills,
            )
        )

        # --------------------------------------------------
        # PROJECT EVIDENCE
        # --------------------------------------------------

        project_evidence = (
            self._build_project_evidence(
                resume=resume,
                github_profile=github_profile,
                github_analysis=github_analysis,
                linkedin_profile=linkedin_profile,
            )
        )

        # --------------------------------------------------
        # CROSS-SOURCE FINDINGS
        # --------------------------------------------------

        findings = (
            self._build_cross_source_findings(
                skill_evidence=skill_evidence,
                project_evidence=project_evidence,
                linkedin_profile=linkedin_profile,
                linkedin_analysis=linkedin_analysis,
                leetcode_analysis=leetcode_analysis,
            )
        )

        # --------------------------------------------------
        # IDENTITY
        # --------------------------------------------------

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

        # --------------------------------------------------
        # FINAL PROFILE
        # --------------------------------------------------

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

        if not isinstance(skill, str):
            return ""

        cleaned = " ".join(
            skill.strip().split()
        ).lower()

        if not cleaned:
            return ""

        # Reject evidence/prose accidentally returned as a skill.
        if len(cleaned) > 70 or len(cleaned.split()) > 7:
            return ""

        prose_prefixes = (
            "practical knowledge of ",
            "knowledge of ",
            "knowledge about ",
            "experience with ",
            "experience in ",
            "experience using ",
            "proficient in ",
            "proficiency in ",
            "familiar with ",
            "working knowledge of ",
            "understanding of ",
            "usage of ",
            "use of ",
            "used for ",
            "used in ",
            "ability to ",
            "worked with ",
            "worked on ",
            "developed using ",
            "built using ",
            "implemented using ",
            "integration using ",
            "integration with ",
            "development using ",
            "development with ",
        )

        if cleaned.startswith(prose_prefixes):
            return ""

        prose_phrases = (
            "verified via",
            "verified through",
            "demonstrated through",
            "demonstrated via",
            "supported by",
            "shown through",
            "shown via",
            "as demonstrated",
            "as evidenced",
            "project dependencies",
            "repository dependencies",
            "repository implementation",
            "project implementation",
            "for model training",
            "for training and prototyping",
            "used for training",
        )

        if any(
            phrase in cleaned
            for phrase in prose_phrases
        ):
            return ""

        if cleaned.endswith((".", "!", "?")):
            return ""

        if cleaned.count(",") >= 3 or cleaned.count(";") >= 2:
            return ""

        aliases = {
            # Programming languages
            "python3": "python",
            "python": "python",
            "cpp": "c++",
            "c plus plus": "c++",
            "c++": "c++",
            "javascript": "javascript",
            "js": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "java": "java",
            "c": "c",
            "golang": "go",
            "go": "go",
            "rust": "rust",
            "kotlin": "kotlin",
            "swift": "swift",

            # Frontend / backend
            "html5": "html",
            "html": "html",
            "css3": "css",
            "css": "css",
            "react.js": "react",
            "reactjs": "react",
            "react": "react",
            "next.js": "next.js",
            "nextjs": "next.js",
            "node.js": "node.js",
            "nodejs": "node.js",
            "fast api": "fastapi",
            "fastapi": "fastapi",
            "flask": "flask",
            "django": "django",
            "spring boot": "spring boot",
            "express.js": "express",
            "expressjs": "express",
            "express": "express",

            # AI / ML
            "ml": "machine learning",
            "machine learning": "machine learning",
            "dl": "deep learning",
            "deep learning": "deep learning",
            "ai": "artificial intelligence (ai)",
            "artificial intelligence": "artificial intelligence (ai)",
            "artificial intelligence (ai)": "artificial intelligence (ai)",
            "nlp": "natural language processing",
            "natural language processing": "natural language processing",
            "computer vision": "computer vision",
            "scikit learn": "scikit-learn",
            "sklearn": "scikit-learn",
            "scikit-learn": "scikit-learn",
            "tensorflow": "tensorflow",
            "pytorch": "pytorch",
            "keras": "keras",
            "xg boost": "xgboost",
            "xgboost": "xgboost",
            "cat boost": "catboost",
            "catboost": "catboost",
            "numpy": "numpy",
            "pandas": "pandas",
            "matplotlib": "matplotlib",
            "seaborn": "seaborn",

            # Databases
            "postgres": "postgresql",
            "postgresql": "postgresql",
            "mysql": "mysql",
            "mongodb": "mongodb",
            "mongo": "mongodb",
            "sql": "sql",
            "redis": "redis",

            # Cloud / DevOps
            "docker": "docker",
            "kubernetes": "kubernetes",
            "k8s": "kubernetes",
            "aws": "aws",
            "gcp": "google cloud",
            "google cloud": "google cloud",
            "azure": "azure",
            "render": "render",
            "git": "git",
            "github": "github",
            "github actions": "github actions",
            "jenkins": "jenkins",
            "ci/cd": "ci/cd",
            "linux": "linux",
            "bash": "bash",

            # APIs
            "rest api": "rest api",
            "rest apis": "rest api",
            "rest": "rest api",
            "api": "api",

            # DSA
            "dsa": "dsa",
            "data structure": "data structures",
            "data structures": "data structures",
            "algorithm": "algorithms",
            "algorithms": "algorithms",
            "array": "arrays",
            "arrays": "arrays",
            "string": "strings",
            "strings": "strings",
            "hashmap": "hash table",
            "hash map": "hash table",
            "hash table": "hash table",
            "stack": "stack",
            "queue": "queue",
            "linked list": "linked list",
            "binary search": "binary search",
            "sorting": "sorting",
            "two pointers": "two pointers",
            "sliding window": "sliding window",
            "tree": "trees",
            "trees": "trees",
            "graph": "graphs",
            "graphs": "graphs",
            "heap": "heap / priority queue",
            "priority queue": "heap / priority queue",
            "heap / priority queue": "heap / priority queue",
            "greedy": "greedy",
            "dynamic programming": "dynamic programming",
            "dp": "dynamic programming",
            "backtracking": "backtracking",
            "recursion": "recursion",
            "bit manipulation": "bit manipulation",
        }

        return aliases.get(cleaned, cleaned)

    @classmethod
    def _normalize_skills(
        cls,
        skills: list[str],
    ) -> list[str]:

        normalized = []
        seen = set()

        for skill in skills or []:

            # Defensive handling in case an object
            # rather than a string is accidentally passed.
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

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            normalized.append(value)

        return normalized

    @classmethod
    def _merge_unique(
        cls,
        *skill_lists: list[str],
    ) -> list[str]:

        result = []
        seen = set()

        for skills in skill_lists or []:

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

                normalized = (
                    cls._normalize_skill(
                        skill
                    )
                )

                if not normalized:
                    continue

                if normalized in seen:
                    continue

                seen.add(normalized)
                result.append(normalized)

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

        if isinstance(analysis, dict):
            analysis = GitHubAIAnalysis.model_validate(analysis)

        skills = []

        # Explicit AI-detected demonstrations.
        for item in analysis.demonstrated_skills or []:
            value = (
                item
                if isinstance(item, str)
                else getattr(item, "skill", None)
            )
            if value:
                skills.append(value)

        # Technical strengths are useful, but only concise
        # skill-like values survive _normalize_skill().
        for item in analysis.technical_strengths or []:
            if item:
                skills.append(item)

        # Project technology evidence is the strongest
        # repository-level source.
        for project in analysis.projects or []:
            for technology in project.technology_evidence or []:
                confidence = str(
                    technology.confidence
                ).lower().strip()

                if confidence in {"high", "medium"}:
                    if technology.technology:
                        skills.append(
                            technology.technology
                        )

            # Legacy compatibility, still filtered by the
            # strict normalizer.
            for technology in project.technologies or []:
                if technology:
                    skills.append(technology)

        return cls._normalize_skills(skills)

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

        # Languages are directly demonstrated by LeetCode work.
        skills.extend(analysis.languages or [])

        # Only established strengths count as demonstrated.
        skills.extend(analysis.strongest_skills or [])
        skills.extend(analysis.strong_areas or [])

        # IMPORTANT:
        # developing_areas are intentionally excluded here.
        # They remain useful for LeetCode analysis, but a
        # developing area should not become a demonstrated
        # career skill.

        return cls._normalize_skills(skills)

    # ==================================================
    # SKILL-SOURCE RELEVANCE
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # LeetCode is NOT a universal skill verifier.
    # ==================================================

    @classmethod
    def _relevant_verification_sources(
        cls,
        skill: str,
    ) -> set[str]:

        normalized = (
            cls._normalize_skill(
                skill
            )
        )

        # --------------------------------------------------
        # Programming languages
        #
        # GitHub + LeetCode can both demonstrate these.
        # --------------------------------------------------

        programming_languages = {
            "python",
            "c",
            "c++",
            "java",
            "javascript",
            "typescript",
            "go",
            "rust",
            "kotlin",
            "swift",
        }

        if normalized in (
            programming_languages
        ):

            return {
                "github",
                "leetcode",
            }

        # --------------------------------------------------
        # DSA / algorithm concepts
        #
        # LeetCode is highly relevant.
        # GitHub is also useful.
        # --------------------------------------------------

        dsa_skills = {
            "dsa",
            "data structures",
            "algorithms",
            "arrays",
            "strings",
            "hash table",
            "stack",
            "queue",
            "linked list",
            "binary search",
            "sorting",
            "two pointers",
            "sliding window",
            "trees",
            "graphs",
            "heap / priority queue",
            "greedy",
            "dynamic programming",
            "backtracking",
            "recursion",
            "bit manipulation",
        }

        if normalized in dsa_skills:

            return {
                "github",
                "leetcode",
            }

        # --------------------------------------------------
        # Technologies / frameworks
        #
        # GitHub is meaningful.
        # LeetCode is NOT.
        # --------------------------------------------------

        github_first_skills = {
            "html",
            "css",

            "react",
            "next.js",

            "node.js",
            "express",

            "fastapi",
            "flask",
            "django",
            "spring boot",

            "docker",
            "kubernetes",

            "git",
            "github",
            "github actions",

            "mysql",
            "postgresql",
            "sql",
            "mongodb",
            "redis",

            "tensorflow",
            "pytorch",
            "keras",

            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",

            "xgboost",
            "catboost",

            "aws",
            "azure",
            "google cloud",

            "render",

            "linux",
            "bash",

            "jenkins",
            "ci/cd",

            "rest api",
            "api",

            "machine learning",
            "deep learning",
            "artificial intelligence (ai)",
        }

        if normalized in github_first_skills:

            return {
                "github",
            }

        # --------------------------------------------------
        # Unknown technical skills:
        #
        # Default to GitHub rather than LeetCode.
        # --------------------------------------------------

        return {
            "github",
        }

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

            normalized = (
                cls._normalize_skill(
                    skill
                )
            )

            # --------------------------------------------------
            # CLAIMS
            # --------------------------------------------------

            resume_claimed = (
                normalized
                in resume_skills
            )

            linkedin_claimed = (
                normalized
                in linkedin_skills
            )

            # --------------------------------------------------
            # DEMONSTRATIONS
            # --------------------------------------------------

            github_demonstrated = (
                normalized
                in github_skills
            )

            leetcode_demonstrated = (
                normalized
                in leetcode_skills
            )

            # --------------------------------------------------
            # WHICH SOURCES ACTUALLY MATTER?
            # --------------------------------------------------

            relevant_sources = (
                cls._relevant_verification_sources(
                    normalized
                )
            )

            # --------------------------------------------------
            # SUPPORTING SOURCES
            # --------------------------------------------------

            supporting_sources = []

            if resume_claimed:

                supporting_sources.append(
                    "resume"
                )

            if linkedin_claimed:

                supporting_sources.append(
                    "linkedin"
                )

            if (
                github_demonstrated
                and "github"
                in relevant_sources
            ):

                supporting_sources.append(
                    "github"
                )

            if (
                leetcode_demonstrated
                and "leetcode"
                in relevant_sources
            ):

                supporting_sources.append(
                    "leetcode"
                )

            # --------------------------------------------------
            # CLAIMED
            # --------------------------------------------------

            claimed = (
                resume_claimed
                or linkedin_claimed
            )

            # --------------------------------------------------
            # DEMONSTRATED
            #
            # A LeetCode result only counts if LeetCode
            # is actually relevant to the skill.
            # --------------------------------------------------

            demonstrated = (
                (
                    github_demonstrated
                    and "github"
                    in relevant_sources
                )
                or
                (
                    leetcode_demonstrated
                    and "leetcode"
                    in relevant_sources
                )
            )

            # --------------------------------------------------
            # MISSING SUPPORT
            #
            # IMPORTANT:
            #
            # We don't call LeetCode "missing" for CSS.
            #
            # We also don't punish an unavailable source.
            # --------------------------------------------------

            missing_sources = []

            if (
                claimed
                and "github"
                in relevant_sources
                and not github_demonstrated
            ):

                missing_sources.append(
                    "github"
                )

            if (
                claimed
                and "leetcode"
                in relevant_sources
                and not leetcode_demonstrated
            ):

                missing_sources.append(
                    "leetcode"
                )

            # --------------------------------------------------
            # STATUS
            # --------------------------------------------------

            if demonstrated:

                if len(
                    supporting_sources
                ) >= 3:

                    status = (
                        "strongly_supported"
                    )

                elif len(
                    supporting_sources
                ) >= 2:

                    status = (
                        "supported"
                    )

                else:

                    status = (
                        "demonstrated"
                    )

            elif claimed:

                if missing_sources:

                    status = (
                        "claimed_not_independently_verified"
                    )

                else:

                    status = (
                        "claimed_only"
                    )

            else:

                status = (
                    "unknown"
                )

            # --------------------------------------------------
            # EVIDENCE ITEMS
            # --------------------------------------------------

            evidence_items = []

            if resume_claimed:

                evidence_items.append(
                    EvidenceItem(
                        source="resume",
                        evidence_type="claim",
                        value=normalized,
                        strength="claim",
                    )
                )

            if linkedin_claimed:

                evidence_items.append(
                    EvidenceItem(
                        source="linkedin",
                        evidence_type="claim",
                        value=normalized,
                        strength="claim",
                    )
                )

            if (
                github_demonstrated
                and "github"
                in relevant_sources
            ):

                evidence_items.append(
                    EvidenceItem(
                        source="github",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=normalized,
                        strength="demonstrated",
                    )
                )

            if (
                leetcode_demonstrated
                and "leetcode"
                in relevant_sources
            ):

                evidence_items.append(
                    EvidenceItem(
                        source="leetcode",
                        evidence_type=(
                            "demonstration"
                        ),
                        value=normalized,
                        strength="demonstrated",
                    )
                )

            # --------------------------------------------------
            # FINAL OBJECT
            # --------------------------------------------------

            evidence.append(
                SkillEvidence(
                    skill=normalized,

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

        # --------------------------------------------------
        # GitHub AI projects
        # --------------------------------------------------

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

                projects[key][
                    "github"
                ] = True

                projects[key][
                    "repository"
                ] = project.repository

        # --------------------------------------------------
        # Raw GitHub repositories
        # --------------------------------------------------

        if github_profile:

            for repository in (
                github_profile.repositories
                or []
            ):

                name = repository.name

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

                projects[key][
                    "github"
                ] = True

                projects[key][
                    "repository"
                ] = getattr(
                    repository,
                    "full_name",
                    None,
                ) or name

        # --------------------------------------------------
        # LinkedIn projects
        # --------------------------------------------------

        if linkedin_profile:

            for project in (
                linkedin_profile.projects
                or []
            ):

                name = project.name

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

                projects[key][
                    "linkedin"
                ] = True

        # --------------------------------------------------
        # Resume project matching
        # --------------------------------------------------

        if (
            resume
            and resume.projects
        ):

            resume_text = (
                str(
                    resume.projects
                )
                .lower()
            )

            for item in (
                projects.values()
            ):

                project_name = (
                    item["name"]
                    .lower()
                )

                if (
                    project_name
                    and project_name
                    in resume_text
                ):

                    item[
                        "resume"
                    ] = True

        # --------------------------------------------------
        # Build final project evidence
        # --------------------------------------------------

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

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

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
                    "resume_claimed"
                )

                finding = (
                    "Project is present in the "
                    "resume but was not matched "
                    "to GitHub or LinkedIn."
                )

            else:

                status = "unknown"

                finding = None

            # ----------------------------------------------
            # EVIDENCE
            # ----------------------------------------------

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
    linkedin_profile: LinkedInProfile | None = None,
    linkedin_analysis: LinkedInAnalysis | None = None,
    leetcode_analysis: LeetCodeAnalysis | None = None,
    )-> list[CrossSourceFinding]:

        findings = []

        # ==================================================
        # 1. SKILL CLAIMS WITHOUT RELEVANT EVIDENCE
        # ==================================================

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

            if not skill.missing_supporting_sources:
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

            verification_sources = (
                skill.missing_supporting_sources
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
                    severity="info",
                    message=(
                        f"{skill.skill} is claimed "
                        f"in {', '.join(claim_sources)}, "
                        "but no independent supporting "
                        "evidence was found in the "
                        "relevant verification source"
                        + (
                            "s"
                            if len(
                                verification_sources
                            ) != 1
                            else ""
                        )
                        + (
                            f" ({', '.join(verification_sources)}). "
                        )
                        + (
                            "This does not mean the "
                            "skill is incorrect."
                        )
                    ),
                    sources=(
                        claim_sources
                        + verification_sources
                    ),
                    evidence=evidence,
                )
            )

        # ==================================================
        # 2. LINKEDIN ↔ LEETCODE SOLVED COUNT
        # ==================================================

        if (
            linkedin_analysis is not None
            and leetcode_analysis is not None
        ):

            actual_solved = getattr(
                leetcode_analysis,
                "total_solved",
                None,
            )

            linkedin_text_parts = []

# ==================================================
# RAW LINKEDIN PROFILE EVIDENCE
# ==================================================

        if linkedin_profile:

            if linkedin_profile.about:

                linkedin_text_parts.append(
                    linkedin_profile.about
                )

            for experience in (
                linkedin_profile.experiences
                or []
            ):

                if experience.description:

                    linkedin_text_parts.append(
                        experience.description
                    )

            for project in (
                linkedin_profile.projects
                or []
            ):

                if project.description:

                    linkedin_text_parts.append(
                        project.description
                    )

        # ==================================================
        # LINKEDIN ANALYSIS EVIDENCE
        # ==================================================

        if linkedin_analysis:

            if linkedin_analysis.about:

                linkedin_text_parts.append(
                    linkedin_analysis.about
                )

            for signal in (
                linkedin_analysis.career_signals
                or []
            ):

                if signal.signal:

                    linkedin_text_parts.append(
                        signal.signal
                    )

                if signal.evidence:

                    linkedin_text_parts.append(
                        signal.evidence
                    )

        # ==================================================
        # CLAIMED SKILLS
        # ==================================================

        if linkedin_analysis:

            for skill in (
                linkedin_analysis.claimed_skills
                or []
            ):

                linkedin_text_parts.append(
                    str(skill)
                )

        linkedin_text = " ".join(
            linkedin_text_parts
        )

            # ----------------------------------------------
            # Extract numeric LeetCode claims.
            #
            # Handles examples such as:
            #
            # "100+ LeetCode problems"
            # "solved 120 problems"
            # "90 LeetCode questions"
            # "150+ problems on LeetCode"
            # ----------------------------------------------


        leetcode_claim_pattern = re.compile(
                        r"(?i)"
                        r"(?:(\d+)\s*\+?\s*"
                        r"(?:leetcode\s*)?"
                        r"(?:problems?|questions?|"
                        r"questions?\s*solved|"
                        r"problems?\s*solved))"
                        r"|"
                        r"(?:(?:solved|completed)"
                        r"\s+(\d+)\s*\+?\s*"
                        r"(?:leetcode\s*)?"
                        r"(?:problems?|questions?))"
                        r"|"
                        r"(?:(?:leetcode)"
                        r"\s*(?:problems?|questions?)"
                        r"\s*(?:solved|completed)"
                        r"\s*(\d+)\s*\+?)"
                    )

        match = (
            leetcode_claim_pattern.search(
                linkedin_text
            )
        )

        linkedin_solved = None

        if match:

            groups = match.groups()

            for value in groups:

                if value:

                        try:

                            linkedin_solved = int(
                                value
                            )

                            break

                        except (
                            TypeError,
                            ValueError,
                        ):

                            pass

            # ----------------------------------------------
            # Compare only when BOTH values are known.
            # ----------------------------------------------

            if (
                actual_solved is not None
                and linkedin_solved is not None
            ):

                try:

                    actual_solved = int(
                        actual_solved
                    )

                    linkedin_solved = int(
                        linkedin_solved
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    actual_solved = None
                    linkedin_solved = None

            if (
                actual_solved is not None
                and linkedin_solved is not None
                and linkedin_solved != actual_solved
            ):

                difference = (
                    linkedin_solved
                    - actual_solved
                )

                direction = (
                    "higher"
                    if difference > 0
                    else "lower"
                )

                evidence = [
                    EvidenceItem(
                        source="linkedin",
                        evidence_type=(
                            "profile_claim"
                        ),
                        value=(
                            f"{linkedin_solved} "
                            "LeetCode problems"
                        ),
                        strength="claim",
                    ),

                    EvidenceItem(
                        source="leetcode",
                        evidence_type=(
                            "platform_statistic"
                        ),
                        value=(
                            f"{actual_solved} "
                            "problems solved"
                        ),
                        strength="demonstrated",
                    ),
                ]

                findings.append(
                    CrossSourceFinding(
                        finding_type=(
                            "leetcode_count_mismatch"
                        ),
                        subject=(
                            "LeetCode problem count"
                        ),
                        severity="low",
                        message=(
                            f"LinkedIn indicates "
                            f"{linkedin_solved}+ "
                            "LeetCode problems, "
                            f"while the current "
                            f"LeetCode profile shows "
                            f"{actual_solved} solved. "
                            f"The LinkedIn figure is "
                            f"{direction} than the "
                            "current platform count. "
                            "Consider updating the "
                            "profile if the LinkedIn "
                            "number is outdated."
                        ),
                        sources=[
                            "linkedin",
                            "leetcode",
                        ],
                        evidence=evidence,
                    )
                )

        # ==================================================
        # 3. GITHUB PROJECT MISSING FROM LINKEDIN
        # ==================================================

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

        # ==================================================
        # 4. LINKEDIN PROJECT WITHOUT GITHUB
        # ==================================================

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
                            "GitHub project was found. "
                            "This is not necessarily a "
                            "problem because the project "
                            "may be private, hosted "
                            "elsewhere, or not code-based."
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
            "/",
            " ",
        )

        value = value.replace(
            ".",
            " ",
        )

        return " ".join(
            value.split()
        )


unified_service = UnifiedService()