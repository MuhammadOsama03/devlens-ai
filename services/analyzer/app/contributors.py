from collections import Counter
from typing import Any


def summarize_contributors(commits: list[dict[str, Any]], limit: int = 10) -> list[dict[str, int | str]]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    counts: Counter[str] = Counter()
    for item in commits:
        author = item.get("author") or {}
        commit_author = (item.get("commit") or {}).get("author") or {}
        identity = author.get("login") or commit_author.get("name") or "Unknown"
        counts[str(identity)] += 1
    return [
        {"author": author, "commits": count}
        for author, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))[:limit]
    ]
