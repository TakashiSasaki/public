"""Git-related data contracts."""

from typing import List, TypedDict


class GitRepoInfo(TypedDict):
    """
    Unified information about a detected Git repository or worktree.
    Combines fields from previous GitRepoInfo and GitWorktreeInfo.
    """

    git_repo_dir: str

    is_bare: bool  # True if it's a bare repository
    is_detached: bool  # True if HEAD is detached

    # Raw HEAD content. Repositories with unreadable/missing HEAD are excluded.
    head: str

    # Detailed Git Info
    refs: List[str]  # e.g. ["refs/heads/main", "refs/remotes/origin/main"]
    remotes: List[str]  # e.g. ["origin: https://github.com/..."]


class GitWorktreeInfo(TypedDict):
    git_worktree_dir: str
    has_dot_git_file: bool #ワークツリーの中には.gitファイルがリポジトリを指すものがある。
    is_clean: bool
    has_untracked: bool
    git_repo_info: GitRepoInfo



class GitHubRepo(TypedDict):
    """
    Information about a detected GitHub repository.
    This might be merged into GitRepoInfo later, but kept separate for now.
    """

    path: str
    git_info: str


class GitHubRepoList(TypedDict):
    """A collection of GitHub repository information."""

    repos: List[GitHubRepo]
    count: int
    backend: str
    roots_found: bool




__all__ = [
    "GitRepoInfo",
    "GitWorktreeInfo",
    "GitHubRepo",
    "GitHubRepoList",
]
