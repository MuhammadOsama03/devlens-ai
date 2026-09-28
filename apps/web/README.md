# DevLens Web

A dependency-free first product interface for the analyzer API.

Serve this directory locally with:

```bash
python -m http.server 3000 --directory apps/web
```

Then open `http://localhost:3000`. The client expects the analyzer at
`http://localhost:8000`. A deployment may set `window.DEVLENS_API_URL`
before the bundled script runs.

The interface renders repository metadata with DOM text nodes so upstream
descriptions cannot inject HTML. Run `python apps/web/check.py` from the
repository root to validate the static document; CI runs the same check.
