import json

from app.schemas.linkedin_rating_schema import (
    LinkedInRating,
    LinkedInSectionScore,
    LinkedInRecommendation,
    LinkedInSuggestedContent,
    LinkedInDataQuality,
)
from app.schemas.linkedin_schema import (
    LinkedInAnalysis,
    LinkedInProfile,
)
from app.services.ai.gemini_client import (
    GeminiClient,
)


class LinkedInRater:
    """
    AI-powered LinkedIn profile intelligence engine.

    Gemini evaluates LinkedIn quality and recommendations,
    while CareerOS UnifiedCandidateProfile provides
    deterministic cross-source evidence.

    Gemini must NEVER invent evidence.
    """

    def __init__(self):
        self.gemini = GeminiClient()

    def rate(
        self,
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
        unified_profile=None,
    ) -> LinkedInRating:

        if not self.gemini.client:
            print(
                "LinkedInRater: GeminiClient not configured, using heuristic fallback.",
                flush=True,
            )
            return self._heuristic_fallback_rate(profile, analysis)

        evidence_packet = (
            self._build_evidence_packet(
                profile,
                analysis,
                unified_profile,
            )
        )

        prompt = self._build_prompt(
            evidence_packet,
        )

        print(
            f"DEBUG EVIDENCE PACKET: "
            f"{len(json.dumps(evidence_packet, ensure_ascii=False))} chars"
        )

        print(
            f"DEBUG FINAL PROMPT: "
            f"{len(prompt)} chars"
        )

        try:
            return self.gemini.generate_structured(
                prompt,
                LinkedInRating,
            )
        except Exception as exc:
            print(
                f"LinkedInRater: Gemini failed ({exc}), using deterministic fallback.",
                flush=True,
            )
            return self._heuristic_fallback_rate(profile, analysis)
    
    @staticmethod
    def _build_evidence_packet(
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
        unified_profile=None,
    ) -> dict:

        packet = {
            "linkedin": {
                "name": profile.name,
                "headline": profile.headline,
                "location": profile.location,
                "about": profile.about,

                "experience_count": len(
                    profile.experiences
                ),

                "education": [
                    {
                        "institution": e.institution,
                        "degree": e.degree,
                        "field": e.field_of_study,
                        "start": e.start_date,
                        "end": e.end_date,
                        "description": e.description,
                    }
                    for e in profile.education
                ],

                "skills": profile.skills,

                "certifications": [
                    {
                        "name": c.name,
                        "issuer": c.issuer,
                        "credential_url": c.credential_url,
                    }
                    for c in profile.certifications
                ],

                "projects": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "url": p.url,
                    }
                    for p in profile.projects
                ],

                "featured_links": profile.links,

                "followers": profile.followers,
                "connections": profile.connections,
            },

            "linkedin_analysis": {
                "career_domains": analysis.career_domains,
                "claimed_skills": analysis.claimed_skills,

                "career_signals": [
                    {
                        "signal": s.signal,
                        "evidence": s.evidence,
                    }
                    for s in analysis.career_signals
                ],

                "profile_signals": analysis.signals,
            },
        }

        if unified_profile is None:

            packet["careeros_evidence"] = {
                "available": False,
            }

            return packet

        packet["careeros_evidence"] = {

            "available": True,

            "source_status": (
                unified_profile.source_status
            ),

            "skill_evidence": [
                {
                    "skill": item.skill,
                    "status": item.status,

                    "resume": item.resume_claimed,
                    "linkedin": item.linkedin_claimed,
                    "github": item.github_demonstrated,
                    "leetcode": item.leetcode_demonstrated,

                    "supporting_sources": (
                        item.supporting_sources
                    ),
                }
                for item in unified_profile.skill_evidence
            ],

            "project_evidence": [
                {
                    "name": item.name,

                    "resume": item.resume_present,
                    "linkedin": item.linkedin_present,
                    "github": item.github_present,

                    "github_repository": (
                        item.github_repository
                    ),

                    "status": item.status,
                    "finding": item.finding,
                }
                for item in unified_profile.project_evidence
            ],

            "findings": [
                {
                    "type": finding.finding_type,
                    "subject": finding.subject,
                    "severity": finding.severity,
                    "message": finding.message,
                    "sources": finding.sources,
                }
                for finding in unified_profile.findings
            ],
        }

        return packet

    # ==================================================
    # GEMINI PROMPT
    # ==================================================

    @staticmethod
    def _build_prompt(
        evidence_packet: dict,
    ) -> str:

        evidence_json = json.dumps(
            evidence_packet,
            indent=2,
            ensure_ascii=False,
        )

        return f"""
You are CareerOS LinkedIn Intelligence.

Evaluate the candidate's LinkedIn profile using ONLY
the provided LinkedIn data and CareerOS evidence.

CareerOS is an evidence-based career intelligence system.

IMPORTANT RULES:

1. Never fabricate candidate information.

2. Missing LinkedIn evidence does NOT mean the candidate
   lacks that skill, project, experience, or achievement.

3. Distinguish:
   - missing from LinkedIn
   - unavailable from the acquisition provider
   - genuinely weak LinkedIn content

4. CareerOS unified evidence is deterministic.
   Do not override its source/status values.

5. Suggested content may ONLY use information supported
   by the supplied LinkedIn, Resume, GitHub, or LeetCode
   evidence.

6. If evidence is insufficient, say so.

==================================================
PROFILE EVALUATION
==================================================

Score these sections from 0-100:

- headline
- about
- experience
- projects
- skills
- education
- certifications
- completeness

Evaluate:

- clarity
- specificity
- credibility
- professional positioning
- completeness

Do not penalize a section merely because provider
data is unavailable.

==================================================
CROSS-SOURCE INTELLIGENCE
==================================================

Prioritize recommendations where strong evidence exists
outside LinkedIn but LinkedIn does not represent it.

Example:

Python:
Resume ✓
LinkedIn ✗
GitHub ✓
LeetCode ✓

Interpretation:
Python is strongly supported but missing from LinkedIn.

Example:

Project:
GitHub ✓
Resume ✓
LinkedIn ✗

Interpretation:
Recommend adding the verified project to LinkedIn.

Never interpret missing LinkedIn evidence as lack
of ability.

==================================================
RECOMMENDATIONS
==================================================

Each recommendation must contain:

- priority
- area
- recommendation
- reason
- evidence

Make recommendations specific and actionable.

==================================================
SUGGESTED CONTENT
==================================================

Generate content only when supported by evidence.

Never invent:

- projects
- technologies
- companies
- metrics
- achievements
- responsibilities
- certifications

==================================================
OUTPUT
==================================================

Return ONLY valid data compatible with LinkedInRating.

Keep the response concise and evidence-based.

==================================================
CAREEROS INPUT
==================================================

{evidence_json}
"""

    def _heuristic_fallback_rate(
        self,
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
    ) -> LinkedInRating:
        has_headline = bool(profile.headline and len(profile.headline.strip()) > 5)
        headline_sec = LinkedInSectionScore(
            score=85.0 if has_headline else 50.0,
            rationale="Professional headline is well-defined." if has_headline else "Headline is missing or overly brief.",
            strengths=[f"Headline '{profile.headline}' communicates professional focus."] if has_headline else [],
            issues=[] if has_headline else ["Create a clear target headline including role and primary tech stack."],
        )

        has_about = bool(profile.about and len(profile.about.strip()) > 30)
        about_sec = LinkedInSectionScore(
            score=80.0 if has_about else 45.0,
            rationale="About section provides background." if has_about else "About section is empty or brief.",
            strengths=["Detailed professional overview present."] if has_about else [],
            issues=[] if has_about else ["Add a 2-3 paragraph summary detailing background, passion, and top skills."],
        )

        exp_count = len(profile.experiences or [])
        exp_sec = LinkedInSectionScore(
            score=min(95.0, max(45.0, 50.0 + exp_count * 15.0)),
            rationale=f"Documented {exp_count} role(s) on profile.",
            strengths=[f"{exp_count} experience position(s) listed."] if exp_count else [],
            issues=[] if exp_count >= 2 else ["Document past work, internships, or academic project experience."],
        )

        proj_count = len(profile.projects or [])
        proj_sec = LinkedInSectionScore(
            score=min(95.0, max(40.0, 45.0 + proj_count * 15.0)),
            rationale=f"Found {proj_count} project(s) on profile.",
            strengths=[f"{proj_count} project(s) featured."] if proj_count else [],
            issues=[] if proj_count >= 2 else ["Feature top software projects directly in the LinkedIn Projects section."],
        )

        skills = profile.skills or []
        skills_sec = LinkedInSectionScore(
            score=min(95.0, max(45.0, 40.0 + len(skills) * 4.0)),
            rationale=f"Found {len(skills)} listed skill(s).",
            strengths=[f"Technical skills include {', '.join(skills[:5])}."] if skills else [],
            issues=[] if len(skills) >= 10 else ["List at least 10 relevant industry skills to improve recruiter discoverability."],
        )

        edu_sec = LinkedInSectionScore(
            score=85.0 if profile.education else 50.0,
            rationale="Education history listed." if profile.education else "Education section is empty.",
            strengths=["Education entries present."] if profile.education else [],
            issues=[] if profile.education else ["Add educational background and degree."],
        )

        cert_sec = LinkedInSectionScore(
            score=75.0 if profile.certifications else 60.0,
            rationale=f"{len(profile.certifications or [])} certification(s) listed.",
            strengths=[f"Certifications documented."] if profile.certifications else [],
            issues=[] if profile.certifications else ["Add relevant industry certifications or course completions."],
        )

        completeness_sec = LinkedInSectionScore(
            score=round(
                (headline_sec.score + about_sec.score + exp_sec.score + skills_sec.score + edu_sec.score) / 5.0,
                1,
            ),
            rationale="Overall profile section completeness.",
            strengths=["Major profile sections populated."],
            issues=[],
        )

        overall = round(
            headline_sec.score * 0.15 +
            about_sec.score * 0.15 +
            exp_sec.score * 0.25 +
            skills_sec.score * 0.20 +
            edu_sec.score * 0.10 +
            proj_sec.score * 0.15,
            1,
        )

        missing = []
        if not profile.about:
            missing.append("about")
        if not profile.projects:
            missing.append("projects")
        if not profile.certifications:
            missing.append("certifications")

        return LinkedInRating(
            overall_score=overall,
            headline=headline_sec,
            about=about_sec,
            experience=exp_sec,
            projects=proj_sec,
            skills=skills_sec,
            education=edu_sec,
            certifications=cert_sec,
            completeness=completeness_sec,
            strengths=[
                "Profile exhibits clean professional identity.",
                "Key technical skills and background aligned.",
            ],
            issues=[
                "Expand project and about descriptions with measurable impact.",
            ],
            recommendations=[
                LinkedInRecommendation(
                    priority="high",
                    area="Headline & About",
                    recommendation="Optimize your headline to showcase core technical specializations and value proposition.",
                    reason="Recruiters heavily weigh headlines and summary sections in keyword search algorithms.",
                    evidence=["Headline and About are key discovery factors."],
                ),
            ],
            suggested_content=[
                LinkedInSuggestedContent(
                    section="headline",
                    content=f"Software Engineer | {', '.join(skills[:3]) if skills else 'Full Stack Development'}",
                    basis=["Profile skills and technical background"],
                ),
            ],
            data_quality=LinkedInDataQuality(
                profile_data_available=True,
                completeness=overall,
                missing_sections=missing,
                unavailable_sections=[],
                note="LinkedIn profile data processed successfully.",
            ),
        )


linkedin_rater = LinkedInRater()