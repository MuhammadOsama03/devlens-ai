import pytest

from app.storage import AnalysisStore


def test_store_lists_and_deletes_repositories(tmp_path):
    store = AnalysisStore(tmp_path / "analyses.db")
    store.save("one/repo", {"score": 1})
    store.save("two/repo", {"score": 2})
    assert set(store.list_repositories()) == {"one/repo", "two/repo"}
    assert store.delete("one/repo")
    assert not store.delete("missing/repo")
    assert store.list_repositories() == ["two/repo"]


def test_store_rejects_invalid_list_limit(tmp_path):
    store = AnalysisStore(tmp_path / "analyses.db")
    with pytest.raises(ValueError):
        store.list_repositories(0)
