from urllib.parse import quote


GRADE_COLORS = {"A": "2ea44f", "B": "76b900", "C": "dfb317", "D": "fe7d37", "F": "e05d44"}


def build_health_badge(score: int, grade: str) -> dict[str, str]:
    bounded_score = max(0, min(int(score), 100))
    normalized_grade = grade.upper() if grade.upper() in GRADE_COLORS else "F"
    message = f"{bounded_score}/100 {normalized_grade}"
    url = (
        "https://img.shields.io/badge/"
        f"DevLens%20health-{quote(message)}-{GRADE_COLORS[normalized_grade]}"
    )
    return {"label": "DevLens health", "message": message, "color": GRADE_COLORS[normalized_grade], "url": url}
