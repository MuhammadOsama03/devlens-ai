from app import dependencies
from app.config import settings


def test_runtime_is_reused_until_reset(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "runtime.db"))
    dependencies.reset_runtime()

    first = dependencies.get_runtime()
    second = dependencies.get_runtime()
    assert first is second

    dependencies.reset_runtime()
    third = dependencies.get_runtime()
    assert third is not first

    dependencies.reset_runtime()
