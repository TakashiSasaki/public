from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import db
from .paths import resolve_desktop_path
from .scanner import scan_desktop_items


def initialize_database(conn: sqlite3.Connection) -> None:
    db.init_db(conn)


def should_skip_rescan(conn: sqlite3.Connection, now: datetime | None = None) -> bool:
    latest = db.latest_last_seen(conn)
    if latest is None:
        return False
    current = now or datetime.now(tz=timezone.utc)
    return latest >= current - timedelta(hours=1)


def refresh_inventory(
    conn: sqlite3.Connection, desktop_path: Path | None = None
) -> tuple[Path, int, bool]:
    target = desktop_path or resolve_desktop_path()
    if should_skip_rescan(conn):
        return target, 0, True
    items = scan_desktop_items(target)
    seen_at = datetime.now(tz=timezone.utc).isoformat()
    count = db.upsert_items(conn, items, seen_at=seen_at)
    return target, count, False
