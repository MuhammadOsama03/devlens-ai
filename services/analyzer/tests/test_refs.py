import pytest

from app.refs import validate_git_ref


@pytest.mark.parametrize("value", ["main", "feature/api", "release-1.2.0", "abc123"])
def test_validate_git_ref_accepts_safe_values(value):
    assert validate_git_ref(value) == value


@pytest.mark.parametrize("value", ["../main", "feature//api", "refs/x.lock", "bad ref", "@{main}"])
def test_validate_git_ref_rejects_unsafe_values(value):
    with pytest.raises(ValueError):
        validate_git_ref(value)
