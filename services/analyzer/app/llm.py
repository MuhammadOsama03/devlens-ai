"""Optional Gemini provider for grounded repository answers."""
import httpx

from .config import settings


class ProviderUnavailable(RuntimeError):
    pass


async def generate_grounded_answer(prompt: str) -> str:
    """Call Gemini with bounded output; do not send requests without an API key."""
    if not settings.gemini_api_key:
        raise ProviderUnavailable("Gemini is not configured")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                url, headers={"x-goog-api-key": settings.gemini_api_key}, json=payload
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderUnavailable("Gemini request failed") from exc

    candidates = data.get("candidates") or []
    parts = (candidates[0].get("content") or {}).get("parts") or [] if candidates else []
    answer = "\n".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
    if not answer:
        raise ProviderUnavailable("Gemini returned no text")
    return answer
