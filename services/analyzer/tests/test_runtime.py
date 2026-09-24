from app.config import Settings
from app.runtime import build_runtime


def test_build_runtime_uses_configured_limits(tmp_path):
    runtime = build_runtime(
        Settings(
            database_path=str(tmp_path / "devlens.db"),
            cache_ttl_seconds=15,
            cache_max_entries=4,
            rate_limit_requests=3,
            rate_limit_window_seconds=30,
        )
    )
    assert runtime.cache.ttl_seconds == 15
    assert runtime.cache.stats()["capacity"] == 4
    assert runtime.rate_limiter.limit == 3
    runtime.store.save("a/b", {"score": 1})
    assert runtime.store.get("a/b") == {"score": 1}
