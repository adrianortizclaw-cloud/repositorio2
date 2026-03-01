from secrets import token_urlsafe

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import decrypt_secret, encrypt_secret
from ..database.session import get_db
from ..models.instagram import InstagramAuthState, InstagramSession
from ..schemas.instagram import InstagramLoginUrlResponse, InstagramSessionResponse
from ..services.instagram_wrapper import Instagram, InstagramError, exchange_code_for_token, get_login_url

router = APIRouter(prefix="/api/instagram", tags=["instagram"])


def _require_session(db: Session, x_session_id: str | None) -> InstagramSession:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Missing X-Session-Id header")
    session = db.query(InstagramSession).filter(InstagramSession.session_id == x_session_id).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session


def _instagram_from_session(session: InstagramSession) -> Instagram:
    return Instagram(decrypt_secret(session.access_token_encrypted))


@router.get("/login-url", response_model=InstagramLoginUrlResponse)
def login_url(db: Session = Depends(get_db)):
    state = token_urlsafe(32)
    db.add(InstagramAuthState(state=state))
    db.commit()
    url = get_login_url(state=state)
    return InstagramLoginUrlResponse(url=url, state=state)


@router.get("/callback")
def callback(code: str = "", state: str = "", db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    auth_state = db.query(InstagramAuthState).filter(InstagramAuthState.state == state).first()
    if not auth_state or auth_state.used:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    auth_state.used = True
    try:
        token_data = exchange_code_for_token(code)
    except InstagramError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session_id = token_urlsafe(32)
    session = InstagramSession(
        session_id=session_id,
        ig_user_id=str(token_data.get("id", "")),
        username=token_data.get("username"),
        name=token_data.get("name"),
        access_token_encrypted=encrypt_secret(token_data["access_token"]),
    )
    db.add(session)
    db.commit()
    callback_origin = settings.frontend_origin.rstrip("/")
    return RedirectResponse(url=f"{callback_origin}/?session={session.session_id}")


@router.get("/session", response_model=InstagramSessionResponse)
def session_info(db: Session = Depends(get_db), x_session_id: str | None = Header(default=None, alias="X-Session-Id")):
    session = _require_session(db, x_session_id)
    return InstagramSessionResponse(
        session_id=session.session_id,
        ig_user_id=session.ig_user_id,
        username=session.username,
        name=session.name,
        created_at=session.created_at,
    )


@router.get("/me")
def me(db: Session = Depends(get_db), x_session_id: str | None = Header(default=None, alias="X-Session-Id")):
    session = _require_session(db, x_session_id)
    try:
        return _instagram_from_session(session).me()
    except InstagramError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/media")
def media(db: Session = Depends(get_db), x_session_id: str | None = Header(default=None, alias="X-Session-Id")):
    session = _require_session(db, x_session_id)
    try:
        return _instagram_from_session(session).get_media()
    except InstagramError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
