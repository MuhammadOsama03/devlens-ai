import pytest

from app.errors import map_upstream_status


@pytest.mark.parametrize(
    ("status", "code", "retryable"),
    [(404, "repository_not_found", False), (403, "github_access_denied", False),
     (429, "github_rate_limited", True), (503, "github_unavailable", True)],
)
def test_map_upstream_status(status, code, retryable):
    error = map_upstream_status(status)
    assert error.code == code
    assert error.retryable is retryable
