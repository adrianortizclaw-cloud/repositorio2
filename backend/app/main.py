from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth
from .core.config import settings
from .database.session import init_db

app = FastAPI(title="InstagramProyect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
