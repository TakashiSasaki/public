"""File listing data contracts."""

from typing import List, TypedDict

# Field mappings match https://purl.org/gag/schema/filelist.jsonld
FileItem = TypedDict(
    "FileItem",
    {
        "Filename": str,  # gag:fullPath
        "Size": int,  # schema:contentSize
        "Date Modified": str,  # gag:winFileTimeModified
        "Date Created": str,  # gag:winFileTimeCreated
        "Attributes": int,  # gag:fileAttributes
    },
)

FileList = TypedDict(
    "FileList",
    {
        "files": List[FileItem],  # gag:files
        "dirs": List[FileItem],  # gag:directories
    },
)

__all__ = ["FileItem", "FileList"]
