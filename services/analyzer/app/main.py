import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .analysis import (
    analyze_paths,
    analyze_root,
    calculate_health,
    summarize_commit_activity,
)
from .auth import require_api_key
from .cache_keys import analysis_cache_key
from .context import select_context_paths
from .github_client import (
    GitHubRepositoryError,
    get_languages,
    get_repository,
    get_repository_paths,
    get_recent_commits,
    get_root_contents,
    get_text_file,
)
from .models import (
    CommitActivity,
    AuthCheckResponse,
    DeleteAnalysisResponse,
    DeepStructureAnalysis,
    HealthResponse,
    RepositoryOverview,
    QuestionContextRequest,
    QuestionContextResponse,
    RepositorySummary,
    SavedAnalysisIndex,
    StructureAnalysis,
)
from .request_id import resolve_request_id
from .qa import ContextFile, build_context_chunks, build_grounded_prompt, prepare_repository_question
from .config import settings
from .dependencies import enforce_rate_limit, get_runtime
from .runtime import RuntimeServices


app = FastAPI(
    title="DevLens Analyzer API",
    version="0.5.0",
    description="Repository intelligence service for DevLens AI.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.exception_handler(GitHubRepositoryError)
async def github_error_handler(
    request: Request,
    exc: GitHubRepositoryError,
) -> JSONResponse:
    error = exc.public_error
    status_code = 404 if error.code == "repository_not_found" else 503 if error.retryable else 502
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "retryable": error.retryable,
            }
        },
    )


@app.middleware("http")
async def add_security_headers(request, call_next):
    request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response

RepoSegment = Annotated[
    str,
    Path(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$"),
]


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok", "service": "devlens-analyzer", "version": app.version}


@app.get("/auth/check", response_model=AuthCheckResponse)
def auth_check(api_key: str = Depends(require_api_key)) -> dict[str, bool]:
    return {"authenticated": bool(api_key)}


@app.get("/analyses", response_model=SavedAnalysisIndex)
def saved_analyses(
    limit: int = Query(default=100, ge=1, le=500),
    runtime: RuntimeServices = Depends(get_runtime),
    api_key: str = Depends(require_api_key),
) -> dict[str, list[str]]:
    return {"repositories": runtime.store.list_repositories(limit)}


@app.get("/analyses/{owner}/{repo}", response_model=RepositoryOverview)
def saved_analysis(
    owner: RepoSegment,
    repo: RepoSegment,
    runtime: RuntimeServices = Depends(get_runtime),
    api_key: str = Depends(require_api_key),
) -> dict:
    result = runtime.store.get(f"{owner}/{repo}")
    if result is None:
        raise HTTPException(status_code=404, detail="Saved analysis not found")
    return result


@app.delete("/analyses/{owner}/{repo}", response_model=DeleteAnalysisResponse)
def delete_saved_analysis(
    owner: RepoSegment,
    repo: RepoSegment,
    runtime: RuntimeServices = Depends(get_runtime),
    api_key: str = Depends(require_api_key),
) -> dict[str, bool]:
    return {"deleted": runtime.store.delete(f"{owner}/{repo}")}


@app.post(
    "/repositories/{owner}/{repo}/qa/context",
    response_model=QuestionContextResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_question_context(
    owner: RepoSegment,
    repo: RepoSegment,
    payload: QuestionContextRequest,
    api_key: str = Depends(require_api_key),
) -> dict:
    resolved_ref = payload.ref
    if resolved_ref is None:
        repository = await get_repository(owner, repo)
        resolved_ref = repository.get("default_branch") or "main"

    repository_paths, tree_truncated = await get_repository_paths(
        owner, repo, resolved_ref
    )
    selected_paths = select_context_paths(repository_paths, limit=payload.max_files)
    contents = await asyncio.gather(
        *(
            get_text_file(owner, repo, path, ref=resolved_ref)
            for path in selected_paths
        )
    )
    chunks = build_context_chunks(
        [
            ContextFile(path=path, content=content)
            for path, content in zip(selected_paths, contents, strict=True)
        ]
    )
    question = prepare_repository_question(
        f"{owner}/{repo}", payload.question, chunks
    )
    return {
        "repository": question.repository,
        "ref": resolved_ref,
        "paths": selected_paths,
        "prompt": build_grounded_prompt(question),
        "tree_truncated": tree_truncated,
    }


@app.get(
    "/repositories/{owner}/{repo}/summary",
    response_model=RepositorySummary,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_summary(owner: RepoSegment, repo: RepoSegment) -> dict:
    repository, languages = await asyncio.gather(
        get_repository(owner, repo),
        get_languages(owner, repo),
    )

    return _build_summary(repository, languages)


@app.get(
    "/repositories/{owner}/{repo}/structure",
    response_model=StructureAnalysis,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_structure(owner: RepoSegment, repo: RepoSegment) -> dict:
    entries = await get_root_contents(owner, repo)

    return {"repository": f"{owner}/{repo}", **analyze_root(entries)}


@app.get(
    "/repositories/{owner}/{repo}/deep-structure",
    response_model=DeepStructureAnalysis,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_deep_structure(
    owner: RepoSegment,
    repo: RepoSegment,
    ref: str | None = Query(default=None, min_length=1, max_length=255),
) -> dict:
    resolved_ref = ref
    if resolved_ref is None:
        repository = await get_repository(owner, repo)
        resolved_ref = repository.get("default_branch") or "main"
    paths, truncated = await get_repository_paths(owner, repo, resolved_ref)

    return {
        "repository": f"{owner}/{repo}",
        "ref": resolved_ref,
        **analyze_paths(paths),
        "truncated": truncated,
    }


@app.get(
    "/repositories/{owner}/{repo}/activity",
    response_model=CommitActivity,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_activity(
    owner: RepoSegment,
    repo: RepoSegment,
    ref: str | None = Query(default=None, min_length=1, max_length=255),
    limit: int = Query(default=30, ge=1, le=100),
) -> dict:
    commits = await get_recent_commits(owner, repo, ref=ref, limit=limit)

    return {
        "repository": f"{owner}/{repo}",
        "ref": ref,
        "requested_limit": limit,
        **summarize_commit_activity(commits),
    }


@app.get(
    "/repositories/{owner}/{repo}/overview",
    response_model=RepositoryOverview,
    dependencies=[Depends(enforce_rate_limit)],
)
async def repository_overview(
    owner: RepoSegment,
    repo: RepoSegment,
    runtime: RuntimeServices = Depends(get_runtime),
) -> dict:
    cache_key = analysis_cache_key(owner, repo, "overview")
    cached = runtime.cache.get(cache_key)
    if cached is not None:
        return cached

    repository, languages, entries = await asyncio.gather(
        get_repository(owner, repo),
        get_languages(owner, repo),
        get_root_contents(owner, repo),
    )

    root_analysis = analyze_root(entries)
    structure = {"repository": f"{owner}/{repo}", **root_analysis}
    result = {
        "repository": f"{owner}/{repo}",
        "summary": _build_summary(repository, languages),
        "structure": structure,
        "engineering_health": calculate_health(root_analysis["quality_signals"]),
    }
    runtime.cache.set(cache_key, result)
    runtime.store.save(f"{owner}/{repo}", result)
    return result


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
