from app.storage import AnalysisStore


def test_analysis_store_persists_and_updates_payload(tmp_path):
    store = AnalysisStore(tmp_path / "analyses.db")
    store.save("example/project", {"score": 70})
    assert store.get("example/project") == {"score": 70}

    store.save("example/project", {"score": 90})
    assert store.get("example/project") == {"score": 90}


def test_analysis_store_returns_none_for_unknown_repository(tmp_path):
    assert AnalysisStore(tmp_path / "analyses.db").get("missing/repo") is None
