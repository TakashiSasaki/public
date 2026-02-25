from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import os


@dataclass(slots=True)
class DesktopItem:
    item_type: str
    name: str
    path: str
    modified_at: str
    permissions: str
    size_bytes: int | None
    folder_total_size_bytes: int | None


def _iso_from_epoch(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat()


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
            files.append(
                DesktopItem(
                    item_type="file",
                    name=file_path.name,
                    path=str(file_path.resolve()),
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
            folders.append(
                DesktopItem(
                    item_type="folder",
                    name=folder_path.name,
                    path=str(folder_path.resolve()),
                    modified_at=_iso_from_epoch(stats.st_mtime),
                    permissions=oct(stats.st_mode & 0o777),
                    size_bytes=None,
                    folder_total_size_bytes=total_size,
                )
            )
            folder_sizes[root_path] = folder_sizes.get(root_path, 0) + total_size

    return sorted(files + folders, key=lambda item: item.path.lower())
