import re


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
]


def redact_secrets(value: str) -> str:
    redacted = value
    redacted = SECRET_PATTERNS[0].sub(lambda match: f"{match.group(1)}=[REDACTED]", redacted)
    redacted = SECRET_PATTERNS[1].sub("[REDACTED_GITHUB_TOKEN]", redacted)
    return redacted
