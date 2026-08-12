import re


class GitHubAnalyzer:

    @staticmethod
    def extract_dependencies(
        dependency_files: dict[str, str],
    ) -> list[str]:

        dependencies = set()

        for filename, content in dependency_files.items():

            if not content:
                continue

            # requirements.txt
            if filename == "requirements.txt":

                for line in content.splitlines():

                    line = line.strip()

                    if (
                        not line
                        or line.startswith("#")
                    ):
                        continue

                    match = re.match(
                        r"^([A-Za-z0-9_.-]+)",
                        line,
                    )

                    if match:
                        dependencies.add(
                            match.group(1)
                        )

            # package.json
            elif filename == "package.json":

                try:
                    import json

                    data = json.loads(content)

                    for section in [
                        "dependencies",
                        "devDependencies",
                    ]:

                        for dependency in data.get(
                            section,
                            {},
                        ).keys():

                            dependencies.add(
                                dependency
                            )

                except Exception:
                    continue

            # pyproject.toml
            elif filename == "pyproject.toml":

                # Lightweight extraction of common
                # dependency declarations.
                matches = re.findall(
                    r"""["']([A-Za-z0-9_.-]+)(?:[<>=!~^].*)?["']""",
                    content,
                )

                for dependency in matches:
                    dependencies.add(
                        dependency
                    )

        return sorted(
            dependencies
        )

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

                first_directory = parts[0]

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
                }:

                    source_directories.add(
                        first_directory
                    )

            # Detect tests
            if (
                "test" in normalized
                or normalized.startswith(
                    "tests/"
                )
            ):

                test_files.append(
                    path
                )

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

                config_files.append(
                    path
                )

            filename = parts[-1].lower()

            # Docker
            if filename in {
                "dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml",
            }:

                has_docker = True

            # Frontend
            if (
                normalized.startswith(
                    "frontend/"
                )
                or normalized.startswith(
                    "client/"
                )
                or filename in {
                    "package.json",
                    "vite.config.js",
                    "vite.config.ts",
                }
            ):

                has_frontend = True

        return {
            "source_directories": sorted(
                source_directories
            ),
            "test_files": test_files,
            "config_files": config_files,
            "has_docker": has_docker,
            "has_frontend": has_frontend,
            "has_tests": bool(
                test_files
            ),
        }