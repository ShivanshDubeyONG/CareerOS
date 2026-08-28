import json

from app.schemas.resume_schema import ResumeData
from app.schemas.resume_rating_schema import ResumeRating
from app.services.ai.gemini_client import GeminiClient


class ResumeRater:

    def __init__(self):
        self.gemini = GeminiClient()

    def rate(
        self,
        resume: ResumeData,
    ) -> ResumeRating:

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

            print(
                "ResumeRating: JSON validation DONE",
                flush=True,
            )

            return result

        except Exception as exc:

            print(
                "ResumeRating: Gemini FAILED:",
                repr(exc),
                flush=True,
            )

            raise


resume_rater = ResumeRater()