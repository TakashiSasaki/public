from __future__ import annotations

from datetime import datetime, timezone
import time

UNIX_EPOCH_AS_FILETIME = 116444736000000000
HUNDREDS_OF_NS_PER_SECOND = 10_000_000
HUNDREDS_OF_NS_PER_HOUR = 36_000_000_000


def unix_ns_to_filetime(unix_ns: int) -> int:
    return UNIX_EPOCH_AS_FILETIME + (unix_ns // 100)


def filetime_to_unix_ns(filetime: int) -> int:
    return (filetime - UNIX_EPOCH_AS_FILETIME) * 100


def now_filetime() -> int:
    return unix_ns_to_filetime(time.time_ns())


def filetime_to_iso8601(filetime: int | None) -> str:
    if filetime is None:
        return ""
    unix_ns = filetime_to_unix_ns(filetime)
    dt = datetime.fromtimestamp(unix_ns / 1_000_000_000, tz=timezone.utc)
    return dt.isoformat(timespec="microseconds")


def iso8601_to_filetime(value: str) -> int:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    unix_ns = int(dt.timestamp() * 1_000_000_000)
    return unix_ns_to_filetime(unix_ns)

