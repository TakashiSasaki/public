from __future__ import annotations

import sqlite3
from pathlib import Path

from . import db
from .filetime import HUNDREDS_OF_NS_PER_HOUR, now_filetime
from .paths import resolve_desktop_path
from .scanner import scan_desktop_items


def initialize_database(conn: sqlite3.Connection) -> None:
    db.init_db(conn)


def should_skip_rescan(conn: sqlite3.Connection, now_filetime_value: int | None = None) -> bool:
    latest = db.latest_last_seen_filetime(conn)
    if latest is None:
        return False
    current = now_filetime_value if now_filetime_value is not None else now_filetime()
    return latest >= current - HUNDREDS_OF_NS_PER_HOUR


def refresh_inventory(
    conn: sqlite3.Connection, scan_root: Path | None = None
) -> tuple[Path, int, bool]:
    target = scan_root or resolve_desktop_path()
    target = target.expanduser()
    if not target.exists():
        raise ValueError(f"Scan root does not exist: {target}")
    if not target.is_dir():
        raise ValueError(f"Scan root is not a directory: {target}")

    skip_allowed = scan_root is None
    if skip_allowed and should_skip_rescan(conn):
        return target, 0, True

    items = scan_desktop_items(target)
    seen_at_filetime = now_filetime()
    count = db.upsert_items(conn, items, seen_at_filetime=seen_at_filetime)
    return target, count, False
