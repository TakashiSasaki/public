from typing import TypedDict, List, Protocol, runtime_checkable

# Field mappings match https://purl.org/gag/schema/filelist.jsonld
FileItem = TypedDict("FileItem", {
    "Filename": str,       # gag:fullPath
    "Size": int,           # schema:contentSize
    "Date Modified": str,  # gag:winFileTimeModified
    "Date Created": str,   # gag:winFileTimeCreated
    "Attributes": int      # gag:fileAttributes
})

FileList = TypedDict("FileList", {
    "files": List[FileItem], # gag:files
    "dirs": List[FileItem]   # gag:directories
})

@runtime_checkable
class FileScanner(Protocol):
    def scan(self, target: str) -> FileList:
        """Recursively scans a target and returns a FileList."""
        ...
