from urllib.parse import urlencode

import httpx

from ..core.config import settings


class InstagramError(Exception):
    """Instagram Graph API error"""


BASE_URL = f"https://graph.instagram.com/{settings.instagram_graph_version}"


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _handle(resp: httpx.Response) -> dict:
    if resp.status_code >= 400:
        raise InstagramError(f"[{resp.status_code}] {resp.text}")
    return resp.json() or {}


def get_login_url(state: str = "") -> str:
    perms = settings.instagram_scopes
    params = {
        "client_id": settings.instagram_app_id,
        "redirect_uri": settings.instagram_callback_url,
        "scope": ",".join(perms),
        "response_type": "code",
        "enable_fb_login": 0,
        "force_authentication": 1,
    }
    if state:
        params["state"] = state
    return f"https://www.instagram.com/oauth/authorize?{urlencode(params)}"


def get_user_info(token: str, fields: str = "id,name,username") -> dict:
    resp = httpx.get("https://graph.instagram.com/me", params={"fields": fields, "access_token": token}, timeout=20)
    return _handle(resp)


def exchange_code_for_token(code: str) -> dict:
    short_resp = httpx.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": settings.instagram_app_id,
            "client_secret": settings.instagram_app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": settings.instagram_callback_url,
            "code": code,
        },
        timeout=20,
    )
    short = _handle(short_resp)
    long_resp = httpx.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": settings.instagram_app_secret,
            "access_token": short["access_token"],
        },
        timeout=20,
    )
    long_lived = _handle(long_resp)
    user_info = get_user_info(long_lived["access_token"])
    return {**long_lived, **user_info}


def refresh_token(token: str) -> dict:
    resp = httpx.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=20,
    )
    return _handle(resp)


class Instagram:
    def __init__(self, token: str):
        self.token = token

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        resp = httpx.get(f"{BASE_URL}{endpoint}", headers=_headers(self.token), params=params or {}, timeout=20)
        return _handle(resp)

    def post(self, endpoint: str, data: dict | None = None) -> dict:
        resp = httpx.post(
            f"{BASE_URL}{endpoint}",
            headers={**_headers(self.token), "Content-Type": "application/json"},
            json=data or {},
            timeout=20,
        )
        return _handle(resp)

    def delete(self, endpoint: str) -> dict:
        resp = httpx.delete(f"{BASE_URL}{endpoint}", headers=_headers(self.token), timeout=20)
        return _handle(resp)

    def me(self, fields: str = "id,name,username") -> dict:
        return self.get("/me", {"fields": fields})

    def get_media(self, fields: str = "id,caption,timestamp,media_url,permalink") -> dict:
        return self.get("/me/media", {"fields": fields})
