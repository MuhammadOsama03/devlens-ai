# DevLens AI

AI-powered GitHub repository intelligence for codebase analysis, engineering health, and actionable insights.

## Current capabilities

- FastAPI analyzer with repository summary, structure, deep-structure, overview, and commit-activity endpoints
- Framework and engineering-quality detection with health scoring
- Dependency-free browser interface in `apps/web`
- Secure grounded repository Q&A preparation and context-file selection
- API-key primitives, bearer parsing, security headers, rate limiting, and audit events
- Bounded in-memory caching and SQLite analysis persistence
- Shareable Markdown report generation
- Contributor summaries, daily activity trends, delivery risk, and health badges
- Readiness probes, server timing, and signed GitHub webhook cache invalidation
- Docker Compose deployment and automated GitHub Actions checks

## Run locally

```bash
cd services/analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API documentation at `http://localhost:8000/docs`.

Run the web interface separately:

```bash
python -m http.server 3000 --directory apps/web
```

## Tests

```bash
cd services/analyzer
python -m compileall -q app tests
python -m pytest
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The web interface is available on port 3000 and the analyzer on port 8000.

## Next production milestones

1. Connect persistence, caching, authentication, audit logging, and rate limiting to request flows
2. Add an external AI provider behind the grounded Q&A boundary
3. Replace local SQLite and cache implementations with managed production services
4. Deploy behind TLS and enable branch protection with required CI checks

## Optional grounded Gemini answers

The existing `POST /repositories/{owner}/{repo}/qa/context` endpoint returns a bounded, redacted prompt without invoking a model.

To enable answer generation, set `GEMINI_API_KEY` in the analyzer environment and optionally `GEMINI_MODEL` (default: `gemini-2.5-flash`). Then call:

```bash
curl -X POST http://localhost:8000/repositories/OWNER/REPO/qa/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"Where is authentication implemented?","max_files":8}'
```

If API-key authentication is configured, include the corresponding bearer authorization header. The endpoint uses the same context selection, secret redaction, and bounded prompt as the context endpoint. It returns the model answer plus source file paths; answers still require human verification. Without a Gemini key, it returns HTTP 503 rather than silently generating an ungrounded response. Avoid sending private code to an external provider unless authorized.

Run tests from `services/analyzer` with `python -m pytest`.
