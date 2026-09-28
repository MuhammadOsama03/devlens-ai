import asyncio

import pytest

from app import github_client


def test_get_recent_commits_encodes_ref_and_limit(monkeypatch):
    requested_paths: list[str] = []

    async def fake_get(path: str):
        requested_paths.append(path)
        return [{"sha": "abc"}]

    monkeypatch.setattr(github_client, "_get", fake_get)

    result = asyncio.run(
        github_client.get_recent_commits(
            "example",
            "project",
            ref="feature/api",
            limit=25,
        )
    )

    assert result == [{"sha": "abc"}]
    assert requested_paths == [
        "repos/example/project/commits?per_page=25&sha=feature%2Fapi"
    ]


def test_get_repository_paths_filters_non_files(monkeypatch):
    async def fake_get(path: str):
        assert path == "repos/example/project/git/trees/main?recursive=1"
        return {
            "tree": [
                {"path": "README.md", "type": "blob"},
                {"path": "services", "type": "tree"},
                {"path": "services/api.py", "type": "blob"},
            ],
            "truncated": True,
        }

    monkeypatch.setattr(github_client, "_get", fake_get)

    paths, truncated = asyncio.run(
        github_client.get_repository_paths("example", "project", "main")
    )

    assert paths == ["README.md", "services/api.py"]
    assert truncated is True


def test_get_recent_commits_rejects_invalid_payload(monkeypatch):
    async def fake_get(path: str):
        return {"message": "unexpected payload"}

    monkeypatch.setattr(github_client, "_get", fake_get)

    with pytest.raises(
        github_client.GitHubRepositoryError,
        match="invalid commit list",
    ):
        asyncio.run(github_client.get_recent_commits("example", "project"))


def test_repository_error_exposes_safe_public_details():
    error = github_client.GitHubRepositoryError("token rejected", status_code=403)

    assert error.public_error.code == "github_access_denied"
    assert error.public_error.retryable is False


def test_transport_error_is_retryable_without_leaking_details():
    error = github_client.GitHubRepositoryError("socket included a secret")

    assert error.public_error.code == "github_unavailable"
    assert "secret" not in error.public_error.message
