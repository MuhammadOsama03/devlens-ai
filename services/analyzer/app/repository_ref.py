from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class RepositoryRef:
    owner: str
    name: str


def parse_repository(value: str) -> RepositoryRef:
    candidate = value.strip()
    if "://" in candidate:
        parsed = urlparse(candidate)
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise ValueError("repository URL must use github.com")
        candidate = parsed.path.strip("/")

    parts = candidate.removesuffix(".git").split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use owner/name format")
    if any(not part.replace("-", "").replace("_", "").replace(".", "").isalnum() for part in parts):
        raise ValueError("repository contains unsupported characters")
    return RepositoryRef(owner=parts[0], name=parts[1])
