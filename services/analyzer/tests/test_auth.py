from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.security import hash_api_key


client = TestClient(app)


def test_auth_check_accepts_configured_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("valid-key"))

    response = client.get("/auth/check", headers={"Authorization": "Bearer valid-key"})

    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_auth_check_rejects_invalid_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key_hash", hash_api_key("valid-key"))

    response = client.get("/auth/check", headers={"Authorization": "Bearer wrong"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_check_reports_missing_server_configuration(monkeypatch):
    monkeypatch.setattr(settings, "api_key_hash", None)

    response = client.get("/auth/check")

    assert response.status_code == 503
