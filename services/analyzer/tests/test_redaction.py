from app.redaction import redact_secrets


def test_redacts_named_credentials():
    value = redact_secrets("API_KEY=abc123 password: hunter2")
    assert "abc123" not in value
    assert "hunter2" not in value
    assert value.count("[REDACTED]") == 2


def test_redacts_github_tokens_without_changing_normal_text():
    token = "ghp_" + "a" * 30
    assert redact_secrets(token) == "[REDACTED_GITHUB_TOKEN]"
    assert redact_secrets("safe repository text") == "safe repository text"
