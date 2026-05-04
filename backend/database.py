from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Iterable

from backend.config import settings

_DB_LOCK = Lock()


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_parent(settings.db_path)
    connection = sqlite3.connect(settings.db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    with _DB_LOCK:
        with get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT NULL,
                    interest TEXT NULL,
                    message TEXT NULL,
                    privacy_accepted INTEGER NOT NULL,
                    one_time_notice_accepted INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'neu',
                    admin_note TEXT NULL,
                    notice_sent_at TEXT NULL,
                    exported_at TEXT NULL,
                    delete_after TEXT NOT NULL,
                    deleted_at TEXT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_leads_delete_after ON leads(delete_after)"
            )
            connection.commit()


def fetch_all(query: str, params: Iterable[Any] | None = None) -> list[sqlite3.Row]:
    with _DB_LOCK:
        with get_connection() as connection:
            cursor = connection.execute(query, tuple(params or ()))
            return cursor.fetchall()


def fetch_one(query: str, params: Iterable[Any] | None = None) -> sqlite3.Row | None:
    with _DB_LOCK:
        with get_connection() as connection:
            cursor = connection.execute(query, tuple(params or ()))
            return cursor.fetchone()


def execute_insert(query: str, params: Iterable[Any] | None = None) -> int:
    with _DB_LOCK:
        with get_connection() as connection:
            cursor = connection.execute(query, tuple(params or ()))
            connection.commit()
            return cursor.lastrowid


def execute_update(query: str, params: Iterable[Any] | None = None) -> int:
    with _DB_LOCK:
        with get_connection() as connection:
            cursor = connection.execute(query, tuple(params or ()))
            connection.commit()
            return cursor.rowcount


def execute_many(query: str, rows: Iterable[Iterable[Any]]) -> None:
    with _DB_LOCK:
        with get_connection() as connection:
            connection.executemany(query, rows)
            connection.commit()
