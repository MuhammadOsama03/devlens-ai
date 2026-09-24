import csv
import io
import json
from typing import Any


def export_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def export_summary_csv(overview: dict[str, Any]) -> str:
    summary = overview.get("summary") or {}
    health = overview.get("engineering_health") or {}
    row = {
        "repository": overview.get("repository", ""),
        "stars": summary.get("stars", 0),
        "forks": summary.get("forks", 0),
        "health_score": health.get("score", 0),
        "health_grade": health.get("grade", ""),
    }
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue()
