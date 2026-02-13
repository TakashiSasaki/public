"""Data contracts shared across core logic and interface layers."""

from .filelist import FileItem, FileList
from .git import (
    GitHubRepo,
    GitHubRepoList,
    GitRepoInfo,
    GitRepoList,
    GitWorktreeInfo,
    GitWorktreeList,
)

__all__ = [
    "FileItem",
    "FileList",
    "GitRepoInfo",
    "GitWorktreeInfo",
    "GitRepoList",
    "GitHubRepo",
    "GitHubRepoList",
    "GitWorktreeList",
]
