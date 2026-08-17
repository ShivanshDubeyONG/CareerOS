import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


load_dotenv()


class LinkedInAcquisitionError(Exception):
    """Raised when LinkedIn profile acquisition fails."""


class LinkedInClient:
    """
    Acquisition boundary for LinkedIn profiles.

    Responsibility:

        LinkedIn URL
            ↓
        ScrapingDog
            ↓
        normalized raw profile dictionary

    This class does NOT:
        - create LinkedInProfile objects
        - normalize skills
        - calculate scores
        - perform cross-source reasoning
    """

    BASE_URL = "https://api.scrapingdog.com/profile/"

    def __init__(self, api_key: str | None = None):
        self.api_key = (
            api_key
            or os.getenv("SCRAPINGDOG_API_KEY")
        )

    @staticmethod
    def extract_profile_id(
        linkedin_url: str,
    ) -> str:
        if not linkedin_url:
            raise ValueError(
                "LinkedIn URL cannot be empty."
            )

        parsed = urlparse(
            linkedin_url.strip()
        )

        hostname = (
            parsed.hostname or ""
        ).lower()

        if hostname not in {
            "linkedin.com",
            "www.linkedin.com",
        }:
            raise ValueError(
                "Invalid LinkedIn URL. "
                "Expected a linkedin.com URL."
            )

        parts = [
            part.strip()
            for part in parsed.path.split("/")
            if part.strip()
        ]

        if (
            len(parts) != 2
            or parts[0].lower() != "in"
        ):
            raise ValueError(
                "Invalid LinkedIn profile URL. "
                "Expected format: "
                "https://www.linkedin.com/in/<profile>/"
            )

        return parts[1]

    def fetch_profile(
        self,
        linkedin_url: str,
    ) -> dict:
        if not self.api_key:
            raise LinkedInAcquisitionError(
                "SCRAPINGDOG_API_KEY is not configured."
            )

        profile_id = self.extract_profile_id(
            linkedin_url
        )

        params = {
            "api_key": self.api_key,
            "type": "profile",
            "id": profile_id,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=60,
            )
        except requests.RequestException as exc:
            raise LinkedInAcquisitionError(
                "Could not reach the LinkedIn "
                "acquisition provider."
            ) from exc

        if response.status_code != 200:
            raise LinkedInAcquisitionError(
                "LinkedIn profile acquisition failed "
                f"with HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise LinkedInAcquisitionError(
                "LinkedIn acquisition provider "
                "returned invalid JSON."
            ) from exc

        if isinstance(data, list):

            if not data:
                raise LinkedInAcquisitionError(
                    "LinkedIn acquisition returned "
                    "an empty profile response."
                )

            profile = data[0]

        elif isinstance(data, dict):

            profile = data

        else:
            raise LinkedInAcquisitionError(
                "LinkedIn acquisition provider "
                "returned an unexpected response type."
            )

        if not isinstance(profile, dict):
            raise LinkedInAcquisitionError(
                "LinkedIn acquisition provider "
                "returned an invalid profile object."
            )

        return profile


linkedin_client = LinkedInClient()