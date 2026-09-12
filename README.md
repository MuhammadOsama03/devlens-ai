# DevLens AI

AI-powered GitHub repository intelligence for codebase analysis, engineering health, and actionable insights.

## Initial scope

DevLens starts with deterministic repository analysis before adding AI-assisted explanations. The analyzer covers repository metadata, language/framework detection, root and recursive structure signals, engineering-health scoring, and typed API responses.

## Architecture

- `apps/web` — Next.js + TypeScript user interface (next milestone)
- `services/analyzer` — FastAPI/Python repository analysis service
- `docs` — architecture and product decisions (planned)

## Analyzer API

Run locally:

```bash
cd services/analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs`.

### Endpoints

- `GET /health` — service status and version
- `GET /repositories/{owner}/{repo}/summary` — metadata and language percentages
- `GET /repositories/{owner}/{repo}/structure` — root files, directories, and detected signals
- `GET /repositories/{owner}/{repo}/deep-structure` — repository-wide file, directory, depth, framework, and quality signals
- `GET /repositories/{owner}/{repo}/overview` — combined summary, root structure, health score, and recommendations

The deep-structure endpoint accepts an optional `ref` query parameter for a branch, tag, or commit:

```text
/repositories/openai/openai-python/deep-structure?ref=main
```

Unauthenticated requests work for public repositories but are subject to GitHub's lower rate limit. Set `GITHUB_TOKEN` to analyze private repositories or receive a higher rate limit.

## Tests

```bash
cd services/analyzer
python -m pytest
```

## Docker

Build and run the analyzer from the repository root:

```bash
docker build -t devlens-analyzer services/analyzer
docker run --rm -p 8000:8000 -e GITHUB_TOKEN devlens-analyzer
```

The container runs as a non-root user and includes a health check against `/health`.

## Roadmap

1. Repository metadata and structure analysis
2. Engineering-health scoring
3. Code-aware AI explanations and repository Q&A
4. Commit/developer analytics
5. Shareable portfolio/recruiter reports
6. Persistent analysis jobs, authentication, caching, CI/CD, and deployment

## Status

Analyzer API v0.4 provides typed root and recursive repository analysis. The web client is the next milestone.
