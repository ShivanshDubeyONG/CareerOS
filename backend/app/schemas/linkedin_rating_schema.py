from pydantic import BaseModel, Field


class LinkedInSectionScore(BaseModel):
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


class LinkedInRecommendation(BaseModel):
    priority: str
    area: str
    recommendation: str
    reason: str
    evidence: list[str] = Field(
        default_factory=list
    )


class LinkedInSuggestedContent(BaseModel):
    section: str
    content: str
    basis: list[str] = Field(
        default_factory=list
    )


class LinkedInDataQuality(BaseModel):
    profile_data_available: bool

    completeness: float = Field(
        ge=0,
        le=100,
    )

    missing_sections: list[str] = Field(
        default_factory=list
    )

    unavailable_sections: list[str] = Field(
        default_factory=list
    )

    note: str


class LinkedInRating(BaseModel):
    overall_score: float = Field(
        ge=0,
        le=100,
    )

    headline: LinkedInSectionScore
    about: LinkedInSectionScore
    experience: LinkedInSectionScore
    projects: LinkedInSectionScore
    skills: LinkedInSectionScore
    education: LinkedInSectionScore
    certifications: LinkedInSectionScore

    completeness: LinkedInSectionScore

    strengths: list[str] = Field(
        default_factory=list
    )

    issues: list[str] = Field(
        default_factory=list
    )

    recommendations: list[LinkedInRecommendation] = Field(
        default_factory=list
    )

    suggested_content: list[LinkedInSuggestedContent] = Field(
        default_factory=list
    )

    data_quality: LinkedInDataQuality