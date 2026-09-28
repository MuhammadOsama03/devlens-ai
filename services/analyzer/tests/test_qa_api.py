from fastapi.testclient import TestClient

from app import main as main_module
from app.config import settings
from app.security import hash_api_key


def test_question_context_fetches_safe_files(monkeypatch):
    async def fake_repository(owner: str, repo: str) -> dict:
        return {"default_branch": "main"}

    async def fake_paths(owner: str, repo: str, ref: str):
        return ["README.md", "src/app.py", "image.png", "node_modules/pkg.js"], False

    async def fake_file(owner: str, repo: str, path: str, *, ref: str) -> str:
        return "API_KEY=hidden" if path == "src/app.py" else "Project docs"

    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("secret"))
    monkeypatch.setattr(main_module, "get_repository", fake_repository)
    monkeypatch.setattr(main_module, "get_repository_paths", fake_paths)
    monkeypatch.setattr(main_module, "get_text_file", fake_file)
    client = TestClient(main_module.app)

    response = client.post(
        "/repositories/example/project/qa/context",
        headers={"Authorization": "Bearer secret"},
        json={"question": "Where is configuration?", "max_files": 5},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["paths"] == ["README.md", "src/app.py"]
    assert "API_KEY=[REDACTED]" in result["prompt"]
    assert "API_KEY=hidden" not in result["prompt"]


def test_question_context_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("secret"))

    response = TestClient(main_module.app).post(
        "/repositories/example/project/qa/context",
        json={"question": "What does it do?"},
    )

    assert response.status_code == 401
