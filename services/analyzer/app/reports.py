from typing import Any


def build_markdown_report(overview: dict[str, Any]) -> str:
    summary = overview.get("summary") or {}
    health = overview.get("engineering_health") or {}
    structure = overview.get("structure") or {}
    repository = overview.get("repository") or summary.get("full_name") or "Unknown repository"
    languages = summary.get("languages") or {}
    language_text = ", ".join(
        f"{name} {share:.1f}%" for name, share in sorted(languages.items(), key=lambda item: -item[1])
    ) or "Not detected"
    recommendations = health.get("recommendations") or []
    recommendation_text = "\n".join(f"- {item}" for item in recommendations) or "- No immediate recommendations."

    return (
        f"# DevLens Report: {repository}\n\n"
        f"**Engineering health:** {health.get('score', 0)}/100 ({health.get('grade', 'N/A')})\n\n"
        f"**Languages:** {language_text}\n\n"
        f"**Root structure:** {structure.get('file_count', 0)} files, "
        f"{structure.get('directory_count', 0)} directories\n\n"
        f"## Recommendations\n\n{recommendation_text}\n"
    )
