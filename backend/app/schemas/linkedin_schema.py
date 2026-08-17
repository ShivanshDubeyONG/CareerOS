from pydantic import BaseModel, Field


class LinkedInExperience(BaseModel):
    company: str
    title: str

    start_date: str | None = None
    end_date: str | None = None

    description: str | None = None
    employment_type: str | None = None


class LinkedInEducation(BaseModel):
    institution: str

    degree: str | None = None
    field_of_study: str | None = None

    start_date: str | None = None
    end_date: str | None = None

    description: str | None = None


class LinkedInCertification(BaseModel):
    name: str
    issuer: str | None = None
    issue_date: str | None = None
    expiration_date: str | None = None
    credential_url: str | None = None


class LinkedInProject(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class LinkedInProfile(BaseModel):
    name: str | None = None
    headline: str | None = None
    location: str | None = None

    experiences: list[LinkedInExperience] = Field(
        default_factory=list
    )

    education: list[LinkedInEducation] = Field(
        default_factory=list
    )

    skills: list[str] = Field(
        default_factory=list
    )

    certifications: list[LinkedInCertification] = Field(
        default_factory=list
    )

    projects: list[LinkedInProject] = Field(
        default_factory=list
    )

    links: list[str] = Field(
        default_factory=list
    )


class LinkedInSkillEvidence(BaseModel):
    skill: str

    claimed: bool = True

    sources: list[str] = Field(
        default_factory=list
    )


class LinkedInCareerSignal(BaseModel):
    signal: str
    evidence: str


class LinkedInAnalysis(BaseModel):
    name: str | None = None
    headline: str | None = None
    location: str | None = None

    experience_count: int
    education_count: int
    skill_count: int
    certification_count: int
    project_count: int

    current_title: str | None = None
    current_company: str | None = None

    claimed_skills: list[str] = Field(
        default_factory=list
    )

    career_domains: list[str] = Field(
        default_factory=list
    )

    skill_evidence: list[LinkedInSkillEvidence] = Field(
        default_factory=list
    )

    career_signals: list[LinkedInCareerSignal] = Field(
        default_factory=list
    )

    signals: list[str] = Field(
        default_factory=list
    )