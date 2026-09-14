import hashlib
import hmac
import secrets


def create_api_key() -> str:
    """Return a cryptographically strong key suitable for client authentication."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    if not api_key:
        raise ValueError("API key cannot be empty")
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def verify_api_key(api_key: str, expected_hash: str) -> bool:
    if not api_key or len(expected_hash) != 64:
        return False
    return hmac.compare_digest(hash_api_key(api_key), expected_hash.lower())
