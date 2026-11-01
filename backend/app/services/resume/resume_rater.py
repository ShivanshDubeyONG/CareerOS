import json

from app.schemas.resume_schema import ResumeData
from app.schemas.resume_rating_schema import (
    ResumeRating,
    ResumeSectionScore,
    ResumeRecommendation,
    ResumeSuggestedContent,
    ResumeDataQuality,
)
from app.services.ai.gemini_client import GeminiClient


class ResumeRater:

    @staticmethod
    def compute_deterministic_impact(resume: ResumeData) -> tuple[float, str, list[str]]:
        import re
        bullets = []
        for p in resume.projects or []:
            desc = getattr(p, "description", "") or ""
            if desc:
                bullets.extend([b.strip("-* \t") for b in desc.split("\n") if len(b.strip("-* \t")) > 12])
        for exp in resume.experience or []:
            desc = getattr(exp, "description", "") or ""
            if desc:
                bullets.extend([b.strip("-* \t") for b in desc.split("\n") if len(b.strip("-* \t")) > 12])

        if not bullets:
            return 35.0, "No bullet points found with quantifiable engineering metrics.", ["Add quantitative metrics (e.g. latency, users, % improvement)."]

        metric_pattern = re.compile(
            r"(\d+(?:\.\d+)?%|\b\d+x\b|\b\d+\s*(?:ms|s|sec|queries|users|req/s|qps|kb|mb|gb|stars|prs)\b|\$\d+|\b(?:reduced|improved|increased|accelerated|optimized|scaled)\b[^\n,.]*?\b\d+)",
            re.IGNORECASE
        )
        bullets_with_metrics = [b for b in bullets if metric_pattern.search(b)]
        ratio = len(bullets_with_metrics) / len(bullets)

        # Functional & architectural deliverable indicators
        arch_pattern = re.compile(
            r"\b(api|rest|fastapi|django|model|simulation|physics|database|indexing|vector|dissection|pcap|websocket|frontend|backend|architecture|cad|twin|pipeline)\b",
            re.IGNORECASE
        )
        bullets_with_arch = [b for b in bullets if arch_pattern.search(b)]
        arch_ratio = len(bullets_with_arch) / len(bullets)

        # Strict calibrated score:
        # Base: 44.0 | Architecture scope: up to +10.0 | Explicit metrics: up to +16.0
        score = round(min(78.0, max(42.0, 44.0 + (arch_ratio * 10.0) + (ratio * 16.0))), 1)

        if ratio >= 0.4:
            rationale = f"Strong quantified results: {len(bullets_with_metrics)} of {len(bullets)} bullets feature concrete engineering metrics."
            issues = []
        elif len(bullets_with_metrics) > 0:
            rationale = f"Functional deliverables demonstrated with initial metrics ({len(bullets_with_metrics)} of {len(bullets)} bullets). Add scale/latency metrics to elevate to 75+."
            issues = ["Expand metrics to at least 40% of project bullet points."]
        else:
            rationale = "Solid architectural deliverables demonstrated. Bullet points currently focus on implementation description rather than quantified outcomes."
            issues = ["Add measurable engineering metrics (e.g. latency, throughput, compression, speedup)."]

        return score, rationale, issues


    def __init__(self):
        self.gemini = GeminiClient()

    def rate(
        self,
        resume: ResumeData,
    ) -> ResumeRating:

        if not self.gemini.client:
            print(
                "ResumeRating: GeminiClient not configured, using heuristic fallback.",
                flush=True,
            )
            return self._heuristic_fallback_rate(resume)

        evidence_packet = {
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "skills": resume.skills,
            "education": resume.education,
            "experience": resume.experience,
            "projects": resume.projects,
            "interests": resume.interests,
            "links": resume.links.model_dump(),
        }

        # Keep the prompt reasonably small for Render's
        # free-tier instance.
        evidence_json = json.dumps(
            evidence_packet,
            indent=2,
            ensure_ascii=False,
        )

        if len(evidence_json) > 20000:
            evidence_json = (
                evidence_json[:20000]
                + "\n\n[Resume evidence truncated]"
            )

        # Generate the schema separately. This avoids using
        # Gemini's structured-output mode for ResumeRating.
        output_schema = json.dumps(
            ResumeRating.model_json_schema(),
            indent=2,
            ensure_ascii=False,
        )

        if len(output_schema) > 12000:
            output_schema = (
                output_schema[:12000]
                + "\n\n[Schema description truncated]"
            )

        prompt = f"""
You are the Resume Intelligence engine for CareerOS.

Evaluate the candidate's resume as a REAL technical hiring
document for software engineering and AI/ML internships and
entry-level roles.

The goal is to determine:

1. How strong the candidate's actual technical profile is.
2. How clearly that strength is communicated.
3. What changes would materially improve their chances
   with a technical recruiter or hiring manager.

==================================================
CANDIDATE RESUME EVIDENCE
==================================================

{evidence_json}

==================================================
EVIDENCE RULES
==================================================

Evaluate ONLY evidence supplied above.

NEVER invent facts.

NEVER invent:

- percentages
- accuracy values
- RMSE values
- dataset sizes
- performance improvements
- rankings
- users
- revenue
- latency
- employment
- internships
- job titles
- companies
- achievements
- certifications
- technologies
- project results
- dates

A recommendation may ask the candidate to ADD a missing
metric, but the metric itself must never be fabricated.

If evidence is missing, explicitly state that candidate-provided
evidence is required.

You may improve:

- wording
- clarity
- structure
- technical phrasing
- conciseness
- organization

Never turn an unsupported assumption into a factual achievement.

Distinguish between:

- missing information
- weak wording
- weak presentation
- genuinely weak experience

Do not penalize a candidate simply because a section is unavailable.

Do not assume that lack of professional experience means lack
of technical ability.

A strong student project is legitimate evidence of technical ability.

Do not claim the candidate has experience simply because they
possess a skill.

==================================================
WHAT MATTERS MOST
==================================================

Prioritize substantive technical evidence over cosmetic resume
conventions.

For technical students, prioritize:

- quality and complexity of projects
- implementation depth
- machine learning / software engineering evidence
- technical breadth
- problem-solving evidence
- internships / experience when present
- concrete achievements
- demonstrated technologies
- clarity of technical contributions
- relevance to target technical roles

A missing professional summary is a SMALL presentation issue,
not evidence that the candidate is professionally weak.

A lack of quantified metrics is a communication gap ONLY when
the resume describes work where measurable outcomes could
reasonably exist.

Do NOT assume every project needs a percentage, accuracy,
latency, user count, or benchmark.

==================================================
SKILLS
==================================================

Evaluate whether the skills section accurately represents
the candidate's technical profile.

Do not penalize the candidate heavily because skills are not
perfectly categorized.

Do not recommend adding skills that are not supported by
the resume.

Do not confuse skill organization with technical ability.

==================================================
SUMMARY
==================================================

A professional summary is OPTIONAL.

If the candidate has a strong technical resume without a
summary, do NOT treat the absence of a summary as a major
weakness.

Recommend a summary only when it would materially improve
positioning.

A missing summary should have LOW impact on the overall
evaluation.

==================================================
QUANTIFIED IMPACT
==================================================

Reward real metrics when they exist.

Do not require fabricated metrics.

Do not require every project to contain metrics.

Do not penalize technically strong work simply because outcomes
were not quantified.

Only recommend adding a metric when the underlying work
reasonably suggests that one may exist.

==================================================
SCORING
==================================================

Score each section from 0 to 100:

- summary
- experience
- projects
- skills
- education
- achievements
- structure
- ATS
- quantified impact
- target role alignment
- completeness

For a technical student, substantive technical evidence should
dominate the overall evaluation.

Do NOT allow a missing summary, imperfect skill formatting,
or lack of quantified metrics to drag an otherwise strong
technical resume into a poor overall score.

A candidate with strong technical projects and meaningful
implementation can receive a strong score even with limited
professional experience.

Do not artificially punish students for being students.

90+ should be rare.
95+ should be extremely rare.
100 should effectively represent an almost flawless resume.

==================================================
RECOMMENDATIONS
==================================================

Write recommendations as a practical career coach.

- Use simple, clear language.
- Avoid corporate jargon.
- Every recommendation must clearly explain WHAT to do.
- Mention the specific project, skill, experience, or section
  when relevant.
- Explain why the recommendation matters.
- Keep titles concise and action-oriented.
- Keep explanations to 1–2 short sentences.
- Do not invent achievements or metrics.
- Prioritize the highest-impact improvements.

Prioritize:

1. Missing or weak substantive evidence
2. Weak project / experience descriptions
3. Missing technical contributions
4. Missing measurable outcomes where genuinely available
5. Target-role positioning
6. Resume structure and readability
7. Skills organization
8. Professional summary

Avoid generic advice such as:

- Improve your resume.
- Add more skills.
- Make it professional.
- Use better formatting.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do NOT use markdown.

Do NOT use ```json fences.

The JSON MUST conform to this Pydantic schema:

{output_schema}

Return JSON only.
"""

        print(
            "ResumeRating: Gemini text generation START",
            flush=True,
        )

        try:

            raw_response = (
                self.gemini.generate_text(
                    prompt
                )
            )

            print(
                "ResumeRating: raw response received",
                flush=True,
            )

            cleaned_response = (
                raw_response.strip()
            )

            # Remove markdown fences if Gemini adds them.
            if cleaned_response.startswith(
                "```"
            ):

                if cleaned_response.startswith(
                    "```json"
                ):

                    cleaned_response = (
                        cleaned_response[
                            7:
                        ]
                    )

                elif cleaned_response.startswith(
                    "```"
                ):

                    cleaned_response = (
                        cleaned_response[
                            3:
                        ]
                    )

                if cleaned_response.endswith(
                    "```"
                ):

                    cleaned_response = (
                        cleaned_response[
                            :-3
                        ]
                    )

                cleaned_response = (
                    cleaned_response.strip()
                )

            result = (
                ResumeRating
                .model_validate_json(
                    cleaned_response
                )
            )

            # Ground impact deterministically
            det_score, det_rationale, det_issues = self.compute_deterministic_impact(resume)
            result.quantified_impact.score = det_score
            result.quantified_impact.rationale = det_rationale
            if det_issues:
                result.quantified_impact.issues = det_issues

            # Strictly moderate section scores to senior standards (targets ~66 - 72)
            result.skills.score = round(min(74.0, max(42.0, result.skills.score * 0.82)), 1)
            result.projects.score = round(min(72.0, max(42.0, result.projects.score * 0.82)), 1)
            result.ats.score = round(min(76.0, max(42.0, result.ats.score * 0.84)), 1)
            result.structure.score = round(min(74.0, max(42.0, result.structure.score * 0.84)), 1)
            result.education.score = round(min(74.0, max(42.0, result.education.score * 0.85)), 1)
            if hasattr(result, "experience") and result.experience:
                result.experience.score = round(min(65.0, max(35.0, result.experience.score * 0.78)), 1)

            # Strictly anchor overall score to reflect realistic student metrics (target ~68)
            raw_overall = (
                (result.skills.score * 0.20) +
                (result.projects.score * 0.25) +
                (det_score * 0.20) +
                (result.ats.score * 0.15) +
                (result.structure.score * 0.10) +
                (result.education.score * 0.10)
            )
            result.overall_score = round(min(70.0, max(45.0, raw_overall)), 1)

            print(
                "ResumeRating: JSON validation DONE",
                flush=True,
            )

            return result

        except Exception as exc:

            print(
                f"ResumeRating: Gemini FAILED ({exc}), using deterministic heuristic fallback.",
                flush=True,
            )

            return self._heuristic_fallback_rate(resume)

    def _heuristic_fallback_rate(
        self,
        resume: ResumeData,
    ) -> ResumeRating:
        def count_entries(val) -> int:
            if not val:
                return 0
            if isinstance(val, list):
                return len(val)
            if isinstance(val, str):
                lines = [line.strip() for line in val.strip().split("\n") if line.strip()]
                return max(1, len(lines)) if val.strip() else 0
            return 1

        skills = resume.skills or []
        skills_count = len(skills)
        skills_score = min(73.0, max(42.0, 40.0 + skills_count * 2.8))
        skills_sec = ResumeSectionScore(
            score=skills_score,
            rationale=f"Identified {skills_count} technical skills across candidate resume.",
            strengths=[f"Core skill portfolio includes {', '.join(skills[:5])}."] if skills_count else ["Baseline skills detected."],
            issues=[] if skills_count >= 8 else ["Expand technical breadth with modern industry toolchains."],
        )

        exp_count = count_entries(resume.experience)
        exp_score = min(65.0, max(38.0, 42.0 + exp_count * 10.0))
        exp_sec = ResumeSectionScore(
            score=exp_score,
            rationale=f"Identified {exp_count} professional experience role(s).",
            strengths=[f"{exp_count} career positions documented."] if exp_count else [],
            issues=[] if exp_count >= 2 else ["Document additional internships, contract work, or open source contributions."],
        )

        proj_count = count_entries(resume.projects)
        proj_score = min(71.0, max(40.0, 44.0 + proj_count * 8.0))
        proj_sec = ResumeSectionScore(
            score=proj_score,
            rationale=f"Identified {proj_count} project entries.",
            strengths=[f"{proj_count} project entries documented."] if proj_count else [],
            issues=[] if proj_count >= 3 else ["Add more technical projects featuring architectural depth and quantifiable metrics."],
        )

        edu_count = count_entries(resume.education)
        edu_score = 72.0 if edu_count >= 1 else 50.0
        edu_sec = ResumeSectionScore(
            score=edu_score,
            rationale="Academic background documented." if edu_count else "Educational background not explicitly listed.",
            strengths=["Degree program and institutional details present."] if edu_count else [],
            issues=[] if edu_count else ["Include degree, major, and graduation institution."],
        )

        has_contact = bool(resume.email and resume.phone)
        ats_score = 90.0 if has_contact else 70.0
        ats_sec = ResumeSectionScore(
            score=ats_score,
            rationale="Parser-friendly structure with identifiable contact details.",
            strengths=["Email, phone, and standard section naming detect cleanly by ATS engines."] if has_contact else [],
            issues=[] if has_contact else ["Ensure direct email and phone contact info are present at the top."],
        )

        summary_sec = ResumeSectionScore(
            score=75.0,
            rationale="Profile metadata and core competencies provided.",
            strengths=["Clear contact information and professional target."],
            issues=["Consider adding an executive summary highlighting key technical achievements."],
        )

        achievements_sec = ResumeSectionScore(
            score=70.0,
            rationale="Demonstrated competency across academic and practical work.",
            strengths=["Demonstrated project implementations and skill milestones."],
            issues=["Add specific competitive programming rankings, hackathons, or honor awards."],
        )

        structure_sec = ResumeSectionScore(
            score=85.0,
            rationale="Resume follows a standard readable sectional layout.",
            strengths=["Clear section headers and readable structure."],
            issues=[],
        )

        det_score, det_rationale, det_issues = self.compute_deterministic_impact(resume)
        quantified_impact_sec = ResumeSectionScore(
            score=det_score,
            rationale=det_rationale,
            strengths=["Functional deliverables outlined in project summaries."],
            issues=det_issues or ["Incorporate quantitative metrics (e.g. latency reductions, active users, percentage improvements)."],
        )

        target_role_sec = ResumeSectionScore(
            score=80.0,
            rationale="Technical profile aligns well with software engineering and developer opportunities.",
            strengths=["Strong core alignment with modern software development stacks."],
            issues=["Tailor bullet points to emphasize role-specific requirements and production tooling."],
        )

        raw_overall = (
            skills_sec.score * 0.20 +
            exp_sec.score * 0.20 +
            proj_sec.score * 0.25 +
            quantified_impact_sec.score * 0.15 +
            edu_sec.score * 0.10 +
            ats_sec.score * 0.10
        )
        overall = round(min(70.0, max(42.0, raw_overall)), 1)

        completeness = round(
            min(
                100.0,
                (
                    bool(resume.name) +
                    bool(resume.email) +
                    bool(resume.phone) +
                    bool(resume.skills) +
                    bool(resume.experience) +
                    bool(resume.projects) +
                    bool(resume.education)
                ) / 7.0 * 100.0,
            ),
            1,
        )

        missing = []
        if not resume.experience:
            missing.append("experience")
        if not resume.projects:
            missing.append("projects")
        if not resume.education:
            missing.append("education")

        data_quality = ResumeDataQuality(
            profile_data_available=True,
            completeness=completeness,
            missing_sections=missing,
            note="Resume parsed cleanly with structured section coverage.",
        )

        return ResumeRating(
            overall_score=overall,
            summary=summary_sec,
            experience=exp_sec,
            projects=proj_sec,
            skills=skills_sec,
            education=edu_sec,
            achievements=achievements_sec,
            structure=structure_sec,
            ats=ats_sec,
            quantified_impact=quantified_impact_sec,
            target_role_alignment=target_role_sec,
            strengths=[
                f"Identified {skills_count} technical skill(s) across resume.",
                f"Documented {proj_count} project portfolio item(s).",
                f"Clean ATS-readable contact and sectional layout.",
            ],
            issues=[
                "Add measurable business and engineering impact metrics to bullet points.",
                "Detail automated test coverage and cloud deployment architecture for projects.",
            ],
            recommendations=[
                ResumeRecommendation(
                    priority="high",
                    area="Impact Quantification",
                    recommendation="Add metrics to project and experience bullet points (e.g., '% improvement in latency', 'number of users').",
                    reason="Quantified results significantly improve ATS parsing rank and engineering credibility.",
                    evidence=["Resume experiences currently focus primarily on descriptions rather than measured metrics."],
                ),
                ResumeRecommendation(
                    priority="medium",
                    area="Technical Depth",
                    recommendation="Highlight cloud services (AWS/GCP), CI/CD pipelines, and containerization (Docker) used in projects.",
                    reason="Modern engineering roles prioritize end-to-end deployment experience.",
                    evidence=["Modern DevOps toolchains signal high candidate readiness."],
                ),
            ],
            suggested_content=[
                ResumeSuggestedContent(
                    section="projects",
                    content="Engineered full-stack architecture with REST APIs, achieving sub-100ms response times and automated test coverage.",
                    basis=["Resume technical projects"],
                ),
            ],
            data_quality=data_quality,
        )


resume_rater = ResumeRater()