import os

import requests
from dotenv import load_dotenv


load_dotenv()


class LinkedInAcquisitionError(Exception):
    pass


class LinkedInClient:
    """
    Acquisition boundary for LinkedIn profiles.

    Responsibility:

        LinkedIn URL
            ↓
        Bright Data
            ↓
        raw LinkedIn profile dictionary

    This class does NOT:
        - create LinkedInProfile objects
        - normalize skills
        - calculate scores
        - perform cross-source reasoning
    """

    BASE_URL = (
        "https://api.brightdata.com"
        "/datasets/v3/scrape"
    )

    DATASET_ID = (
        "gd_l1viktl72bvl7bjuj0"
    )

    def __init__(
        self,
        api_key: str | None = None,
    ):

        self.api_key = (
            api_key
            or os.getenv(
                "BRIGHTDATA_API_KEY"
            )
        )

    @staticmethod
    def validate_profile_url(
        linkedin_url: str,
    ) -> str:

        if not linkedin_url:
            raise ValueError(
                "LinkedIn URL cannot be empty."
            )

        url = linkedin_url.strip()

        if "linkedin.com/in/" not in url:
            raise ValueError(
                "Invalid LinkedIn profile URL."
            )

        return url

    def fetch_profile(
        self,
        linkedin_url: str,
    ) -> dict:

        if not self.api_key:

            raise LinkedInAcquisitionError(
                "BRIGHTDATA_API_KEY is not configured."
            )

        profile_url = (
            self.validate_profile_url(
                linkedin_url
            )
        )

        params = {
            "dataset_id": self.DATASET_ID,
            "format": "json",
        }

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        payload = [
            {
                "url": profile_url,
            }
        ]

        try:

            response = requests.post(
                self.BASE_URL,
                params=params,
                headers=headers,
                json=payload,
                timeout=120,
            )

        except requests.RequestException as exc:

            raise LinkedInAcquisitionError(
                "Could not reach the Bright Data "
                "LinkedIn acquisition provider."
            ) from exc

        if response.status_code != 200:

            raise LinkedInAcquisitionError(
                "Bright Data LinkedIn profile "
                "acquisition failed with HTTP "
                f"{response.status_code}: "
                f"{response.text[:500]}"
            )

        try:

            data = response.json()

        except ValueError as exc:

            raise LinkedInAcquisitionError(
                "Bright Data returned invalid JSON."
            ) from exc

        if isinstance(data, list):

            if not data:

                raise LinkedInAcquisitionError(
                    "Bright Data returned an "
                    "empty LinkedIn profile."
                )

            profile = data[0]

        elif isinstance(data, dict):

            if "snapshot_id" in data:

                raise LinkedInAcquisitionError(
                    "Bright Data returned an asynchronous "
                    "snapshot instead of completed "
                    "profile data."
                )

            profile = data

        else:

            raise LinkedInAcquisitionError(
                "Bright Data returned an unexpected "
                "response type."
            )

        if not isinstance(profile, dict):

            raise LinkedInAcquisitionError(
                "Bright Data returned an invalid "
                "LinkedIn profile object."
            )

        return profile


linkedin_client = LinkedInClient()