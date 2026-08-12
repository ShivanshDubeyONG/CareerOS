from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GitHubRepository(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    url: str

    language: Optional[str] = None
    languages: Dict[str, int] = Field(
        default_factory=dict
    )

    stars: int = 0
    forks: int = 0

    topics: List[str] = Field(
        default_factory=list
    )

    is_fork: bool = False
    is_archived: bool = False

    default_branch: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    readme: Optional[str] = None

    dependencies: List[str] = Field(
        default_factory=list
    )

    dependency_files: List[str] = Field(
        default_factory=list
    )

    # Repository structure
    file_paths: List[str] = Field(
        default_factory=list
    )

    source_directories: List[str] = Field(
        default_factory=list
    )

    test_files: List[str] = Field(
        default_factory=list
    )

    config_files: List[str] = Field(
        default_factory=list
    )

    has_docker: bool = False
    has_frontend: bool = False
    has_tests: bool = False

    # Fork ownership evidence
    fork_parent: Optional[str] = None

    fork_unique_commits: int = 0

    fork_changed_files: int = 0

    fork_additions: int = 0

    fork_deletions: int = 0

    fork_contribution_available: bool = False


class GitHubProfile(BaseModel):
    username: str

    name: Optional[str] = None
    bio: Optional[str] = None

    profile_url: str

    public_repository_count: int = 0

    followers: int = 0
    following: int = 0

    repositories: List[GitHubRepository] = Field(
        default_factory=list
    )