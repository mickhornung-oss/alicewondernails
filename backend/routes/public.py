from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError

from backend.config import settings
from backend.schemas import LeadCreateSchema, parse_bool
from backend.security import get_client_ip
from backend.services.lead_service import create_lead

router = APIRouter(tags=["public"])


async def _extract_payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        payload = await request.json()
        if isinstance(payload, dict):
            return payload
        return {}

    form_data = await request.form()
    payload = dict(form_data)

    if "early-access" in payload and "one_time_notice_accepted" not in payload:
        payload["one_time_notice_accepted"] = payload.get("early-access")

    if "privacy" in payload and "privacy_accepted" not in payload:
        payload["privacy_accepted"] = payload.get("privacy")

    return payload


@router.post("/api/lead")
async def create_lead_endpoint(request: Request) -> dict[str, Any]:
    client_ip = get_client_ip(request)
    limiter = request.app.state.public_rate_limiter
    allowed = limiter.allow(
        key=f"public_lead:{client_ip}",
        limit=settings.public_rate_limit_per_minute,
        window_seconds=60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="zu viele Anfragen, bitte spaeter erneut versuchen",
        )

    raw_payload = await _extract_payload(request)

    for bool_key in ("privacy_accepted", "one_time_notice_accepted"):
        if bool_key in raw_payload:
            raw_payload[bool_key] = parse_bool(raw_payload.get(bool_key))

    try:
        payload = LeadCreateSchema.model_validate(raw_payload)
    except ValidationError as exc:
        try:
            detail = exc.errors(include_url=False, include_context=False)
        except TypeError:
            detail = []
            for item in exc.errors():
                cleaned = dict(item)
                ctx = cleaned.get("ctx")
                if isinstance(ctx, dict) and "error" in ctx:
                    ctx = dict(ctx)
                    ctx["error"] = str(ctx["error"])
                    cleaned["ctx"] = ctx
                detail.append(cleaned)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        ) from exc

    # Honeypot: silent success, but do not store spam payloads.
    if payload.website:
        return {"success": True}

    lead_id = create_lead(payload)
    return {"success": True, "lead_id": lead_id}
