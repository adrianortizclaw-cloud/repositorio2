from fastapi.testclient import TestClient

from app.database.session import reset_db
from app.scripts.seed_users import seed_users
from app.main import app

client = TestClient(app)


def setup_module() -> None:
    reset_db()
    seed_users()


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_refresh_flow() -> None:
    response = client.post(
        "/auth/login",
        data={"username": "client@example.com", "password": "secret"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload

    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == "client@example.com"

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()
