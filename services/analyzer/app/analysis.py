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

HEALTH_WEIGHTS = {
    "documentation": 25,
    "license": 15,
    "github_automation": 20,
    "tests": 25,
    "containerization": 15,
}

HEALTH_RECOMMENDATIONS = {
    "documentation": "Add a README with setup, usage, and contribution guidance.",
    "license": "Add a license so reuse terms are explicit.",
    "github_automation": "Add a GitHub Actions workflow for automated checks.",
    "tests": "Add automated tests for the repository's core behavior.",
    "containerization": "Add a Dockerfile for reproducible runtime environments.",
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


def calculate_health(quality_signals: list[str]) -> dict[str, Any]:
    detected = set(quality_signals)
    score = sum(
        weight for signal, weight in HEALTH_WEIGHTS.items() if signal in detected
    )
    recommendations = [
        recommendation
        for signal, recommendation in HEALTH_RECOMMENDATIONS.items()
        if signal not in detected
    ]

    if score >= 80:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 40:
        grade = "C"
    elif score >= 20:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "recommendations": recommendations,
    }
