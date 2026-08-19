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
    while CareerOS UnifiedCandidateProfile provides the
    deterministic cross-source evidence.

    Gemini must NEVER invent evidence or decide that missing
    LinkedIn data means the candidate lacks something.
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
            f"\nDEBUG GEMINI PROMPT LENGTH: "
            f"{len(prompt)} characters"
        )
        return self.gemini.generate_structured(
            prompt,
            LinkedInRating,
        )

    # ==================================================
    # EVIDENCE PACKET
    # ==================================================

    @staticmethod
    def _build_evidence_packet(
        profile: LinkedInProfile,
        analysis: LinkedInAnalysis,
        unified_profile=None,
    ) -> dict:

        packet = {
            "linkedin_profile": {
                "name": profile.name,
                "headline": profile.headline,
                "location": profile.location,
                "about": profile.about,

                "profile_url": profile.profile_url,

                "public_identifier": (
                    profile.public_identifier
                ),

                "followers": profile.followers,
                "connections": profile.connections,

                "experiences": [
                    {
                        "company": experience.company,
                        "title": experience.title,
                        "start_date": experience.start_date,
                        "end_date": experience.end_date,
                        "description": experience.description,
                        "employment_type": (
                            experience.employment_type
                        ),
                        "location": experience.location,
                    }
                    for experience in profile.experiences
                ],

                "education": [
                    {
                        "institution": education.institution,
                        "degree": education.degree,
                        "field_of_study": (
                            education.field_of_study
                        ),
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
                        "issue_date": (
                            certification.issue_date
                        ),
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
                        "description": (
                            organization.description
                        ),
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

                "featured_links": profile.links,
            },

            "linkedin_analysis": {
                "name": analysis.name,
                "headline": analysis.headline,
                "location": analysis.location,
                "current_title": (
                    analysis.current_title
                ),
                "current_company": (
                    analysis.current_company
                ),

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

        # ==================================================
        # CROSS-SOURCE CAREEROS EVIDENCE
        # ==================================================

        if unified_profile is None:

            packet["unified_careeros_evidence"] = {
                "available": False,
                "note": (
                    "Unified cross-source evidence "
                    "was not provided."
                ),
            }

            return packet

        packet[
            "unified_careeros_evidence"
        ] = {

            "available": True,

            "source_status": (
                unified_profile.source_status
            ),

            "skills": (
                unified_profile.skills
            ),

            "career_domains": (
                unified_profile.career_domains
            ),

            "skill_evidence": [
                {
                    "skill": item.skill,

                    "resume_claimed": (
                        item.resume_claimed
                    ),

                    "linkedin_claimed": (
                        item.linkedin_claimed
                    ),

                    "github_demonstrated": (
                        item.github_demonstrated
                    ),

                    "leetcode_demonstrated": (
                        item.leetcode_demonstrated
                    ),

                    "supporting_sources": (
                        item.supporting_sources
                    ),

                    "missing_supporting_sources": (
                        item.missing_supporting_sources
                    ),

                    "status": item.status,

                    "evidence": [
                        {
                            "source": evidence.source,
                            "evidence_type": (
                                evidence.evidence_type
                            ),
                            "value": evidence.value,
                            "strength": evidence.strength,
                            "details": evidence.details,
                        }
                        for evidence
                        in item.evidence
                    ],
                }
                for item
                in unified_profile.skill_evidence
            ],

            "project_evidence": [
                {
                    "name": item.name,

                    "resume_present": (
                        item.resume_present
                    ),

                    "linkedin_present": (
                        item.linkedin_present
                    ),

                    "github_present": (
                        item.github_present
                    ),

                    "github_repository": (
                        item.github_repository
                    ),

                    "status": item.status,

                    "finding": item.finding,

                    "evidence": [
                        {
                            "source": evidence.source,
                            "evidence_type": (
                                evidence.evidence_type
                            ),
                            "value": evidence.value,
                            "strength": evidence.strength,
                            "details": evidence.details,
                        }
                        for evidence
                        in item.evidence
                    ],
                }
                for item
                in unified_profile.project_evidence
            ],

            "cross_source_findings": [
                {
                    "finding_type": finding.finding_type,
                    "subject": finding.subject,
                    "severity": finding.severity,
                    "message": finding.message,
                    "sources": finding.sources,

                    "evidence": [
                        {
                            "source": evidence.source,
                            "evidence_type": (
                                evidence.evidence_type
                            ),
                            "value": evidence.value,
                            "strength": evidence.strength,
                            "details": evidence.details,
                        }
                        for evidence
                        in finding.evidence
                    ],
                }
                for finding
                in unified_profile.findings
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

You are NOT a generic LinkedIn profile grader.

Your job is to determine how effectively the candidate's
LinkedIn profile represents their actual career evidence
and then provide precise, actionable improvements.

CareerOS has already performed deterministic evidence
matching across:

- Resume
- LinkedIn
- GitHub
- LeetCode

You must use that evidence.

==================================================
CORE RULE
==================================================

CareerOS evidence is authoritative for cross-source facts.

Do NOT invent evidence.

Do NOT infer that a candidate lacks a skill, project,
experience, achievement, or technology simply because it
is absent from LinkedIn.

A missing LinkedIn item means:

"Not represented in the available LinkedIn data."

It does NOT mean:

"The candidate does not have it."

==================================================
IMPORTANT DISTINCTION
==================================================

There are three different situations:

1. LINKEDIN MISSING

Example:

Python:
Resume ✓
LinkedIn ✗
GitHub ✓
LeetCode ✓

Correct interpretation:

"Python is not represented on LinkedIn despite being
strongly supported elsewhere."

2. PROVIDER UNAVAILABLE

If the acquisition provider did not return a section,
do NOT call the section empty.

Example:

Projects:
provider did not return project data

Correct:

"Projects cannot be fully evaluated because project
data was unavailable from the acquisition provider."

3. ACTUAL LINKEDIN WEAKNESS

If the section is available and contains weak,
incomplete, vague, or poorly presented information,
you may identify that as a profile weakness.

==================================================
SCORING
==================================================

Score independently from 0 to 100:

- headline
- about
- experience
- projects
- skills
- education
- certifications
- completeness

The score measures LinkedIn PROFILE QUALITY.

Do NOT reduce a score simply because another source
contains information that LinkedIn does not.

Instead, identify cross-source omissions as
recommendations.

For example:

A project missing from LinkedIn should not automatically
make the Projects score 0 if project acquisition itself
is unavailable.

==================================================
HEADLINE
==================================================

Evaluate:

- professional identity
- clarity
- target direction
- specificity
- differentiation
- unnecessary keyword stuffing

If the headline is a list of technologies, explain
how to turn it into a professional positioning statement.

==================================================
ABOUT
==================================================

Evaluate:

- identity
- technical direction
- what the candidate builds
- evidence
- specificity
- readability
- career goal

Use verified cross-source evidence when recommending
what should be emphasized.

==================================================
EXPERIENCE
==================================================

Evaluate only the experience data actually available.

Never fabricate responsibilities, achievements,
companies, metrics, or roles.

If experience data is unavailable from the provider,
state that explicitly.

==================================================
PROJECTS
==================================================

Use BOTH:

1. LinkedIn project data
2. CareerOS project evidence

If GitHub/Resume evidence identifies a project that is
missing from LinkedIn, this is a HIGH-VALUE recommendation.

Example:

"CareerOS found CareerOS on GitHub and Resume evidence,
but it is not represented in LinkedIn project evidence.
Consider adding it to LinkedIn Projects."

Do not claim the candidate has no projects.

==================================================
SKILLS
==================================================

Use CareerOS skill evidence.

Pay special attention to:

- strongly_supported
- demonstrated
- claimed_only
- unknown

If a skill is strongly supported by Resume + GitHub +
LeetCode but missing from LinkedIn, recommend adding it.

Example:

"Python is strongly supported across CareerOS evidence
but is not represented on LinkedIn."

Do NOT call such a skill unsupported.

==================================================
EDUCATION
==================================================

Evaluate:

- institution
- degree
- field
- dates
- grades
- completeness

Flag actual inconsistencies when supported by the data.

==================================================
CERTIFICATIONS
==================================================

Evaluate:

- relevance
- issuer
- credential
- dates
- whether the credential information is complete

==================================================
CROSS-SOURCE INTELLIGENCE
==================================================

This is the most important differentiator of CareerOS.

Prioritize recommendations where:

- strong evidence exists outside LinkedIn
- LinkedIn does not represent that evidence
- the missing representation materially affects
  professional positioning

Examples:

- strong GitHub project missing from LinkedIn
- demonstrated technology missing from LinkedIn skills
- strong technical direction not reflected in headline
- Resume achievement not represented in About
- LinkedIn claim lacking supporting evidence

Use the exact evidence supplied.

==================================================
RECOMMENDATION QUALITY
==================================================

Every recommendation should answer:

1. WHAT should change?
2. WHY does it matter?
3. WHAT evidence supports the recommendation?

Avoid generic recommendations such as:

"Improve your profile."

Prefer:

"Add CareerOS to LinkedIn Projects because it is
supported by GitHub and Resume evidence but is currently
not represented in LinkedIn."

==================================================
SUGGESTED CONTENT
==================================================

Generated content MUST ONLY use verified candidate
information present in:

- LinkedIn
- Resume evidence
- GitHub evidence
- LeetCode evidence

Never invent:

- projects
- technologies
- metrics
- achievements
- companies
- responsibilities
- certifications

If there is insufficient evidence, return no suggested
content.

==================================================
DATA QUALITY
==================================================

Distinguish:

- missing from LinkedIn
- unavailable from provider
- genuinely weak LinkedIn content

Never collapse those into one category.

==================================================
OUTPUT
==================================================

Return ONLY data compatible with LinkedInRating.

Keep recommendations concise.

Prioritize high-impact improvements.

==================================================
CAREEROS EVIDENCE
==================================================

{evidence_json}
"""

    
linkedin_rater = LinkedInRater()