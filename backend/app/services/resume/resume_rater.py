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

Your job is to evaluate a candidate resume and provide
structured, evidence-grounded career advice.

CANDIDATE RESUME EVIDENCE
=========================

{json.dumps(
    evidence_packet,
    indent=2,
    ensure_ascii=False,
)}

IMPORTANT RULES
===============

1. Evaluate ONLY the evidence supplied above.

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

4. A recommendation may suggest that the candidate
   ADD a missing metric, but the metric itself must
   NEVER be fabricated.

5. Suggested content must contain only facts supported
   by the supplied resume.

6. If a stronger bullet requires information that is
   missing, explicitly say that candidate-provided
   evidence is required.

7. You may improve:
   - wording
   - clarity
   - structure
   - technical phrasing
   - conciseness
   - organization

8. You may NOT transform an unsupported assumption into
   a factual achievement.

9. Distinguish between:
   - missing information
   - weak wording
   - genuinely weak experience.

10. Do not penalize the candidate merely because a section
    is unavailable if the supplied evidence clearly indicates
    that the section was not provided.

11. Evaluate ATS compatibility based on the actual resume
    evidence and structure.

12. Evaluate target-role alignment based only on the skills,
    projects, education, experience, certifications and other
    evidence actually supplied.

13. Recommendations must be specific and actionable.

14. Evidence fields must contain short references to actual
    supplied resume evidence.

15. If the resume contains no quantified achievements,
    identify that as a gap rather than creating one.

16. Suggested content must be truthful even if that means
    leaving a placeholder such as:
    "[add actual accuracy if available]"

17. Do not claim that the candidate has experience simply
    because they possess a skill.

SCORING
=======

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

Be realistic.

A student with strong technical projects but no professional
experience should not automatically receive a high experience
score.

OUTPUT
======

Return the required structured ResumeRating object.

The output must be useful to a real student applying for
internships and entry-level software engineering / ML roles.
"""

        return self.gemini.generate_structured(
            prompt=prompt,
            response_schema=ResumeRating,
        )


resume_rater = ResumeRater()