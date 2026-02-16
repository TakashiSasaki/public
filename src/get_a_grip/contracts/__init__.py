"""Data contracts shared across core logic and interface layers."""

from .filelist import FileItem, FileList
from .git import (
    GitHubRepo,
    GitHubRepoList,
    GitRepoInfo,
    GitWorktreeInfo,
    GitWorktreeList,
)

__all__ = [
    "FileItem",
    "FileList",
    "GitRepoInfo",
    "GitWorktreeInfo",
    "GitHubRepo",
    "GitHubRepoList",
    "GitWorktreeList",
]
