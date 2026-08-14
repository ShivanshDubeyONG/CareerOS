import json

import httpx

from app.schemas.leetcode_schema import (
    LeetCodeLanguage,
    LeetCodeProfile,
    LeetCodeSkill,
)


class LeetCodeClient:

    BASE_URL = "https://leetcode.com/graphql"

    def __init__(self):

        self.client = httpx.Client(
            timeout=20.0,
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com/",
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 "
                    "Safari/537.36"
                ),
            },
        )

    def get_user_profile(
        self,
        username: str,
    ) -> LeetCodeProfile:

        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {

                username

                profile {
                    realName
                    userAvatar
                    ranking
                }

                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }

                languageProblemCount {
                    languageName
                    problemsSolved
                }

                tagProblemCounts {
                    advanced {
                        tagName
                        problemsSolved
                    }

                    intermediate {
                        tagName
                        problemsSolved
                    }

                    fundamental {
                        tagName
                        problemsSolved
                    }
                }

                submissionCalendar
            }
        }
        """

        response = self.client.post(
            self.BASE_URL,
            json={
                "query": query,
                "variables": {
                    "username": username,
                },
            },
        )

        response.raise_for_status()

        data = response.json()

        if data.get("errors"):

            raise ValueError(
                f"LeetCode API error: "
                f"{data['errors']}"
            )

        matched_user = (
            data.get("data", {})
            .get("matchedUser")
        )

        if matched_user is None:

            raise ValueError(
                f"LeetCode user "
                f"'{username}' not found."
            )

        # --------------------------------
        # SOLVED / SUBMISSION STATS
        # --------------------------------

        stats = (
            matched_user
            .get("submitStats", {})
            .get("acSubmissionNum", [])
        )

        solved = {
            "All": 0,
            "Easy": 0,
            "Medium": 0,
            "Hard": 0,
        }

        submissions = {
            "All": 0,
            "Easy": 0,
            "Medium": 0,
            "Hard": 0,
        }

        for item in stats:

            difficulty = item.get(
                "difficulty"
            )

            if difficulty not in solved:
                continue

            solved[difficulty] = max(
                item.get("count", 0),
                0,
            )

            submissions[difficulty] = max(
                item.get("submissions", 0),
                0,
            )

        # --------------------------------
        # LANGUAGES
        # --------------------------------

        languages = []

        for item in matched_user.get(
            "languageProblemCount",
            [],
        ):

            languages.append(
                LeetCodeLanguage(
                    language=item.get(
                        "languageName",
                        "Unknown",
                    ),
                    problems_solved=max(
                        item.get(
                            "problemsSolved",
                            0,
                        ),
                        0,
                    ),
                )
            )

        # --------------------------------
        # SKILLS
        # --------------------------------

        skills = []

        tag_problem_counts = (
            matched_user.get(
                "tagProblemCounts",
                {},
            )
        )

        for level in [
            "advanced",
            "intermediate",
            "fundamental",
        ]:

            for item in (
                tag_problem_counts.get(
                    level,
                    [],
                )
            ):

                skills.append(
                    LeetCodeSkill(
                        skill=item.get(
                            "tagName",
                            "Unknown",
                        ),
                        problems_solved=max(
                            item.get(
                                "problemsSolved",
                                0,
                            ),
                            0,
                        ),
                        level=level,
                    )
                )

        # --------------------------------
        # SUBMISSION CALENDAR
        # --------------------------------

        submission_calendar = {}

        raw_calendar = matched_user.get(
            "submissionCalendar"
        )

        if raw_calendar:

            try:

                if isinstance(
                    raw_calendar,
                    str,
                ):

                    parsed_calendar = json.loads(
                        raw_calendar
                    )

                elif isinstance(
                    raw_calendar,
                    dict,
                ):

                    parsed_calendar = raw_calendar

                else:

                    parsed_calendar = {}

                for timestamp, count in (
                    parsed_calendar.items()
                ):

                    try:

                        submission_calendar[
                            int(timestamp)
                        ] = max(
                            int(count),
                            0,
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):

                submission_calendar = {}

        # --------------------------------
        # PROFILE
        # --------------------------------

        profile = matched_user.get(
            "profile",
            {},
        )

        return LeetCodeProfile(
            username=matched_user.get(
                "username",
                username,
            ),
            ranking=profile.get(
                "ranking"
            ),
            total_solved=solved["All"],
            easy_solved=solved["Easy"],
            medium_solved=solved["Medium"],
            hard_solved=solved["Hard"],
            total_submissions=(
                submissions["All"]
            ),
            easy_submissions=(
                submissions["Easy"]
            ),
            medium_submissions=(
                submissions["Medium"]
            ),
            hard_submissions=(
                submissions["Hard"]
            ),
            languages=languages,
            skills=skills,
            submission_calendar=(
                submission_calendar
            ),
        )

    def close(self):

        self.client.close()