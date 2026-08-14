from pydantic import BaseModel, Field


class LeetCodeLanguage(BaseModel):
    language: str
    problems_solved: int = 0


class LeetCodeSkill(BaseModel):
    skill: str
    problems_solved: int = 0
    level: str = ""


class LeetCodeProfile(BaseModel):
    username: str
    ranking: int | None = None

    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0

    total_submissions: int = 0
    easy_submissions: int = 0
    medium_submissions: int = 0
    hard_submissions: int = 0

    languages: list[LeetCodeLanguage] = Field(
        default_factory=list
    )

    skills: list[LeetCodeSkill] = Field(
        default_factory=list
    )

    submission_calendar: dict[int, int] = Field(
        default_factory=dict
    )


class LeetCodeAnalysis(BaseModel):
    username: str

    total_solved: int

    difficulty_distribution: dict[str, float]

    medium_hard_ratio: float

    difficulty_exposure: str

    strongest_skills: list[str]

    languages: list[str]

    dsa_coverage: dict[str, dict]

    strong_areas: list[str]

    developing_areas: list[str]

    evidence_gaps: list[str]

    dsa_breadth_score: float

    problem_solving_score: float

    active_days: int

    active_days_30d: int

    active_days_90d: int

    active_months: int

    latest_activity: str | None

    recent_activity_ratio: float

    activity_consistency: str

    signals: list[str]