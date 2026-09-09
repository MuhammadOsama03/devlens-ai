from typing import Any


FRAMEWORK_SIGNALS = {
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "next.config.ts": "Next.js",
    "vite.config.js": "Vite",
    "vite.config.ts": "Vite",
    "manage.py": "Django",
    "pyproject.toml": "Python project",
    "requirements.txt": "Python project",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "compose.yml": "Docker Compose",
}

QUALITY_SIGNALS = {
    "README.md": "documentation",
    "LICENSE": "license",
    ".github": "github_automation",
    "tests": "tests",
    "test": "tests",
    "Dockerfile": "containerization",
}


def analyze_root(entries: list[dict[str, Any]]) -> dict[str, Any]:
    names = {entry.get("name", "") for entry in entries}
    directories = sorted(
        entry["name"] for entry in entries if entry.get("type") == "dir" and entry.get("name")
    )
    files = sorted(
        entry["name"] for entry in entries if entry.get("type") == "file" and entry.get("name")
    )

    frameworks = sorted(
        {label for filename, label in FRAMEWORK_SIGNALS.items() if filename in names}
    )
    quality = sorted(
        {label for filename, label in QUALITY_SIGNALS.items() if filename in names}
    )

    return {
        "file_count": len(files),
        "directory_count": len(directories),
        "files": files,
        "directories": directories,
        "framework_signals": frameworks,
        "quality_signals": quality,
    }
