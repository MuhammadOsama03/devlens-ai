import asyncio
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

from .analysis import (\n    analyze_paths,\n    analyze_root,\n    calculate_health,\n    summarize_commit_activity,\n)
from .github_client import (
    GitHubRepositoryError,
    get_languages,
    get_repository,
    get_repository_paths,
    get_recent_commits,
    get_root_contents,
)
from .models import (
    CommitActivity,
    DeepStructureAnalysis,
    HealthResponse,
    RepositoryOverview,
    RepositorySummary,
    StructureAnalysis,
)


app = FastAPI(
    title="DevLens Analyzer API",
    version="0.5.0",
    description="Repository intelligence service for DevLens AI.",
)

RepoSegment = Annotated[
    str,
    Path(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$"),
]


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok", "service": "devlens-analyzer", "version": app.version}


@app.get(
    "/repositories/{owner}/{repo}/summary",
    response_model=RepositorySummary,
)
async def repository_summary(owner: RepoSegment, repo: RepoSegment) -> dict:
    try:
        repository, languages = await asyncio.gather(
            get_repository(owner, repo),
            get_languages(owner, repo),
        )
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return _build_summary(repository, languages)


@app.get(
    "/repositories/{owner}/{repo}/structure",
    response_model=StructureAnalysis,
)
async def repository_structure(owner: RepoSegment, repo: RepoSegment) -> dict:
    try:
        entries = await get_root_contents(owner, repo)
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"repository": f"{owner}/{repo}", **analyze_root(entries)}


@app.get(
    "/repositories/{owner}/{repo}/deep-structure",
    response_model=DeepStructureAnalysis,
)
async def repository_deep_structure(
    owner: RepoSegment,
    repo: RepoSegment,
    ref: str | None = Query(default=None, min_length=1, max_length=255),
) -> dict:
    try:
        resolved_ref = ref
        if resolved_ref is None:
            repository = await get_repository(owner, repo)
            resolved_ref = repository.get("default_branch") or "main"
        paths, truncated = await get_repository_paths(owner, repo, resolved_ref)
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "repository": f"{owner}/{repo}",
        "ref": resolved_ref,
        **analyze_paths(paths),
        "truncated": truncated,
    }


@app.get(
    "/repositories/{owner}/{repo}/activity",
    response_model=CommitActivity,
)
async def repository_activity(
    owner: RepoSegment,
    repo: RepoSegment,
    ref: str | None = Query(default=None, min_length=1, max_length=255),
    limit: int = Query(default=30, ge=1, le=100),
) -> dict:
    try:
        commits = await get_recent_commits(owner, repo, ref=ref, limit=limit)
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "repository": f"{owner}/{repo}",
        "ref": ref,
        "requested_limit": limit,
        **summarize_commit_activity(commits),
    }


@app.get(
    "/repositories/{owner}/{repo}/overview",
    response_model=RepositoryOverview,
)
async def repository_overview(owner: RepoSegment, repo: RepoSegment) -> dict:
    try:
        repository, languages, entries = await asyncio.gather(
            get_repository(owner, repo),
            get_languages(owner, repo),
            get_root_contents(owner, repo),
        )
    except GitHubRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    root_analysis = analyze_root(entries)
    structure = {"repository": f"{owner}/{repo}", **root_analysis}
    return {
        "repository": f"{owner}/{repo}",
        "summary": _build_summary(repository, languages),
        "structure": structure,
        "engineering_health": calculate_health(root_analysis["quality_signals"]),
    }


def _build_summary(repository: dict, languages: dict[str, int]) -> dict:
    total_bytes = sum(languages.values())
    language_share = (
        {
            language: round((byte_count / total_bytes) * 100, 2)
            for language, byte_count in languages.items()
        }
        if total_bytes
        else {}
    )

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
