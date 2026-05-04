from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("true", "1", "yes", "on")


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass
class Settings:
    project_root: Path
    app_name: str
    api_host: str
    api_port: int
    cors_origin_regex: str
    secret_key: str
    session_cookie_name: str
    session_max_age_seconds: int
    https_only_sessions: bool
    admin_username: str
    admin_password_hash: str | None
    admin_password: str | None
    db_path: Path
    export_dir: Path
    public_dir: Path
    templates_dir: Path
    public_rate_limit_per_minute: int
    login_rate_limit_per_minute: int


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parent.parent
    _load_dotenv(project_root / ".env")

    return Settings(
        project_root=project_root,
        app_name="Alice Wonder Nails V1 API",
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=_int_env("API_PORT", 8000),
        cors_origin_regex=os.getenv(
            "CORS_ORIGIN_REGEX",
            r"https?://(localhost|127\\.0\\.0\\.1)(:\\d+)?$",
        ),
        secret_key=os.getenv("SESSION_SECRET", "change-me-in-env"),
        session_cookie_name=os.getenv("SESSION_COOKIE_NAME", "awn_admin_session"),
        session_max_age_seconds=_int_env("SESSION_MAX_AGE_SECONDS", 60 * 60 * 8),
        https_only_sessions=_bool_env("HTTPS_ONLY_SESSIONS", False),
        admin_username=os.getenv("ADMIN_USERNAME", "michael"),
        admin_password_hash=os.getenv("ADMIN_PASSWORD_HASH"),
        admin_password=os.getenv("ADMIN_PASSWORD"),
        db_path=project_root / "data" / "db" / "alicewonder_v1.sqlite",
        export_dir=project_root / "data" / "exports",
        public_dir=project_root / "public",
        templates_dir=project_root / "backend" / "templates",
        public_rate_limit_per_minute=_int_env("PUBLIC_RATE_LIMIT_PER_MINUTE", 20),
        login_rate_limit_per_minute=_int_env("LOGIN_RATE_LIMIT_PER_MINUTE", 10),
    )


settings = load_settings()
