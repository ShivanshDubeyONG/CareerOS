from pydantic import BaseModel


class LeetCodeLanguage(BaseModel):
    language: str
    problems_solved: int


class LeetCodeSkill(BaseModel):
    skill: str
    problems_solved: int
    level: str


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

    languages: list[LeetCodeLanguage] = []
    skills: list[LeetCodeSkill] = []


class LeetCodeAnalysis(BaseModel):
    username: str
    total_solved: int

    difficulty_distribution: dict[str, float]

    medium_hard_ratio: float
    difficulty_level: str

    strongest_skills: list[str]
    languages: list[str]

    signals: list[str]