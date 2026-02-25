from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PureWindowsPath
import os
import re
from urllib.parse import urlsplit


@dataclass(slots=True)
class DesktopItem:
    item_type: str
    name: str
    root: str
    path: str
    target: str | None
    modified_at: str
    permissions: str
    size_bytes: int | None
    folder_total_size_bytes: int | None


def _iso_from_epoch(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat()


def extract_root(path_text: str) -> str:
    win_drive = PureWindowsPath(path_text).drive
    if win_drive:
        return win_drive
    if "://" in path_text:
        parsed = urlsplit(path_text)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return ""


def _looks_like_absolute_path(path_text: str) -> bool:
    if PureWindowsPath(path_text).drive:
        return True
    if path_text.startswith("\\\\"):
        return True
    if path_text.startswith("//"):
        return True
    return "://" in path_text


def split_path_components(path_text: str) -> tuple[str, str, str]:
    root = extract_root(path_text)
    if not root and not _looks_like_absolute_path(path_text):
        root = "."
    rest = path_text[len(root) :] if root and path_text.startswith(root) else path_text

    if "://" in path_text:
        sep = "/"
        rest = rest.replace("\\", "/")
    else:
        sep = "\\"
        rest = re.sub(r"[\\/]+", "\\\\", rest)

    rest = rest.lstrip("\\/")
    if not rest:
        return root, sep, ""

    parts = [part for part in re.split(r"[\\/]+", rest) if part]
    if not parts:
        return root, sep, ""

    name = parts[-1]
    parent_parts = parts[:-1]
    middle = f"{sep}{sep.join(parent_parts)}{sep}" if parent_parts else sep
    return root, middle, name


def _is_junction(path: Path) -> bool:
    path_is_junction = getattr(path, "is_junction", None)
    if callable(path_is_junction):
        try:
            return bool(path_is_junction())
        except OSError:
            return False

    os_isjunction = getattr(os.path, "isjunction", None)
    if callable(os_isjunction):
        try:
            return bool(os_isjunction(path))
        except OSError:
            return False
    return False


def _safe_absolute_path(path: Path) -> str:
    try:
        return str(path.absolute())
    except OSError:
        return str(path)


def _safe_target(path: Path) -> str | None:
    is_link = path.is_symlink() or _is_junction(path)
    if not is_link:
        return None
    try:
        raw_target = os.readlink(path)
    except OSError:
        return None

    target = Path(raw_target)
    if not target.is_absolute():
        target = (path.parent / target).resolve(strict=False)
    return str(target)


def scan_desktop_items(desktop_path: Path) -> list[DesktopItem]:
    files: list[DesktopItem] = []
    folders: list[DesktopItem] = []
    folder_sizes: dict[Path, int] = {}

    for root, dirnames, filenames in os.walk(desktop_path, topdown=False, followlinks=False):
        root_path = Path(root)

        for filename in filenames:
            file_path = root_path / filename
            try:
                stats = file_path.stat()
            except OSError:
                continue
            file_size = stats.st_size
            absolute_path = _safe_absolute_path(file_path)
            root, middle_path, name = split_path_components(absolute_path)
            files.append(
                DesktopItem(
                    item_type="file",
                    name=name,
                    root=root,
                    path=middle_path,
                    target=_safe_target(file_path),
                    modified_at=_iso_from_epoch(stats.st_mtime),
                    permissions=oct(stats.st_mode & 0o777),
                    size_bytes=file_size,
                    folder_total_size_bytes=None,
                )
            )
            folder_sizes[root_path] = folder_sizes.get(root_path, 0) + file_size

        for dirname in dirnames:
            folder_path = root_path / dirname
            try:
                stats = folder_path.stat()
            except OSError:
                continue
            total_size = folder_sizes.get(folder_path, 0)
            absolute_path = _safe_absolute_path(folder_path)
            root, middle_path, name = split_path_components(absolute_path)
            folders.append(
                DesktopItem(
                    item_type="folder",
                    name=name,
                    root=root,
                    path=middle_path,
                    target=_safe_target(folder_path),
                    modified_at=_iso_from_epoch(stats.st_mtime),
                    permissions=oct(stats.st_mode & 0o777),
                    size_bytes=None,
                    folder_total_size_bytes=total_size,
                )
            )
            folder_sizes[root_path] = folder_sizes.get(root_path, 0) + total_size

    return sorted(files + folders, key=lambda item: f"{item.root}{item.path}{item.name}".lower())
