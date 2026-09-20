import pytest

from app.repository_ref import RepositoryRef, parse_repository


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("openai/openai-python", RepositoryRef("openai", "openai-python")),
        ("https://github.com/openai/openai-python", RepositoryRef("openai", "openai-python")),
        ("https://github.com/openai/openai-python.git", RepositoryRef("openai", "openai-python")),
    ],
)
def test_parse_repository(value, expected):
    assert parse_repository(value) == expected


@pytest.mark.parametrize("value", ["owner", "gitlab.com/owner/repo", "https://example.com/a/b"])
def test_parse_repository_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_repository(value)
