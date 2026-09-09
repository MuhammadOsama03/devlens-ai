from fastapi import FastAPI, HTTPException, Path

from .analysis import analyze_root
from .github_client import (
    GitHubRepositoryError,
    get_languages,
    get_repository,
    get_root_contents,
)


app = FastAPI(
    title="DevLens Analyzer API",
    version="0.1.0",
    description="Repository intelligence service for DevLens AI.",
)


repo_segment = Path(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "devlens-analyzer", "version": app.version}


@app.get("/repositories/{owner}/{repo}/summary")
async def repository_summary(
    owner: str = repo_segment,
    repo: str = repo_segment,
) -> dict:
    try:
        repository = await get_repository(owner, repo)
        languages = await get_languages(owner, repo)
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    total_bytes = sum(languages.values())
    language_share = {
        language: round((byte_count / total_bytes) * 100, 2)
        for language, byte_count in languages.items()
    } if total_bytes else {}

    return {
        "full_name": repository.get("full_name"),
        "description": repository.get("description"),
        "default_branch": repository.get("default_branch"),
        "visibility": repository.get("visibility"),
        "stars": repository.get("stargazers_count", 0),
        "forks": repository.get("forks_count", 0),
        "open_issues": repository.get("open_issues_count", 0),
        "size_kb": repository.get("size", 0),
        "languages": language_share,
        "updated_at": repository.get("updated_at"),
    }


@app.get("/repositories/{owner}/{repo}/structure")
async def repository_structure(
    owner: str = repo_segment,
    repo: str = repo_segment,
) -> dict:
    try:
        entries = await get_root_contents(owner, repo)
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"repository": f"{owner}/{repo}", **analyze_root(entries)}
