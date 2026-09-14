import pytest

from app.security import create_api_key, hash_api_key, verify_api_key


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
