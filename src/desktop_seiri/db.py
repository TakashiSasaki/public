from __future__ import annotations

import sqlite3
from pathlib import Path

from platformdirs import user_data_dir

from .scanner import DesktopItem

APP_NAME = "work.moukaeritai.desktop-seiri"


def _data_dir() -> Path:
    path = Path(user_data_dir(appname=APP_NAME, appauthor=None))
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return _data_dir() / "desktop_items.sqlite3"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('file', 'folder')),
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            modified_at TEXT NOT NULL,
            permissions TEXT NOT NULL,
            size_bytes INTEGER,
            folder_total_size_bytes INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
        """
    )
    _migrate_items_schema(conn)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_last_seen ON items(last_seen)")
    conn.commit()


def _migrate_items_schema(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(items)")}
    if {"first_seen", "last_seen"}.issubset(columns):
        return
    if "scanned_at" not in columns:
        return

    conn.execute(
        """
        CREATE TABLE items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('file', 'folder')),
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            modified_at TEXT NOT NULL,
            permissions TEXT NOT NULL,
            size_bytes INTEGER,
            folder_total_size_bytes INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        INSERT INTO items_new (
            item_type,
            name,
            path,
            modified_at,
            permissions,
            size_bytes,
            folder_total_size_bytes,
            first_seen,
            last_seen
        )
        SELECT
            item_type,
            name,
            path,
            modified_at,
            permissions,
            size_bytes,
            folder_total_size_bytes,
            scanned_at,
            scanned_at
        FROM items
        """
    )
    conn.execute("DROP TABLE items")
    conn.execute("ALTER TABLE items_new RENAME TO items")


def upsert_items(conn: sqlite3.Connection, items: list[DesktopItem], seen_at: str) -> int:
    conn.executemany(
        """
        INSERT INTO items (
            item_type,
            name,
            path,
            modified_at,
            permissions,
            size_bytes,
            folder_total_size_bytes,
            first_seen,
            last_seen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            item_type=excluded.item_type,
            name=excluded.name,
            modified_at=excluded.modified_at,
            permissions=excluded.permissions,
            size_bytes=excluded.size_bytes,
            folder_total_size_bytes=excluded.folder_total_size_bytes,
            last_seen=excluded.last_seen
        """,
        [
            (
                item.item_type,
                item.name,
                item.path,
                item.modified_at,
                item.permissions,
                item.size_bytes,
                item.folder_total_size_bytes,
                seen_at,
                seen_at,
            )
            for item in items
        ],
    )
    conn.commit()
    return len(items)


def search_items(
    conn: sqlite3.Connection,
    query: str = "",
    item_type: str = "all",
    limit: int = 500,
) -> list[sqlite3.Row]:
    sql = """
    SELECT
      item_type,
      name,
      path,
      modified_at,
      permissions,
      size_bytes,
      folder_total_size_bytes,
      first_seen,
      last_seen
    FROM items
    WHERE 1=1
    """
    params: list[object] = []
    if query:
        sql += " AND (name LIKE ? OR path LIKE ?)"
        like_q = f"%{query}%"
        params.extend([like_q, like_q])
    if item_type in {"file", "folder"}:
        sql += " AND item_type = ?"
        params.append(item_type)
    sql += " ORDER BY name COLLATE NOCASE ASC LIMIT ?"
    params.append(limit)
    return list(conn.execute(sql, params))
