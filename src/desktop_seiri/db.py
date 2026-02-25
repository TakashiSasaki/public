from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

from .scanner import DesktopItem, extract_root, split_path_components

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
            root TEXT NOT NULL,
            path TEXT NOT NULL,
            target TEXT,
            modified_at TEXT NOT NULL,
            permissions TEXT NOT NULL,
            size_bytes INTEGER,
            folder_total_size_bytes INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            UNIQUE(root, path, name)
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
    target_source_col = "target" if "target" in columns else "target_path"
    has_seen_columns = {"first_seen", "last_seen"}.issubset(columns)
    path_is_legacy_unique = _has_unique_index_on(conn, "items", ["path"])
    target_rename_required = "target" not in columns and "target_path" in columns
    needs_rebuild = (
        not has_seen_columns
        or "root" not in columns
        or "path" not in columns
        or target_rename_required
        or path_is_legacy_unique
    )
    if not needs_rebuild:
        _backfill_components(conn)
        return

    conn.execute("DROP TABLE IF EXISTS items_new")
    conn.execute(
        """
        CREATE TABLE items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('file', 'folder')),
            name TEXT NOT NULL,
            root TEXT NOT NULL,
            path TEXT NOT NULL,
            target TEXT,
            modified_at TEXT NOT NULL,
            permissions TEXT NOT NULL,
            size_bytes INTEGER,
            folder_total_size_bytes INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            UNIQUE(root, path, name)
        )
        """
    )

    select_cols = ["id", "item_type", "name", "path", "modified_at", "permissions"]
    if target_source_col in columns:
        select_cols.append(target_source_col)
    if "size_bytes" in columns:
        select_cols.append("size_bytes")
    if "folder_total_size_bytes" in columns:
        select_cols.append("folder_total_size_bytes")
    if "first_seen" in columns:
        select_cols.append("first_seen")
    if "last_seen" in columns:
        select_cols.append("last_seen")
    if "scanned_at" in columns:
        select_cols.append("scanned_at")

    rows = conn.execute(f"SELECT {', '.join(select_cols)} FROM items ORDER BY id").fetchall()
    for row in rows:
        row_keys = set(row.keys())
        root, middle_path, normalized_name = _normalize_components(
            root=row["root"] if "root" in row_keys else "",
            path_value=row["path"],
            name=row["name"] if "name" in row_keys else "",
        )
        target_value = row[target_source_col] if target_source_col in row_keys else None
        first_seen = (
            row["first_seen"]
            if "first_seen" in row_keys and row["first_seen"]
            else row["scanned_at"]
            if "scanned_at" in row_keys
            else ""
        )
        last_seen = (
            row["last_seen"]
            if "last_seen" in row_keys and row["last_seen"]
            else row["scanned_at"]
            if "scanned_at" in row_keys
            else first_seen
        )
        conn.execute(
            """
            INSERT INTO items_new (
                item_type,
                name,
                root,
                path,
                target,
                modified_at,
                permissions,
                size_bytes,
                folder_total_size_bytes,
                first_seen,
                last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(root, path, name) DO UPDATE SET
                item_type=excluded.item_type,
                target=excluded.target,
                modified_at=excluded.modified_at,
                permissions=excluded.permissions,
                size_bytes=excluded.size_bytes,
                folder_total_size_bytes=excluded.folder_total_size_bytes,
                first_seen=CASE
                    WHEN items_new.first_seen <= excluded.first_seen THEN items_new.first_seen
                    ELSE excluded.first_seen
                END,
                last_seen=CASE
                    WHEN items_new.last_seen >= excluded.last_seen THEN items_new.last_seen
                    ELSE excluded.last_seen
                END
            """,
            (
                row["item_type"],
                normalized_name,
                root,
                middle_path,
                target_value,
                row["modified_at"],
                row["permissions"],
                row["size_bytes"] if "size_bytes" in row_keys else None,
                row["folder_total_size_bytes"] if "folder_total_size_bytes" in row_keys else None,
                first_seen,
                last_seen,
            ),
        )

    conn.execute("DROP TABLE items")
    conn.execute("ALTER TABLE items_new RENAME TO items")


def _has_unique_index_on(conn: sqlite3.Connection, table: str, index_columns: list[str]) -> bool:
    for index_row in conn.execute(f"PRAGMA index_list({table})"):
        if not index_row["unique"]:
            continue
        idx_name = index_row["name"]
        cols = [row["name"] for row in conn.execute(f"PRAGMA index_info({idx_name})")]
        if cols == index_columns:
            return True
    return False


