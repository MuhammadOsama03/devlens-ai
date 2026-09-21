from app.cache import TTLCache


def test_cache_stats_report_live_occupancy():
    cache = TTLCache[str](max_entries=3)
    assert cache.stats() == {"entries": 0, "capacity": 3}
    cache.set("one", "value")
    cache.set("two", "value")
    assert cache.stats() == {"entries": 2, "capacity": 3}
