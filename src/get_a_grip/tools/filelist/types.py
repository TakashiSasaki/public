from typing import TypedDict, List, Protocol, runtime_checkable

FileItem = TypedDict("FileItem", {
    "Filename": str,
    "Size": int,
    "Date Modified": str,
    "Date Created": str,
    "Attributes": int
})

FileList = TypedDict("FileList", {
    "files": List[FileItem],
    "dirs": List[FileItem]
})

@runtime_checkable
class FileScanner(Protocol):
    def scan(self, target: str) -> FileList:
        """Recursively scans a target and returns a FileList."""
        ...
