from fastapi.testclient import TestClient

from app.database.session import reset_db
from app.scripts.seed_users import seed_users
from app.main import app

client = TestClient(app)

USER_CREDENTIALS = {
    "client@example.com": "secret",
    "admin@example.com": "secret",
}


def setup_module() -> None:
    reset_db()
    seed_users()


def login(username: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": username, "password": USER_CREDENTIALS[username]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def register_user(username: str, password: str) -> tuple[str, str, str]:
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    payload = response.json()
    return payload["code_preview"], payload["username"], payload["purpose"]


def confirm_code(username: str, code: str, purpose: str = "register") -> str:
    response = client.post(
        "/auth/confirm",
        json={"username": username, "code": code, "purpose": purpose},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_refresh_flow() -> None:
    access_token = login("client@example.com")

    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == "client@example.com"

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_admin_route_restricted_to_admins() -> None:
    admin_token = login("admin@example.com")
    response = client.get("/auth/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

    client_token = login("client@example.com")
    response = client.get("/auth/admin", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 403


def test_refresh_after_logout_is_denied() -> None:
    token = login("client@example.com")
    logout_response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_response.status_code == 200

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 401


def test_register_flow_and_auto_login() -> None:
    new_user = "tester@example.com"
    new_password = "ultrasecret"
    code, username, purpose = register_user(new_user, new_password)
    token = confirm_code(username, code, purpose=purpose)
    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == new_user

    USER_CREDENTIALS[new_user] = new_password
    second_token = login(new_user)
    assert second_token
