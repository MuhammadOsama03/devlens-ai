# DevLens AI

AI-powered GitHub repository intelligence for codebase analysis, engineering health, and actionable insights.

## Initial scope

DevLens starts with deterministic repository analysis before adding AI-assisted explanations. The first milestone covers repository metadata, language/framework detection, structure signals, and a clean API for the web client.

## Architecture

- `apps/web` — Next.js + TypeScript user interface (next milestone)
- `services/analyzer` — FastAPI/Python repository analysis service
- `docs` — architecture and product decisions

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

## Roadmap

1. Repository metadata and structure analysis
2. Engineering-health scoring
3. Code-aware AI explanations and repository Q&A
4. Commit/developer analytics
5. Shareable portfolio/recruiter reports
6. Persistent analysis jobs, authentication, caching, CI/CD, and deployment

## Status

Foundation milestone in progress.
