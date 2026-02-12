from typing import TypedDict, Optional, List

class GitRepoInfo(TypedDict):
    """
    Information about a detected Git repository entry (.git directory or file).
    """
    path: str
    is_file: bool
    target: Optional[str]
    is_bare: bool
    error: Optional[str]

class GitRepoList(TypedDict):
    """
    A collection of Git repository information.
    """
    repos: List[GitRepoInfo]
    count: int

class GitWorktreeInfo(TypedDict):
    """
    Information about a detected Git worktree.
    """
    path: str
    head: str
    gitpython: str
    pygit2: str
    dulwich: str

class GitWorktreeList(TypedDict):
    """
    A collection of Git worktree information.
    """
    worktrees: List[GitWorktreeInfo]
    count: int

class GitHubRepo(TypedDict):
    """
    Information about a detected GitHub repository.
    """
    path: str
    git_info: str

class GitHubRepoList(TypedDict):
    """
    A collection of GitHub repository information.
    """
    repos: List[GitHubRepo]
    count: int
    backend: str
    roots_found: bool  # Whether any 'GitHub' named folders were found
