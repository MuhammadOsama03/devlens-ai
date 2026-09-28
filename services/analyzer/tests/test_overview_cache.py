from fastapi.testclient import TestClient

from app import main as main_module
from app.cache import TTLCache
from app.dependencies import get_runtime
from app.rate_limit import RateLimiter
from app.runtime import RuntimeServices
from app.storage import AnalysisStore


def test_overview_reuses_cached_analysis(monkeypatch, tmp_path):
    calls = 0

    async def fake_repository(owner: str, repo: str) -> dict:
        nonlocal calls
        calls += 1
        return {"full_name": f"{owner}/{repo}", "default_branch": "main"}

    async def fake_languages(owner: str, repo: str) -> dict[str, int]:
        return {"Python": 10}

    async def fake_contents(owner: str, repo: str) -> list[dict]:
        return [{"name": "README.md", "type": "file"}]

    runtime = RuntimeServices(
        cache=TTLCache(ttl_seconds=60, max_entries=4),
        store=AnalysisStore(tmp_path / "cache.db"),
        rate_limiter=RateLimiter(limit=10),
    )
    main_module.app.dependency_overrides[get_runtime] = lambda: runtime
    monkeypatch.setattr(main_module, "get_repository", fake_repository)
    monkeypatch.setattr(main_module, "get_languages", fake_languages)
    monkeypatch.setattr(main_module, "get_root_contents", fake_contents)
    client = TestClient(main_module.app)

    try:
        first = client.get("/repositories/example/project/overview")
        second = client.get("/repositories/example/project/overview")
        assert first.status_code == second.status_code == 200
        assert first.json() == second.json()
        assert calls == 1
        assert runtime.cache.stats()["entries"] == 1
    finally:
        main_module.app.dependency_overrides.clear()
