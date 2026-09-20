import json
import logging
from datetime import UTC, datetime
from typing import Any


def build_audit_event(event: str, **fields: Any) -> dict[str, Any]:
    return {
        "event": event,
        "timestamp": datetime.now(UTC).isoformat(),
        **{key: value for key, value in fields.items() if value is not None},
    }


def log_audit_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(json.dumps(build_audit_event(event, **fields), sort_keys=True))
