from app.request_id import resolve_request_id


def test_preserves_safe_request_id():
    assert resolve_request_id("deploy_42.trace-1") == "deploy_42.trace-1"


def test_replaces_unsafe_request_id():
    request_id = resolve_request_id("contains spaces")

    assert len(request_id) == 32
    assert request_id.isalnum()
