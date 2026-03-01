import urllib.parse

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.database.session import reset_db, SessionLocal
from app.main import app
from app.models.instagram import InstagramAuthState

client = TestClient(app)


@pytest.fixture(autouse=True)
def prepare_database() -> None:
    reset_db()


@pytest.fixture(autouse=True)
def preserve_instagram_config() -> None:
    original_app_id = settings.instagram_app_id
    original_app_secret = settings.instagram_app_secret
    try:
        yield
    finally:
        settings.instagram_app_id = original_app_id
        settings.instagram_app_secret = original_app_secret


def test_instagram_login_url_requires_configuration() -> None:
    settings.instagram_app_id = ""
    settings.instagram_app_secret = ""
    response = client.get("/api/instagram/login-url")
    assert response.status_code == 503
    assert "INSTAGRAM_APP_ID" in response.json()["detail"]


def test_instagram_login_url_emits_state_and_client_id() -> None:
    settings.instagram_app_id = "app-123"
    settings.instagram_app_secret = "secret-value"
    response = client.get("/api/instagram/login-url")
    assert response.status_code == 200
    payload = response.json()
    assert "url" in payload
    assert "state" in payload
    params = urllib.parse.parse_qs(urllib.parse.urlparse(payload["url"]).query)
    assert params.get("client_id") == ["app-123"]

    session = SessionLocal()
    try:
        db_state = session.query(InstagramAuthState).filter(InstagramAuthState.state == payload["state"]).first()
        assert db_state is not None
        assert db_state.state == payload["state"]
        assert not db_state.used
    finally:
        session.close()
