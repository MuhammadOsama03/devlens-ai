import pytest
from pydantic import ValidationError

from app.config import Settings


def test_runtime_settings_accept_explicit_overrides():
    settings = Settings(cache_ttl_seconds=30, cache_max_entries=10, database_path="test.db")
    assert settings.cache_ttl_seconds == 30
    assert settings.cache_max_entries == 10
    assert settings.database_path == "test.db"


def test_runtime_settings_reject_non_positive_limits():
    with pytest.raises(ValidationError):
        Settings(rate_limit_requests=0)
