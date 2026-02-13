"""File listing data contracts."""

from typing import Annotated, List, TypedDict

# Field mappings match https://purl.org/gag/schema/filelist.jsonld
FileItem = TypedDict(
    "FileItem",
    {
        "Filename": Annotated[str, "https://purl.org/gag/schema/vocab#fullPath"],
        "Size": Annotated[int, "https://schema.org/contentSize"],
        "Date Modified": Annotated[str, "https://purl.org/gag/schema/vocab#winFileTimeModified"],
        "Date Created": Annotated[str, "https://purl.org/gag/schema/vocab#winFileTimeCreated"],
        "Attributes": Annotated[int, "https://purl.org/gag/schema/vocab#fileAttributes"],
    },
)

FileList = TypedDict(
    "FileList",
    {
        "files": Annotated[List[FileItem], "https://purl.org/gag/schema/vocab#files"],
        "dirs": Annotated[List[FileItem], "https://purl.org/gag/schema/vocab#directories"],
    },
)

__all__ = ["FileItem", "FileList"]
