import pytest

from app.cache import TTLCache


def test_cache_round_trip_and_clear():
    cache = TTLCache[dict](ttl_seconds=60)
    cache.set("repo", {"score": 80})

    assert cache.get("repo") == {"score": 80}
    cache.clear()
    assert cache.get("repo") is None


def test_cache_evicts_earliest_entry_at_capacity():
    cache = TTLCache[str](ttl_seconds=60, max_entries=1)
    cache.set("first", "one")
    cache.set("second", "two")

    assert cache.get("first") is None
    assert cache.get("second") == "two"


@pytest.mark.parametrize("ttl,max_entries", [(0, 1), (1, 0)])
def test_cache_rejects_invalid_configuration(ttl, max_entries):
    with pytest.raises(ValueError):
        TTLCache(ttl_seconds=ttl, max_entries=max_entries)
