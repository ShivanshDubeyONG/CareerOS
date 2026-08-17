from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source: str
    evidence_type: str
    value: str
    strength: str = "unknown"
    details: str | None = None


class SkillEvidence(BaseModel):
    skill: str

    resume_claimed: bool = False
    linkedin_claimed: bool = False

    github_demonstrated: bool = False
    leetcode_demonstrated: bool = False

    supporting_sources: list[str] = Field(
        default_factory=list
    )

    missing_supporting_sources: list[str] = Field(
        default_factory=list
    )

    status: str = "unknown"

    evidence: list[EvidenceItem] = Field(
        default_factory=list
    )


class ProjectEvidence(BaseModel):
    name: str

    resume_present: bool = False
    linkedin_present: bool = False
    github_present: bool = False

    github_repository: str | None = None

    status: str = "unknown"

    finding: str | None = None

    evidence: list[EvidenceItem] = Field(
        default_factory=list
    )


class CrossSourceFinding(BaseModel):
    finding_type: str

    subject: str

    severity: str = "info"

    message: str

    sources: list[str] = Field(
        default_factory=list
    )

    evidence: list[EvidenceItem] = Field(
        default_factory=list
    )


class UnifiedCandidateProfile(BaseModel):
    name: str | None = None

    headline: str | None = None

    location: str | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    career_domains: list[str] = Field(
        default_factory=list
    )

    current_title: str | None = None

    current_company: str | None = None

    skill_evidence: list[SkillEvidence] = Field(
        default_factory=list
    )

    project_evidence: list[ProjectEvidence] = Field(
        default_factory=list
    )

    findings: list[CrossSourceFinding] = Field(
        default_factory=list
    )

    source_status: dict[str, bool] = Field(
        default_factory=dict
    )