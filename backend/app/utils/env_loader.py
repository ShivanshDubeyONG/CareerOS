import os
from pathlib import Path
from dotenv import load_dotenv


def load_project_env() -> None:
    """
    Search and load .env files from backend/, project root, or current directory.
    Ensures environment variables are reliably loaded regardless of how or from where
    CareerOS is launched (root, backend/, Docker, Render, etc.).
    """
    current_file = Path(__file__).resolve()
    # current_file is backend/app/utils/env_loader.py
    backend_dir = current_file.parents[2]
    repo_root = backend_dir.parent

    env_candidates = [
        backend_dir / ".env",
        repo_root / ".env",
        Path.cwd() / ".env",
        backend_dir / ".env.local",
        repo_root / ".env.local",
    ]

    for candidate in env_candidates:
        if candidate.is_file():
            load_dotenv(dotenv_path=candidate, override=False)
