from pathlib import Path
from typing import Any


def assess_readiness(database_path: str, cache_stats: dict[str, int]) -> dict[str, Any]:
    parent = Path(database_path).expanduser().resolve().parent
    database_ready = parent.exists() and parent.is_dir()
    capacity = int(cache_stats.get("capacity", 0))
    entries = int(cache_stats.get("entries", 0))
    cache_ready = capacity > 0 and 0 <= entries <= capacity
    checks = {"database": database_ready, "cache": cache_ready}
    return {"ready": all(checks.values()), "checks": checks}
