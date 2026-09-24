import hashlib
import hmac

from app.webhooks import verify_github_signature


def test_verify_github_signature_accepts_valid_digest():
    payload = b'{"action":"push"}'
    secret = "webhook-secret"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_github_signature(payload, signature, secret)


def test_verify_github_signature_rejects_missing_or_invalid_digest():
    assert not verify_github_signature(b"payload", None, "secret")
    assert not verify_github_signature(b"payload", "sha256=bad", "secret")
