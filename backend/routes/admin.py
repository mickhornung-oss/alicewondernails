from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from backend.config import settings
from backend.models import LEAD_STATUSES
from backend.schemas import AdminActionSchema, AdminLeadUpdateSchema, AdminLoginSchema, parse_bool
from backend.security import ensure_csrf_token, get_client_ip, validate_csrf_token, verify_password
from backend.services.cleanup_service import cleanup_expired_leads
from backend.services.export_service import export_leads
from backend.services.lead_service import (
    list_leads,
    mark_startmail_sent,
    soft_delete_lead,
    update_lead,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


def _is_admin(request: Request) -> bool:
    return request.session.get("admin_authenticated") is True


def _set_flash(request: Request, message: str, level: str = "info") -> None:
    request.session["flash"] = {"message": message, "level": level}


def _pop_flash(request: Request) -> dict[str, str] | None:
    flash = request.session.get("flash")
    if flash is not None:
        request.session.pop("flash", None)
    return flash


@router.get("")
@router.get("/")
async def admin_root(request: Request):
    if _is_admin(request):
        return _redirect("/admin/dashboard")
    return _redirect("/admin/login")


@router.get("/login")
async def admin_login_page(request: Request):
    if _is_admin(request):
        return _redirect("/admin/dashboard")

    csrf_token = ensure_csrf_token(request)
    flash = _pop_flash(request)
    return templates.TemplateResponse(
        request,
        "admin_login.html",
        {
            "csrf_token": csrf_token,
            "flash": flash,
            "admin_username": settings.admin_username,
        },
    )


@router.post("/login")
async def admin_login_submit(request: Request):
    client_ip = get_client_ip(request)
    allowed = request.app.state.login_rate_limiter.allow(
        key=f"admin_login:{client_ip}",
        limit=settings.login_rate_limit_per_minute,
        window_seconds=60,
    )
    if not allowed:
        _set_flash(request, "Zu viele Login-Versuche. Bitte kurz warten.", "error")
        return _redirect("/admin/login")

    form = await request.form()
    raw_payload: dict[str, Any] = {
        "username": form.get("username", ""),
        "password": form.get("password", ""),
        "csrf_token": form.get("csrf_token", ""),
    }

    try:
        payload = AdminLoginSchema.model_validate(raw_payload)
        validate_csrf_token(request, payload.csrf_token)
    except (ValidationError, Exception):
        _set_flash(request, "Login fehlgeschlagen.", "error")
        return _redirect("/admin/login")

    if not settings.admin_password_hash:
        _set_flash(request, "Admin-Konfiguration unvollstaendig.", "error")
        return _redirect("/admin/login")

    username_ok = payload.username == settings.admin_username
    password_ok = verify_password(payload.password, settings.admin_password_hash)

    if not (username_ok and password_ok):
        _set_flash(request, "Login fehlgeschlagen.", "error")
        return _redirect("/admin/login")

    request.session["admin_authenticated"] = True
    request.session["admin_username"] = settings.admin_username
    ensure_csrf_token(request)

    cleanup_removed = cleanup_expired_leads()
    if cleanup_removed:
        _set_flash(request, f"Login erfolgreich. Cleanup: {cleanup_removed} Datensaetze geloescht.", "success")
    else:
        _set_flash(request, "Login erfolgreich.", "success")

    return _redirect("/admin/dashboard")


@router.get("/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return _redirect("/admin/login")


@router.get("/dashboard")
async def admin_dashboard(request: Request, status_filter: str | None = None, include_deleted: int = 0):
    if not _is_admin(request):
        return _redirect("/admin/login")

    csrf_token = ensure_csrf_token(request)
    flash = _pop_flash(request)

    include_deleted_flag = bool(include_deleted)
    selected_status = status_filter if status_filter in LEAD_STATUSES else None

    leads = list_leads(status=selected_status, include_deleted=include_deleted_flag)

    return templates.TemplateResponse(
        request,
        "admin_dashboard.html",
        {
            "csrf_token": csrf_token,
            "flash": flash,
            "leads": leads,
            "statuses": LEAD_STATUSES,
            "selected_status": selected_status or "",
            "include_deleted": include_deleted_flag,
        },
    )


@router.post("/leads/{lead_id}/update")
async def admin_update_lead(request: Request, lead_id: int):
    if not _is_admin(request):
        return _redirect("/admin/login")

    form = await request.form()
    raw_payload: dict[str, Any] = {
        "status": form.get("status", ""),
        "admin_note": form.get("admin_note"),
        "csrf_token": form.get("csrf_token", ""),
    }

    try:
        payload = AdminLeadUpdateSchema.model_validate(raw_payload)
        validate_csrf_token(request, payload.csrf_token)
    except (ValidationError, Exception):
        _set_flash(request, "Aenderung konnte nicht gespeichert werden.", "error")
        return _redirect("/admin/dashboard")

    if not update_lead(lead_id=lead_id, status=payload.status, admin_note=payload.admin_note):
        _set_flash(request, "Lead nicht gefunden oder unveraendert.", "error")
        return _redirect("/admin/dashboard")

    _set_flash(request, f"Lead #{lead_id} aktualisiert.", "success")
    return _redirect("/admin/dashboard")


@router.post("/leads/{lead_id}/startmail")
async def admin_mark_startmail(request: Request, lead_id: int):
    if not _is_admin(request):
        return _redirect("/admin/login")

    form = await request.form()
    raw_payload: dict[str, Any] = {
        "csrf_token": form.get("csrf_token", ""),
        "anonymize_now": parse_bool(form.get("anonymize_now")),
    }

    try:
        payload = AdminActionSchema.model_validate(raw_payload)
        validate_csrf_token(request, payload.csrf_token)
    except (ValidationError, Exception):
        _set_flash(request, "Startmail-Aktion fehlgeschlagen.", "error")
        return _redirect("/admin/dashboard")

    if not mark_startmail_sent(lead_id=lead_id, anonymize_now=payload.anonymize_now):
        _set_flash(request, "Lead nicht gefunden.", "error")
        return _redirect("/admin/dashboard")

    if payload.anonymize_now:
        _set_flash(request, f"Lead #{lead_id} als Startmail gesendet markiert und anonymisiert.", "success")
    else:
        _set_flash(request, f"Lead #{lead_id} als Startmail gesendet markiert.", "success")
    return _redirect("/admin/dashboard")


@router.post("/leads/{lead_id}/delete")
async def admin_delete_lead(request: Request, lead_id: int):
    if not _is_admin(request):
        return _redirect("/admin/login")

    form = await request.form()
    csrf_token = str(form.get("csrf_token", ""))

    try:
        validate_csrf_token(request, csrf_token)
    except Exception:
        _set_flash(request, "Loeschaktion fehlgeschlagen.", "error")
        return _redirect("/admin/dashboard")

    if not soft_delete_lead(lead_id):
        _set_flash(request, "Lead nicht gefunden.", "error")
        return _redirect("/admin/dashboard")

    _set_flash(request, f"Lead #{lead_id} wurde geloescht/anonymisiert.", "success")
    return _redirect("/admin/dashboard")


@router.post("/export")
async def admin_export(request: Request):
    if not _is_admin(request):
        return _redirect("/admin/login")

    form = await request.form()
    csrf_token = str(form.get("csrf_token", ""))

    try:
        validate_csrf_token(request, csrf_token)
    except Exception:
        _set_flash(request, "CSV-Export fehlgeschlagen.", "error")
        return _redirect("/admin/dashboard")

    export_rows = list_leads(include_deleted=False)
    if not export_rows:
        _set_flash(request, "Keine Leads zum Export vorhanden.", "info")
        return _redirect("/admin/dashboard")

    export_path = export_leads(export_rows)
    _set_flash(request, f"CSV exportiert: {export_path.name}", "success")
    return _redirect("/admin/dashboard")


@router.post("/cleanup")
async def admin_cleanup(request: Request):
    if not _is_admin(request):
        return _redirect("/admin/login")

    form = await request.form()
    csrf_token = str(form.get("csrf_token", ""))

    try:
        validate_csrf_token(request, csrf_token)
    except Exception:
        _set_flash(request, "Cleanup fehlgeschlagen.", "error")
        return _redirect("/admin/dashboard")

    removed = cleanup_expired_leads()
    _set_flash(request, f"Cleanup abgeschlossen: {removed} Datensaetze geloescht.", "success")
    return _redirect("/admin/dashboard")
