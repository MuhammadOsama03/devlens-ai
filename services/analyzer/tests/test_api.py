from fastapi.testclient import TestClient

from app import main as main_module


client = TestClient(main_module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "devlens-analyzer",
        "version": "0.4.0",
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
