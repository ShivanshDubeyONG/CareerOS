import json
import re
from pathlib import Path


class SkillExtractor:

    def __init__(self):

        skills_path = (
            Path(__file__).parent.parent
            / "data"
            / "skills.json"
        )

        with open(skills_path, "r", encoding="utf-8") as f:
            self.skills = json.load(f)

    def extract(self, text: str):

        found = []

        for skill in self.skills:

            pattern = (
                r"(?<![A-Za-z0-9+#.-])"
                + re.escape(skill)
                + r"(?![A-Za-z0-9+#.-])"
            )

            if re.search(pattern, text, re.IGNORECASE):
                found.append(skill)

        return sorted(set(found))


skill_extractor = SkillExtractor()