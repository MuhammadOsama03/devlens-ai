from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_responses_include_security_headers():
    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert len(response.headers["x-request-id"]) == 32


def test_safe_request_id_is_echoed():
    response = client.get("/health", headers={"X-Request-ID": "check-123"})

    assert response.headers["x-request-id"] == "check-123"
