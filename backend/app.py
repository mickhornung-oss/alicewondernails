from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routes.admin import router as admin_router
from backend.routes.public import router as public_router
from backend.security import SimpleSessionMiddleware, SlidingWindowRateLimiter, hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    if not settings.admin_password_hash:
        if settings.admin_password:
            settings.admin_password_hash = hash_password(settings.admin_password)
        else:
            raise RuntimeError(
                "ADMIN_PASSWORD_HASH oder ADMIN_PASSWORD muss in der Umgebung gesetzt sein."
            )

    app.state.public_rate_limiter = SlidingWindowRateLimiter()
    app.state.login_rate_limiter = SlidingWindowRateLimiter()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    SimpleSessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    https_only=settings.https_only_sessions,
    same_site="lax",
    max_age=settings.session_max_age_seconds,
)

app.mount("/public", StaticFiles(directory=settings.public_dir), name="public")
app.mount("/static", StaticFiles(directory=settings.public_dir / "assets"), name="static")

app.include_router(public_router)
app.include_router(admin_router)


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/public/index.html", status_code=307)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
