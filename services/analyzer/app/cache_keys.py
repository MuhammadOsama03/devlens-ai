from urllib.parse import quote


def analysis_cache_key(
    owner: str,
    repo: str,
    analysis: str,
    *,
    ref: str | None = None,
    version: int = 1,
) -> str:
    if version <= 0:
        raise ValueError("version must be positive")
    segments = [
        f"v{version}",
        quote(owner.lower(), safe=""),
        quote(repo.lower(), safe=""),
        quote(analysis.lower(), safe=""),
        quote(ref or "default", safe=""),
    ]
    return ":".join(segments)
