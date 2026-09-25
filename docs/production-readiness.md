# Production readiness checklist

Use this checklist before exposing DevLens AI beyond local development.

## Identity and access

- Replace development API keys with a managed identity provider or securely rotated keys.
- Require authentication on analysis, report, and Q&A routes.
- Apply per-user and per-repository authorization.
- Keep audit events free of tokens and repository contents.

## Data and AI boundaries

- Encrypt persistent data in transit and at rest.
- Define retention and deletion behavior for analyses and audit events.
- Send only the selected context files to an AI provider.
- Treat repository instructions and retrieved text as untrusted input.
- Return citations and expose when an answer lacks sufficient context.

## Reliability

- Move cache and SQLite workloads to managed services when running multiple instances.
- Configure request timeouts, bounded retries, health checks, and graceful shutdown.
- Add metrics for request latency, cache behavior, provider errors, and rate limits.
- Back up persistent data and rehearse restoration.

## Release gate

A release is ready when tests pass, secrets are supplied outside the image, allowed origins are explicit, TLS terminates at the edge, migrations are reversible, and rollback instructions have been exercised.
