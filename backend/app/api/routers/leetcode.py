from fastapi import APIRouter, HTTPException

from app.integrations.leetcode.leetcode_client import (
    LeetCodeClient,
)
from app.services.leetcode.leetcode_service import (
    leetcode_service,
)


router = APIRouter(
    prefix="/leetcode",
    tags=["LeetCode"],
)


@router.get("/{username}")
def analyze_leetcode(
    username: str,
):

    client = LeetCodeClient()

    try:

        profile = client.get_user_profile(
            username
        )

        return leetcode_service.analyze(
            profile
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to analyze "
                "LeetCode profile."
            ),
        )

    finally:

        client.close()