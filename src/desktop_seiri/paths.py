from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import uuid


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


def _guid_from_uuid(value: str) -> GUID:
    u = uuid.UUID(value)
    data = u.bytes_le
    return GUID.from_buffer_copy(data)


FOLDERID_DESKTOP = _guid_from_uuid("B4BFCC3A-DB2C-424C-B029-7FE99A87C641")


def _desktop_path_from_windows_api() -> Path | None:
    """Resolve desktop path using Windows known folder API."""
    if not hasattr(ctypes, "windll"):
        return None

    ole32 = ctypes.windll.ole32
    shell32 = ctypes.windll.shell32
    co_task_mem_free = ole32.CoTaskMemFree

    path_ptr = wintypes.LPWSTR()
    shell32.SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID),
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.LPWSTR),
    ]
    shell32.SHGetKnownFolderPath.restype = ctypes.c_long

    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole32.CoTaskMemFree.restype = None

    # Signature: SHGetKnownFolderPath(REFKNOWNFOLDERID, DWORD, HANDLE, PWSTR*)
    result = shell32.SHGetKnownFolderPath(
        ctypes.byref(FOLDERID_DESKTOP),
        0,
        None,
        ctypes.byref(path_ptr),
    )
    if result != 0:
        return None

    try:
        return Path(path_ptr.value)
    finally:
        co_task_mem_free(path_ptr)


def resolve_desktop_path() -> Path:
    """Resolve a desktop path on Windows with practical fallbacks."""
    api_path = _desktop_path_from_windows_api()
    if api_path and api_path.exists():
        return api_path

    candidates = [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]
