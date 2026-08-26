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

        prompt = f"""
You are the Resume Intelligence engine for CareerOS.

Your job is to evaluate the candidate's resume as a REAL
technical hiring document for software engineering and
AI/ML internships and entry-level roles.

The goal is NOT to reward cosmetic resume formatting.

The goal is to determine:

1. How strong the candidate's actual technical profile is.
2. How clearly that strength is communicated.
3. What changes would materially improve their chances
   with a technical recruiter or hiring manager.

CANDIDATE RESUME EVIDENCE
=========================

{json.dumps(
    evidence_packet,
    indent=2,
    ensure_ascii=False,
)}

==================================================
EVIDENCE RULES
==================================================

1. Evaluate ONLY evidence supplied above.

2. NEVER invent facts.

3. NEVER invent:
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

4. A recommendation may ask the candidate to ADD a missing
   metric, but the metric itself must never be fabricated.

5. If evidence is missing, explicitly state that
   candidate-provided evidence is required.

6. You may improve:
   - wording
   - clarity
   - structure
   - technical phrasing
   - conciseness
   - organization

7. Never turn an unsupported assumption into a factual
   achievement.

8. Distinguish between:
   - missing information
   - weak wording
   - weak presentation
   - genuinely weak experience

9. Do not penalize a candidate simply because a section
   is unavailable.

10. Do not assume that lack of professional experience means
    lack of technical ability.

11. A strong student project is legitimate evidence of
    technical ability.

12. Do not claim the candidate has experience simply because
    they possess a skill.

==================================================
WHAT MATTERS MOST
==================================================

Prioritize substantive technical evidence over cosmetic
resume conventions.

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

For example:

GOOD:
"Built a Flask API for serving a trained ML model."

Potential improvement:
"Add the model's actual validation metric if available."

BAD:
"Project is weak because it has no quantified impact."

==================================================
SKILLS EVALUATION
==================================================

Evaluate whether the skills section accurately represents
the candidate's technical profile.

Do NOT penalize the candidate heavily because skills are not
perfectly categorized.

Only recommend grouping skills when:

- the list is genuinely difficult to scan,
- categories would materially improve readability,
- or the current structure makes important skills difficult
  to find.

Do NOT recommend adding skills that are not supported by the
resume.

Do NOT confuse skill organization with technical ability.

==================================================
SUMMARY EVALUATION
==================================================

A professional summary is OPTIONAL.

If the candidate has a strong technical resume without a
summary, do NOT treat the absence of a summary as a major
weakness.

Recommend a summary only when it would materially improve
positioning, such as when:

- the candidate's direction is unclear,
- their strongest technical focus is difficult to infer,
- or the resume lacks a clear professional narrative.

A missing summary should have a LOW impact on the overall
evaluation.

==================================================
QUANTIFIED IMPACT
==================================================

Evaluate quantified impact intelligently.

Reward real metrics when they exist.

However:

- do not require fabricated metrics,
- do not require every project to contain metrics,
- do not penalize technically strong work simply because
  outcomes were not quantified,
- distinguish between measurable engineering work and work
  where meaningful metrics may not exist.

Examples of legitimate evidence include:

- model accuracy / F1 / RMSE
- dataset size
- number of users
- API latency
- throughput
- number of endpoints
- number of problems solved
- deployment scale
- benchmark results
- measurable performance improvements

Only recommend adding a metric when the underlying work
reasonably suggests that one may exist.

==================================================
SCORING PHILOSOPHY
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

IMPORTANT:

These section scores are NOT equally important.

For a technical student, substantive technical evidence
should dominate the overall evaluation.

Do NOT allow a missing summary, imperfect skill formatting,
or lack of quantified metrics to drag an otherwise strong
technical resume into a poor overall score.

A candidate with:

- strong technical projects,
- meaningful ML/software implementation,
- relevant technologies,
- strong problem-solving evidence,

can legitimately receive a strong overall score even if they
have limited professional experience.

Likewise, a candidate with excellent formatting but weak
technical evidence should NOT receive a high score merely
because the resume looks polished.

==================================================
RECOMMENDATIONS
==================================================

Recommendations must be:

- specific
- actionable
- evidence-grounded
- prioritized by actual hiring impact

Prioritize recommendations approximately in this order:

1. Missing or weak substantive evidence
2. Weak project / experience descriptions
3. Missing technical contributions
4. Missing measurable outcomes where genuinely available
5. Target-role positioning
6. Resume structure and readability
7. Skills organization
8. Professional summary

Do NOT produce recommendations simply because a common resume
best practice is absent.

Every recommendation should answer:

"Why would fixing this materially improve the candidate's
resume?"

Avoid generic advice such as:

- "Improve your resume."
- "Add more skills."
- "Make it professional."
- "Use better formatting."

==================================================
IMPORTANT CALIBRATION
==================================================

CareerOS is intended to be a DEEP career intelligence system.

Do not behave like a generic resume checker.

Do not over-penalize students.

Do not reward empty buzzwords.

Do not reward formatting over substance.

Do not punish missing optional sections.

Do not invent achievements.

Strong technical evidence should be recognized as strong
technical evidence.

Weak presentation should be identified separately from weak
career substance.

==================================================
OUTPUT
==================================================

Return the required structured ResumeRating object.

The output must be useful to a real student applying for
software engineering, AI/ML, backend, full-stack, and related
technical internships and entry-level roles.
"""

        return self.gemini.generate_structured(
            prompt=prompt,
            response_schema=ResumeRating,
        )


resume_rater = ResumeRater()