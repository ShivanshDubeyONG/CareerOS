from typing import List

from pydantic import BaseModel, Field


class SkillEvidence(BaseModel):
    skill: str = Field(
        description="Technical skill demonstrated by the candidate."
    )

    confidence: str = Field(
        description="Confidence level: high, medium, or low."
    )

    evidence: str = Field(
        description="Specific GitHub evidence supporting the skill."
    )


class ProjectInsight(BaseModel):
    repository: str = Field(
        description="Repository name."
    )

    project_type: str = Field(
        description="Likely project type, such as ML, backend, frontend, data science, CLI, or library."
    )

    technologies: List[str] = Field(
        description="Technologies clearly demonstrated by the repository."
    )

    assessment: str = Field(
        description="Concise assessment of the technical substance and quality of the project."
    )


class EvidenceGap(BaseModel):
    area: str = Field(
        description="Skill, engineering practice, or technology with weak evidence."
    )

    reason: str = Field(
        description="Why the GitHub evidence is weak or insufficient."
    )


class GitHubAIAnalysis(BaseModel):
    overall_assessment: str = Field(
        description="High-level assessment of the candidate's GitHub profile."
    )

    technical_strengths: List[str] = Field(
        description="The candidate's strongest technical areas demonstrated on GitHub."
    )

    demonstrated_skills: List[SkillEvidence] = Field(
        description="Skills supported by concrete GitHub evidence."
    )

    strongest_projects: List[ProjectInsight] = Field(
        description="The strongest repositories from a career/engineering perspective."
    )

    evidence_gaps: List[EvidenceGap] = Field(
        description="Important areas where GitHub provides weak or insufficient evidence."
    )

    career_relevance: str = Field(
        description="How useful the current GitHub portfolio appears for software/ML engineering careers."
    )

    recommendations: List[str] = Field(
        description="Specific, actionable recommendations for improving the GitHub portfolio."
    )