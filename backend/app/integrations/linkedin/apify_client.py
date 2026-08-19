import os

import requests
from dotenv import load_dotenv


load_dotenv()


class ApifyLinkedInAcquisitionError(Exception):
    pass


class ApifyLinkedInClient:
    """
    LinkedIn acquisition adapter using the
    API Maestro Full Sections LinkedIn scraper.

    Provider:
        apimaestro/linkedin-profile-full-sections-scraper

    This layer ONLY acquires raw LinkedIn data.

    It does not:
        - normalize data
        - create LinkedInProfile
        - score the profile
        - call Gemini
        - perform cross-source reasoning
    """

    BASE_URL = (
        "https://api.apify.com/v2/acts/"
        "apimaestro~linkedin-profile-full-sections-scraper/"
        "run-sync-get-dataset-items"
    )

    def __init__(
        self,
        api_token: str | None = None,
    ):
        self.api_token = (
            api_token
            or os.getenv("APIFY_API_TOKEN")
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

        return url.rstrip("/")

    @staticmethod
    def extract_username(
        linkedin_url: str,
    ) -> str:

        url = (
            linkedin_url
            .strip()
            .rstrip("/")
        )

        username = (
            url.split("/in/")[-1]
            .split("?")[0]
            .strip("/")
        )

        if not username:
            raise ValueError(
                "Could not extract LinkedIn username."
            )

        return username

    def fetch_profile(
        self,
        linkedin_url: str,
    ) -> dict:

        if not self.api_token:
            raise ApifyLinkedInAcquisitionError(
                "APIFY_API_TOKEN is not configured."
            )

        profile_url = (
            self.validate_profile_url(
                linkedin_url
            )
        )

        username = (
            self.extract_username(
                profile_url
            )
        )

        payload = {
            "usernames": [
                username
            ]
        }

        try:
            response = requests.post(
                self.BASE_URL,
                params={
                    "token": self.api_token
                },
                headers={
                    "Content-Type": (
                        "application/json"
                    ),
                    "Accept": (
                        "application/json"
                    ),
                },
                json=payload,
                timeout=300,
            )

        except requests.RequestException as exc:
            raise ApifyLinkedInAcquisitionError(
                "Could not reach the Apify "
                "LinkedIn acquisition provider."
            ) from exc

        if response.status_code not in (
            200,
            201,
        ):
            raise ApifyLinkedInAcquisitionError(
                "Apify LinkedIn acquisition failed "
                f"with HTTP "
                f"{response.status_code}: "
                f"{response.text[:1000]}"
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise ApifyLinkedInAcquisitionError(
                "Apify returned invalid JSON."
            ) from exc

        if not isinstance(data, list):
            raise ApifyLinkedInAcquisitionError(
                "Apify returned an unexpected "
                f"response type: "
                f"{type(data).__name__}"
            )

        if not data:
            raise ApifyLinkedInAcquisitionError(
                "Apify returned no LinkedIn "
                "profile data."
            )

        profile = data[0]

        if not isinstance(profile, dict):
            raise ApifyLinkedInAcquisitionError(
                "Apify returned an invalid "
                "profile object."
            )

        return profile


apify_linkedin_client = ApifyLinkedInClient()