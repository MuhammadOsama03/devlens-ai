# DevLens AI

AI-powered GitHub repository intelligence for codebase analysis, engineering health, and actionable insights.

## Initial scope

DevLens starts with deterministic repository analysis before adding AI-assisted explanations. The first milestone covers repository metadata, language/framework detection, structure signals, engineering-health scoring, and a clean API for the web client.

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
- `GET /repositories/{owner}/{repo}/overview` — combined summary, structure, health score, and recommendations

Unauthenticated requests work for public repositories but are subject to GitHub's lower rate limit. Set `GITHUB_TOKEN` to analyze private repositories or receive a higher rate limit.

## Tests

```bash
cd services/analyzer
pytest
```

## Roadmap

1. Repository metadata and structure analysis
2. Engineering-health scoring
3. Code-aware AI explanations and repository Q&A
4. Commit/developer analytics
5. Shareable portfolio/recruiter reports
6. Persistent analysis jobs, authentication, caching, CI/CD, and deployment

## Status

The analyzer foundation is operational. The web client is the next milestone.
