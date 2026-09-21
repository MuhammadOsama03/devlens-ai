# Runtime configuration

DevLens reads runtime values from environment variables through Pydantic settings.

| Variable | Default | Purpose |
| --- | ---: | --- |
| `GITHUB_TOKEN` | empty | Higher GitHub limits and private repository access |
| `REQUEST_TIMEOUT_SECONDS` | 10 | GitHub request timeout |
| `CACHE_TTL_SECONDS` | 300 | Analysis cache lifetime |
| `CACHE_MAX_ENTRIES` | 256 | Maximum in-memory cache entries |
| `DATABASE_PATH` | `devlens.db` | SQLite persistence file |
| `RATE_LIMIT_REQUESTS` | 60 | Requests allowed per window |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 | Rate-limit window duration |

Use a managed secret store for `GITHUB_TOKEN` in production. Never commit real tokens.
