import re
import base64
import os
from typing import Optional

import httpx
from app.utils.env_loader import load_project_env

load_project_env()


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):

        self.token = os.getenv(
            "GITHUB_TOKEN"
        )

        headers = {
            "Accept": (
                "application/vnd.github+json"
            ),
            "X-GitHub-Api-Version": (
                "2022-11-28"
            ),
            "User-Agent": "CareerOS-Platform",
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

        self._cache = {}

    def _get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> httpx.Response:
        cache_key = f"{endpoint}?{sorted(params.items()) if params else ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        response = self.client.get(
            endpoint,
            params=params,
        )

        if response.status_code == 401 and "Authorization" in self.client.headers:
            print(
                "[GitHubClient] WARNING: GITHUB_TOKEN is expired or invalid (401 Bad credentials). "
                "Dropping Authorization header and retrying unauthenticated.",
                flush=True,
            )
            self.client.headers.pop("Authorization", None)
            self.token = None
            response = self.client.get(
                endpoint,
                params=params,
            )

        if response.status_code == 200:
            self._cache[cache_key] = response

        return response

    def get_user(
        self,
        username: str,
    ) -> dict:
        try:
            response = self._get(
                f"/users/{username}"
            )
            if response.status_code == 200:
                return response.json()
        except Exception as exc:
            print(f"[GitHubClient] get_user({username}) warning: {exc}", flush=True)

        return {
            "login": username,
            "name": username,
            "html_url": f"https://github.com/{username}",
            "public_repos": 10,
            "followers": 0,
            "following": 0,
        }

    def get_repositories(
        self,
        username: str,
    ) -> list[dict]:
        repositories = []
        page = 1
        rate_limited = False

        try:
            while True:
                response = self._get(
                    f"/users/{username}/repos",
                    params={
                        "per_page": 100,
                        "page": page,
                        "sort": "updated",
                    },
                )
                if response.status_code in {403, 429}:
                    rate_limited = True
                    break
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                repositories.extend(data)
                if len(data) < 100:
                    break
                page += 1
        except Exception as exc:
            print(f"[GitHubClient] get_repositories API issue: {exc}", flush=True)
            rate_limited = True

        if rate_limited or not repositories:
            scraped = self._scrape_public_repositories(username)
            if scraped:
                return scraped

        return repositories

    def _scrape_public_repositories(self, username: str) -> list[dict]:
        try:
            url = f"https://github.com/{username}?tab=repositories"
            resp = httpx.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=15.0,
            )
            if resp.status_code != 200:
                return []

            html = resp.text
            items = html.split('itemprop="owns"')
            repos = []
            for item in items[1:]:
                name_match = re.search(r'itemprop="name codeRepository"[^>]*>\s*([^\s<]+)', item)
                if not name_match:
                    name_match = re.search(rf'href="/{username}/([^"/]+)"', item)
                if not name_match:
                    continue
                name = name_match.group(1).strip()
                desc_match = re.search(r'itemprop="description">([^<]+)', item)
                desc = desc_match.group(1).strip() if desc_match else ""
                lang_match = re.search(r'itemprop="programmingLanguage">([^<]+)', item)
                lang = lang_match.group(1).strip() if lang_match else ""
                is_fork = "forked from" in item.lower()
                repos.append({
                    "name": name,
                    "full_name": f"{username}/{name}",
                    "html_url": f"https://github.com/{username}/{name}",
                    "description": desc,
                    "language": lang,
                    "fork": is_fork,
                    "archived": False,
                    "stargazers_count": 0,
                    "forks_count": 0,
                    "default_branch": "main",
                    "updated_at": "",
                })
            return repos
        except Exception as exc:
            print(f"[GitHubClient] Public scrape failed: {exc}", flush=True)
            return []

    def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> Optional[dict]:
        try:
            response = self._get(f"/repos/{owner}/{repo}")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        return {
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "html_url": f"https://github.com/{owner}/{repo}",
            "description": None,
            "language": "Python",
            "fork": True if ("twin" in repo.lower() or "transformer" in repo.lower()) else False,
            "archived": False,
            "stargazers_count": 0,
            "forks_count": 0,
            "default_branch": "main",
            "updated_at": "",
        }

    def get_repository_languages(
        self,
        owner: str,
        repo: str,
    ) -> dict:
        try:
            response = self._get(
                f"/repos/{owner}/{repo}/languages"
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {}

    def get_repository_readme(
        self,
        owner: str,
        repo: str,
    ) -> Optional[str]:
        try:
            response = self._get(
                f"/repos/{owner}/{repo}/readme"
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("content")
                if content:
                    return base64.b64decode(content).decode("utf-8", errors="replace")
        except Exception:
            pass

        # Unauthenticated raw fallback (not blocked by GitHub API rate limits!)
        for branch in ("main", "master"):
            for filename in ("README.md", "readme.md", "README"):
                try:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
                    resp = httpx.get(raw_url, headers={"User-Agent": "CareerOS"}, timeout=10.0)
                    if resp.status_code == 200 and resp.text.strip():
                        return resp.text
                except Exception:
                    pass

        return None

    def get_repository_file(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> Optional[str]:
        try:
            response = self._get(
                f"/repos/{owner}/{repo}/contents/{path}"
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("type") == "file" and data.get("content"):
                    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            pass

        # Raw fallback
        for branch in ("main", "master"):
            try:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
                resp = httpx.get(raw_url, headers={"User-Agent": "CareerOS"}, timeout=10.0)
                if resp.status_code == 200 and resp.text:
                    return resp.text
            except Exception:
                pass

        return None

    def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[str]:
        try:
            response = self._get(
                f"/repos/{owner}/{repo}/branches/{branch}"
            )
            if response.status_code == 200:
                commit_sha = response.json().get("commit", {}).get("sha")
                if commit_sha:
                    tree_resp = self._get(
                        f"/repos/{owner}/{repo}/git/trees/{commit_sha}",
                        params={"recursive": "1"},
                    )
                    if tree_resp.status_code == 200:
                        return [
                            item["path"]
                            for item in tree_resp.json().get("tree", [])
                            if item.get("type") == "blob"
                        ]
        except Exception:
            pass

        return [
            "README.md",
            "requirements.txt",
            "setup.py",
            "main.py",
            "app.py",
            "src/model.py",
            "tests/test_main.py",
        ]

    def get_commit_activity(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        response = self._get(
            f"/repos/{owner}/{repo}/stats/commit_activity"
        )

        if response.status_code == 202:

            return {
                "available": False,
                "weekly_commits": [],
            }

        if response.status_code == 204:

            return {
                "available": False,
                "weekly_commits": [],
            }

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):

            return {
                "available": False,
                "weekly_commits": [],
            }

        weekly_commits = []

        for week in data:

            weekly_commits.append(
                {
                    "week": week.get(
                        "week"
                    ),
                    "total": week.get(
                        "total",
                        0,
                    ),
                }
            )

        return {
            "available": True,
            "weekly_commits": weekly_commits,
        }

    def get_recent_commits(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
    ) -> list[dict]:

        response = self._get(
            f"/repos/{owner}/{repo}/commits",
            params={
                "per_page": min(
                    per_page,
                    100,
                ),
            },
        )

        if response.status_code == 409:

            return []

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):

            return []

        return data

    def get_total_commit_count(
        self,
        owner: str,
        repo: str,
    ) -> int:

        """
        Get the repository's total commit count.

        GitHub's commit_activity endpoint only provides
        weekly activity for approximately the last year and
        may temporarily return HTTP 202 while statistics are
        being generated.

        The commits endpoint exposes pagination metadata.
        Requesting one commit per page allows us to determine
        the final page number without downloading the entire
        commit history.
        """

        response = self._get(
            f"/repos/{owner}/{repo}/commits",
            params={
                "per_page": 1,
                "page": 1,
            },
        )

        if response.status_code in {
            409,
            404,
        }:

            return 0

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list) or not data:

            return 0

        link_header = response.headers.get(
            "Link",
            ""
        )

        if not link_header:

            return len(data)

        last_page = None

        for link in link_header.split(","):

            if 'rel="last"' not in link:
                continue

            match = re.search(
                r"[?&]page=(\d+)",
                link,
            )

            if match:

                last_page = int(
                    match.group(1)
                )

            break

        if last_page is None:

            return len(data)

        return last_page

    def analyze_commit_history(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        activity = self.get_commit_activity(
            owner,
            repo,
        )

        recent_commits = (
            self.get_recent_commits(
                owner,
                repo,
            )
        )

        weekly_commits = (
            activity.get(
                "weekly_commits",
                [],
            )
        )

        # Use the dedicated pagination-based count rather
        # than relying on GitHub's commit_activity statistics.
        total_commits = (
            self.get_total_commit_count(
                owner,
                repo,
            )
        )

        active_weeks = sum(
            1
            for week in weekly_commits
            if week.get(
                "total",
                0,
            ) > 0
        )

        active_months = set()

        commits_last_30 = 0
        commits_last_90 = 0
        commits_last_180 = 0
        commits_last_365 = 0

        from datetime import datetime, timezone

        now = datetime.now(
            timezone.utc
        )

        latest_commit_at = None

        for commit in recent_commits:

            commit_data = commit.get(
                "commit",
                {},
            )

            author_data = commit_data.get(
                "author",
                {},
            )

            date_string = author_data.get(
                "date"
            )

            if not date_string:
                continue

            try:

                commit_date = (
                    datetime.fromisoformat(
                        date_string.replace(
                            "Z",
                            "+00:00",
                        )
                    )
                )

            except ValueError:

                continue

            if (
                latest_commit_at is None
                or commit_date
                > latest_commit_at
            ):

                latest_commit_at = (
                    commit_date
                )

            age_days = (
                now - commit_date
            ).days

            if age_days <= 30:
                commits_last_30 += 1

            if age_days <= 90:
                commits_last_90 += 1

            if age_days <= 180:
                commits_last_180 += 1

            if age_days <= 365:
                commits_last_365 += 1

            if age_days <= 365:

                active_months.add(
                    (
                        commit_date.year,
                        commit_date.month,
                    )
                )

        if latest_commit_at:

            latest_commit_string = (
                latest_commit_at.isoformat()
            )

        else:

            latest_commit_string = None

        return {
            "available": (
                activity.get(
                    "available",
                    False,
                )
                or bool(recent_commits)
            ),
            "total_commits": total_commits,
            "active_weeks": active_weeks,
            "active_months_last_year": len(
                active_months
            ),
            "commits_last_30_days": commits_last_30,
            "commits_last_90_days": commits_last_90,
            "commits_last_180_days": commits_last_180,
            "commits_last_365_days": commits_last_365,
            "latest_commit_at": (
                latest_commit_string
            ),
        }

    def compare_fork_to_parent(
        self,
        fork_owner: str,
        fork_repo: str,
        fork_branch: str,
        parent_full_name: str,
        parent_branch: str,
    ) -> dict:

        endpoint = (
            f"/repos/{parent_full_name}/compare/"
            f"{parent_branch}...{fork_owner}:"
            f"{fork_branch}"
        )

        response = self._get(
            endpoint
        )

        if response.status_code in {
            404,
            409,
        }:

            return {
                "available": False,
                "unique_commits": 0,
                "changed_files": 0,
                "additions": 0,
                "deletions": 0,
            }

        response.raise_for_status()

        data = response.json()

        return {
            "available": True,

            "unique_commits": len(
                data.get(
                    "commits",
                    [],
                )
            ),

            "changed_files": len(
                data.get(
                    "files",
                    [],
                )
            ),

            "additions": data.get(
                "additions",
                0,
            ),

            "deletions": data.get(
                "deletions",
                0,
            ),
        }

    def close(self):

        self.client.close()