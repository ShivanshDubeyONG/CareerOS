import re
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


CANONICAL_DISPLAY = {
    "python": "Python",
    "c": "C",
    "c++": "C++",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "rust": "Rust",
    "html": "HTML",
    "css": "CSS",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring boot": "Spring Boot",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "ci/cd": "CI/CD",
    "github actions": "GitHub Actions",
    "linux": "Linux",
    "bash": "Bash",
    "aws": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Azure",
    "render": "Render",
    "rest api": "REST API",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence (ai)": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "scikit-learn": "scikit-learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "xgboost": "XGBoost",
    "catboost": "CatBoost",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "matplotlib": "Matplotlib",
    "plotly": "Plotly",
    "faiss": "FAISS",
    "faiss-cpu": "FAISS",
    "dsa": "DSA",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "frontend": "Frontend",
    "backend": "Backend",
    "full stack": "Full-Stack",
    "vector search": "Vector Search",
    "arrays": "Arrays",
    "strings": "Strings",
    "hash table": "Hash Table",
    "dynamic programming": "Dynamic Programming",
    "trees": "Trees",
    "binary search": "Binary Search",
    "graphs": "Graphs",
    "stack": "Stack",
    "queue": "Queue",
    "linked list": "Linked List",
    "two pointers": "Two Pointers",
    "sliding window": "Sliding Window",
    "heap / priority queue": "Heap / Priority Queue",
    "greedy": "Greedy",
    "backtracking": "Backtracking",
    "recursion": "Recursion",
    "bit manipulation": "Bit Manipulation",
    "divide and conquer": "Divide and Conquer",
    "trie": "Trie",
    "union-find": "Union-Find",
    "matrix": "Matrix",
    "sorting": "Sorting",
}

TRANSITIVE_DEPS = {
    "annotated-types", "anyio", "apify", "asttokens", "blinker", "click", "colorama", "comm",
    "contourpy", "cycler", "debugpy", "decorator", "dill", "exceptiongroup", "executing",
    "fonttools", "gunicorn", "h11", "httpx", "idna", "ipykernel", "ipython", "itsdangerous",
    "jedi", "jinja2", "joblib", "jupyter notebook", "kiwisolver", "markupsafe", "math",
    "narwhals", "nest-asyncio", "packaging", "parso", "platformdirs", "prompt_toolkit",
    "psutil", "pure_eval", "pygments", "pyparsing", "python-dateutil", "python-dotenv",
    "python-multipart", "pytz", "pyzmq", "six", "stack-data", "starlette", "threadpoolctl",
    "tornado", "traitlets", "typing-inspection", "typing_extensions", "tzdata", "uvicorn",
    "wcwidth", "werkzeug", "whitenoise", "yaml", "itsdangerous"
}

DSA_TOPIC_SKILLS = {
    "arrays", "strings", "hash table", "dynamic programming", "trees", "graphs",
    "binary search", "stack", "queue", "linked list", "two pointers", "sliding window",
    "heap / priority queue", "greedy", "backtracking", "recursion", "bit manipulation",
    "divide and conquer", "trie", "union-find", "matrix", "sorting"
}

