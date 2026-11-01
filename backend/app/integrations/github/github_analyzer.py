import re


class GitHubAnalyzer:

    @staticmethod
    def extract_dependencies(
        content: str,
        filename: str,
    ) -> list[str]:

        if not content:
            return []

        dependencies = set()
        filename = filename.lower()

        if filename.endswith("requirements.txt"):
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                match = re.match(r"^([A-Za-z0-9_.-]+)", line)
                if match:
                    dep = match.group(1).strip()
                    if dep and not dep.startswith((".", "/")):
                        dependencies.add(dep)

        elif filename.endswith("package.json"):
            try:
                import json
                data = json.loads(content)
                for section in ("dependencies", "devDependencies"):
                    for dependency in data.get(section, {}).keys():
                        dependencies.add(dependency)
            except Exception:
                return []

        elif filename.endswith("pyproject.toml"):
            # Target dependencies arrays e.g. dependencies = [ ... ]
            dep_blocks = re.findall(
                r"""(?:dependencies|requires)\s*=\s*\[(.*?)\]""",
                content,
                re.DOTALL,
            )
            poetry_match = re.search(
                r"""\[tool\.poetry\.dependencies\](.*?)(?:\[|\Z)""",
                content,
                re.DOTALL,
            )
            if poetry_match:
                dep_blocks.append(poetry_match.group(1))

            target_text = "\n".join(dep_blocks) if dep_blocks else ""

            matches = re.findall(
                r"""["']([A-Za-z0-9_.-]+)(?:[<>=!~^@].*)?["']""",
                target_text,
            )

            ignored = {
                "setuptools",
                "wheel",
                "build",
                "hatchling",
                "poetry",
                "python",
                "readme",
                "mit",
                "apache",
            }

            for dependency in matches:
                normalized = dependency.lower().strip()
                if (
                    not normalized
                    or re.match(r"^\d", normalized)
                    or normalized.endswith((".md", ".txt", ".rst"))
                ):
                    continue

                if normalized not in ignored and len(normalized) > 1:
                    dependencies.add(dependency)

        return sorted(dependencies)

    @staticmethod
    def analyze_repository_structure(
        file_paths: list[str],
    ) -> dict:

        source_directories = set()
        test_files = []
        config_files = []

        has_docker = False
        has_frontend = False

        for path in file_paths:
            normalized = path.lower()
            parts = path.split("/")

            # Detect meaningful source directories
            if len(parts) > 1:
                first_directory = parts[0].lower()
                if first_directory in {
                    "app",
                    "src",
                    "lib",
                    "backend",
                    "frontend",
                    "server",
                    "client",
                    "components",
                    "services",
                    "api",
                    "templates",
                    "static",
                    "ui",
                }:
                    source_directories.add(first_directory)

            # Detect tests
            if (
                "test" in normalized
                or normalized.startswith("tests/")
                or normalized.startswith("spec/")
            ):
                test_files.append(path)

            # Detect configuration files
            if normalized.endswith(
                (
                    ".env",
                    ".ini",
                    ".toml",
                    ".yaml",
                    ".yml",
                    ".json",
                    ".cfg",
                )
            ):
                config_files.append(path)

            filename = parts[-1].lower()

            # Docker
            if filename in {
                "dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml",
            } or "docker" in filename:
                has_docker = True

            # Frontend
            if (
                normalized.startswith(
                    ("frontend/", "client/", "templates/", "static/", "ui/")
                )
                or normalized.endswith((".html", ".jsx", ".tsx", ".vue"))
                or filename in {
                    "package.json",
                    "vite.config.js",
                    "vite.config.ts",
                    "webpack.config.js",
                }
            ):
                has_frontend = True

        return {
            "source_directories": sorted(source_directories),
            "test_files": test_files,
            "config_files": config_files,
            "has_docker": has_docker,
            "has_frontend": has_frontend,
            "has_tests": bool(test_files),
        }
