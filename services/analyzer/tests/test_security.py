import pytest

from app.security import create_api_key, extract_bearer_token, hash_api_key, verify_api_key


def test_api_keys_are_random_and_verifiable():
    first = create_api_key()
    second = create_api_key()
    assert first != second
    assert verify_api_key(first, hash_api_key(first))
    assert not verify_api_key(second, hash_api_key(first))


def test_hash_api_key_rejects_empty_values():
    with pytest.raises(ValueError, match="cannot be empty"):
        hash_api_key("")


def test_verify_api_key_rejects_malformed_hash():
    assert not verify_api_key("secret", "not-a-sha256-hash")


@pytest.mark.parametrize(
    ("header", "expected"),
    [("Bearer secret", "secret"), ("bearer token-value ", "token-value"), (None, None), ("Basic abc", None), ("Bearer ", None)],
)
def test_extract_bearer_token(header, expected):
    assert extract_bearer_token(header) == expected
