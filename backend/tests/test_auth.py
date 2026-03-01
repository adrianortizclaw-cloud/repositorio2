import pytest
from fastapi.testclient import TestClient

from app.database.session import SessionLocal, reset_db
from app.models.auth_code import AuthCode
from app.models.pending_registration import PendingRegistration
from app.models.user import RefreshToken, User
from app.scripts.seed_users import seed_users
from app.main import app

client = TestClient(app)

USER_CREDENTIALS = {
    "client@example.com": "secret",
    "admin@example.com": "secret",
}


@pytest.fixture(autouse=True)
def prepare_database() -> None:
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


def test_register_creates_pending_and_auth_code_records() -> None:
    pending_username = "pending@example.com"
    register_user(pending_username, "pendingpass123")
    session = SessionLocal()
    try:
        pending = session.query(PendingRegistration).filter(PendingRegistration.username == pending_username).first()
        assert pending is not None
        auth_code = session.query(AuthCode).filter(AuthCode.pending_registration_id == pending.id).first()
        assert auth_code is not None
        assert not auth_code.used
        assert auth_code.pending_registration_id == pending.id
    finally:
        session.close()


def test_confirm_registration_cleans_up_pending_and_refresh_relationships() -> None:
    confirm_username = "confirm@example.com"
    confirm_password = "confirmsecret"
    code, username, purpose = register_user(confirm_username, confirm_password)
    session = SessionLocal()
    try:
        pending = session.query(PendingRegistration).filter(PendingRegistration.username == username).first()
        assert pending is not None
        pending_id = pending.id
    finally:
        session.close()

    confirm_code(username, code, purpose=purpose)
    session = SessionLocal()
    try:
        assert session.query(PendingRegistration).filter(PendingRegistration.id == pending_id).first() is None
        auth_code = session.query(AuthCode).filter(AuthCode.pending_registration_id == pending_id).first()
        assert auth_code is not None
        assert auth_code.used
        user = session.query(User).filter(User.username == confirm_username).first()
        assert user is not None
        refresh_token = session.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        assert refresh_token is not None
        assert not refresh_token.revoked
    finally:
        session.close()
