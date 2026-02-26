from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from platformdirs import user_data_dir

# Provide thread-safe singleton-like DB wrapper for A records.
# Note: sqlite3 is thread-safe mostly if isolated, but we can also use check_same_thread=False
# and use a strict lock for write operations if needed. By default, sqlite3 connection can't be shared across threads.
# We'll use a thread-local storage or just open/close connection since traffic might not be crazy,
# or single writer model.

app_dir = Path(user_data_dir(appname="work.moukaeritai.mdns-inspector", appauthor=False))
app_dir.mkdir(parents=True, exist_ok=True)
db_path = app_dir / "mdns_records.db"

# Setup the DB on import.
def init_db() -> None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS a_records (
                name TEXT,
                ip TEXT,
                PRIMARY KEY (name, ip)
            )
            """
        )
        conn.commit()

# Ensure it's initialized
init_db()

# We need a lock when writing specifically to avoid concurrent sqlite writes issues
_write_lock = threading.Lock()

def add_a_record(name: str, ip: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO a_records (name, ip) VALUES (?, ?)",
                (name, ip)
            )
            conn.commit()

def get_all_a_records() -> list[tuple[str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ip FROM a_records ORDER BY name ASC")
        return cursor.fetchall()
