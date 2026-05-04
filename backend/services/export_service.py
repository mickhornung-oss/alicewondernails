from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings
from backend.services.lead_service import mark_exported


def export_leads(rows: list[dict]) -> Path:
    settings.export_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = settings.export_dir / f"leads_export_{timestamp}.csv"

    fieldnames = [
        "id",
        "created_at",
        "email",
        "name",
        "interest",
        "message",
        "privacy_accepted",
        "one_time_notice_accepted",
        "status",
        "admin_note",
        "notice_sent_at",
        "exported_at",
        "delete_after",
        "deleted_at",
    ]

    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})

    mark_exported([row["id"] for row in rows if row.get("id") is not None])
    return output_path
