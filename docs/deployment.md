# Deployment

## Docker Compose

Copy `.env.example` to `.env`, set `GITHUB_TOKEN` when required, then run:

```bash
docker compose up --build
```

The interface is exposed on port 3000 and the analyzer on port 8000.

## Production checklist

- Terminate TLS at a managed load balancer or reverse proxy.
- Store tokens in the platform secret manager, never in image layers.
- Restrict allowed browser origins to the deployed web hostname.
- Place a managed database and Redis-compatible cache behind private networking.
- Enable branch protection and require the Analyzer CI check before merge.
