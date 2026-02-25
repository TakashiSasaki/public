from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from . import db
from .paths import resolve_desktop_path
from .scanner import scan_desktop_items


def initialize_database(conn: sqlite3.Connection) -> None:
    db.init_db(conn)


def refresh_inventory(conn: sqlite3.Connection, desktop_path: Path | None = None) -> tuple[Path, int]:
    target = desktop_path or resolve_desktop_path()
    items = scan_desktop_items(target)
    seen_at = datetime.now(tz=timezone.utc).isoformat()
    count = db.upsert_items(conn, items, seen_at=seen_at)
    return target, count
