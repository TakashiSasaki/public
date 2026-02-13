from typing import TypedDict, Optional, List, Union


class GitRepoInfo(TypedDict):
    """
    Unified information about a detected Git repository or worktree.
    Combines fields from previous GitRepoInfo and GitWorktreeInfo.
    """
    git_repo_dir : str

    is_bare: bool      # True if it's a bare repository
    is_detached: bool  # True if HEAD is detached
    
    # Consensus status (None if undetermined or conflicting)
    head: str # HEADファイルの中身
    
    # Detailed Git Info
    refs: List[str]    # List of all refs (e.g., ["refs/heads/main", "refs/remotes/origin/main"])
    remotes: List[str] # List of remote URLs or info (e.g., ["origin: https://github.com/..."])


class GitWorktreeInfo(TypedDict):
    git_worktree_dir: str
    is_clean: bool
    has_untracked: bool
    git_repo_info: GitRepoInfo

class GitRepoList(TypedDict):
    """
    A collection of Git repository information.
    """
    repos: List[GitRepoInfo]
    count: int

class GitHubRepo(TypedDict):
    """
    Information about a detected GitHub repository.
    This might be merged into GitRepoInfo later, but kept separate for now as it uses a simpler check.
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
    roots_found: bool

class GitWorktreeList(TypedDict):
    """
    A collection of Git worktree information.
    """
    worktrees: List[GitWorktreeInfo]
    count: int
