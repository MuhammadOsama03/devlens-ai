import pytest

from app.cache_keys import analysis_cache_key


def test_analysis_cache_key_normalizes_and_encodes_values():
    key = analysis_cache_key("OpenAI", "SDK", "Deep Structure", ref="feature/api")
    assert key == "v1:openai:sdk:deep%20structure:feature%2Fapi"


def test_analysis_cache_key_versions_entries():
    assert analysis_cache_key("a", "b", "overview", version=2).startswith("v2:")


def test_analysis_cache_key_rejects_invalid_version():
    with pytest.raises(ValueError):
        analysis_cache_key("a", "b", "overview", version=0)
