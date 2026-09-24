from collections import Counter
from datetime import datetime
from typing import Any


def summarize_daily_commits(commits: list[dict[str, Any]]) -> list[dict[str, int | str]]:
    counts: Counter[str] = Counter()
    for item in commits:
        date = ((item.get("commit") or {}).get("author") or {}).get("date")
        if not isinstance(date, str):
            continue
        try:
            day = datetime.fromisoformat(date.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            continue
        counts[day] += 1
    return [{"date": day, "commits": counts[day]} for day in sorted(counts)]
