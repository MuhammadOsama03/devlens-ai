import base64
from typing import Any
from urllib.parse import quote, urlencode

import httpx

from .config import settings
from .errors import PublicError, map_upstream_status


class GitHubRepositoryError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

    @property
    def public_error(self) -> PublicError:
        if self.status_code is None:
            return PublicError(
                "github_unavailable",
                "GitHub is temporarily unavailable.",
                True,
            )
        return map_upstream_status(self.status_code)


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
        raise GitHubRepositoryError(
            "Repository not found or not accessible",
            status_code=response.status_code,
        )
    if response.status_code >= 400:
        raise GitHubRepositoryError(
            f"GitHub API returned {response.status_code}: {response.reason_phrase}",
            status_code=response.status_code,
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


async def get_recent_commits(
    owner: str,
    repo: str,
    *,
    ref: str | None = None,
    limit: int = 30,
) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {"per_page": limit}
    if ref:
        params["sha"] = ref
    query = urlencode(params)
    result = await _get(f"repos/{owner}/{repo}/commits?{query}")
    if not isinstance(result, list):
        raise GitHubRepositoryError("GitHub returned an invalid commit list")
    return result


async def get_text_file(
    owner: str,
    repo: str,
    path: str,
    *,
    ref: str,
) -> str:
    encoded_path = quote(path.strip("/"), safe="/")
    if not encoded_path:
        raise ValueError("path cannot be empty")
    query = urlencode({"ref": ref})
    result = await _get(f"repos/{owner}/{repo}/contents/{encoded_path}?{query}")
    if not isinstance(result, dict) or result.get("type") != "file":
        raise GitHubRepositoryError("GitHub did not return a file")
    if int(result.get("size", 0)) > settings.max_context_file_bytes:
        raise GitHubRepositoryError("Repository file exceeds the context size limit")
    if result.get("encoding") != "base64" or not isinstance(result.get("content"), str):
        raise GitHubRepositoryError("Repository file content is unavailable")
    try:
        encoded_content = "".join(result["content"].split())
        decoded = base64.b64decode(encoded_content, validate=True)
        return decoded.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise GitHubRepositoryError("Repository file is not valid UTF-8 text") from exc
