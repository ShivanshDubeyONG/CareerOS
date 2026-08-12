from typing import List

from pydantic import BaseModel, Field


class ScoreDimension(BaseModel):
    score: float = Field(
        ge=0,
        le=100,
    )

    rationale: str


class GitHubPortfolioScore(BaseModel):
    overall_score: float = Field(
        ge=0,
        le=100,
    )

    project_quality: ScoreDimension

    portfolio_depth: ScoreDimension

    technical_breadth: ScoreDimension

    activity_consistency: ScoreDimension

    documentation: ScoreDimension

    originality_ownership: ScoreDimension

    meaningful_project_count: int

    strongest_area: str

    biggest_weakness: str

    recommendations: List[str]