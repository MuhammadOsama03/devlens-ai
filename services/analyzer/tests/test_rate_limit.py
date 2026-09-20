import pytest

from app.rate_limit import RateLimiter


def test_rate_limiter_blocks_and_resets_after_window():
    limiter = RateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("client", now=0)
    assert limiter.allow("client", now=1)
    assert not limiter.allow("client", now=2)
    assert limiter.allow("client", now=11)


def test_rate_limiter_isolated_by_identity():
    limiter = RateLimiter(limit=1)
    assert limiter.allow("first", now=0)
    assert limiter.allow("second", now=0)


def test_rate_limiter_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        RateLimiter(limit=0)
