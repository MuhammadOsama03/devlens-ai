from fastapi.testclient import TestClient

from app import main as main_module


client = TestClient(main_module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "devlens-analyzer",
        "version": "0.5.0",
    }


def test_repository_overview(monkeypatch):
    async def fake_repository(owner: str, repo: str) -> dict:
        return {
            "full_name": f"{owner}/{repo}",
            "description": "Example repository",
            "default_branch": "main",
            "visibility": "public",
            "stargazers_count": 4,
            "forks_count": 2,
            "open_issues_count": 1,
            "size": 20,
            "updated_at": "2026-09-11T00:00:00Z",
        }

    async def fake_languages(owner: str, repo: str) -> dict[str, int]:
        return {"Python": 75, "HTML": 25}

    async def fake_contents(owner: str, repo: str) -> list[dict]:
        return [
            {"name": "README.md", "type": "file"},
            {"name": "tests", "type": "dir"},
        ]

    monkeypatch.setattr(main_module, "get_repository", fake_repository)
    monkeypatch.setattr(main_module, "get_languages", fake_languages)
    monkeypatch.setattr(main_module, "get_root_contents", fake_contents)

    response = client.get("/repositories/example/project/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["languages"] == {"Python": 75.0, "HTML": 25.0}
    assert payload["structure"]["repository"] == "example/project"
    assert payload["engineering_health"]["score"] == 50


def test_deep_structure_uses_requested_ref(monkeypatch):
    async def fake_paths(
        owner: str,
        repo: str,
        ref: str,
    ) -> tuple[list[str], bool]:
        assert (owner, repo, ref) == ("example", "project", "feature/api")
        return (
            [
                "README.md",
                ".github/workflows/ci.yml",
                "services/api/requirements.txt",
                "services/api/tests/test_api.py",
            ],
            False,
        )

    monkeypatch.setattr(main_module, "get_repository_paths", fake_paths)

    response = client.get(
        "/repositories/example/project/deep-structure",
        params={"ref": "feature/api"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ref"] == "feature/api"
    assert payload["file_count"] == 4
    assert payload["max_depth"] == 4
    assert payload["truncated"] is False


def test_repository_name_validation():
    response = client.get("/repositories/invalid owner/project/summary")

    assert response.status_code == 422


def test_repository_activity(monkeypatch):
    async def fake_commits(
        owner: str,
        repo: str,
        *,
        ref: str | None,
        limit: int,
    ) -> list[dict]:
        assert (owner, repo, ref, limit) == ("example", "project", "main", 10)
        return [
            {
                "author": {"login": "alice"},
                "commit": {"author": {"date": "2026-09-13T10:00:00Z"}},
                "parents": [{"sha": "one"}],
            },
            {
                "author": {"login": "bob"},
                "commit": {"author": {"date": "2026-09-12T10:00:00Z"}},
                "parents": [{"sha": "one"}, {"sha": "two"}],
            },
        ]

    monkeypatch.setattr(main_module, "get_recent_commits", fake_commits)

    response = client.get(
        "/repositories/example/project/activity",
        params={"ref": "main", "limit": 10},
    )

    assert response.status_code == 200
    assert response.json() == {
        "repository": "example/project",
        "ref": "main",
        "requested_limit": 10,
        "commit_count": 2,
        "unique_author_count": 2,
        "merge_commit_count": 1,
        "newest_commit_at": "2026-09-13T10:00:00Z",
        "oldest_commit_at": "2026-09-12T10:00:00Z",
    }


def test_repository_activity_limit_validation():
    response = client.get(
        "/repositories/example/project/activity",
        params={"limit": 101},
    )

    assert response.status_code == 422
