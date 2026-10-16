from typing import List, Union

from pydantic import BaseModel, Field, field_validator


class SkillEvidence(BaseModel):
    skill: str
    confidence: str
    evidence: str

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, v):
        if isinstance(v, list):
            return " ".join(str(item) for item in v)
        return str(v) if v is not None else ""


class TechnologyEvidence(BaseModel):
    technology: str

    evidence_sources: List[str] = Field(
        default_factory=list
    )

    confidence: str = "medium"


class ProjectInsight(BaseModel):
    repository: str

    meaningful_project: bool

    project_score: float = Field(
        ge=0,
        le=10,
    )

    project_stage: str

    project_type: str

    technologies: List[str] = Field(
        default_factory=list
    )

    technology_evidence: List[TechnologyEvidence] = Field(
        default_factory=list
    )

    assessment: str


class EvidenceGap(BaseModel):
    area: str
    reason: str


class GitHubAIAnalysis(BaseModel):
    projects: List[ProjectInsight]

    technical_strengths: List[str]

    demonstrated_skills: List[SkillEvidence]

    evidence_gaps: List[EvidenceGap]

    overall_assessment: str

    career_relevance: str

    recommendations: List[str]