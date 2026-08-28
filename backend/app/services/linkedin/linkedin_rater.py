import json

from app.schemas.linkedin_rating_schema import (
    LinkedInRating,
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

        return self.gemini.generate_structured(
            prompt,
            LinkedInRating,
        )
    
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


linkedin_rater = LinkedInRater()