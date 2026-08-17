from app.schemas.linkedin_schema import (
    LinkedInCareerSignal,
    LinkedInAnalysis,
    LinkedInProfile,
    LinkedInSkillEvidence,
)
from app.services.linkedin.linkedin_normalizer import (
    linkedin_normalizer,
)


class LinkedInService:

    def analyze(
        self,
        profile: LinkedInProfile,
    ) -> LinkedInAnalysis:

        profile = (
            linkedin_normalizer.normalize_profile(
                profile
            )
        )

        experiences = profile.experiences
        skills = profile.skills

        current_experience = (
            self._find_current_experience(
                experiences
            )
        )

        current_title = (
            current_experience.title
            if current_experience
            else None
        )

        current_company = (
            current_experience.company
            if current_experience
            else None
        )

        career_domains = (
            linkedin_normalizer.detect_career_domains(
                profile
            )
        )

        skill_evidence = (
            self._build_skill_evidence(
                skills
            )
        )

        career_signals = (
            self._build_career_signals(
                profile
            )
        )

        signals = self._build_signals(
            profile=profile,
            career_domains=career_domains,
        )

        return LinkedInAnalysis(
            name=profile.name,
            headline=profile.headline,
            location=profile.location,
            about=profile.about,

            experience_count=len(
                experiences
            ),

            education_count=len(
                profile.education
            ),

            skill_count=len(
                skills
            ),

            certification_count=len(
                profile.certifications
            ),

            project_count=len(
                profile.projects
            ),

            language_count=len(
                profile.languages
            ),

            organization_count=len(
                profile.organizations
            ),

            award_count=len(
                profile.awards
            ),

            publication_count=len(
                profile.publications
            ),

            volunteering_count=len(
                profile.volunteering
            ),

            current_title=current_title,
            current_company=current_company,

            claimed_skills=skills,
            career_domains=career_domains,
            skill_evidence=skill_evidence,
            career_signals=career_signals,
            signals=signals,
        )

    # ==================================================
    # CURRENT EXPERIENCE
    # ==================================================

    @staticmethod
    def _find_current_experience(
        experiences,
    ):

        if not experiences:
            return None

        for experience in experiences:

            end_date = (
                experience.end_date
                or ""
            ).strip().lower()

            if end_date in {
                "present",
                "current",
                "now",
            }:
                return experience

        return experiences[0]

    # ==================================================
    # SKILL EVIDENCE
    # ==================================================

    @staticmethod
    def _build_skill_evidence(
        skills: list[str],
    ) -> list[LinkedInSkillEvidence]:

        return [
            LinkedInSkillEvidence(
                skill=skill,
                claimed=True,
                sources=["linkedin"],
            )
            for skill in skills
        ]

    # ==================================================
    # CAREER SIGNALS
    # ==================================================

    def _build_career_signals(
        self,
        profile: LinkedInProfile,
    ) -> list[LinkedInCareerSignal]:

        signals = []

        if profile.experiences:

            signals.append(
                LinkedInCareerSignal(
                    signal="professional_experience",
                    evidence=(
                        f"{len(profile.experiences)} "
                        "experience entries found."
                    ),
                )
            )

        if profile.projects:

            signals.append(
                LinkedInCareerSignal(
                    signal="project_presence",
                    evidence=(
                        f"{len(profile.projects)} "
                        "projects listed on LinkedIn."
                    ),
                )
            )

        else:

            signals.append(
                LinkedInCareerSignal(
                    signal="project_absence",
                    evidence=(
                        "No projects were found "
                        "in the acquired LinkedIn profile."
                    ),
                )
            )

        if profile.certifications:

            signals.append(
                LinkedInCareerSignal(
                    signal="certification_presence",
                    evidence=(
                        f"{len(profile.certifications)} "
                        "certifications listed."
                    ),
                )
            )

        if profile.skills:

            signals.append(
                LinkedInCareerSignal(
                    signal="technical_skill_claims",
                    evidence=(
                        f"{len(profile.skills)} "
                        "skills explicitly claimed."
                    ),
                )
            )

        else:

            signals.append(
                LinkedInCareerSignal(
                    signal="skill_claims_unavailable",
                    evidence=(
                        "No LinkedIn skill claims "
                        "were available in the "
                        "acquired profile."
                    ),
                )
            )

        if profile.languages:

            signals.append(
                LinkedInCareerSignal(
                    signal="language_presence",
                    evidence=(
                        f"{len(profile.languages)} "
                        "languages listed."
                    ),
                )
            )

        if profile.organizations:

            signals.append(
                LinkedInCareerSignal(
                    signal="organization_presence",
                    evidence=(
                        f"{len(profile.organizations)} "
                        "organizations listed."
                    ),
                )
            )

        if profile.awards:

            signals.append(
                LinkedInCareerSignal(
                    signal="award_presence",
                    evidence=(
                        f"{len(profile.awards)} "
                        "awards listed."
                    ),
                )
            )

        if profile.publications:

            signals.append(
                LinkedInCareerSignal(
                    signal="publication_presence",
                    evidence=(
                        f"{len(profile.publications)} "
                        "publications listed."
                    ),
                )
            )

        if profile.volunteering:

            signals.append(
                LinkedInCareerSignal(
                    signal="volunteering_presence",
                    evidence=(
                        f"{len(profile.volunteering)} "
                        "volunteering entries found."
                    ),
                )
            )

        trajectory = (
            self._detect_trajectory(
                profile
            )
        )

        if trajectory:

            signals.append(
                LinkedInCareerSignal(
                    signal="career_trajectory",
                    evidence=trajectory,
                )
            )

        return signals

    # ==================================================
    # CAREER TRAJECTORY
    # ==================================================

    @staticmethod
    def _detect_trajectory(
        profile: LinkedInProfile,
    ) -> str | None:

        if len(profile.experiences) < 2:
            return None

        titles = [
            experience.title.lower()
            for experience
            in profile.experiences
            if experience.title
        ]

        progression_terms = {
            "intern": 0,
            "trainee": 1,
            "junior": 2,
            "associate": 3,
            "engineer": 4,
            "developer": 4,
            "senior": 5,
            "lead": 6,
            "manager": 7,
        }

        levels = []

        for title in titles:

            level = None

            for term, value in (
                progression_terms.items()
            ):

                if term in title:

                    level = max(
                        level or 0,
                        value,
                    )

            if level is not None:
                levels.append(level)

        if len(levels) < 2:
            return None

        if levels[-1] > levels[0]:

            return (
                "Experience history shows "
                "evidence of increasing "
                "role seniority."
            )

        if levels[-1] < levels[0]:

            return (
                "Experience history shows "
                "a decrease in apparent "
                "role seniority."
            )

        return (
            "Experience history shows "
            "a relatively stable role level."
        )

    # ==================================================
    # PROFILE SIGNALS
    # ==================================================

    def _build_signals(
        self,
        profile: LinkedInProfile,
        career_domains: list[str],
    ) -> list[str]:

        signals = []

        if profile.experiences:

            signals.append(
                "professional_experience_present"
            )

        else:

            signals.append(
                "no_professional_experience_listed"
            )

        if len(profile.experiences) >= 3:

            signals.append(
                "multiple_experience_entries"
            )

        if profile.skills:

            if len(profile.skills) >= 15:

                signals.append(
                    "broad_skill_claims"
                )

            elif len(profile.skills) >= 5:

                signals.append(
                    "moderate_skill_claims"
                )

            else:

                signals.append(
                    "limited_skill_claims"
                )

        else:

            signals.append(
                "no_linkedin_skill_claims_available"
            )

        if profile.projects:

            signals.append(
                "projects_present"
            )

        else:

            signals.append(
                "no_projects_listed"
            )

        if profile.certifications:

            signals.append(
                "certifications_present"
            )

        if profile.education:

            signals.append(
                "education_present"
            )

        else:

            signals.append(
                "education_data_incomplete"
            )

        if profile.languages:

            signals.append(
                "languages_present"
            )

        if profile.organizations:

            signals.append(
                "organizations_present"
            )

        if profile.awards:

            signals.append(
                "awards_present"
            )

        if profile.publications:

            signals.append(
                "publications_present"
            )

        if profile.volunteering:

            signals.append(
                "volunteering_present"
            )

        if profile.about:

            signals.append(
                "about_section_present"
            )

        else:

            signals.append(
                "about_section_unavailable"
            )

        if len(career_domains) >= 2:

            signals.append(
                "multi_domain_career_profile"
            )

        elif len(career_domains) == 1:

            signals.append(
                "clear_primary_career_domain"
            )

        else:

            signals.append(
                "career_domain_unclear"
            )

        if profile.headline:

            headline = (
                profile.headline.lower()
            )

            technical_terms = (
                "engineer",
                "developer",
                "programmer",
                "data scientist",
                "machine learning",
                "software",
                "artificial intelligence",
                "ai",
                "backend",
                "frontend",
                "full stack",
                "fullstack",
            )

            if any(
                term in headline
                for term in technical_terms
            ):

                signals.append(
                    "technical_headline"
                )

        return signals


linkedin_service = LinkedInService()