def _normalize_components(root: str, path_value: str, name: str) -> tuple[str, str, str]:
    if _is_full_path(path_value):
        return split_path_components(path_value)
    normalized_root = root or "."
    normalized_name = name or ""
    separator = "/" if "://" in normalized_root else "\\"
    normalized_path = _normalize_middle_path(path_value or separator, separator=separator)
    return normalized_root, normalized_path, normalized_name


def _normalize_middle_path(path_value: str, separator: str) -> str:
    if separator == "/":
        normalized = path_value.replace("\\", "/")
    else:
        normalized = path_value.replace("/", "\\")
    normalized = normalized.strip("\\/")
    if not normalized:
        return separator
    return f"{separator}{normalized}{separator}"


def _is_full_path(path_value: str) -> bool:
    if not path_value:
        return False
    if "://" in path_value:
        return True
    if path_value.startswith("\\\\") or path_value.startswith("//"):
        return True
    return bool(extract_root(path_value))


def _backfill_components(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT id, root, path, name
        FROM items
        WHERE root IS NULL
           OR root = ''
           OR path IS NULL
           OR path = ''
           OR substr(path, 1, 1) NOT IN ('\\', '/')
           OR substr(path, length(path), 1) NOT IN ('\\', '/')
        """
    ).fetchall()
    if not rows:
        return
    updates = []
    for row in rows:
        root, middle_path, name = _normalize_components(row["root"], row["path"], row["name"])
        updates.append((root, middle_path, name, row["id"]))
    conn.executemany("UPDATE items SET root = ?, path = ?, name = ? WHERE id = ?", updates)


def _validate_item_for_storage(item: DesktopItem) -> None:
    if not item.root:
        raise ValueError("Invalid item.root: root must not be empty. Use '.' for relative paths.")
    if not item.name:
        raise ValueError("Invalid item.name: name must not be empty.")
    if item.name[0] in {"\\", "/"}:
        raise ValueError(
            f"Invalid item.name '{item.name}': name must not start with a path separator."
        )
    if item.root != "." and item.root[-1] in {"\\", "/"}:
        raise ValueError(
            f"Invalid item.root '{item.root}': root must not end with a path separator."
        )
    if not item.path:
        raise ValueError("Invalid item.path: path must not be empty.")
    if item.path[0] not in {"\\", "/"}:
        raise ValueError(
            f"Invalid item.path '{item.path}': path must start with a path separator."
        )
    if item.path[-1] not in {"\\", "/"}:
        raise ValueError(
            f"Invalid item.path '{item.path}': path must end with a path separator."
        )


def upsert_items(conn: sqlite3.Connection, items: list[DesktopItem], seen_at: str) -> int:
    for item in items:
        _validate_item_for_storage(item)

    conn.executemany(
        """
        INSERT INTO items (
            item_type,
            name,
            root,
            path,
            target,
            modified_at,
            permissions,
            size_bytes,
            folder_total_size_bytes,
            first_seen,
            last_seen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(root, path, name) DO UPDATE SET
            item_type=excluded.item_type,
            root=excluded.root,
            target=excluded.target,
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
                item.root,
                item.path,
                item.target,
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
    offset: int = 0,
) -> list[sqlite3.Row]:
    sql = """
    SELECT
      item_type,
      name,
      root,
      path,
      target,
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
        sql += " AND (name LIKE ? OR root LIKE ? OR path LIKE ? OR target LIKE ?)"
        like_q = f"%{query}%"
        params.extend([like_q, like_q, like_q, like_q])
    if item_type in {"file", "folder"}:
        sql += " AND item_type = ?"
        params.append(item_type)
    sql += " ORDER BY name COLLATE NOCASE ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return list(conn.execute(sql, params))


def count_items(
    conn: sqlite3.Connection,
    query: str = "",
    item_type: str = "all",
) -> int:
    sql = """
    SELECT COUNT(*) AS cnt
    FROM items
    WHERE 1=1
    """
    params: list[object] = []
    if query:
        sql += " AND (name LIKE ? OR root LIKE ? OR path LIKE ? OR target LIKE ?)"
        like_q = f"%{query}%"
        params.extend([like_q, like_q, like_q, like_q])
    if item_type in {"file", "folder"}:
        sql += " AND item_type = ?"
        params.append(item_type)
    row = conn.execute(sql, params).fetchone()
    return int(row["cnt"]) if row else 0


def latest_last_seen(conn: sqlite3.Connection) -> datetime | None:
    row = conn.execute("SELECT MAX(last_seen) AS latest FROM items").fetchone()
    if not row:
        return None
    value = row["latest"]
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
