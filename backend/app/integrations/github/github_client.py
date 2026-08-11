import httpx


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10.0,
        )

    def get_user(self, username: str):
        response = self.client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()

    def get_repositories(self, username: str):
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
            page += 1

        return repositories

    def get_repository_languages(
        self,
        owner: str,
        repo: str,
    ):
        response = self.client.get(
            f"/repos/{owner}/{repo}/languages"
        )

        response.raise_for_status()
        return response.json()

    def get_repository_readme(
        self,
        owner: str,
        repo: str,
    ):
        response = self.client.get(
            f"/repos/{owner}/{repo}/readme",
            headers={
                "Accept": "application/vnd.github.raw+json"
            },
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.text

    def get_repository_file(
        self,
        owner: str,
        repo: str,
        path: str,
    ):
        response = self.client.get(
            f"/repos/{owner}/{repo}/contents/{path}",
            headers={
                "Accept": "application/vnd.github.raw+json"
            },
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.text

    def close(self):
        self.client.close()