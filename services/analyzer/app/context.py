from pathlib import PurePosixPath


DEFAULT_CONTEXT_EXTENSIONS = {
    ".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".toml", ".yaml", ".yml"
}
EXCLUDED_PARTS = {".git", "node_modules", "dist", "build", ".venv", "vendor"}


def select_context_paths(paths: list[str], limit: int = 100) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    selected = []
    for raw_path in sorted(set(paths)):
        path = PurePosixPath(raw_path)
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in DEFAULT_CONTEXT_EXTENSIONS:
            continue
        selected.append(str(path))
        if len(selected) == limit:
            break
    return selected
