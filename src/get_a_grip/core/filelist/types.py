"""Core-local scanner protocol and compatibility exports for filelist contracts."""

from typing import Protocol, runtime_checkable

from get_a_grip.contracts.filelist import FileItem, FileList

@runtime_checkable
class FileScanner(Protocol):
    def scan(self, target: str) -> FileList:
        """Recursively scans a target and returns a FileList."""
        ...


__all__ = ["FileItem", "FileList", "FileScanner"]
