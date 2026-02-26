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
                last_seen TEXT,
                source_ip TEXT,
                is_multicast BOOLEAN,
                PRIMARY KEY (name, ip)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS aaaa_records (
                name TEXT,
                ip TEXT,
                last_seen TEXT,
                source_ip TEXT,
                is_multicast BOOLEAN,
                PRIMARY KEY (name, ip)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS srv_records (
                name TEXT,
                target TEXT,
                port INTEGER,
                priority INTEGER,
                weight INTEGER,
                last_seen TEXT,
                source_ip TEXT,
                PRIMARY KEY (name, target, port)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ptr_records (
                name TEXT,
                ptrdname TEXT,
                last_seen TEXT,
                source_ip TEXT,
                PRIMARY KEY (name, ptrdname)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS txt_records (
                name TEXT,
                text TEXT,
                last_seen TEXT,
                source_ip TEXT,
                PRIMARY KEY (name, text)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                name TEXT,
                type TEXT,
                count INTEGER DEFAULT 1,
                last_seen TEXT,
                source_ip TEXT,
                PRIMARY KEY (name, type)
            )
            """
        )
        # Attempt to add columns to existing tables if they don't exist
        for table in ["a_records", "aaaa_records", "srv_records", "ptr_records", "txt_records"]:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN last_seen TEXT")
            except sqlite3.OperationalError: pass
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN source_ip TEXT")
            except sqlite3.OperationalError: pass
        
        for table in ["a_records", "aaaa_records"]:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN is_multicast BOOLEAN")
            except sqlite3.OperationalError: pass
            
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ui_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.commit()

# Ensure it's initialized
init_db()

# We need a lock when writing specifically to avoid concurrent sqlite writes issues
_write_lock = threading.Lock()

def add_a_record(name: str, ip: str, last_seen: str, source_ip: str, is_multicast: bool) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO a_records (name, ip, last_seen, source_ip, is_multicast) VALUES (?, ?, ?, ?, ?)",
                (name, ip, last_seen, source_ip, is_multicast)
            )
            conn.commit()

def get_all_a_records() -> list[tuple[str, str, str, str, bool]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ip, last_seen, source_ip, is_multicast FROM a_records ORDER BY last_seen DESC")
        return cursor.fetchall()


def add_aaaa_record(name: str, ip: str, last_seen: str, source_ip: str, is_multicast: bool) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO aaaa_records (name, ip, last_seen, source_ip, is_multicast) VALUES (?, ?, ?, ?, ?)",
                (name, ip, last_seen, source_ip, is_multicast)
            )
            conn.commit()

def get_all_aaaa_records() -> list[tuple[str, str, str, str, bool]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ip, last_seen, source_ip, is_multicast FROM aaaa_records ORDER BY last_seen DESC")
        return cursor.fetchall()


def add_srv_record(name: str, target: str, port: int, priority: int, weight: int, last_seen: str, source_ip: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO srv_records (name, target, port, priority, weight, last_seen, source_ip) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, target, port, priority, weight, last_seen, source_ip)
            )
            conn.commit()

def get_all_srv_records() -> list[tuple[str, str, int, int, int, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, target, port, priority, weight, last_seen, source_ip FROM srv_records ORDER BY last_seen DESC")
        return cursor.fetchall()


def add_ptr_record(name: str, ptrdname: str, last_seen: str, source_ip: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO ptr_records (name, ptrdname, last_seen, source_ip) VALUES (?, ?, ?, ?)",
                (name, ptrdname, last_seen, source_ip)
            )
            conn.commit()

def get_all_ptr_records() -> list[tuple[str, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ptrdname, last_seen, source_ip FROM ptr_records ORDER BY last_seen DESC")
        return cursor.fetchall()


def add_txt_record(name: str, text: str, last_seen: str, source_ip: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO txt_records (name, text, last_seen, source_ip) VALUES (?, ?, ?, ?)",
                (name, text, last_seen, source_ip)
            )
            conn.commit()

def get_all_txt_records() -> list[tuple[str, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, text, last_seen, source_ip FROM txt_records ORDER BY last_seen DESC")
        return cursor.fetchall()


def add_query(name: str, qtype: str, last_seen: str, source_ip: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO queries (name, type, count, last_seen, source_ip)
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(name, type) DO UPDATE SET
                    count = count + 1,
                    last_seen = excluded.last_seen,
                    source_ip = excluded.source_ip
                """,
                (name, qtype, last_seen, source_ip)
            )
            conn.commit()

def get_all_queries() -> list[tuple[str, str, int, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, count, last_seen, source_ip FROM queries ORDER BY last_seen DESC")
        return cursor.fetchall()


def set_ui_setting(key: str, value: str) -> None:
    with _write_lock:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO ui_settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()


def get_ui_setting(key: str) -> str | None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ui_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
