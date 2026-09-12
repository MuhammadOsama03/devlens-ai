from typing import Any
from urllib.parse import quote

import httpx

from .config import settings


class GitHubRepositoryError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "devlens-ai",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


async def _get(path: str) -> Any:
    url = f"{settings.github_api_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, headers=_headers())
    except httpx.HTTPError as exc:
        raise GitHubRepositoryError("GitHub API request failed") from exc

    if response.status_code == 404:
        raise GitHubRepositoryError("Repository not found or not accessible")
    if response.status_code >= 400:
        raise GitHubRepositoryError(
            f"GitHub API returned {response.status_code}: {response.reason_phrase}"
        )
    return response.json()


async def get_repository(owner: str, repo: str) -> dict[str, Any]:
    return await _get(f"repos/{owner}/{repo}")


async def get_languages(owner: str, repo: str) -> dict[str, int]:
    return await _get(f"repos/{owner}/{repo}/languages")


async def get_root_contents(owner: str, repo: str) -> list[dict[str, Any]]:
    result = await _get(f"repos/{owner}/{repo}/contents")
    if not isinstance(result, list):
        raise GitHubRepositoryError("Repository root is not a directory")
    return result


async def get_repository_paths(
    owner: str,
    repo: str,
    ref: str,
) -> tuple[list[str], bool]:
    encoded_ref = quote(ref, safe="")
    result = await _get(f"repos/{owner}/{repo}/git/trees/{encoded_ref}?recursive=1")
    tree = result.get("tree")
    if not isinstance(tree, list):
        raise GitHubRepositoryError("GitHub returned an invalid repository tree")

    paths = [
        item["path"]
        for item in tree
        if item.get("type") == "blob" and isinstance(item.get("path"), str)
    ]
    return paths, bool(result.get("truncated", False))
