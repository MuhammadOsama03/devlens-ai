import json
import logging

from app.audit import build_audit_event, log_audit_event


def test_build_audit_event_omits_none_values():
    event = build_audit_event("analysis.requested", repository="a/b", user=None)
    assert event["event"] == "analysis.requested"
    assert event["repository"] == "a/b"
    assert "user" not in event
    assert event["timestamp"].endswith("+00:00")


def test_log_audit_event_emits_json(caplog):
    logger = logging.getLogger("devlens-test")
    with caplog.at_level(logging.INFO):
        log_audit_event(logger, "cache.hit", repository="a/b")
    assert json.loads(caplog.records[-1].message)["event"] == "cache.hit"
