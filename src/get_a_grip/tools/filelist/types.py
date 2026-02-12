from typing import TypedDict, List

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
