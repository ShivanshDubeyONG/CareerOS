from typing import List

from pydantic import BaseModel, Field


class SkillEvidence(BaseModel):
    skill: str

    confidence: str

    evidence: str


class ProjectInsight(BaseModel):
    repository: str

    meaningful_project: bool

    project_score: float = Field(
        ge=0,
        le=10,
    )

    project_stage: str

    project_type: str

    technologies: List[str]

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