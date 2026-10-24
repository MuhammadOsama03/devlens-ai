import asyncio
import pytest
import httpx

from app import llm


def test_provider_requires_configuration(monkeypatch):
    monkeypatch.setattr(llm.settings, "gemini_api_key", None)
    with pytest.raises(llm.ProviderUnavailable, match="not configured"):
        asyncio.run(llm.generate_grounded_answer("test"))


def test_provider_extracts_answer(monkeypatch):
    monkeypatch.setattr(llm.settings, "gemini_api_key", "test-key")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, **kwargs):
            request = httpx.Request("POST", url)
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "See README.md"}]}}]}, request=request)
    monkeypatch.setattr(llm.httpx, "AsyncClient", lambda **kwargs: FakeClient())
    assert asyncio.run(llm.generate_grounded_answer("Question")) == "See README.md"
