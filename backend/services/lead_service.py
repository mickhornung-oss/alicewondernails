from __future__ import annotations

import calendar
from datetime import datetime, timezone
from typing import Any

from backend.database import execute_insert, execute_update, fetch_all, fetch_one
from backend.models import LEAD_STATUSES
from backend.schemas import LeadCreateSchema


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_months(dt: datetime, months: int) -> datetime:
    target_month = dt.month - 1 + months
    year = dt.year + target_month // 12
    month = target_month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def create_lead(payload: LeadCreateSchema) -> int:
    created_at_dt = datetime.now(timezone.utc).replace(microsecond=0)
    created_at = created_at_dt.isoformat()
    delete_after = add_months(created_at_dt, 6).isoformat()

    return execute_insert(
        """
        INSERT INTO leads (
            created_at,
            email,
            name,
            interest,
            message,
            privacy_accepted,
            one_time_notice_accepted,
            status,
            admin_note,
            notice_sent_at,
            exported_at,
            delete_after,
            deleted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'neu', NULL, NULL, NULL, ?, NULL)
        """,
        (
            created_at,
            payload.email,
            payload.name,
            payload.interest,
            payload.message,
            1 if payload.privacy_accepted else 0,
            1 if payload.one_time_notice_accepted else 0,
            delete_after,
        ),
    )


def _row_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "email": row["email"],
        "name": row["name"],
        "interest": row["interest"],
        "message": row["message"],
        "privacy_accepted": bool(row["privacy_accepted"]),
        "one_time_notice_accepted": bool(row["one_time_notice_accepted"]),
        "status": row["status"],
        "admin_note": row["admin_note"],
        "notice_sent_at": row["notice_sent_at"],
        "exported_at": row["exported_at"],
        "delete_after": row["delete_after"],
        "deleted_at": row["deleted_at"],
    }


def list_leads(status: str | None = None, include_deleted: bool = False) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if status:
        where.append("status = ?")
        params.append(status)

    if not include_deleted:
        where.append("deleted_at IS NULL")

    query = "SELECT * FROM leads"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY created_at DESC, id DESC"

    rows = fetch_all(query, params)
    return [_row_to_dict(row) for row in rows]


def get_lead(lead_id: int) -> dict[str, Any] | None:
    row = fetch_one("SELECT * FROM leads WHERE id = ?", (lead_id,))
    if row is None:
        return None
    return _row_to_dict(row)


def update_lead(lead_id: int, status: str, admin_note: str | None) -> bool:
    if status not in LEAD_STATUSES:
        return False
    rows_changed = execute_update(
        """
        UPDATE leads
        SET status = ?, admin_note = ?
        WHERE id = ?
        """,
        (status, admin_note, lead_id),
    )
    return rows_changed > 0


def mark_startmail_sent(lead_id: int, anonymize_now: bool = False) -> bool:
    now = utc_now_iso()
    if anonymize_now:
        rows_changed = execute_update(
            """
            UPDATE leads
            SET status = 'geloescht',
                notice_sent_at = ?,
                deleted_at = ?,
                email = 'deleted+' || id || '@local.invalid',
                name = NULL,
                message = NULL,
                admin_note = COALESCE(admin_note, '') || ' | Startmail gesendet und anonymisiert'
            WHERE id = ?
            """,
            (now, now, lead_id),
        )
        return rows_changed > 0

    rows_changed = execute_update(
        """
        UPDATE leads
        SET status = 'startmail_gesendet',
            notice_sent_at = ?
        WHERE id = ?
        """,
        (now, lead_id),
    )
    return rows_changed > 0


def soft_delete_lead(lead_id: int) -> bool:
    now = utc_now_iso()
    rows_changed = execute_update(
        """
        UPDATE leads
        SET status = 'geloescht',
            deleted_at = ?,
            email = 'deleted+' || id || '@local.invalid',
            name = NULL,
            message = NULL,
            admin_note = COALESCE(admin_note, '') || ' | manuell geloescht'
        WHERE id = ?
        """,
        (now, lead_id),
    )
    return rows_changed > 0


def mark_exported(lead_ids: list[int]) -> None:
    if not lead_ids:
        return
    timestamp = utc_now_iso()
    placeholders = ",".join("?" for _ in lead_ids)
    execute_update(
        f"UPDATE leads SET exported_at = ? WHERE id IN ({placeholders})",
        [timestamp, *lead_ids],
    )
