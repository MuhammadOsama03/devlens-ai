from fastapi.testclient import TestClient

from app import main as main_module
from app.cache import TTLCache
from app.config import settings
from app.dependencies import get_runtime
from app.rate_limit import RateLimiter
from app.runtime import RuntimeServices
from app.security import hash_api_key
from app.storage import AnalysisStore


def _overview() -> dict:
    return {
        "repository": "example/project",
        "summary": {"full_name": "example/project"},
        "structure": {
            "repository": "example/project",
            "file_count": 0,
            "directory_count": 0,
            "files": [],
            "directories": [],
            "framework_signals": [],
            "quality_signals": [],
        },
        "engineering_health": {"score": 0, "grade": "F", "recommendations": []},
    }


def test_saved_analysis_lifecycle(monkeypatch, tmp_path):
    store = AnalysisStore(tmp_path / "saved.db")
    store.save("example/project", _overview())
    runtime = RuntimeServices(
        cache=TTLCache(), store=store, rate_limiter=RateLimiter()
    )
    main_module.app.dependency_overrides[get_runtime] = lambda: runtime
    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("secret"))
    client = TestClient(main_module.app)
    headers = {"Authorization": "Bearer secret"}

    try:
        assert client.get("/analyses", headers=headers).json() == {
            "repositories": ["example/project"]
        }
        fetched = client.get("/analyses/example/project", headers=headers)
        assert fetched.status_code == 200
        assert fetched.json()["repository"] == "example/project"
        assert client.delete("/analyses/example/project", headers=headers).json() == {
            "deleted": True
        }
        assert client.get("/analyses/example/project", headers=headers).status_code == 404
    finally:
        main_module.app.dependency_overrides.clear()


def test_saved_analyses_require_authentication(monkeypatch):
    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("secret"))

    assert TestClient(main_module.app).get("/analyses").status_code == 401
