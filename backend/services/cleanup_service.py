from __future__ import annotations

from datetime import datetime, timezone

from backend.database import execute_update


def cleanup_expired_leads() -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    # Hard-delete all leads whose retention window ended.
    deleted_count = execute_update(
        "DELETE FROM leads WHERE delete_after <= ?",
        (now,),
    )
    return deleted_count if deleted_count >= 0 else 0
