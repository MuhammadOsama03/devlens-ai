from fastapi.testclient import TestClient

from app import main as main_module
from app.cache import TTLCache
from app.dependencies import get_runtime
from app.rate_limit import RateLimiter
from app.runtime import RuntimeServices
from app.storage import AnalysisStore


def test_repository_routes_enforce_rate_limit(monkeypatch, tmp_path):
    async def fake_repository(owner: str, repo: str) -> dict:
        return {"full_name": f"{owner}/{repo}"}

    async def fake_languages(owner: str, repo: str) -> dict[str, int]:
        return {}

    runtime = RuntimeServices(
        cache=TTLCache(ttl_seconds=60, max_entries=2),
        store=AnalysisStore(tmp_path / "rate-limit.db"),
        rate_limiter=RateLimiter(limit=1, window_seconds=30),
    )
    main_module.app.dependency_overrides[get_runtime] = lambda: runtime
    monkeypatch.setattr(main_module, "get_repository", fake_repository)
    monkeypatch.setattr(main_module, "get_languages", fake_languages)
    client = TestClient(main_module.app)

    try:
        assert client.get("/repositories/example/project/summary").status_code == 200
        blocked = client.get("/repositories/example/project/summary")
        assert blocked.status_code == 429
        assert blocked.headers["retry-after"] == "30"
    finally:
        main_module.app.dependency_overrides.clear()
