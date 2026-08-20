from pydantic import BaseModel, Field


class ResumeSectionScore(BaseModel):
    score: float = Field(
        ge=0,
        le=100,
    )

    rationale: str

    strengths: list[str] = Field(
        default_factory=list
    )

    issues: list[str] = Field(
        default_factory=list
    )


class ResumeRecommendation(BaseModel):
    priority: str
    area: str
    recommendation: str
    reason: str

    evidence: list[str] = Field(
        default_factory=list
    )


class ResumeSuggestedContent(BaseModel):
    section: str
    content: str

    basis: list[str] = Field(
        default_factory=list
    )


class ResumeDataQuality(BaseModel):
    profile_data_available: bool

    completeness: float = Field(
        ge=0,
        le=100,
    )

    missing_sections: list[str] = Field(
        default_factory=list
    )

    note: str


class ResumeRating(BaseModel):
    overall_score: float = Field(
        ge=0,
        le=100,
    )

    summary: ResumeSectionScore

    experience: ResumeSectionScore

    projects: ResumeSectionScore

    skills: ResumeSectionScore

    education: ResumeSectionScore

    achievements: ResumeSectionScore

    structure: ResumeSectionScore

    ats: ResumeSectionScore

    quantified_impact: ResumeSectionScore

    target_role_alignment: ResumeSectionScore

    strengths: list[str] = Field(
        default_factory=list
    )

    issues: list[str] = Field(
        default_factory=list
    )

    recommendations: list[ResumeRecommendation] = Field(
        default_factory=list
    )

    suggested_content: list[
        ResumeSuggestedContent
    ] = Field(
        default_factory=list
    )

    data_quality: ResumeDataQuality