from app.readiness import assess_readiness


def test_readiness_reports_healthy_local_dependencies(tmp_path):
    result = assess_readiness(str(tmp_path / "devlens.db"), {"entries": 1, "capacity": 10})
    assert result == {"ready": True, "checks": {"database": True, "cache": True}}


def test_readiness_rejects_invalid_cache_state(tmp_path):
    result = assess_readiness(str(tmp_path / "devlens.db"), {"entries": 2, "capacity": 1})
    assert not result["ready"]
    assert not result["checks"]["cache"]
