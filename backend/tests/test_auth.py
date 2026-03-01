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


def request_code(route: str, username: str) -> str:
    response = client.post(
        f"/auth/{route}",
        data={"username": username, "password": USER_CREDENTIALS[username]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("code_preview"), payload.get("username")


def register_user(username: str, password: str) -> str:
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("code_preview"), payload.get("username")


def confirm_code(username: str, code: str, purpose: str = "login") -> str:
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
    code, username = request_code("login", "client@example.com")
    assert code
    access_token = confirm_code(username, code)

    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == "client@example.com"

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_admin_route_restricted_to_admins() -> None:
    admin_code, admin_user = request_code("login", "admin@example.com")
    admin_token = confirm_code(admin_user, admin_code)
    response = client.get("/auth/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

    client_code, client_user = request_code("login", "client@example.com")
    client_token = confirm_code(client_user, client_code)
    response = client.get("/auth/admin", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 403


def test_refresh_after_logout_is_denied() -> None:
    code, username = request_code("login", "client@example.com")
    token = confirm_code(username, code)
    logout_response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_response.status_code == 200

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 401


def test_register_flow_and_auto_login() -> None:
    new_user = "tester@example.com"
    new_password = "ultrasecret"
    code, username = register_user(new_user, new_password)
    assert code
    token = confirm_code(username, code, purpose="register")
    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["username"] == new_user

    USER_CREDENTIALS[new_user] = new_password
    second_code, username = request_code("login", new_user)
    assert second_code
    second_token = confirm_code(username, second_code)
    assert second_token
