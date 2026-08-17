from pydantic import BaseModel, Field


class LinkedInExperience(BaseModel):
    company: str
    title: str

    start_date: str | None = None
    end_date: str | None = None

    description: str | None = None
    employment_type: str | None = None
    location: str | None = None


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
    credential_id: str | None = None
    credential_url: str | None = None


class LinkedInProject(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class LinkedInLanguage(BaseModel):
    name: str
    proficiency: str | None = None


class LinkedInOrganization(BaseModel):
    name: str
    role: str | None = None
    description: str | None = None


class LinkedInAward(BaseModel):
    name: str
    issuer: str | None = None
    date: str | None = None
    description: str | None = None


class LinkedInPublication(BaseModel):
    title: str
    publisher: str | None = None
    date: str | None = None
    url: str | None = None
    description: str | None = None


class LinkedInVolunteerExperience(BaseModel):
    organization: str
    role: str | None = None
    cause: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class LinkedInProfile(BaseModel):
    name: str | None = None
    headline: str | None = None
    location: str | None = None
    about: str | None = None

    profile_url: str | None = None
    public_identifier: str | None = None

    followers: int | None = None
    connections: int | None = None

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

    languages: list[LinkedInLanguage] = Field(
        default_factory=list
    )

    organizations: list[LinkedInOrganization] = Field(
        default_factory=list
    )

    awards: list[LinkedInAward] = Field(
        default_factory=list
    )

    publications: list[LinkedInPublication] = Field(
        default_factory=list
    )

    volunteering: list[LinkedInVolunteerExperience] = Field(
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
    about: str | None = None

    experience_count: int
    education_count: int
    skill_count: int
    certification_count: int
    project_count: int

    language_count: int
    organization_count: int
    award_count: int
    publication_count: int
    volunteering_count: int

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