# Repository intelligence modules

DevLens now includes reusable building blocks beyond its HTTP endpoints:

- `runtime.py` composes cache, persistence, and request-limiting services.
- `refs.py` validates branch, tag, and commit references before GitHub requests.
- `trends.py` produces daily commit activity series.
- `contributors.py` ranks contributor participation deterministically.
- `badges.py` creates shareable engineering-health badge metadata.
- `exports.py` supports stable JSON and CSV output.
- `webhooks.py` verifies GitHub webhook signatures with constant-time comparison.
- `cache_keys.py` creates versioned analysis cache keys.
- `timing.py` records operation durations for observability.

Each module has focused automated tests and is intentionally provider-independent so it can be connected to API routes or background jobs without duplicating business logic.
