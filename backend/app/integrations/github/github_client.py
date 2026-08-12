import base64
import os
from typing import Optional

import httpx


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=20.0,
        )

    def get_user(
        self,
        username: str,
    ) -> dict:

        response = self.client.get(
            f"/users/{username}"
        )

        response.raise_for_status()

        return response.json()

    def get_repositories(
        self,
        username: str,
    ) -> list[dict]:

        repositories = []

        page = 1

        while True:

            response = self.client.get(
                f"/users/{username}/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                },
            )

            response.raise_for_status()

            data = response.json()

            if not data:
                break

            repositories.extend(data)

            if len(data) < 100:
                break

            page += 1

        return repositories

    def get_repository_languages(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        response = self.client.get(
            f"/repos/{owner}/{repo}/languages"
        )

        response.raise_for_status()

        return response.json()

    def get_repository_readme(
        self,
        owner: str,
        repo: str,
    ) -> Optional[str]:

        response = self.client.get(
            f"/repos/{owner}/{repo}/readme"
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        data = response.json()

        content = data.get("content")

        if not content:
            return None

        try:
            return base64.b64decode(
                content
            ).decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            return None

    def get_repository_file(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> Optional[str]:

        response = self.client.get(
            f"/repos/{owner}/{repo}/contents/{path}"
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        data = response.json()

        if data.get("type") != "file":
            return None

        content = data.get("content")

        if not content:
            return None

        try:
            return base64.b64decode(
                content
            ).decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            return None

    def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[str]:

        response = self.client.get(
            f"/repos/{owner}/{repo}/git/trees/{branch}",
            params={
                "recursive": "1",
            },
        )

        response.raise_for_status()

        data = response.json()

        return [
            item["path"]
            for item in data.get(
                "tree",
                [],
            )
            if item.get("type") == "blob"
        ]

    def close(self):
        self.client.close()