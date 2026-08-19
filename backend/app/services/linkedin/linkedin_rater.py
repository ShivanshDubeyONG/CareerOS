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

    The rater evaluates the LinkedIn profile using the
    canonical LinkedInProfile and LinkedInAnalysis.

    It never treats missing LinkedIn information as proof
    that the candidate lacks a skill, project, or experience.
    """

    def __init__(self):
        self.gemini = GeminiClient()

    def rate(
        self,
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
    ) -> LinkedInRating:
        evidence_packet = self._build_evidence_packet(
            profile,
            analysis,
        )

        prompt = self._build_prompt(
            evidence_packet,
        )

        return self.gemini.generate_structured(
            prompt,
            LinkedInRating,
        )

    @staticmethod
    def _build_evidence_packet(
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
    ) -> dict:
        return {
            "linkedin_profile": {
                "name": profile.name,
                "headline": profile.headline,
                "location": profile.location,
                "about": profile.about,

                "experiences": [
                    {
                        "company": experience.company,
                        "title": experience.title,
                        "start_date": experience.start_date,
                        "end_date": experience.end_date,
                        "description": experience.description,
                    }
                    for experience in profile.experiences
                ],

                "education": [
                    {
                        "institution": education.institution,
                        "degree": education.degree,
                        "field_of_study": education.field_of_study,
                        "start_date": education.start_date,
                        "end_date": education.end_date,
                        "description": education.description,
                    }
                    for education in profile.education
                ],

                "skills": profile.skills,

                "certifications": [
                    {
                        "name": certification.name,
                        "issuer": certification.issuer,
                        "issue_date": certification.issue_date,
                        "expiration_date": (
                            certification.expiration_date
                        ),
                        "credential_id": (
                            certification.credential_id
                        ),
                        "credential_url": (
                            certification.credential_url
                        ),
                    }
                    for certification in profile.certifications
                ],

                "projects": [
                    {
                        "name": project.name,
                        "description": project.description,
                        "url": project.url,
                    }
                    for project in profile.projects
                ],

                "languages": [
                    {
                        "name": language.name,
                        "proficiency": language.proficiency,
                    }
                    for language in profile.languages
                ],

                "organizations": [
                    {
                        "name": organization.name,
                        "role": organization.role,
                        "description": organization.description,
                    }
                    for organization in profile.organizations
                ],

                "awards": [
                    {
                        "name": award.name,
                        "issuer": award.issuer,
                        "date": award.date,
                        "description": award.description,
                    }
                    for award in profile.awards
                ],

                "publications": [
                    {
                        "title": publication.title,
                        "publisher": publication.publisher,
                        "date": publication.date,
                        "url": publication.url,
                        "description": publication.description,
                    }
                    for publication in profile.publications
                ],

                "volunteering": [
                    {
                        "organization": volunteer.organization,
                        "role": volunteer.role,
                        "cause": volunteer.cause,
                        "description": volunteer.description,
                        "start_date": volunteer.start_date,
                        "end_date": volunteer.end_date,
                    }
                    for volunteer in profile.volunteering
                ],
            },

            "linkedin_analysis": {
                "name": analysis.name,
                "headline": analysis.headline,
                "location": analysis.location,
                "current_title": analysis.current_title,
                "current_company": analysis.current_company,

                "experience_count": (
                    analysis.experience_count
                ),
                "education_count": (
                    analysis.education_count
                ),
                "skill_count": (
                    analysis.skill_count
                ),
                "project_count": (
                    analysis.project_count
                ),
                "certification_count": (
                    analysis.certification_count
                ),

                "claimed_skills": (
                    analysis.claimed_skills
                ),

                "career_domains": (
                    analysis.career_domains
                ),

                "career_signals": [
                    {
                        "signal": signal.signal,
                        "evidence": signal.evidence,
                    }
                    for signal in analysis.career_signals
                ],

                "profile_signals": (
                    analysis.signals
                ),
            },
        }

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

Your job is to evaluate the quality of a candidate's
LinkedIn profile and provide precise, actionable
recommendations.

This is NOT a generic LinkedIn checklist.

You must reason about:

- profile quality
- professional positioning
- completeness
- clarity
- technical/career direction
- project visibility
- skill visibility
- experience quality
- credibility
- career narrative

IMPORTANT:

Never fabricate candidate information.

Never assume that missing LinkedIn information means
the candidate does not have that skill, project,
experience, or achievement.

For example:

If LinkedIn does not list Python, you must NOT say:

"The candidate does not know Python."

Instead say:

"Python is not represented in the available LinkedIn
data."

If information is unavailable, explicitly identify it
as unavailable.

==================================================
SCORING
==================================================

Score these sections independently from 0 to 100:

- headline
- about
- experience
- projects
- skills
- education
- certifications
- completeness

The overall score must reflect the quality of the
AVAILABLE LinkedIn profile.

Do not invent missing information to increase the score.

Do not automatically give a high score simply because
a section exists.

==================================================
HEADLINE
==================================================

Evaluate:

- clarity
- specificity
- professional identity
- career direction
- relevance
- differentiation

==================================================
ABOUT
==================================================

Evaluate:

- professional identity
- career direction
- what the candidate does
- what the candidate builds
- evidence
- specificity
- readability

==================================================
EXPERIENCE
==================================================

Evaluate:

- role clarity
- company clarity
- descriptions
- responsibilities
- impact
- technical relevance
- progression

Do not invent achievements or metrics.

==================================================
PROJECTS
==================================================

Evaluate:

- presence
- descriptions
- relevance
- technical depth
- links
- credibility

If projects are absent from LinkedIn, say that
LinkedIn project evidence is missing.

Do not say the candidate has no projects.

==================================================
SKILLS
==================================================

Evaluate:

- relevance
- breadth
- career alignment
- representation

Missing skills are LinkedIn representation gaps,
not proof that the candidate lacks those skills.

==================================================
EDUCATION
==================================================

Evaluate:

- institution
- degree
- field
- dates
- completeness

==================================================
CERTIFICATIONS
==================================================

Evaluate:

- relevance
- issuer
- credential information
- completeness

==================================================
RECOMMENDATIONS
==================================================

Recommendations must be:

- specific
- actionable
- prioritized
- evidence-based

Avoid generic advice.

Bad:

"Improve your profile."

Good:

"Add the strongest demonstrated project to LinkedIn
Projects because it is present in other CareerOS
evidence but missing from the LinkedIn profile."

==================================================
SUGGESTED CONTENT
==================================================

Suggested content may ONLY use information explicitly
supported by the provided evidence.

Never invent:

- projects
- technologies
- achievements
- metrics
- responsibilities
- companies
- certifications

If there is insufficient evidence, return an empty
suggested_content list.

==================================================
DATA QUALITY
==================================================

Clearly distinguish:

1. Missing LinkedIn information.
2. Unavailable acquired data.
3. Actual weakness in the profile.

For example:

Correct:

"Projects cannot be fully evaluated because project
data is unavailable in the acquired LinkedIn profile."

Incorrect:

"The candidate has no projects."

==================================================
OUTPUT
==================================================

Return ONLY data compatible with the LinkedInRating
schema.

Keep recommendations concise and useful.

Prioritize high-impact improvements.

==================================================
AVAILABLE CAREEROS EVIDENCE
==================================================

{evidence_json}
"""


linkedin_rater = LinkedInRater()