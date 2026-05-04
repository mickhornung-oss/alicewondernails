from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque
from http.cookies import SimpleCookie
from threading import Lock
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.datastructures import Headers, MutableHeaders


class SimpleSessionMiddleware:
    def __init__(
        self,
        app: Any,
        *,
        secret_key: str,
        session_cookie: str = "session",
        max_age: int = 60 * 60 * 8,
        https_only: bool = False,
        same_site: str = "lax",
    ) -> None:
        self.app = app
        self.secret_key = secret_key.encode("utf-8")
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.https_only = https_only
        self.same_site = same_site.lower()

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        raw_cookie_header = headers.get("cookie", "")
        session = self._load_session_from_cookie(raw_cookie_header)
        session_before = dict(session)
        scope["session"] = session

        async def send_wrapper(message: dict[str, Any]) -> None:
            if message.get("type") == "http.response.start":
                mutable_headers = MutableHeaders(scope=message)
                if session:
                    mutable_headers.append(
                        "Set-Cookie",
                        self._build_set_cookie(self._encode_session(session)),
                    )
                elif session_before:
                    mutable_headers.append("Set-Cookie", self._build_clear_cookie())
            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _build_set_cookie(self, value: str) -> str:
        segments = [
            f"{self.session_cookie}={value}",
            "Path=/",
            f"Max-Age={self.max_age}",
            "HttpOnly",
            f"SameSite={self.same_site.capitalize()}",
        ]
        if self.https_only:
            segments.append("Secure")
        return "; ".join(segments)

    def _build_clear_cookie(self) -> str:
        segments = [
            f"{self.session_cookie}=",
            "Path=/",
            "Max-Age=0",
            "HttpOnly",
            f"SameSite={self.same_site.capitalize()}",
        ]
        if self.https_only:
            segments.append("Secure")
        return "; ".join(segments)

    @staticmethod
    def _to_urlsafe_b64(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @staticmethod
    def _from_urlsafe_b64(raw: str) -> bytes:
        padding = "=" * ((4 - (len(raw) % 4)) % 4)
        return base64.urlsafe_b64decode(raw + padding)

    def _encode_session(self, session: dict[str, Any]) -> str:
        payload = json.dumps(session, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        payload_b64 = self._to_urlsafe_b64(payload)
        signature = hmac.new(self.secret_key, payload_b64.encode("ascii"), hashlib.sha256).digest()
        signature_b64 = self._to_urlsafe_b64(signature)
        return f"{payload_b64}.{signature_b64}"

    def _decode_session(self, token: str) -> dict[str, Any]:
        try:
            payload_b64, signature_b64 = token.split(".", 1)
            expected_signature = hmac.new(
                self.secret_key,
                payload_b64.encode("ascii"),
                hashlib.sha256,
            ).digest()
            supplied_signature = self._from_urlsafe_b64(signature_b64)
            if not hmac.compare_digest(expected_signature, supplied_signature):
                return {}
            payload_json = self._from_urlsafe_b64(payload_b64).decode("utf-8")
            decoded = json.loads(payload_json)
            if isinstance(decoded, dict):
                return decoded
            return {}
        except Exception:
            return {}

    def _load_session_from_cookie(self, cookie_header: str) -> dict[str, Any]:
        if not cookie_header:
            return {}
        jar = SimpleCookie()
        try:
            jar.load(cookie_header)
        except Exception:
            return {}
        morsel = jar.get(self.session_cookie)
        if morsel is None:
            return {}
        return self._decode_session(morsel.value)


def hash_password(password: str, iterations: int = 260_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${digest_b64}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_raw, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_raw)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
    except Exception:
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


def ensure_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if token:
        return token
    token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = token
    return token


def validate_csrf_token(request: Request, token_from_form: str | None) -> None:
    session_token = request.session.get("csrf_token")
    if not session_token or not token_from_form:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ungueltiger CSRF-Token")
    if not hmac.compare_digest(session_token, token_from_form):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ungueltiger CSRF-Token")


def require_admin(request: Request) -> None:
    if request.session.get("admin_authenticated") is True:
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="admin login erforderlich")