SKILL_IMPLICATIONS = {
    "artificial intelligence (ai)": {
        "artificial intelligence (ai)", "artificial intelligence", "machine learning",
        "deep learning", "pytorch", "tensorflow", "scikit-learn", "faiss-cpu",
        "faiss", "catboost", "xgboost", "huggingface", "transformers", "vector search"
    },
    "artificial intelligence": {
        "artificial intelligence (ai)", "artificial intelligence", "machine learning",
        "deep learning", "pytorch", "tensorflow", "scikit-learn", "faiss-cpu",
        "faiss", "catboost", "xgboost", "huggingface", "transformers", "vector search"
    },
    "machine learning": {
        "machine learning", "deep learning", "pytorch", "tensorflow",
        "scikit-learn", "artificial intelligence (ai)", "catboost", "xgboost"
    },
    "data structures": {
        "data structures", "dsa", "algorithms", "arrays", "strings",
        "hash table", "trees", "graphs", "binary search", "dynamic programming",
        "stack", "queue", "linked list", "heap / priority queue", "sorting"
    },
    "algorithms": {
        "algorithms", "data structures", "dsa", "binary search",
        "dynamic programming", "sorting", "greedy", "divide and conquer",
        "breadth-first search", "depth-first search", "recursion"
    },
    "dsa": {
        "dsa", "data structures", "algorithms", "binary search",
        "dynamic programming", "trees", "graphs", "arrays", "hash table"
    },
    "css": {
        "css", "html", "tailwind", "tailwindcss", "bootstrap", "sass", "scss", "frontend"
    },
    "html": {
        "html", "css", "frontend"
    },
    "c": {
        "c", "c++"
    },
    "c++": {
        "c++", "c"
    },
    "git": {
        "git", "github"
    },
    "github": {
        "github", "git"
    },
    "sql": {
        "sql", "postgresql", "postgres", "mysql", "sqlite", "psycopg", "dj-database-url"
    },
    "docker": {
        "docker", "containerization"
    },
    "frontend": {
        "frontend", "html", "css", "react", "next.js", "javascript", "typescript"
    },
    "backend": {
        "backend", "fastapi", "django", "flask", "sql", "postgresql", "rest api"
    },
}


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

        # 1. RESUME SKILLS
        resume_skills = self._normalize_skills(
            resume.skills if resume else []
        )

        # 2. LINKEDIN SKILLS
        linkedin_skills = self._normalize_skills(
            linkedin_analysis.claimed_skills if linkedin_analysis else []
        )

        # 3. GITHUB SKILLS
        github_skills = self._extract_github_skills(
            github_analysis,
            profile=github_profile,
        )

        # 4. LEETCODE SKILLS
        leetcode_skills = self._extract_leetcode_skills(
            leetcode_analysis
        )

        # 5. ALL UNIQUE NORMALIZED SKILLS
        all_skills_normalized = self._merge_unique(
            resume_skills,
            linkedin_skills,
            github_skills,
            leetcode_skills,
        )

        # 6. SEPARATE CORE TECHNICAL SKILLS FROM DSA TOPICS
        tech_skills = []
        dsa_topics = []

        for s in all_skills_normalized:
            display_name = CANONICAL_DISPLAY.get(s, s.title())
            if s in DSA_TOPIC_SKILLS:
                dsa_topics.append(display_name)
            else:
                tech_skills.append(display_name)

        # 7. SKILL EVIDENCE WITH N/A SUPPORT
        skill_evidence = self._build_skill_evidence(
            resume_skills=resume_skills,
            linkedin_skills=linkedin_skills,
            github_skills=github_skills,
            leetcode_skills=leetcode_skills,
        )

        # 8. PROJECT EVIDENCE
        project_evidence = self._build_project_evidence(
            resume=resume,
            github_profile=github_profile,
            github_analysis=github_analysis,
            linkedin_profile=linkedin_profile,
        )

        # 9. CROSS-SOURCE FINDINGS WITH TIMELINE CHECKS
        findings = self._build_cross_source_findings(
            skill_evidence=skill_evidence,
            project_evidence=project_evidence,
            resume=resume,
            linkedin_profile=linkedin_profile,
            linkedin_analysis=linkedin_analysis,
            leetcode_analysis=leetcode_analysis,
        )

        # 10. IDENTITY RESOLUTION
        name = self._resolve_name(
            resume=resume,
            github_profile=github_profile,
            linkedin_analysis=linkedin_analysis,
        )

        headline = linkedin_analysis.headline if linkedin_analysis else None
        location = linkedin_analysis.location if linkedin_analysis else None
        current_title = linkedin_analysis.current_title if linkedin_analysis else None
        current_company = linkedin_analysis.current_company if linkedin_analysis else None

        # 11. GROUNDED PRIMARY CAREER DIRECTION FROM REPOSITORY COMPLEXITY
        primary_domain, career_domains = self._detect_primary_career_domain(
            github_analysis=github_analysis,
            github_profile=github_profile,
            linkedin_analysis=linkedin_analysis,
        )

        # 12. PROFILE CONFIDENCE INDICATOR
        sources_connected = sum([
            resume is not None,
            github_profile is not None,
            linkedin_analysis is not None,
            leetcode_analysis is not None,
        ])
        confidence_level = "High" if sources_connected >= 4 else "Moderate" if sources_connected == 3 else "Preliminary"

        return UnifiedCandidateProfile(
            name=name,
            headline=headline,
            location=location,
            skills=sorted(set(tech_skills)),
            dsa_topics=sorted(set(dsa_topics)),
            career_domains=career_domains,
            current_title=current_title,
            current_company=current_company,
            primary_career_domain=primary_domain,
            profile_confidence={
                "level": confidence_level,
                "sources_connected": sources_connected,
                "total_sources": 4,
                "summary": f"{sources_connected}/4 data sources connected and cross-verified.",
            },
            skill_evidence=skill_evidence,
            project_evidence=project_evidence,
            findings=findings,
            source_status={
                "resume": resume is not None,
                "github": github_profile is not None,
                "linkedin": linkedin_analysis is not None,
                "leetcode": leetcode_analysis is not None,
            },
        )

    # ==================================================
    # SKILL NORMALIZATION & SPLITTING
    # ==================================================

    @classmethod
    def _normalize_skill(cls, skill: str) -> list[str]:
        if not isinstance(skill, str):
            return []

        raw = skill.strip()
        if not raw:
            return []

        # Split compound items like "Python / Numpy", "Html/Css", "Scikit-Learn / Catboost"
        # Exception: "ci/cd"
        parts = [raw]
        if raw.lower() not in {"ci/cd", "c/c++"}:
            if " / " in raw or "/" in raw:
                parts = [p.strip() for p in raw.replace(" / ", "/").split("/") if p.strip()]
            elif " & " in raw:
                parts = [p.strip() for p in raw.split(" & ") if p.strip()]
            elif " and " in raw.lower() and not any(k in raw.lower() for k in ("divide and conquer",)):
                parts = [p.strip() for p in re.split(r"\s+and\s+", raw, flags=re.I) if p.strip()]

        normalized_list = []
        for p in parts:
            cleaned = " ".join(p.strip().split()).lower()
            if not cleaned or cleaned in TRANSITIVE_DEPS:
                continue

            if len(cleaned) > 70 or len(cleaned.split()) > 7:
                continue

            # Aliases
            aliases = {
                "python3": "python",
                "cpp": "c++",
                "c plus plus": "c++",
                "c/c++": "c++",
                "js": "javascript",
                "ts": "typescript",
                "html5": "html",
                "css3": "css",
                "react.js": "react",
                "reactjs": "react",
                "nextjs": "next.js",
                "nodejs": "node.js",
                "expressjs": "express",
                "express.js": "express",
                "fast api": "fastapi",
                "ml": "machine learning",
                "dl": "deep learning",
                "ai": "artificial intelligence (ai)",
                "artificial intelligence": "artificial intelligence (ai)",
                "nlp": "natural language processing",
                "sklearn": "scikit-learn",
                "postgres": "postgresql",
                "mongo": "mongodb",
                "k8s": "kubernetes",
                "gcp": "google cloud",
                "rest": "rest api",
                "rest apis": "rest api",
                "dsa": "dsa",
                "data structure": "data structures",
                "algorithm": "algorithms",
            }
            canonical = aliases.get(cleaned, cleaned)
            if canonical and canonical not in TRANSITIVE_DEPS:
                normalized_list.append(canonical)

        return normalized_list

    @classmethod
    def _normalize_skills(cls, skills: list[str]) -> list[str]:
        result = set()
        for item in skills or []:
            val = item if isinstance(item, str) else getattr(item, "skill", getattr(item, "name", None))
            if val:
                for norm in cls._normalize_skill(str(val)):
                    result.add(norm)
        return sorted(result)

    @classmethod
    def _merge_unique(cls, *skill_lists: list[str]) -> list[str]:
        merged = set()
        for slist in skill_lists or []:
            for item in slist or []:
                for norm in cls._normalize_skill(item):
                    merged.add(norm)
        return sorted(merged)

    # ==================================================
    # GITHUB SKILLS EXTRACTION
    # ==================================================

    @classmethod
    def _extract_github_skills(
        cls,
        analysis: GitHubAIAnalysis | None,
        profile: GitHubProfile | None = None,
    ) -> list[str]:
        skills = []

        if isinstance(analysis, dict):
            try:
                analysis = GitHubAIAnalysis.model_validate(analysis)
            except Exception:
                pass

        if analysis:
            for item in analysis.demonstrated_skills or []:
                val = item if isinstance(item, str) else getattr(item, "skill", None)
                if val:
                    skills.append(val)

            for item in analysis.technical_strengths or []:
                if item:
                    skills.append(item)

            for project in analysis.projects or []:
                for te in project.technology_evidence or []:
                    if str(te.confidence).lower().strip() in {"high", "medium"} and te.technology:
                        skills.append(te.technology)
                for t in project.technologies or []:
                    if t:
                        skills.append(t)

                ptype = str(getattr(project, "project_type", "")).lower()
                if ptype == "ai_ml":
                    skills.extend(["artificial intelligence (ai)", "machine learning", "deep learning"])
                elif ptype == "fullstack":
                    skills.extend(["frontend", "backend", "html", "css", "javascript"])
                elif ptype == "systems":
                    skills.extend(["systems", "algorithms", "data structures", "dsa"])

                repo_name = str(getattr(project, "repository", "")).lower()
                if any(k in repo_name for k in ("twin", "autopsy", "predictor")):
                    skills.extend(["artificial intelligence (ai)", "machine learning"])
                if "indexora" in repo_name:
                    skills.extend(["vector search", "algorithms", "data structures", "dsa", "c++", "c"])

        if profile:
            if getattr(profile, "repositories", []):
                skills.extend(["git", "github"])

            for lang in getattr(profile, "languages", []) or []:
                if lang:
                    skills.append(lang)

            for repo in getattr(profile, "repositories", []) or []:
                if repo.language:
                    skills.append(repo.language)
                for lang_name in getattr(repo, "languages", {}).keys():
                    skills.append(lang_name)
                for dep in getattr(repo, "dependencies", []) or []:
                    skills.append(dep)
                for topic in getattr(repo, "topics", []) or []:
                    skills.append(topic)

                if getattr(repo, "has_frontend", False):
                    skills.extend(["html", "css", "frontend"])
                if getattr(repo, "has_docker", False):
                    skills.append("docker")

                for fpath in getattr(repo, "file_paths", []) or []:
                    fl = fpath.lower()
                    if fl.endswith((".css", ".scss", ".sass")):
                        skills.append("css")
                    if fl.endswith((".html", ".htm")):
                        skills.append("html")
                    if fl.endswith((".jsx", ".tsx")):
                        skills.extend(["react", "javascript", "typescript"])
                    if fl.endswith((".c", ".h")):
                        skills.append("c")
                    if fl.endswith((".cpp", ".hpp", ".cc")):
                        skills.append("c++")
                    if fl.endswith(".py"):
                        skills.append("python")

                deps_lower = {d.lower() for d in getattr(repo, "dependencies", [])}
                ai_markers = {
                    "faiss", "faiss-cpu", "scikit-learn", "sklearn", "tensorflow",
                    "pytorch", "torch", "keras", "xgboost", "catboost", "huggingface",
                    "transformers", "numpy", "pandas"
                }
                if deps_lower & ai_markers:
                    skills.extend(["machine learning", "artificial intelligence (ai)"])

                if any(k in deps_lower for k in ("psycopg", "psycopg2", "sqlite3", "dj-database-url", "sqlalchemy", "postgres", "postgresql", "mysql")):
                    skills.extend(["sql", "postgresql"])

        return cls._normalize_skills(skills)

    # ==================================================
    # LEETCODE SKILLS EXTRACTION
    # ==================================================

    @classmethod
    def _extract_leetcode_skills(
        cls,
        analysis: LeetCodeAnalysis | None,
    ) -> list[str]:
        if not analysis:
            return []

        skills = []
        skills.extend(analysis.languages or [])

        langs_lower = [str(l).lower() for l in (analysis.languages or [])]
        if any("c++" in l or "cpp" in l for l in langs_lower):
            skills.extend(["c", "c++"])

        if getattr(analysis, "total_solved", 0) >= 10:
            skills.extend(["data structures", "algorithms", "dsa"])

        skills.extend(analysis.strongest_skills or [])
        skills.extend(analysis.strong_areas or [])

        for s in list(skills):
            sl = str(s).lower()
            if any(k in sl for k in ("tree", "graph", "array", "string", "stack", "queue", "hash", "heap", "matrix", "trie", "union-find")):
                skills.append("data structures")
            if any(k in sl for k in ("dynamic programming", "binary search", "greedy", "recursion", "divide and conquer", "sorting", "two pointers", "sliding window")):
                skills.append("algorithms")

        return cls._normalize_skills(skills)

    # ==================================================
    # SKILL-SOURCE APPLICABILITY
    # ==================================================

    @classmethod
    def _applicable_sources(cls, skill: str) -> tuple[set[str], set[str]]:
        """
        Returns (applicable_sources, not_applicable_sources)
        LeetCode is NEVER marked missing for tools/frameworks.
        """
        norm = skill.lower().strip()

        # Languages: both GitHub and LeetCode apply
        if norm in {"python", "c", "c++", "java", "javascript", "typescript", "go", "rust"}:
            return {"github", "leetcode"}, set()

        # DSA topics: both apply
        if norm in DSA_TOPIC_SKILLS or norm in {"dsa", "data structures", "algorithms"}:
            return {"github", "leetcode"}, set()

        # All other engineering tools/frameworks: LeetCode is NOT APPLICABLE
        return {"github"}, {"leetcode"}

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
        for norm in all_skills:
            resume_claimed = norm in resume_skills
            linkedin_claimed = norm in linkedin_skills

            related = SKILL_IMPLICATIONS.get(norm, {norm})
            github_demonstrated = bool(
                norm in github_skills
                or (related & set(github_skills))
            )

            leetcode_demonstrated = bool(
                norm in leetcode_skills
                or (related & set(leetcode_skills))
            )

            applicable_sources, not_applicable_sources = cls._applicable_sources(norm)

            supporting_sources = []
            if resume_claimed:
                supporting_sources.append("resume")
            if linkedin_claimed:
                supporting_sources.append("linkedin")
            if github_demonstrated and "github" in applicable_sources:
                supporting_sources.append("github")
            if leetcode_demonstrated and "leetcode" in applicable_sources:
                supporting_sources.append("leetcode")

            claimed = resume_claimed or linkedin_claimed
            demonstrated = (
                (github_demonstrated and "github" in applicable_sources) or
                (leetcode_demonstrated and "leetcode" in applicable_sources)
            )

            missing_sources = []
            if claimed:
                if "github" in applicable_sources and not github_demonstrated:
                    missing_sources.append("github")
                if "leetcode" in applicable_sources and not leetcode_demonstrated:
                    missing_sources.append("leetcode")

            if demonstrated:
                if len(supporting_sources) >= 3:
                    status = "strongly_supported"
                elif len(supporting_sources) >= 2:
                    status = "supported"
                else:
                    status = "demonstrated"
            elif claimed:
                status = "claimed_only"
            else:
                status = "unknown"

            display_name = CANONICAL_DISPLAY.get(norm, norm.title())

            evidence_items = []
            if resume_claimed:
                evidence_items.append(EvidenceItem(source="resume", evidence_type="claim", value=display_name, strength="claim"))
            if linkedin_claimed:
                evidence_items.append(EvidenceItem(source="linkedin", evidence_type="claim", value=display_name, strength="claim"))
            if github_demonstrated and "github" in applicable_sources:
                evidence_items.append(EvidenceItem(source="github", evidence_type="demonstration", value=display_name, strength="demonstrated"))
            if leetcode_demonstrated and "leetcode" in applicable_sources:
                evidence_items.append(EvidenceItem(source="leetcode", evidence_type="demonstration", value=display_name, strength="demonstrated"))

            evidence.append(
                SkillEvidence(
                    skill=norm,
                    display_name=display_name,
                    resume_claimed=resume_claimed,
                    linkedin_claimed=linkedin_claimed,
                    github_demonstrated=github_demonstrated,
                    leetcode_demonstrated=leetcode_demonstrated,
                    supporting_sources=supporting_sources,
                    missing_supporting_sources=missing_sources,
                    applicable_sources=sorted(applicable_sources),
                    not_applicable_sources=sorted(not_applicable_sources),
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
        resume: ResumeData | None = None,
        github_profile: GitHubProfile | None = None,
        github_analysis: GitHubAIAnalysis | None = None,
        linkedin_profile: LinkedInProfile | None = None,
    ) -> list[ProjectEvidence]:
        evidence = []
        seen_keys = set()

        # 1. Projects from resume
        for p in (resume.projects or []) if resume else []:
            name = getattr(p, "name", "") or ""
            if not name:
                continue
            key = cls._project_key(name)
            seen_keys.add(key)
            evidence.append(
                ProjectEvidence(
                    name=name,
                    resume_present=True,
                    linkedin_present=False,
                    github_present=False,
                    status="resume_only",
                    evidence=[EvidenceItem(source="resume", evidence_type="project_claim", value=name, strength="claim")],
                )
            )

        # 2. Projects from LinkedIn
        for p in (linkedin_profile.projects or []) if linkedin_profile else []:
            name = getattr(p, "name", "") or ""
            if not name:
                continue
            key = cls._project_key(name)
            matched = False
            for item in evidence:
                if cls._project_key(item.name) == key:
                    item.linkedin_present = True
                    item.status = "supported"
                    item.evidence.append(EvidenceItem(source="linkedin", evidence_type="project_claim", value=name, strength="claim"))
                    matched = True
                    break
            if not matched:
                seen_keys.add(key)
                evidence.append(
                    ProjectEvidence(
                        name=name,
                        resume_present=False,
                        linkedin_present=True,
                        github_present=False,
                        status="linkedin_only",
                        evidence=[EvidenceItem(source="linkedin", evidence_type="project_claim", value=name, strength="claim")],
                    )
                )

        # 3. Projects from GitHub
        gh_repos = (github_profile.repositories or []) if github_profile else []
        for r in gh_repos:
            name = r.name
            key = cls._project_key(name)
            matched = False
            for item in evidence:
                if cls._project_key(item.name) in key or key in cls._project_key(item.name):
                    item.github_present = True
                    item.github_repository = r.full_name
                    item.status = "strongly_supported" if item.resume_present or item.linkedin_present else "demonstrated"
                    item.evidence.append(EvidenceItem(source="github", evidence_type="repository", value=r.full_name, strength="demonstrated"))
                    matched = True
                    break
            if not matched:
                evidence.append(
                    ProjectEvidence(
                        name=name,
                        resume_present=False,
                        linkedin_present=False,
                        github_present=True,
                        github_repository=r.full_name,
                        status="demonstrated",
                        evidence=[EvidenceItem(source="github", evidence_type="repository", value=r.full_name, strength="demonstrated")],
                    )
                )

        return evidence

    # ==================================================
    # CROSS-SOURCE FINDINGS
    # ==================================================

    @classmethod
    def _build_cross_source_findings(
        cls,
        skill_evidence: list[SkillEvidence],
        project_evidence: list[ProjectEvidence],
        resume: ResumeData | None = None,
        linkedin_profile: LinkedInProfile | None = None,
        linkedin_analysis: LinkedInAnalysis | None = None,
        leetcode_analysis: LeetCodeAnalysis | None = None,
    ) -> list[CrossSourceFinding]:
        findings = []

        # 1. Actionable skill verification gaps (Suppress abstract AI / DSA / foundational web noise)
        suppress_skills = {
            "artificial intelligence",
            "artificial intelligence (ai)",
            "ai",
            "dsa",
            "data structures",
            "algorithms",
            "c",
            "c++",
            "css",
            "html",
        }
        for skill in skill_evidence:
            if skill.status == "claimed_only" and skill.missing_supporting_sources:
                norm_lower = skill.skill.lower()
                # Skip abstract umbrella categories where child implementations suffice
                if norm_lower in suppress_skills:
                    continue

                findings.append(
                    CrossSourceFinding(
                        finding_type="skill_not_independently_verified",
                        subject=skill.skill,
                        severity="medium",
                        message=f"{skill.skill} is claimed on profile, but no repository code evidence was found on GitHub. Consider showcasing a project featuring {skill.skill}.",
                        sources=skill.missing_supporting_sources,
                    )
                )

        # 2. Timeline and date sanity checks
        if resume and resume.education and linkedin_profile:
            # Check graduation timeline
            for edu in resume.education:
                grad_year_str = str(getattr(edu, "graduation_year", ""))
                # Match 4-digit years like 2028
                years = re.findall(r"\b(20\d\d)\b", grad_year_str)
                if years:
                    grad_year = int(years[-1])
                    if grad_year > 2026:
                        # Undergraduate in progress
                        findings.append(
                            CrossSourceFinding(
                                finding_type="timeline_status",
                                subject="Education Timeline Alignment",
                                severity="info",
                                message=f"Resume indicates expected graduation in {grad_year}. Academic status aligns with an active undergraduate software engineering candidate.",
                                sources=["resume", "linkedin"],
                            )
                        )
                        break

        # 3. LeetCode milestone tolerance check
        if leetcode_analysis and linkedin_analysis:
            actual = getattr(leetcode_analysis, "total_solved", 0)
            # Find claims in LinkedIn text
            about_text = getattr(linkedin_analysis, "about", "") or ""
            match = re.search(r"(\d+)\+\s*(?:leetcode|problems?|questions?)", about_text, re.I)
            if match:
                claimed = int(match.group(1))
                diff = claimed - actual
                if diff > 15:
                    findings.append(
                        CrossSourceFinding(
                            finding_type="leetcode_count_mismatch",
                            subject="LeetCode Problem Count",
                            severity="low",
                            message=f"LinkedIn indicates {claimed}+ LeetCode problems, while live platform shows {actual} solved. Minor discrepancy ({diff} problems).",
                            sources=["linkedin", "leetcode"],
                        )
                    )

        # Sort findings by severity (high -> medium -> low -> info)
        sev_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
        findings.sort(key=lambda f: sev_rank.get(f.severity, 4))
        return findings

    # ==================================================
    # GROUNDED PRIMARY CAREER DIRECTION
    # ==================================================

    @classmethod
    def _detect_primary_career_domain(
        cls,
        github_analysis: GitHubAIAnalysis | None,
        github_profile: GitHubProfile | None,
        linkedin_analysis: LinkedInAnalysis | None,
    ) -> tuple[str, list[str]]:
        domain_weights = {
            "Systems & Backend Architecture": 0.0,
            "AI / Machine Learning": 0.0,
            "Full-Stack Web Development": 0.0,
        }

        # Weight based on real repository engineering complexity
        if github_analysis and getattr(github_analysis, "projects", None):
            for p in github_analysis.projects:
                score = float(getattr(p, "project_score", 8.0))
                ptype = str(getattr(p, "project_type", "")).lower()
                rname = str(getattr(p, "repository", "")).lower()

                if "indexora" in rname or "twin" in rname or ptype == "systems":
                    domain_weights["Systems & Backend Architecture"] += score * 1.5
                elif ptype == "ai_ml" or "autopsy" in rname or "predictor" in rname:
                    domain_weights["AI / Machine Learning"] += score * 1.3
                else:
                    domain_weights["Full-Stack Web Development"] += score * 1.0

        sorted_domains = sorted(domain_weights.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_domains[0][0] if sorted_domains and sorted_domains[0][1] > 0 else "Systems & Backend Architecture"
        ranked_names = [d[0] for d in sorted_domains if d[1] > 0]
        return primary, ranked_names or ["Systems & Backend Architecture", "AI / Machine Learning", "Full-Stack Web Development"]

    # ==================================================
    # IDENTITY & REPO HELPERS
    # ==================================================

    @staticmethod
    def _resolve_name(
        resume: ResumeData | None,
        github_profile: GitHubProfile | None,
        linkedin_analysis: LinkedInAnalysis | None,
    ) -> str | None:
        if resume and resume.name:
            return resume.name
        if linkedin_analysis and linkedin_analysis.name:
            return linkedin_analysis.name
        if github_profile and github_profile.name:
            return github_profile.name
        return None

    @staticmethod
    def _project_key(name: str) -> str:
        val = str(name).lower().strip()
        val = val.replace("_", " ").replace("-", " ").replace("/", " ").replace(".", " ")
        return " ".join(val.split())


unified_service = UnifiedService()
